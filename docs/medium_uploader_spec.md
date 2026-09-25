# Medium Uploader Specification

## 1. Purpose

The Medium uploader converts an authoritative Markdown article into a **saved Medium draft** using browser automation.

The Markdown source is always authoritative and must never be modified by the tool.

The tool is intentionally limited to the common publication workflow. Rare or ambiguous formatting may be left for a short manual review in Medium rather than over-automated.

The uploader must never publish an article, submit an article to a publication, or otherwise trigger any irreversible publishing action.

---

## 2. Design Principles

1. **Markdown is authoritative**
   - The input `.md` file is never rewritten.
   - Validation, preparation and upload operate on an in-memory representation and generated build assets only.

2. **Portable filesystem assumptions**
   - The caller always supplies the path to the article.
   - All relative resources referenced by the article are resolved relative to the article file.
   - No code may assume a fixed repository root, `LightBeams` directory, `post` directory, or `outputs` directory.
   - The current implementation may live in `LightBeams/scripts`, but must remain portable to a future generic `posts/tools` location.

3. **Draft only**
   - The tool creates/updates a Medium draft and stops.
   - There must be no implementation for clicking `Publish`, `Submit`, or selecting/submitting to a publication.
   - Successful completion must leave the user with a saved draft for manual inspection.

4. **Automate the stable 95%**
   - Common formatting is automated.
   - Rare formatting may produce warnings or be skipped with `--force`.
   - Manual final inspection is part of the intended workflow.

5. **Fail safely**
   - Validation happens before browser automation starts.
   - Ambiguous content must not be silently guessed.
   - Unsupported content should be reported clearly.

---

## 3. Current Repository Layout

During development in the LightBeams repository:

```text
LightBeams/
├── post/
│   └── LightBeams/
│       └── post1/
│           └── article.md
├── scripts/
│   ├── upload_medium.py
│   └── medium_uploader/
│       ├── __init__.py
│       ├── models.py
│       ├── validate.py
│       ├── prepare.py
│       ├── render_math.py
│       └── medium_browser.py
├── tests/
│   └── medium_uploader/
│       ├── test_validate.py
│       ├── test_prepare.py
│       └── fixtures/
├── docs/
│   └── medium_uploader_spec.md
└── .medium_build/
```

Later, the package may move to a generic structure such as:

```text
posts/
├── tools/
│   └── medium_uploader/
└── post/
    ├── LightBeams/
    │   └── post1/article.md
    └── HOM/
        └── article.md
```

The move must not require changes to article path handling.

---

## 4. Command-Line Interface

Primary invocation:

```bash
python scripts/upload_medium.py post/LightBeams/post1/article.md
```

Supported modes:

```bash
python scripts/upload_medium.py ARTICLE.md --validate-only
python scripts/upload_medium.py ARTICLE.md --prepare-only
python scripts/upload_medium.py ARTICLE.md --force
```

Expected behavior:

- no option:
  1. validate
  2. prepare
  3. upload to Medium as draft
  4. stop on the saved draft

- `--validate-only`:
  - validate and print findings
  - do not render equations
  - do not launch browser

- `--prepare-only`:
  - validate
  - build the internal article representation
  - render display equations
  - write generated build artifacts
  - do not launch browser

- `--force`:
  - warnings continue normally
  - recoverable errors may be skipped
  - fatal errors still stop the process
  - skipped elements must be listed clearly in the final report

---

## 5. Validation Severity

Validation uses four severities.

### INFO

Non-blocking suggestions.

Examples:

- SEO title outside a preferred length range
- preview subtitle unusually long
- stylistic recommendations

### WARNING

Content is uploadable but may be unintended.

Warnings never stop normal execution.

Examples:

- section heading is not Title Case
- figure lacks a `Source:` field
- suspicious Unicode/math notation
- inconsistent prose conventions

### ERROR

The item cannot be uploaded reliably.

Normal execution stops before browser automation.

With `--force`, the affected item may be skipped if the remainder of the article is unambiguous.

Examples:

