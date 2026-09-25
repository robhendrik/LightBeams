import ast
import importlib.util
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from medium_uploader import medium_browser
from medium_uploader.models import Article, DisplayEquation, Figure, Footnote, Paragraph, PullQuote, SectionHeading


def prepared_article(tmp_path: Path) -> Article:
    source = tmp_path / "posts" / "article.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    return Article(
        source_path=source,
        title="A Draft",
        subtitle="A short subtitle",
        metadata={},
        blocks=[Paragraph("First."), SectionHeading("A Section"), PullQuote("A quote.")],
        footnotes=[],
        build_dir=source.parent / ".medium_build" / "article-id",
    )


class FakeLocator:
    first = None

    def __init__(self):
        self.first = self
        self.clicked = False

    def count(self):
        return 0

    def is_visible(self):
        return False


class FakePage:
    url = "about:blank"

    def __init__(self):
        self.visited = []
        self.screenshots = []

    def goto(self, url, **kwargs):
        self.visited.append((url, kwargs))
        if "signin" not in self.url:
            self.url = url

    def get_by_role(self, *args, **kwargs):
        return FakeLocator()

    def screenshot(self, *, path, **kwargs):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"fake screenshot")
        self.screenshots.append(target)


class ShapeElement:
    def __init__(self, role, events, index):
        self.role = role
        self.events = events
        self.index = index
        self.first = self

    def count(self):
        return 1

    def is_visible(self):
        return True

    def get_attribute(self, name):
        return self.role if name == "role" else None

    def evaluate(self, _expression):
        return "div"

    def fill(self, text):
        self.events.append(("fill", self.index, text))

    def click(self):
        self.events.append(("click", self.index))


class ShapeCollection:
    def __init__(self, items):
        self.items = items

    def count(self):
        return len(self.items)

    def nth(self, index):
        return self.items[index]


class EmptyLocator:
    first = None

    def __init__(self):
        self.first = self

    def count(self):
        return 0

    def is_visible(self):
        return False


class ObservedEditorPage(FakePage):
    def __init__(self, roles):
        super().__init__()
        self.events = []
        self.editors = ShapeCollection([ShapeElement(role, self.events, index) for index, role in enumerate(roles)])
        self.keyboard = type("Keyboard", (), {
            "insert_text": lambda _, text: self.events.append(("text", text)),
            "press": lambda _, key: self.events.append(("key", key)),
        })()

    def get_by_label(self, *args, **kwargs):
        return EmptyLocator()

    def locator(self, selector):
        if selector == '[contenteditable="true"]':
            return self.editors
        return EmptyLocator()


class FakeSession:
    def __init__(self, page):
        self.page = page
        self.context = object()
        self.playwright = object()
        self.profile_dir = Path(".medium_browser_profile")
        self.waited_until_closed = False

    def wait_until_closed(self):
        self.waited_until_closed = True


def test_profile_is_portable_and_next_to_the_article(tmp_path):
    article = prepared_article(tmp_path)
    profile = medium_browser.profile_directory(article.source_path)
    assert profile == article.source_path.parent / ".medium_browser_profile"
    assert "workspaces" not in str(profile).lower()


def test_exact_live_dom_shape_uses_first_contenteditable_for_title_and_second_for_body(tmp_path):
    article = prepared_article(tmp_path)
    page = ObservedEditorPage(["textbox", None])
    medium_browser.MediumDraftEditor(page).populate(article)
    assert ("fill", 0, "A Draft") in page.events
    assert ("click", 1) in page.events
    assert ("text", "A short subtitle") in page.events


@pytest.mark.parametrize(
    ("roles", "message"),
    [
        (["textbox"], "expected exactly 2"),
        ([None, None], "expected 'textbox'"),
        (["textbox", None, None], "expected exactly 2"),
    ],
)
def test_contenteditable_fallback_rejects_ambiguous_dom(roles, message):
    with pytest.raises(medium_browser.MediumBrowserError, match=message):
        medium_browser._editor_fields(ObservedEditorPage(roles))


def test_failed_editor_discovery_saves_screenshot_and_diagnostics(tmp_path):
    article = prepared_article(tmp_path)
    page = ObservedEditorPage([None, None])
    session = FakeSession(page)
    with pytest.raises(medium_browser.MediumBrowserError, match="expected 'textbox'"):
        medium_browser.upload_article(article, session_factory=lambda _: session)
    failure_dir = article.build_dir / "browser_failures"
    assert list(failure_dir.glob("*.png"))
    diagnostics = list(failure_dir.glob("*.txt"))
    assert diagnostics
    report = diagnostics[0].read_text(encoding="utf-8")
    assert "contenteditable_count: 2" in report
    assert "candidate_0: tag=div, role=None" in report


