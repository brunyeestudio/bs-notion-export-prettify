# Notion Prettify

Turn a Notion HTML export into a branded PDF. One repo, one package:

- `notion_prettify.core` — the conversion pipeline and the `notion-prettify` CLI
- `notion_prettify.gui` — the desktop app (`notion-prettify-gui`), a PySide6 front end over the same pipeline

The GUI imports the pipeline directly. There is no published package and nothing to release between the two.

## Features

- Accepts the ZIP downloaded from Notion (current exports, with the HTML page and its asset folder, or older ones with a nested `ExportBlock-*.zip`), or the extracted HTML file next to its asset folder
- Cleans up the HTML: strips internal callouts and database properties, numbers headings, rejigs the table of contents
- Renders mermaid code blocks as diagrams
- Applies your template: page CSS, branded headers and footers with metadata and page numbers, a cover page, a PDF table of contents and embedded metadata
- GUI extras: metadata fields, tri-state option toggles, a live log, cancellable runs and a system light/dark theme

Everything template-related is optional and only applied when the template folder provides the resource. Templates live in the separate `notion-prettify-templates` repo; the two built-in examples are under `src/notion_prettify/templates/`.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --group dev
uv run playwright install chromium   # first run only; the app also does this on demand
```

## Usage

```bash
# GUI
uv run notion-prettify-gui

# CLI
uv run notion-prettify export.zip -t path/to/template --title "My Document"
uv run notion-prettify --help
```

From Python:

```python
from notion_prettify.core import prettify

prettify(input_file="export.zip", output="my-document.pdf", template="path/to/template")
```

### GUI workflow

1. **Files** — pick the Notion export (`.zip` or `.html`), optionally an output PDF path and a template/config file.
2. **Metadata** — fill in any fields you want embedded in the PDF (all optional).
3. **Options** — each switch cycles through *default* (library default), *on* and *off*.
4. Click **Generate PDF** and watch the Output log.

| Option | Description |
|---|---|
| Cover page | Add a cover page if the template defines one |
| Heading numbers | Prefix headings with hierarchical numbers |
| Strip internal info | Remove internal callouts and database properties |
| Table of contents | Keep the table of contents from the Notion export |

## Development

```bash
uv run pytest
uv run ruff check src tests
uv run mypy src
```

## Building the desktop app

```bash
bash scripts/build_macos.sh      # dist/NotionPrettify.app
scripts\build_windows.bat        # dist\NotionPrettify.exe
```

## Project structure

```
src/notion_prettify/
├── core/                 # pipeline + CLI
│   ├── main.py           # prettify() and the CLI entry point
│   ├── args.py           # CLI arguments and template resolution
│   ├── notion_export.py  # locating the export HTML and its assets
│   ├── notion_html_manipulator.py
│   ├── html_templator.py
│   ├── pdf_maker.py      # Playwright + PyMuPDF
│   └── browser_setup.py  # Chromium install on demand
├── gui/                  # desktop app
│   ├── app.py
│   ├── models/options.py
│   ├── services/         # runner, zip handling, cfg loading
│   └── widgets/
└── templates/            # built-in example templates
```
