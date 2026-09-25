"""Playwright automation for creating an unpublished Medium story draft."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from .models import Article, DisplayEquation, Figure, Footnote, Link, Paragraph, PullQuote, SectionHeading

NEW_STORY_URL = "https://medium.com/new-story"
_LINK_MARKDOWN = re.compile(r"\[([^]]+)\]\(([^)]+)\)")


class MediumBrowserError(RuntimeError):
    """A clear failure while creating a draft in the Medium editor."""

    def __init__(self, message: str, session: BrowserSession | None = None):
        super().__init__(message)
        self.session = session


class MediumLoginRequired(MediumBrowserError):
    """The persistent browser profile needs a manual Medium login."""


@dataclass
class BrowserSession:
    """Open persistent browser objects retained while the draft is reviewed."""

    playwright: Any
    context: Any
    page: Any
    profile_dir: Path

    def wait_until_closed(self) -> None:
        """Keep the headed browser connected until the user closes its page."""
        self.page.wait_for_event("close", timeout=0)


def profile_directory(article_path: str | Path) -> Path:
    """Return the portable persistent profile location beside the supplied article."""
    return Path(article_path).expanduser().resolve().parent / ".medium_browser_profile"


def _playwright_factory() -> Any:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise MediumBrowserError("Playwright is required for draft upload. Install the project requirements first.") from exc
    return sync_playwright()


def _start_session(article: Article, playwright_factory: Callable[[], Any] | None = None) -> BrowserSession:
    profile_dir = profile_directory(article.source_path)
    profile_dir.mkdir(parents=True, exist_ok=True)
    playwright = (playwright_factory or _playwright_factory)().start()
    try:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
        )
    except Exception as exc:
        playwright.stop()
        raise MediumBrowserError(
            f"Could not launch headed Chromium with the local profile at {profile_dir}: {exc}. "
            "Install the Playwright Chromium browser on this machine and retry."
        ) from exc
    page = context.pages[0] if context.pages else context.new_page()
    return BrowserSession(playwright=playwright, context=context, page=page, profile_dir=profile_dir)


def _visible(locator: Any) -> bool:
    try:
        return locator.count() > 0 and locator.first.is_visible()
    except Exception:
        return False


def _first_visible(candidates: Iterable[Any]) -> Any | None:
    for candidate in candidates:
        if _visible(candidate):
            return candidate.first
    return None


def _get_by_role(page: Any, role: str, name: str, *, exact: bool = True) -> Any:
    return page.get_by_role(role, name=name, exact=exact)


def _editable(page: Any, label: str) -> Any:
    """Find a named editor field through accessible names or semantic attributes."""
    name = re.compile(re.escape(label), re.IGNORECASE)
    candidates = [
        page.get_by_role("textbox", name=name),
        page.get_by_label(name),
        page.locator(f'[contenteditable="true"][aria-label*="{label}" i]'),
        page.locator(f'[contenteditable="true"][data-placeholder*="{label}" i]'),
    ]
    locator = _first_visible(candidates)
    if locator is not None:
        return locator
    raise MediumBrowserError(f"Could not find the Medium {label.lower()} editor control.")


class MediumDraftEditor:
    """Writes prepared typed blocks into Medium's story editor."""

    def __init__(self, page: Any):
        self.page = page
        self.keyboard = page.keyboard
        self.title_field: Any | None = None
        self.body_field: Any | None = None

    def populate(self, article: Article) -> None:
        self.title_field = _editable(self.page, "Title")
        self.body_field = _editable(self.page, "Tell your story")
        self.title_field.fill(article.title)
        self.body_field.click()
        if article.subtitle:
            self._type_plain_text(article.subtitle)
            self.keyboard.press("Enter")
        for block in article.blocks:
            if isinstance(block, Paragraph):
                self._paragraph(block)
            elif isinstance(block, SectionHeading):
                self.keyboard.press("Control+Alt+2")
                self._type_plain_text(block.text)
                self.keyboard.press("Enter")
            elif isinstance(block, Figure):
                self._figure(block)
            elif isinstance(block, DisplayEquation):
                self._image(block.rendered_path)
                self.keyboard.press("Enter")
            elif isinstance(block, PullQuote):
                # Medium's documented quote shortcut toggles from a quote to a
                # pull-out quote on its second use.
                self.keyboard.press("Control+Alt+5")
                self.keyboard.press("Control+Alt+5")
                self._type_plain_text(block.text)
                self.keyboard.press("Enter")
            else:
                raise MediumBrowserError(f"Unsupported prepared block type: {type(block).__name__}.")
        if article.footnotes:
            if not any(isinstance(block, SectionHeading) and block.text.casefold() == "notes" for block in article.blocks):
                self.keyboard.press("Control+Alt+2")
                self._type_plain_text("Notes")
                self.keyboard.press("Enter")
            for note in article.footnotes:
                self._type_plain_text(f"{note.marker} {note.text}")
                self.keyboard.press("Enter")

    def wait_until_saved(self, timeout_ms: int = 30_000) -> None:
        saved = self.page.get_by_text(re.compile(r"\bSaved\b", re.IGNORECASE))
        saved.first.wait_for(state="visible", timeout=timeout_ms)

    def _type_plain_text(self, text: str) -> None:
        self.keyboard.insert_text(text)

    def _paragraph(self, paragraph: Paragraph) -> None:
        matches = list(_LINK_MARKDOWN.finditer(paragraph.text))
        if not matches or not paragraph.links:
            self._type_plain_text(paragraph.text)
        else:
            self._type_paragraph_with_links(paragraph.text, paragraph.links, matches)
        self.keyboard.press("Enter")

    def _type_paragraph_with_links(self, text: str, links: list[Link], matches: list[re.Match[str]]) -> None:
        link_index = 0
        cursor = 0
        for match in matches:
            self._type_plain_text(text[cursor:match.start()])
            label, target = match.groups()
            authored_link = links[link_index] if link_index < len(links) else None
            if authored_link is None or authored_link.text != label or authored_link.target != target:
                self._type_plain_text(match.group(0))
            else:
                self._type_plain_text(label)
                self._select_recent_text(label)
                self.keyboard.press("Control+K")
                self._apply_link(target)
                link_index += 1
            cursor = match.end()
        self._type_plain_text(text[cursor:])

    def _select_recent_text(self, text: str) -> None:
        for _ in text:
            self.keyboard.press("Shift+ArrowLeft")

    def _apply_link(self, target: str) -> None:
        name = re.compile(r"link|url", re.IGNORECASE)
        field = _first_visible([
            self.page.get_by_role("textbox", name=name),
            self.page.get_by_placeholder(name),
        ])
        if field is None:
            raise MediumBrowserError("Medium opened no accessible link destination field after the link shortcut.")
        field.fill(target)
        field.press("Enter")
        self.keyboard.press("ArrowRight")

    def _open_image_picker(self) -> None:
        # Medium exposes the insertion action as an accessible image button or
        # menu item. We never click an unlabeled/nearby control as a fallback.
        direct = _first_visible([_get_by_role(self.page, "button", "Add an image")])
        if direct is not None:
            direct.click()
            return
        image = _first_visible([
            _get_by_role(self.page, "button", "Image"),
            _get_by_role(self.page, "menuitem", "Image"),
        ])
        if image is not None:
            image.click()
            return
        add_block = _first_visible([
            _get_by_role(self.page, "button", "Add a block"),
            _get_by_role(self.page, "button", "Insert block"),
        ])
        if add_block is None:
            raise MediumBrowserError("Could not find Medium's accessible image upload control.")
        add_block.click()
        image = _first_visible([
            _get_by_role(self.page, "button", "Image"),
            _get_by_role(self.page, "menuitem", "Image"),
        ])
        if image is None:
            raise MediumBrowserError("Medium's image menu did not expose an accessible Image action.")
        image.click()

    def _image(self, image_path: Path) -> None:
        if not image_path.is_file():
            raise MediumBrowserError(f"Prepared image file does not exist: {image_path}")
        before = self.page.get_by_role("img").count()
        try:
            with self.page.expect_file_chooser(timeout=8_000) as chooser_info:
                self._open_image_picker()
            chooser_info.value.set_files(str(image_path))
        except MediumBrowserError:
            raise
        except Exception as exc:
            raise MediumBrowserError(f"Medium image upload control failed for {image_path}: {exc}") from exc
        images = self.page.get_by_role("img")
        images.nth(max(before, 0)).wait_for(state="visible", timeout=30_000)

    def _figure(self, figure: Figure) -> None:
        self._image(figure.source_path)
        image = self.page.get_by_role("img").last
        image.click()
        if figure.alt_text:
            alt_button = _first_visible([_get_by_role(self.page, "button", "Alt text")])
            if alt_button is not None:
                alt_button.click()
                alt_field = _first_visible([
                    self.page.get_by_role("textbox", name=re.compile("alt text", re.IGNORECASE)),
                    self.page.get_by_label(re.compile("alt text", re.IGNORECASE)),
                ])
                if alt_field is None:
                    raise MediumBrowserError("Medium opened image settings but no accessible alt-text field was found.")
                alt_field.fill(figure.alt_text)
                save = _first_visible([_get_by_role(self.page, "button", "Save"), _get_by_role(self.page, "button", "Done")])
                if save is not None:
                    save.click()
                else:
                    alt_field.press("Enter")
        caption_parts = [part for part in (figure.caption, f"Source: {figure.source_attribution}" if figure.source_attribution else None) if part]
        if caption_parts:
            self.page.get_by_role("img").last.click()
            self._type_plain_text(" — ".join(caption_parts))
        self.keyboard.press("Enter")


