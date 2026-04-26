from __future__ import annotations

from injector import inject
from fastapi import APIRouter, Query, Path
from fastapi.responses import RedirectResponse

from octofiestaspotifyapi.controller.base_controller import BaseController
from octofiestaspotifyapi.service.spotify_proxy_service import SpotifyProxyService

class SpotifyController(BaseController):
    @inject
    def __init__(self, proxy_service: SpotifyProxyService) -> None:
        self.router = APIRouter()
        self._proxy_service = proxy_service

        self.router.add_api_route("/", self.root, methods=["GET"], include_in_schema=False)
        self.router.add_api_route("/health", self.health, methods=["GET"], tags=["Health"])
        self.router.add_api_route(
            "/spotify/search",
            self.search,
            methods=["GET"],
            tags=["Spotify API"],
            summary="Search tracks, albums, and artists on Spotify",
            operation_id="search",
        )
        self.router.add_api_route(
            "/spotify/tracks/{track_id}",
            self.get_track,
            methods=["GET"],
            tags=["Spotify API"],
            summary="Get Spotify track details",
            operation_id="get_track",
        )
        self.router.add_api_route(
            "/spotify/albums/{album_id}",
            self.get_album,
            methods=["GET"],
            tags=["Spotify API"],
            summary="Get Spotify album details",
            operation_id="get_album",
        )
        self.router.add_api_route(
            "/spotify/artists/{artist_id}",
            self.get_artist,
            methods=["GET"],
            tags=["Spotify API"],
            summary="Get Spotify artist details",
            operation_id="get_artist",
        )
        self.router.add_api_route(
            "/spotify/tracks/{track_id}/download",
            self.download_track,
            methods=["POST"],
            tags=["Spotify API"],
            summary="Download Spotify track",
            operation_id="download_track",
        )

    async def root(self):
        return {"message": "Octo-Fiesta Spotify API"}

    async def health(self):
        return {"status": "ok"}

    async def search(self, q: str = Query(..., description="Search query string"), limit: int = Query(20, description="Max results")):
        return await self._proxy_service.search(q, limit)

    async def get_track(self, track_id: str = Path(..., description="Spotify Track ID")):
        return await self._proxy_service.get_track(track_id)

    async def get_album(self, album_id: str = Path(..., description="Spotify Album ID")):
        return await self._proxy_service.get_album(album_id)

    async def get_artist(self, artist_id: str = Path(..., description="Spotify Artist ID")):
        return await self._proxy_service.get_artist(artist_id)

    async def download_track(self, track_id: str = Path(..., description="Spotify Track ID to download")):
        return await self._proxy_service.download_track(track_id)
