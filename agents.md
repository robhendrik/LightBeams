# AGENTS.md

## Project purpose

This repository contains code, article drafts, figures, and supporting material
for the LightBeams project.

## Working principles

- Read the relevant existing files before making changes.
- Preserve existing project structure unless there is a clear reason to change it.
- Prefer small, understandable changes over large rewrites.
- Do not silently change scientific assumptions or equations.
- If something is ambiguous, explain the assumption you made.

## Python

- Python 3.12.
- Prefer NumPy, SciPy, Pandas, and Matplotlib.
- Do not use seaborn.
- Use Google-style docstrings.
- Add or update pytest tests when changing reusable code.

## Running code

Install dependencies with:

    pip install -r requirements.txt

Run tests with:

    pytest

## Figures

- Figure-generating scripts belong in `scripts/` or the relevant project folder.
- Generated figures should be reproducible from source.
- Do not manually edit generated figures when the source script can be changed instead.

## Git

- Do not commit large generated binary files unless needed.
- Never commit API keys, tokens, `.env` files, or credentials.
- Before finishing a coding task, show which files changed and whether tests passed.