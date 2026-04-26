from __future__ import annotations

from octofiestaspotifyapi.client.download.spotiflac_client import SpotiflacClient

class SpotifyDownloadProvider:
    def __init__(self, spotiflac_client: SpotiflacClient) -> None:
        self._spotiflac_client = spotiflac_client