def _is_login_page(page: Any) -> bool:
    if re.search(r"/(?:m/)?(?:sign-?in|login)(?:[/?#]|$)", getattr(page, "url", ""), re.IGNORECASE):
        return True
    return _visible(page.get_by_role("button", name=re.compile(r"sign in|log in", re.IGNORECASE)))


def _save_failure_screenshot(session: BrowserSession, article: Article) -> Path | None:
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        screenshot_dir = article.build_dir / "browser_failures"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot = screenshot_dir / f"medium_failure_{timestamp}.png"
        session.page.screenshot(path=str(screenshot), full_page=True)
        return screenshot
    except Exception:
        return None


def upload_article(
    article: Article,
    *,
    session_factory: Callable[[Article], BrowserSession] | None = None,
    editor_factory: Callable[[Any], MediumDraftEditor] | None = None,
) -> BrowserSession:
    """Create and leave open an unpublished draft from a prepared article."""
    try:
        session = (session_factory or _start_session)(article)
    except MediumBrowserError:
        raise
    except Exception as exc:
        raise MediumBrowserError(f"Could not start the local Medium browser session: {exc}") from exc
    try:
        session.page.goto(NEW_STORY_URL, wait_until="domcontentloaded")
        if _is_login_page(session.page):
            raise MediumLoginRequired(
                "Medium is not logged in for this local browser profile. Log in manually in the open browser, then rerun the command.",
                session=session,
            )
        editor = (editor_factory or MediumDraftEditor)(session.page)
        editor.populate(article)
        editor.wait_until_saved()
        return session
    except MediumLoginRequired as exc:
        exc.session = session
        screenshot = _save_failure_screenshot(session, article)
        if screenshot:
            exc.args = (f"{exc}. Screenshot: {screenshot}",)
        raise
    except MediumBrowserError as exc:
        exc.session = session
        screenshot = _save_failure_screenshot(session, article)
        if screenshot:
            exc.args = (f"{exc}. Screenshot: {screenshot}",)
        raise
    except Exception as exc:
        screenshot = _save_failure_screenshot(session, article)
        detail = f"Medium draft creation failed: {exc}"
        if screenshot:
            detail += f". Screenshot: {screenshot}"
        raise MediumBrowserError(detail, session=session) from exc
