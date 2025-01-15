import logging
from os.path import exists
from os import getenv, mkdir
from typing import Optional
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class Log:
    def __init__(self, name: Optional[str]) -> None:
        self.debug = getenv("DEBUG", "False").lower() == "true"
        self.log_dir = getenv("LOG_DIR", "logs")
        if not exists(self.log_dir):
            mkdir(self.log_dir)

        self.handlers: list = []
        self.name = name
        self.logger = logging.getLogger(self.name)

    def add_stream_handler(self) -> None:
        self.handlers.append(logging.StreamHandler())

    def add_file_handler(self) -> None:
        if self.name and self.log_dir:
            file_path = f"{self.log_dir}/{self.name}.log"
            # file_path = f"{self.log_dir}/{'application'}.log"
            self.handlers.append(logging.FileHandler(filename=file_path, mode="a"))

    def basic_config(self) -> None:
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format="[%(asctime)s][%(levelname)s][%(name)s:%(funcName)s:%(lineno)d] %(message)s",
            handlers=self.handlers,
        )

    def get_logger(self):
        return self.logger


def log_factory(name: Optional[str]) -> logging.Logger:
    logger = logging.getLogger(name)
    _logger_ = Log(name)
    _logger_.add_stream_handler()
    _logger_.add_file_handler()
    _logger_.basic_config()

    return logger
