from __future__ import annotations

import asyncio
import json
from typing import Callable, Any
from urllib.parse import quote_plus

from playwright.async_api import async_playwright, Playwright, BrowserContext, Page, Response
from fastapi import HTTPException
from octofiestaspotifyapi.logger.spotify_client_logger import SpotifyClientLogger

class SpotifyBrowserClient:
    def __init__(self, logger: SpotifyClientLogger, timeout_seconds: float, session_path: str) -> None:
        self._logger = logger.get_logger()
        self._timeout_seconds = timeout_seconds
        self._session_path = session_path
        self._playwright: Playwright | None = None
        self._context: BrowserContext | None = None
        self._lock = asyncio.Lock()

    async def _get_context(self) -> BrowserContext:
        async with self._lock:
            if self._context is None:
                self._logger.info(f"Starting Playwright with persistent context at {self._session_path}")
                self._playwright = await async_playwright().start()
                self._context = await self._playwright.chromium.launch_persistent_context(
                    user_data_dir=self._session_path,
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
            return self._context

    async def _capture_matching_response(self, url: str, url_predicate: Callable[[str], bool], body_predicate: Callable[[dict], bool] | None = None) -> dict:
        context = await self._get_context()
        page = await context.new_page()
        result_future = asyncio.Future()

        async def on_response(response: Response):
            if result_future.done():
                return
            if url_predicate(response.url):
                self._logger.debug(f"Candidate response URL matched: {response.url}")
                try:
                    # Some responses might not be JSON or might fail to read
                    text = await response.text()
                    data = json.loads(text)
                    if body_predicate is None or body_predicate(data):
                        self._logger.info(f"Found matching response for {url}")
                        if not result_future.done():
                            result_future.set_result(data)
                except Exception as e:
                    self._logger.debug(f"Failed to parse or match candidate response: {e}")

        page.on("response", on_response)
        
        self._logger.info(f"Navigating to {url}")
        try:
            # We don't await page.goto fully here if the response happens during navigation, 
            # but usually it's fine to await goto then wait for the future, or do them concurrently.
            await page.goto(url, wait_until="domcontentloaded")
            
            # Wait for the future to complete with a timeout
            result = await asyncio.wait_for(result_future, timeout=self._timeout_seconds)
            return result
        except asyncio.TimeoutError:
            self._logger.error(f"Timeout waiting for matching response on {url}")
            raise HTTPException(status_code=502, detail="Upstream timeout while fetching Spotify data")
        except Exception as e:
            self._logger.error(f"Error during browser capture for {url}: {e}")
            raise HTTPException(status_code=502, detail="Upstream error while fetching Spotify data")
        finally:
            await page.close()

    async def search(self, query: str) -> dict:
        # 1. url: https://open.spotify.com/search/{query_separated_by_plus}
        # 2. response url: https://api-partner.spotify.com/pathfinder/v2/query
        # 3. body: data.searchV2
        
        url_query = quote_plus(query)
        url = f"https://open.spotify.com/search/{url_query}"
        
        def url_predicate(res_url: str) -> bool:
            return "api-partner.spotify.com/pathfinder/v2/query" in res_url

        def body_predicate(body: dict) -> bool:
            return "data" in body and "searchV2" in body["data"]

        return await self._capture_matching_response(url, url_predicate, body_predicate)

    async def get_track(self, track_id: str) -> dict:
        # url: https://open.spotify.com/intl-it/track/{track_id}
        # response url: api-partner.spotify.com/pathfinder/v2/query
        # body: data.trackUnion
        
        url = f"https://open.spotify.com/intl-it/track/{track_id}"
        
        def url_predicate(res_url: str) -> bool:
            return "api-partner.spotify.com/pathfinder/v2/query" in res_url

        def body_predicate(body: dict) -> bool:
            return "data" in body and "trackUnion" in body["data"]

        return await self._capture_matching_response(url, url_predicate, body_predicate)

    async def get_album(self, album_id: str) -> dict:
        # url: https://open.spotify.com/intl-it/album/{album_id}
        # response url: api-partner.spotify.com/pathfinder/v2/query
        # body: data.albumUnion
        
        url = f"https://open.spotify.com/intl-it/album/{album_id}"
        
        def url_predicate(res_url: str) -> bool:
            return "api-partner.spotify.com/pathfinder/v2/query" in res_url

        def body_predicate(body: dict) -> bool:
            return "data" in body and "albumUnion" in body["data"]

        return await self._capture_matching_response(url, url_predicate, body_predicate)

    async def get_artist(self, artist_id: str) -> dict:
        # url: https://open.spotify.com/intl-it/artist/{artist_id}
        # response url: api-partner.spotify.com/pathfinder/v2/query
        # body: data.artistUnion
        
        url = f"https://open.spotify.com/intl-it/artist/{artist_id}"
        
        def url_predicate(res_url: str) -> bool:
            return "api-partner.spotify.com/pathfinder/v2/query" in res_url

        def body_predicate(body: dict) -> bool:
            return "data" in body and "artistUnion" in body["data"]

        return await self._capture_matching_response(url, url_predicate, body_predicate)
