"""Locate a Notion HTML export and the local assets it references."""

import shutil
from os import path
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup


def find_export_html(root_dir: str) -> str:
    """Return the single HTML file anywhere under *root_dir*.

    Notion now nests the page inside a folder (e.g. "Private & Shared/") in its
    export ZIP, so the file is searched for recursively.
    """
    html_files = list(Path(root_dir).rglob("*.html"))
    if len(html_files) != 1:
        raise ValueError(
            f"Expected exactly one HTML file in the Notion export, found {len(html_files)}"
        )
    return str(html_files[0])


def copy_referenced_assets(html_file: str, dest_dir: str) -> None:
    """Copy the sibling folders that *html_file* references with relative links.

    The asset folder no longer shares the HTML file's name (Notion dropped the
    page id from it), so the folders are discovered from the links themselves.
    """
    source_dir = path.dirname(path.abspath(html_file))
    with open(html_file, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    references = [tag["src"] for tag in soup.find_all(src=True)]
    references += [tag["href"] for tag in soup.find_all(href=True)]

    for folder in _referenced_top_level_folders(references):
        source = path.join(source_dir, folder)
        if path.isdir(source):
            shutil.copytree(source, path.join(dest_dir, folder), dirs_exist_ok=True)


def _referenced_top_level_folders(references: list[str]) -> set[str]:
    folders = set()
    for reference in references:
        if urlparse(reference).scheme or reference.startswith("#"):
            continue
        parts = Path(unquote(reference)).parts
        if len(parts) > 1:
            folders.add(parts[0])
    return folders