- referenced image file does not exist
- malformed figure metadata block
- display equation cannot be rendered
- unresolved footnote reference
- duplicate footnote identifier

### FATAL

The article cannot be interpreted safely.

`--force` must not bypass fatal errors.

Examples:

- no identifiable title
- article structure cannot be parsed
- malformed block syntax makes content boundaries ambiguous
- metadata cannot be parsed deterministically

---

## 6. Markdown Contract

### 6.1 Title

Exactly one article title:

```md
# Why Doesn't a Laser Beam Lose Its Shape?
```

Mapped to the Medium story title.

Validation:

- required
- duplicate level-1 headings are errors unless future specification explicitly allows them

### 6.2 Subtitle

The article subtitle is a level-3 heading immediately after the title, allowing only comments/metadata between them:

```md
# Article Title

### Article Subtitle
```

Mapped to the Medium subtitle.

The uploader must not treat arbitrary later `###` headings as subtitles.

### 6.3 Section Headers

Section headers use:

```md
## Section Header
```

Mapped to Medium's large section-heading style.

Validation:

- Title Case is a **warning**, not an error.
- The exact Markdown is preserved.
- The validator may identify likely Title Case violations but must never rewrite the heading.

### 6.4 Inline Mathematics and Symbols

Medium-ready Markdown must contain **no inline LaTeX math delimiters**.

Forbidden:

```md
$n+m$
$x$
$\phi$
```

Required style:

```md
*n* + *m*
*x*
*φ*
```

Rules:

- mathematical variables are written as Unicode characters
- variables are italicized using Markdown emphasis where appropriate
- operators, digits and ordinary prose remain non-italic unless explicitly authored otherwise
- Unicode subscripts/superscripts may be used where readable
- the validator flags any remaining inline `$...$` as an error
- the uploader does not automatically convert inline LaTeX

Examples:

```md
HG₁₀
π/2
eⁱφ
*n* + *m*
ξ = √2 *x*/*w*(*z*)
```

### 6.5 Display Mathematics

Display mathematics remains LaTeX in the authoritative Markdown:

```md
$$
u(x,z)=\frac{1}{\sqrt{w(z)}}e^{-x^2/w(z)^2}
$$
```

Preparation behavior:

1. parse the LaTeX block
2. render it as a high-resolution PNG
3. use a transparent background
4. place generated image in `.medium_build/...`
5. replace the equation only in the in-memory upload representation
6. leave the source Markdown untouched

Generated names should be deterministic where practical:

```text
equation_001.png
equation_002.png
```

Rendering failure is an ERROR.

---

## 7. Figures

Required source structure:

```md
![Figure 2](../outputs/figure_2_hermite_gaussian_modes.png)
> Caption: **Figure 2. Gaussian beams come in families.**
> Alt text: Four-by-four grid showing...
> Source: Image by author.
```

Rules:

- image path is resolved relative to the article `.md`
- referenced image must exist
- `Caption:` is required
- `Alt text:` is required
- exact spelling is `Alt text:`
- variants such as `Alt-text:` should be flagged so source conventions remain disciplined
- `Source:` is expected but absence is only a WARNING
- figure ordering follows document order

Medium behavior:

- upload image
- enter caption
- set image alt text through Medium's image settings
- include source attribution in the visible caption or immediately associated figure text according to the implementation chosen during browser testing

The source Markdown must not be rewritten.

---

## 8. Feature Image

The Medium metadata block identifies the feature image:

```md
feature_image: ../outputs/feature_twisted_light.png
```

The image path is resolved relative to the article.

The feature image may also appear in the body.

The uploader must set the Medium feature/preview image using the editor's feature-image control.

Missing feature image is an ERROR if `feature_image` is specified.

---

## 9. Pull Quotes

A standalone Markdown blockquote that is not figure metadata becomes a Medium pull quote.

Example:

```md
> **All light beams undergo diffraction. But some beams keep their shape while doing so.**
```

Excluded metadata blockquotes:

```md
> Caption:
> Alt text:
> Source:
```

Medium behavior:

