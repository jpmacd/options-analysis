import logging
from os.path import exists
from os import getenv, mkdir
from typing import Optional


class Log:
    def __init__(self, name: Optional[str]) -> None:
        self.debug = getenv("DEBUG")
        self.log_dir = getenv("LOG_DIR")
        self.handlers: list = []
        self.name = name
        self.logger = logging.getLogger(self.name)

    def make_log_dir(self) -> None:
        if self.log_dir:
            if not exists(f"{self.log_dir}"):
                mkdir(f"{self.log_dir}")

    def add_stream_handler(self) -> None:
        self.handlers.append(logging.StreamHandler())

    def add_file_handler(self) -> None:
        if self.name and self.log_dir:
            self.handlers.append(
                logging.FileHandler(filename=f"{self.log_dir}/{self.name}.log")
            )

    def basic_config(self) -> None:
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format="[%(asctime)s][%(levelname)s][%(name)s:%(funcName)s:%(lineno)d] %(message)s",
            handlers=self.handlers,
        )

    def get_logger(self):
        return self.logger


def log_factory(name: Optional[str]) -> logging.Logger:
    _logger_ = Log(name)
    _logger_.add_stream_handler()
    _logger_.make_log_dir()
    _logger_.add_file_handler()
    _logger_.basic_config()
    return _logger_.get_logger()


logging.basicConfig(
    format="[%(asctime)s][%(levelname)s][%(name)s:%(funcName)s:%(lineno)d] %(message)s",
)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
