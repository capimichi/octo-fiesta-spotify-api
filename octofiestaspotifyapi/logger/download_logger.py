from octofiestaspotifyapi.logger.base_logger import BaseLogger


class DownloadLogger(BaseLogger):
    def __init__(self, log_file: str, debug: bool = False) -> None:
        super().__init__(log_file, "download_logger", debug)