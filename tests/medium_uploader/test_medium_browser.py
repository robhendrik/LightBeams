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

    def is_editable(self):
        return True

    def wait_for(self, *, state, timeout):
        self.events.append(("wait_for", self.index, state, timeout))

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
        self.second_available = len(items) > 1

    def count(self):
        return len(self.items)

    def nth(self, index):
        return self.items[index]

    @property
    def first(self):
        return self.items[0]


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
        self.selectors = []
        self.keyboard = type("Keyboard", (), {
            "insert_text": lambda _, text: self.events.append(("text", text)),
            "press": lambda _, key: self.events.append(("key", key)),
        })()

    def get_by_label(self, *args, **kwargs):
        return EmptyLocator()

    def locator(self, selector):
        self.selectors.append(selector)
        if selector in {'[contenteditable="true"]', '[contenteditable="true"][role="textbox"]'}:
            return self.editors
        return EmptyLocator()


class DelayedBodyPage(ObservedEditorPage):
    def __init__(self):
        super().__init__(["textbox"])

        class Keyboard:
            def insert_text(inner_self, text):
                self.events.append(("text", text))

            def press(inner_self, key):
                self.events.append(("key", key))
                if key == "Enter" and len(self.editors.items) == 1:
                    self.editors.items.append(ShapeElement(None, self.events, 1))
                    self.editors.second_available = True

        self.keyboard = Keyboard()

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


def test_main_editor_uses_single_semantic_story_surface():
    page = ObservedEditorPage(["textbox"])
    assert medium_browser._main_editor(page) is page.editors.first
    assert page.selectors == ['[contenteditable="true"][role="textbox"]']


@pytest.mark.parametrize(
    ("roles", "message"),
    [
        ([], "expected exactly one"),
        (["textbox", "textbox"], "expected exactly one"),
    ],
)
def test_main_editor_rejects_ambiguous_dom(roles, message):
    with pytest.raises(medium_browser.MediumBrowserError, match=message):
        medium_browser._main_editor(ObservedEditorPage(roles))


def test_single_initial_contenteditable_is_accepted_as_story_editor():
    page = ObservedEditorPage(["textbox"])
    assert medium_browser._main_editor(page) is page.editors.nth(0)


def test_title_enters_next_block_before_subtitle_without_clicking_second_editor(tmp_path, monkeypatch):
    article = prepared_article(tmp_path)
    page = ObservedEditorPage(["textbox"])
    page.get_by_test_id = lambda testid: FakeTestIdCollection(page.events, testid)
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "wait_until_saved", lambda self: page.events.append(("saved",)))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_wait_for_new_paragraph", lambda self: page.events.append(("next_block_ready",)))
    article.blocks = []
    medium_browser.MediumDraftEditor(page).populate(article)
    assert page.events.index(("click", 0)) < page.events.index(("text", "A Draft"))
    enter_index = page.events.index(("key", "Enter"))
    ready_index = page.events.index(("next_block_ready",))
    assert enter_index < ready_index < page.events.index(("saved",))
    assert page.events.index(("text", "A short subtitle")) > ready_index
    assert ("key", "Control+Alt+2") in page.events
    assert page.events.count(("click", 0)) == 1


class FakeTestIdCollection:
    def __init__(self, events, testid):
        self.events = events
        self.testid = testid

    @property
    def first(self):
        return self

    @property
    def last(self):
        return self

    def nth(self, index):
        return self

    def count(self):
        return 1

    def wait_for(self, *, state, timeout):
        self.events.append(("testid_wait", self.testid, state, timeout))


def test_subtitle_is_formatted_after_keyboard_insertion(tmp_path, monkeypatch):
    article = prepared_article(tmp_path)
    article.blocks = []
    page = ObservedEditorPage(["textbox"])
    page.get_by_test_id = lambda testid: FakeTestIdCollection(page.events, testid)
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "wait_until_saved", lambda self: None)
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_wait_for_new_paragraph", lambda self: None)
    medium_browser.MediumDraftEditor(page).populate(article)
    subtitle = page.events.index(("text", "A short subtitle"))
    styled = page.events.index(("key", "Control+Alt+2"))
    verified = page.events.index(("testid_wait", "editorSubtitleParagraph", "visible", 15_000))
    assert subtitle < styled < verified


def test_paragraph_uses_keyboard_text_and_enter(monkeypatch):
    events = []

    class Keyboard:
        def insert_text(self, text):
            events.append(("text", text))

        def press(self, key):
            events.append(("key", key))

    editor = medium_browser.MediumDraftEditor(type("Page", (), {"keyboard": Keyboard()})())
    monkeypatch.setattr(editor, "_enter_new_paragraph", lambda: events.append(("next",)))
    editor._paragraph(Paragraph("Body text"))
    assert events == [("text", "Body text"), ("next",)]


def test_heading_and_pull_quote_use_medium_format_shortcuts(tmp_path, monkeypatch):
    article = prepared_article(tmp_path)
    article.blocks = [SectionHeading("Heading"), PullQuote("Quote")]
    events = []

    class Keyboard:
        def insert_text(self, text):
            events.append(("text", text))

        def press(self, key):
            events.append(("key", key))

    class Story:
        def click(self):
            events.append(("focus_story",))

    page = type("Page", (), {"keyboard": Keyboard()})()
    monkeypatch.setattr(medium_browser, "_main_editor", lambda _page: Story())
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_wait_for_testid", lambda self, testid, **kwargs: events.append(("state", testid)))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_wait_for_new_paragraph", lambda self: None)
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_enter_new_paragraph", lambda self: None)
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "wait_until_saved", lambda self: None)
    article.subtitle = ""
    medium_browser.MediumDraftEditor(page).populate(article)
    assert events.count(("key", "Control+Alt+1")) == 1
    assert events.count(("key", "Control+Alt+5")) == 2
    assert ("state", "editorHeadingText") in events
    assert ("state", "editorParagraphText") in events


