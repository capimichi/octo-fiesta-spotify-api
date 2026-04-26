from __future__ import annotations

class LocalLibraryService:
    def __init__(self, download_dir: str) -> None:
        self._download_dir = download_dir
