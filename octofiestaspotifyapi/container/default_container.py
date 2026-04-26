from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from injector import Injector

from octofiestaspotifyapi.logger.app_logger import AppLogger
from octofiestaspotifyapi.logger.api_logger import ApiLogger
from octofiestaspotifyapi.logger.spotify_client_logger import SpotifyClientLogger
from octofiestaspotifyapi.logger.download_logger import DownloadLogger
from octofiestaspotifyapi.logger.browser_logger import BrowserLogger


class DefaultContainer:
    _instance: "DefaultContainer | None" = None

    def __init__(self) -> None:
        self.injector = Injector()
        load_dotenv()
        self._init_environment_variables()
        self._init_directories()
        self._init_logging()
        self._init_bindings()

    @classmethod
    def getInstance(cls) -> "DefaultContainer":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get(self, cls: type[Any]) -> Any:
        return self.injector.get(cls)

    def get_var(self, key: str) -> Any:
        if key not in self.__dict__:
            raise KeyError(f"Unknown container var: {key}")
        return self.__dict__[key]

    def _env_bool(self, key: str, default: str) -> bool:
        return os.environ.get(key, default).strip().lower() in {"1", "true", "yes", "on"}

    def _init_environment_variables(self) -> None:
        self.app_name = os.environ.get("APP_NAME", "octofiestaspotifyapi")
        self.debug = self._env_bool("DEBUG", "false")
        self.api_host = os.environ.get("API_HOST", "127.0.0.1")
        self.api_port = int(os.environ.get("API_PORT", "8000"))
        
        self.log_dir_env = os.environ.get("LOG_DIR", "var/log")
        self.download_dir_env = os.environ.get("DOWNLOAD_DIR", "var/downloads")
        self.temp_dir_env = os.environ.get("TEMP_DIR", "var/tmp")

        self.spotify_browser_enabled = self._env_bool("SPOTIFY_BROWSER_ENABLED", "true")
        self.spotify_browser_timeout_seconds = float(os.environ.get("SPOTIFY_BROWSER_TIMEOUT_SECONDS", "30"))
        
        self.spotiflac_enabled = self._env_bool("SPOTIFLAC_ENABLED", "true")
        self.spotiflac_binary = os.environ.get("SPOTIFLAC_BINARY", "spotiflac")
        self.spotiflac_output_dir = os.environ.get("SPOTIFLAC_OUTPUT_DIR", "var/downloads")
        self.spotiflac_timeout_seconds = int(os.environ.get("SPOTIFLAC_TIMEOUT_SECONDS", "600"))

        self.spotify_session_storage_path_env = os.environ.get("SPOTIFY_SESSION_STORAGE_PATH", "var/tmp/spotify-session")

        self.app_log_file = os.environ.get("APP_LOG_FILE", "var/log/app.log")
        self.api_log_file = os.environ.get("API_LOG_FILE", "var/log/api.log")
        self.spotify_client_log_file = os.environ.get("SPOTIFY_CLIENT_LOG_FILE", "var/log/spotify-client.log")
        self.download_log_file = os.environ.get("DOWNLOAD_LOG_FILE", "var/log/download.log")
        self.browser_log_file = os.environ.get("BROWSER_LOG_FILE", "var/log/browser.log")

    def _init_directories(self) -> None:
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.var_dir = os.path.join(self.root_dir, "var")
        os.makedirs(self.var_dir, exist_ok=True)
        
        self.log_dir = os.path.join(self.root_dir, self.log_dir_env)
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.download_dir = os.path.join(self.root_dir, self.download_dir_env)
        os.makedirs(self.download_dir, exist_ok=True)

        self.temp_dir = os.path.join(self.root_dir, self.temp_dir_env)
        os.makedirs(self.temp_dir, exist_ok=True)

        self.spotify_session_storage_path = os.path.join(self.root_dir, self.spotify_session_storage_path_env)
        os.makedirs(self.spotify_session_storage_path, exist_ok=True) # Ensure session storage path exists


    def _init_logging(self) -> None:
        self.app_logger = AppLogger(os.path.join(self.root_dir, self.app_log_file), debug=self.debug)
        self.api_logger = ApiLogger(os.path.join(self.root_dir, self.api_log_file), debug=self.debug)
        self.spotify_client_logger = SpotifyClientLogger(os.path.join(self.root_dir, self.spotify_client_log_file), debug=self.debug)
        self.download_logger = DownloadLogger(os.path.join(self.root_dir, self.download_log_file), debug=self.debug)
        self.browser_logger = BrowserLogger(os.path.join(self.root_dir, self.browser_log_file), debug=self.debug)

        self.app_logger.configure_root() # Configure the root logger with the app logger

    def _init_bindings(self) -> None:
        # Placeholder for bindings - will be populated in later phases
        self.injector.binder.bind(AppLogger, to=self.app_logger)
        self.injector.binder.bind(ApiLogger, to=self.api_logger)
        self.injector.binder.bind(SpotifyClientLogger, to=self.spotify_client_logger)
        self.injector.binder.bind(DownloadLogger, to=self.download_logger)
        self.injector.binder.bind(BrowserLogger, to=self.browser_logger)

        from octofiestaspotifyapi.client.browser.spotify_browser_client import SpotifyBrowserClient
        from octofiestaspotifyapi.client.download.spotiflac_client import SpotiflacClient
        from octofiestaspotifyapi.provider.spotify_metadata_provider import SpotifyMetadataProvider
        from octofiestaspotifyapi.provider.spotify_download_provider import SpotifyDownloadProvider
        from octofiestaspotifyapi.service.spotify_search_service import SpotifySearchService
        from octofiestaspotifyapi.service.spotify_track_service import SpotifyTrackService
        from octofiestaspotifyapi.service.spotify_album_service import SpotifyAlbumService
        from octofiestaspotifyapi.service.spotify_artist_service import SpotifyArtistService
        from octofiestaspotifyapi.service.spotify_download_service import SpotifyDownloadService
        from octofiestaspotifyapi.service.local_library_service import LocalLibraryService
        from octofiestaspotifyapi.service.spotify_proxy_service import SpotifyProxyService
        from octofiestaspotifyapi.controller.spotify_controller import SpotifyController

        browser_client = SpotifyBrowserClient(self.spotify_client_logger, self.spotify_browser_timeout_seconds)
        spotiflac_client = SpotiflacClient(self.download_logger, self.spotiflac_binary, self.spotiflac_output_dir, self.spotiflac_timeout_seconds)
        
        metadata_provider = SpotifyMetadataProvider(browser_client)
        download_provider = SpotifyDownloadProvider(spotiflac_client)

        search_service = SpotifySearchService(metadata_provider)
        track_service = SpotifyTrackService(metadata_provider)
        album_service = SpotifyAlbumService(metadata_provider)
        artist_service = SpotifyArtistService(metadata_provider)
        download_service = SpotifyDownloadService(download_provider)
        local_library_service = LocalLibraryService(self.download_dir)

        proxy_service = SpotifyProxyService(
            search_service=search_service,
            track_service=track_service,
            album_service=album_service,
            artist_service=artist_service,
            download_service=download_service,
            local_library_service=local_library_service
        )
        self.injector.binder.bind(SpotifyProxyService, to=proxy_service)
        self.injector.binder.bind(SpotifyController, to=SpotifyController(proxy_service))
