from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from notion_prettify.gui.services.zip_handler import ZipExtractionError, ZipHandler


def _make_zip(path: Path, entries: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return path


def test_zip_holding_html_export_is_passed_through(tmp_path: Path) -> None:
    outer = _make_zip(
        tmp_path / "abc_ExportBlock-123.zip",
        {
            "Private & Shared/Page abc.html": b"<html></html>",
            "Private & Shared/Page/image.png": b"png",
        },
    )

    assert ZipHandler().resolve(outer) == outer


def test_legacy_nested_export_zip_is_unwrapped(tmp_path: Path) -> None:
    inner = _make_zip(tmp_path / "ExportBlock-1.zip", {"Page.html": b"<html></html>"})
    outer = _make_zip(tmp_path / "download.zip", {inner.name: inner.read_bytes()})

    handler = ZipHandler()
    resolved = handler.resolve(outer)

    assert resolved.name == "ExportBlock-1.zip"
    assert resolved != inner
    handler.cleanup()


def test_zip_without_export_raises(tmp_path: Path) -> None:
    outer = _make_zip(tmp_path / "download.zip", {"notes.txt": b"hi"})

    with pytest.raises(ZipExtractionError):
        ZipHandler().resolve(outer)


def test_html_input_is_passed_through(tmp_path: Path) -> None:
    page = tmp_path / "Page.html"
    page.write_text("<html></html>")

    assert ZipHandler().resolve(page) == page
