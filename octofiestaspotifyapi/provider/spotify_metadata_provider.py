from __future__ import annotations

from octofiestaspotifyapi.client.browser.spotify_browser_client import SpotifyBrowserClient

class SpotifyMetadataProvider:
    def __init__(self, browser_client: SpotifyBrowserClient) -> None:
        self._browser_client = browser_client

    async def search(self, query: str) -> dict:
        return await self._browser_client.search(query)

    async def get_track(self, track_id: str) -> dict:
        return await self._browser_client.get_track(track_id)

    async def get_album(self, album_id: str) -> dict:
        return await self._browser_client.get_album(album_id)

    async def get_artist(self, artist_id: str) -> dict:
        return await self._browser_client.get_artist(artist_id)
