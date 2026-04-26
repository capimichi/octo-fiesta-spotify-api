import logging
import os
from logging.handlers import RotatingFileHandler

from octofiestaspotifyapi.logger.base_logger import BaseLogger


class AppLogger(BaseLogger):
    def __init__(self, log_file: str, debug: bool = False) -> None:
        super().__init__(log_file, "app_logger", debug)

    def configure_root(self) -> None:
        root_logger = logging.getLogger()
        root_logger.setLevel(self.logger.level)

        # Clear existing handlers from root logger
        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Add rotating file handler to root logger
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        rotating_file_handler = RotatingFileHandler(
            self.log_file, maxBytes=1024 * 1024 * 5, backupCount=5
        )  # 5 MB per file, 5 backup files
        rotating_file_handler.setFormatter(formatter)
        root_logger.addHandler(rotating_file_handler)

        # Add console handler to root logger if in debug mode
        if self.logger.level == logging.DEBUG:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
