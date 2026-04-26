from __future__ import annotations

from octofiestaspotifyapi.service.spotify_search_service import SpotifySearchService
from octofiestaspotifyapi.service.spotify_track_service import SpotifyTrackService
from octofiestaspotifyapi.service.spotify_album_service import SpotifyAlbumService
from octofiestaspotifyapi.service.spotify_artist_service import SpotifyArtistService
from octofiestaspotifyapi.service.spotify_download_service import SpotifyDownloadService
from octofiestaspotifyapi.service.local_library_service import LocalLibraryService

class SpotifyProxyService:
    def __init__(
        self,
        search_service: SpotifySearchService,
        track_service: SpotifyTrackService,
        album_service: SpotifyAlbumService,
        artist_service: SpotifyArtistService,
        download_service: SpotifyDownloadService,
        local_library_service: LocalLibraryService,
    ) -> None:
        self._search_service = search_service
        self._track_service = track_service
        self._album_service = album_service
        self._artist_service = artist_service
        self._download_service = download_service
        self._local_library_service = local_library_service

    async def search(self, query: str, limit: int):
        return await self._search_service.search(query)

    async def get_track(self, track_id: str):
        return await self._track_service.get_track(track_id)

    async def get_album(self, album_id: str):
        return await self._album_service.get_album(album_id)

    async def get_artist(self, artist_id: str):
        return await self._artist_service.get_artist(artist_id)

    async def download_track(self, track_id: str):
        return {"status": "not_implemented", "track_id": track_id}