def test_figure_uses_alt_settings_and_combines_caption_with_source(tmp_path, monkeypatch):
    events = []

    class VisibleControl:
        def __init__(self, label):
            self.label = label

        @property
        def first(self):
            return self

        def count(self):
            return 1

        def is_visible(self):
            return True

        def click(self):
            events.append(("click", self.label))

        def fill(self, text):
            events.append(("fill", self.label, text))

        def press(self, key):
            events.append(("press", self.label, key))

        def wait_for(self, **kwargs):
            events.append(("wait", self.label, kwargs["state"]))

    class ImageFigure:
        def get_by_role(self, role):
            assert role == "img"
            return VisibleControl("image")

        def locator(self, selector):
            assert selector == "figcaption"
            return VisibleControl("caption")

    class Page:
        keyboard = type("Keyboard", (), {"insert_text": lambda self, text: events.append(("text", text))})()

        def get_by_role(self, role, name, **kwargs):
            return VisibleControl(str(name))

        def get_by_label(self, name):
            return VisibleControl(str(name))

    editor = medium_browser.MediumDraftEditor(Page())
    monkeypatch.setattr(editor, "_image", lambda path: ImageFigure())
    monkeypatch.setattr(editor, "_focus_next_paragraph", lambda: events.append(("focus_next",)))
    editor._figure(Figure("image", tmp_path / "image.png", "A caption.", "Helpful alt text", "Image by author"))
    assert ("fill", "re.compile('alt text', re.IGNORECASE)", "Helpful alt text") in events
    assert ("text", "A caption. Source: Image by author") in events
    assert ("focus_next",) in events


def test_image_insertion_waits_for_medium_figure_and_uploads_file(tmp_path, monkeypatch):
    events = []
    image = tmp_path / "equation_001.png"
    image.write_bytes(b"png")

    class FigureLocator:
        def wait_for(self, **kwargs):
            events.append(("figure_wait", kwargs["state"]))

    class Figures:
        def count(self):
            return 0

        def nth(self, index):
            assert index == 0
            return FigureLocator()

    class Chooser:
        def set_files(self, path):
            events.append(("file", path))

    class ChooserExpectation:
        value = Chooser()

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    class Page:
        keyboard = object()

        def get_by_test_id(self, testid):
            assert testid == "editorImageParagraph"
            return Figures()

        def expect_file_chooser(self, **kwargs):
            events.append(("chooser_wait", kwargs["timeout"]))
            return ChooserExpectation()

    editor = medium_browser.MediumDraftEditor(Page())
    monkeypatch.setattr(editor, "_open_image_picker", lambda: events.append(("open_picker",)))
    editor._image(image)
    assert events == [
        ("chooser_wait", 8_000), ("open_picker",), ("file", str(image)),
        ("figure_wait", "visible"),
    ]


def test_failed_editor_discovery_saves_screenshot_and_diagnostics(tmp_path):
    article = prepared_article(tmp_path)
    page = ObservedEditorPage([None, None])
    session = FakeSession(page)
    with pytest.raises(medium_browser.MediumBrowserError, match="expected exactly one"):
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

        def type(self, text, *, delay):
            events.append(("type", text, delay))

    class Page:
        keyboard = Keyboard()

    class Field:
        def __init__(self, label):
            self.label = label

        def fill(self, text):
            events.append(("fill", self.label, text))

        def click(self):
            events.append(("click", self.label))

        def inner_text(self):
            raise RuntimeError("mock does not expose rendered text")

    monkeypatch.setattr(medium_browser, "_main_editor", lambda page: Field("Story"))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "wait_until_saved", lambda self: events.append(("saved",)))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_wait_for_testid", lambda self, testid, **kwargs: events.append(("state", testid)))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_wait_for_new_paragraph", lambda self: events.append(("next_paragraph",)))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_enter_new_paragraph", lambda self: events.append(("enter_paragraph",)))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_paragraph", lambda self, block: events.append(("paragraph", block.text)))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_figure", lambda self, block: events.append(("figure", block.caption)))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_image", lambda self, path: events.append(("equation", path.name)))
    monkeypatch.setattr(medium_browser.MediumDraftEditor, "_focus_next_paragraph", lambda self: events.append(("focus_next",)))

    medium_browser.MediumDraftEditor(Page()).populate(article)
    important = [event for event in events if event[0] in {"paragraph", "figure", "equation", "text", "saved"}]
    assert important == [
        ("text", "A Draft"),
        ("saved",),
        ("text", "A short subtitle"),
        ("paragraph", "Paragraph"),
        ("text", "Heading"),
        ("figure", "Caption"),
        ("equation", "equation.png"),
        ("text", "Quote"),
        ("text", "Notes"),
        ("text", "¹ A note"),
    ]


def test_keyboard_input_falls_back_to_type_when_insert_text_fails():
    events = []

    class Keyboard:
        def insert_text(self, text):
            events.append(("insert_text", text))
            raise RuntimeError("insert_text unavailable")

        def type(self, text, *, delay):
            events.append(("type", text, delay))

    editor = medium_browser.MediumDraftEditor(type("Page", (), {"keyboard": Keyboard()})())
    editor._type_plain_text("Title")
    assert events == [
        ("insert_text", "Title"),
        ("type", "Title", 15),
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
