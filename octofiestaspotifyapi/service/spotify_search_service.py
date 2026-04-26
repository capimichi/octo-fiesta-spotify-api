from __future__ import annotations

from octofiestaspotifyapi.provider.spotify_metadata_provider import SpotifyMetadataProvider

class SpotifySearchService:
    def __init__(self, metadata_provider: SpotifyMetadataProvider) -> None:
        self._metadata_provider = metadata_provider

    async def search(self, query: str) -> dict:
        return await self._metadata_provider.search(query)
