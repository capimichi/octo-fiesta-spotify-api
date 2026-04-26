from __future__ import annotations

from octofiestaspotifyapi.provider.spotify_metadata_provider import SpotifyMetadataProvider

class SpotifyTrackService:
    def __init__(self, metadata_provider: SpotifyMetadataProvider) -> None:
        self._metadata_provider = metadata_provider

    async def get_track(self, track_id: str) -> dict:
        return await self._metadata_provider.get_track(track_id)
