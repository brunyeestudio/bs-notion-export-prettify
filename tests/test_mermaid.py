from pathlib import Path

from notion_prettify.core.notion_html_manipulator import NotionHtmlManipulator

MERMAID_SOURCE = "flowchart TB\n  a[&quot;A &lt;br&gt; B&quot;] --&gt; b"


def _manipulator(tmp_path: Path, body: str) -> NotionHtmlManipulator:
    page = tmp_path / "page.html"
    page.write_text(
        "<html><head></head><body><article><header><h1>T</h1>"
        '<p class="page-description"></p></header>'
        f'<div class="page-body">{body}</div></article></body></html>',
        encoding="utf-8",
    )
    return NotionHtmlManipulator(str(page))


def test_mermaid_code_blocks_become_diagram_containers(tmp_path: Path) -> None:
    manipulator = _manipulator(
        tmp_path,
        '<pre class="code code-wrap" data-notion-code-syntax="mermaid">'
        f'<code class="language-mermaid">{MERMAID_SOURCE}</code></pre>'
        '<pre class="code" data-notion-code-syntax="python"><code>print(1)</code></pre>',
    )

    manipulator.render_mermaid_diagrams()
    soup = manipulator.soup

    diagrams = soup.find_all("div", class_="mermaid")
    assert len(diagrams) == 1
    assert diagrams[0].get_text() == 'flowchart TB\n  a["A <br> B"] --> b'
    assert soup.find("pre", attrs={"data-notion-code-syntax": "mermaid"}) is None
    assert soup.find("pre", attrs={"data-notion-code-syntax": "python"}) is not None
    assert "mermaid" in soup.find("script", type="module").string


def test_no_mermaid_blocks_leaves_document_untouched(tmp_path: Path) -> None:
    manipulator = _manipulator(tmp_path, "<p>hello</p>")

    manipulator.render_mermaid_diagrams()

    assert manipulator.soup.find("script") is None
