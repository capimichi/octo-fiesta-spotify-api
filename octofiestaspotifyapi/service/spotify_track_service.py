from __future__ import annotations

from octofiestaspotifyapi.provider.spotify_metadata_provider import SpotifyMetadataProvider

class SpotifyTrackService:
    def __init__(self, metadata_provider: SpotifyMetadataProvider) -> None:
        self._metadata_provider = metadata_provider
