from __future__ import annotations

from octofiestaspotifyapi.logger.download_logger import DownloadLogger

class SpotiflacClient:
    def __init__(self, logger: DownloadLogger, binary_path: str, output_dir: str, timeout_seconds: int) -> None:
        self._logger = logger.get_logger()
        self._binary_path = binary_path
        self._output_dir = output_dir
        self._timeout_seconds = timeout_seconds