- use the large pull-quote style
- preserve authored emphasis where Medium supports it

Ambiguous nested or multi-purpose blockquotes should generate a warning or error rather than being guessed.

---

## 10. Links and References

Standard Markdown links:

```md
[description](https://example.com)
```

must become native Medium hyperlinks.

Numbered references in prose may remain plain numbers or bracketed references such as `[1]` if the author intends them to refer to a reference section at the bottom.

The first implementation does not need to create internal anchor links for numbered bibliography references.

---

## 11. Footnotes / Side Remarks

Authoring syntax uses standard Markdown-style footnotes:

```md
Main text with an additional remark.[^1]

...

## Notes

[^1]: Extra explanation that would interrupt the main argument.
```

Preparation behavior:

- convert the inline reference to a superscript Unicode marker where possible
- render notes at the end in readable form
- no requirement for clickable backlinks in v1
- original Markdown remains unchanged

Validation:

- unresolved reference: ERROR
- duplicate definition: ERROR
- unused definition: WARNING

---

## 12. Medium Metadata Block

Medium-specific metadata is stored in a single HTML comment block.

Recommended format:

```md
<!-- medium
topics:
  - Science
  - Physics
  - Quantum Physics
  - Optics
  - Technology

seo_title: Why Doesn't a Laser Beam Lose Its Shape?
seo_description: A concise search description.

preview_title: Why Doesn't a Laser Beam Lose Its Shape?
preview_subtitle: A separate subtitle used in the Medium preview card.

feature_image: ../outputs/feature_twisted_light.png
-->
```

Rules:

- metadata stays invisible in normal Markdown rendering
- metadata must never replace body content
- parser should tolerate blank lines
- unknown keys should generate a WARNING and be ignored unless later supported
- malformed metadata is ERROR or FATAL depending on whether it can be isolated safely

Potential future keys may include:

```text
canonical_url
publication
license
custom_slug
```

They are not part of v1 behavior.

---

## 13. Medium Topics

Metadata field:

```yaml
topics:
  - Science
  - Physics
  - Quantum Physics
  - Optics
  - Technology
```

Rules:

- Medium allows at most five Reader Interests/topics
- more than five should not be silently truncated
- v1 should report the issue and refuse to guess which topics to discard
- uploader sets exactly the supplied topics where Medium accepts them

---

## 14. SEO Settings

Metadata:

```yaml
seo_title: ...
seo_description: ...
```

Mapped to Medium SEO settings.

Validation may report preferred/recommended lengths as INFO or WARNING.

SEO warnings never block upload unless Medium itself imposes a hard input limit that prevents completion.

---

## 15. Preview Settings

Metadata:

```yaml
preview_title: ...
preview_subtitle: ...
```

Mapped to Medium's preview/social-card settings.

These may intentionally differ from the article title and subtitle.

If omitted, v1 may leave Medium defaults unchanged rather than inventing values.

---

## 16. Internal Article Model

The preparation layer should produce a Medium-independent internal model.

Suggested entities:

```text
Article
Metadata
Block
Paragraph
SectionHeading
Figure
DisplayEquation
PullQuote
Footnote
Link
```

The parser and preparer must not depend on Medium DOM details.

Only `medium_browser.py` should know how Medium represents controls and formatting.

---

## 17. Build Artifacts

Generated assets go outside the authoritative article directory.

Preferred development location:

```text
.medium_build/
└── <article-id>/
    ├── equation_001.png
    ├── equation_002.png
    └── manifest.json
```

`.medium_build/` must be ignored by Git.

The manifest may record:

- source article path
- generated assets
- equation source text
- validation summary
- preparation timestamp
- skipped elements when `--force` is used

The manifest is optional for the first implementation but the directory convention should be preserved.

---

## 18. Browser Automation

Use Playwright with Chromium/Chrome.

Authentication:

- use a persistent browser profile
- first run: user logs into Medium manually
- subsequent runs reuse the authenticated profile
- do not store Medium credentials in source code or config files

Suggested profile location:

