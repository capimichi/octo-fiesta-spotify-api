from __future__ import annotations

from octofiestaspotifyapi.client.browser.spotify_browser_client import SpotifyBrowserClient

class SpotifyMetadataProvider:
    def __init__(self, browser_client: SpotifyBrowserClient) -> None:
        self._browser_client = browser_client