def test_launch_uses_persistent_profile_and_headed_browser(tmp_path):
    article = prepared_article(tmp_path)
    page = FakePage()
    context = type("Context", (), {"pages": [page]})()
    captured = {}

    class Chromium:
        def launch_persistent_context(self, **kwargs):
            captured.update(kwargs)
            return context

    class Playwright:
        chromium = Chromium()

        def stop(self):
            captured["stopped"] = True

    class Starter:
        def start(self):
            return Playwright()

    session = medium_browser._start_session(article, playwright_factory=Starter)
    assert captured["user_data_dir"] == str(article.source_path.parent / ".medium_browser_profile")
    assert captured["headless"] is False
    assert session.page is page


def test_upload_orchestration_passes_prepared_article_and_leaves_browser_open(tmp_path):
    article = prepared_article(tmp_path)
    page = FakePage()
    session = FakeSession(page)
    observed = []

    class Editor:
        def __init__(self, editor_page):
            assert editor_page is page

        def populate(self, passed_article):
            observed.extend(passed_article.blocks)

        def wait_until_saved(self):
            observed.append("saved")

    result = medium_browser.upload_article(
        article,
        session_factory=lambda _: session,
        editor_factory=Editor,
    )
    assert result is session
    assert page.visited == [(medium_browser.NEW_STORY_URL, {"wait_until": "domcontentloaded"})]
    assert observed == [*article.blocks, "saved"]
    assert not session.waited_until_closed


def test_writer_dispatches_prepared_blocks_in_document_order(tmp_path, monkeypatch):
    article = prepared_article(tmp_path)
    article.blocks = [
        Paragraph("Paragraph"), SectionHeading("Heading"),
        Figure("image alt", article.source_path.parent / "figure.png", "Caption", "Alt", "Source"),
        DisplayEquation("x^2", article.source_path.parent / "equation.png"),
        PullQuote("Quote"),
    ]
    article.footnotes = [Footnote("1", "A note", "¹")]
    events = []

    class Keyboard:
        def press(self, key):
            events.append(("key", key))

        def insert_text(self, text):
            events.append(("text", text))

    class Page:
        keyboard = Keyboard()

    class Field:
        def __init__(self, label):
            self.label = label

        def fill(self, text):
            events.append(("fill", self.label, text))

        def click(self):
            events.append(("click", self.label))

    monkeypatch.setattr(medium_browser, "_editor_fields", lambda page: (Field("Title"), Field("Body")))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_paragraph", lambda self, block: events.append(("paragraph", block.text)))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_figure", lambda self, block: events.append(("figure", block.caption)))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_image", lambda self, path: events.append(("equation", path.name)))

    medium_browser.MediumDraftEditor(Page()).populate(article)
    important = [event for event in events if event[0] in {"paragraph", "figure", "equation", "text"}]
    assert important == [
        ("text", "A short subtitle"),
        ("paragraph", "Paragraph"),
        ("text", "Heading"),
        ("figure", "Caption"),
        ("equation", "equation.png"),
        ("text", "Quote"),
        ("text", "Notes"),
        ("text", "¹ A note"),
    ]


def test_login_required_leaves_open_session_and_saves_screenshot(tmp_path):
    article = prepared_article(tmp_path)
    page = FakePage()
    session = FakeSession(page)
    page.url = "https://medium.com/m/signin"
    with pytest.raises(medium_browser.MediumLoginRequired, match="Log in manually") as raised:
        medium_browser.upload_article(article, session_factory=lambda _: session)
    assert raised.value.session is session
    assert len(page.screenshots) == 1
    assert page.screenshots[0].is_relative_to(article.build_dir)


def test_browser_module_contains_no_publication_controls_or_actions():
    source = Path(medium_browser.__file__).read_text(encoding="utf-8").casefold()
    assert not re.search(r"\b(?:publish|publishing|submit|submission)\b", source)
    tree = ast.parse(source)
    called_methods = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "publish" not in called_methods
    assert "submit" not in called_methods


def test_cli_default_mode_invokes_draft_upload_only(tmp_path, monkeypatch, capsys):
    article_path = tmp_path / "article.md"
    article_path.write_text("# Title\n\n### Subtitle\n\nText.\n", encoding="utf-8")
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "upload_medium.py"
    spec = importlib.util.spec_from_file_location("upload_medium_default_test", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    class Session:
        waited = False

        def wait_until_closed(self):
            self.waited = True

    session = Session()
    monkeypatch.setattr(medium_browser, "upload_article", lambda prepared: session)
    assert module.main([str(article_path)]) == 0
    output = capsys.readouterr().out
    assert "Draft created successfully." in output
    assert "No publication or submission action was performed." in output
    assert "Review the open Medium draft manually." in output
    assert session.waited