```text
.medium_browser_profile/
```

This directory must be ignored by Git.

Browser workflow:

1. launch persistent browser context
2. open Medium's new-story editor
3. populate title
4. populate subtitle
5. insert body blocks in order
6. apply section-heading formatting
7. apply pull-quote formatting
8. upload figures
9. set captions
10. set image alt text
11. upload rendered equation images
12. create hyperlinks
13. apply footnote superscripts / notes
14. set feature image
15. set topics
16. set SEO title and description
17. set preview title and subtitle
18. wait for Medium draft save confirmation/state
19. stop and leave the browser on the draft

---

## 19. Publishing Safety Requirements

These are mandatory.

### V1 must not contain:

- a function named or intended to publish
- selectors for Medium's Publish button
- selectors for Submit-to-publication actions
- logic that chooses a Medium publication
- code that confirms publication
- code that schedules publication

The tool's success path ends with a saved draft.

Suggested final console message:

```text
Draft created successfully.
No publication or submission action was performed.
Review the open Medium draft manually.
```

A code review/test should explicitly verify that publishing behavior has not been introduced accidentally.

---

## 20. Browser Robustness

Medium is a dynamic web editor and its DOM may change.

Implementation guidance:

- prefer accessibility roles, labels and visible text over fragile CSS classes
- isolate selectors in `medium_browser.py`
- wait for editor state rather than using arbitrary sleeps where possible
- save screenshots on browser failures
- report which action failed
- never continue into a different control when the expected control is absent

---

## 21. Tests

### Validator tests

At minimum:

- valid article passes
- missing title is fatal
- non-Title-Case heading is warning
- inline `$...$` is error
- valid `$$...$$` accepted
- missing figure file is error
- missing caption is error
- missing alt text is error
- wrong `Alt-text:` spelling is flagged
- missing source is warning
- unresolved footnote is error
- duplicate footnote is error
- unknown metadata key is warning

### Preparation tests

At minimum:

- paths resolve relative to article
- display equations are rendered without source modification
- figures preserve order
- pull quotes are distinguished from figure metadata
- links survive parsing
- footnotes map to superscripts/notes
- metadata is parsed correctly

### Browser tests

Initially keep these lightweight:

- browser launches with persistent profile
- new Medium draft can be opened
- title/subtitle can be entered
- one paragraph can be inserted
- one heading can be formatted
- one image can be uploaded

Full browser automation can be verified manually against a disposable draft until selectors stabilize.

---

## 22. Implementation Phases

### Phase 1 — Validator

Implement:

- Markdown parsing
- metadata parsing
- validation severities
- line-numbered findings
- command-line `--validate-only`
- unit tests

No browser and no equation rendering required.

### Phase 2 — Preparation

Implement:

- internal article model
- relative path resolution
- equation rendering
- figure extraction
- pull quote extraction
- links
- footnotes
- `.medium_build`

No browser.

### Phase 3 — Core Medium Upload

Implement:

- persistent Playwright profile
- draft editor
- title/subtitle
- paragraphs
- headings
- images
- captions
- alt text
- pull quotes
- links
- equation images

### Phase 4 — Medium Settings

Implement:

- feature image
- topics
- SEO
- preview title/subtitle

### Phase 5 — Hardening

Implement only after real use demonstrates value:

- screenshots on failure
- better selector fallbacks
- manifest
- additional validation
- optional support for rare formatting

Do not add publishing/submission automation.

---

## 23. Definition of Done for V1

V1 is successful when:

```bash
python scripts/upload_medium.py post/LightBeams/post1/article.md
```

can reliably:

1. validate the article
2. report warnings without blocking
3. stop on genuine errors
4. render display equations as images
5. open Medium using an authenticated persistent browser profile
6. create a correctly formatted draft containing title, subtitle, headings, paragraphs, links, figures, captions, alt text, pull quotes, equation images and notes
7. set feature image, topics, SEO and preview fields
8. leave the article as a saved draft
9. perform no publish or publication-submission action
10. require only a short manual review before the user manually submits/publishes it
