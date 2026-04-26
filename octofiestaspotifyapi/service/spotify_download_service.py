from __future__ import annotations

from octofiestaspotifyapi.provider.spotify_download_provider import SpotifyDownloadProvider

class SpotifyDownloadService:
    def __init__(self, download_provider: SpotifyDownloadProvider) -> None:
        self._download_provider = download_provider
