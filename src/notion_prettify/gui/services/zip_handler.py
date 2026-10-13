from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path


class ZipExtractionError(Exception):
    pass


class ZipHandler:
    """Resolves the input that notion_prettify.core expects.

    Notion's current export ZIPs hold the page HTML (nested in a folder) and its
    assets directly, which the library handles itself. Older web downloads
    wrapped an ExportBlock-*.zip inside a generic outer ZIP; this handler
    extracts those and locates the inner ExportBlock-*.zip.
    """

    def __init__(self, keep_temp: bool = False) -> None:
        self._keep_temp = keep_temp
        self._temp_dir: tempfile.TemporaryDirectory[str] | None = None

    def resolve(self, input_path: Path) -> Path:
        """Return the path that should be passed to notion_prettify.core.

        If *input_path* is not a zip, or is a zip that already contains an HTML
        export, it is returned unchanged. Otherwise the zip is extracted and the
        first ExportBlock-*.zip found inside is returned.
        """
        if input_path.suffix.lower() != ".zip":
            return input_path

        if not zipfile.is_zipfile(input_path):
            raise ZipExtractionError(f"'{input_path}' is not a valid ZIP file.")

        with zipfile.ZipFile(input_path) as zf:
            if any(name.lower().endswith(".html") for name in zf.namelist()):
                return input_path

        return self._extract_and_find_export_zip(input_path)

    def _extract_and_find_export_zip(self, outer_zip: Path) -> Path:
        self._temp_dir = tempfile.TemporaryDirectory(
            prefix="notion-prettify-", delete=self._keep_temp
        )
        extract_dir = Path(self._temp_dir.name)

        with zipfile.ZipFile(outer_zip) as zf:
            zf.extractall(extract_dir)

        matches = list(extract_dir.rglob("ExportBlock-*.zip"))
        if not matches:
            raise ZipExtractionError(
                f"No HTML export or 'ExportBlock-*.zip' found inside '{outer_zip.name}'. "
                "Make sure the file is a valid Notion export."
            )

        return matches[0]

    @property
    def extraction_dir(self) -> Path | None:
        """The temporary directory used for ZIP extraction, or None if unused."""
        return Path(self._temp_dir.name) if self._temp_dir is not None else None

    def cleanup(self) -> None:
        """Remove any temporary extraction directory."""
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None
