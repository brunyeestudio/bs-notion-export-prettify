from pathlib import Path

import pytest

from notion_prettify.core.notion_export import (
    copy_referenced_assets,
    find_export_html,
)


def test_find_export_html_in_nested_folder(tmp_path: Path) -> None:
    page = tmp_path / "Private & Shared" / "Handover Guide abc123.html"
    page.parent.mkdir()
    page.write_text("<html></html>")

    assert find_export_html(str(tmp_path)) == str(page)


def test_find_export_html_requires_exactly_one(tmp_path: Path) -> None:
    (tmp_path / "a.html").write_text("<html></html>")
    (tmp_path / "b.html").write_text("<html></html>")

    with pytest.raises(ValueError):
        find_export_html(str(tmp_path))


def test_copy_referenced_assets_copies_folders_used_by_html(tmp_path: Path) -> None:
    source = tmp_path / "source"
    assets = source / "Handover Guide"
    assets.mkdir(parents=True)
    (assets / "diagram.png").write_bytes(b"png")
    (source / "Unrelated").mkdir()
    page = source / "Handover Guide e121b0ca.html"
    page.write_text(
        '<html><body><a href="Handover%20Guide/diagram.png">'
        '<img src="Handover%20Guide/diagram.png"/></a>'
        '<img src="https://example.com/remote.png"/>'
        '<a href="#heading">anchor</a></body></html>'
    )
    dest = tmp_path / "dest"
    dest.mkdir()

    copy_referenced_assets(str(page), str(dest))

    assert (dest / "Handover Guide" / "diagram.png").read_bytes() == b"png"
    assert not (dest / "Unrelated").exists()
