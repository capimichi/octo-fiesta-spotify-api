from octofiestaspotifyapi.logger.base_logger import BaseLogger


class ApiLogger(BaseLogger):
    def __init__(self, log_file: str, debug: bool = False) -> None:
        super().__init__(log_file, "api_logger", debug)