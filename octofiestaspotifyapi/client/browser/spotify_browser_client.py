from __future__ import annotations

from octofiestaspotifyapi.logger.spotify_client_logger import SpotifyClientLogger

class SpotifyBrowserClient:
    def __init__(self, logger: SpotifyClientLogger, timeout_seconds: float) -> None:
        self._logger = logger.get_logger()
        self._timeout_seconds = timeout_seconds
