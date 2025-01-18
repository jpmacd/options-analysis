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

        self.handlers = []
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)

    def add_stream_handler(self) -> None:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s][%(levelname)s][%(name)s:%(funcName)s:%(lineno)d] %(message)s"
            )
        )
        self.handlers.append(stream_handler)

    def add_file_handler(self) -> None:
        if self.name and self.log_dir:
            file_path = f"{self.log_dir}/{self.name}.log"
            file_handler = logging.FileHandler(filename=file_path, mode="a")
            file_handler.setFormatter(
                logging.Formatter(
                    "[%(asctime)s][%(levelname)s][%(name)s:%(funcName)s:%(lineno)d] %(message)s"
                )
            )
            self.handlers.append(file_handler)

    def apply_handlers(self) -> None:
        for handler in self.handlers:
            if handler not in self.logger.handlers:
                self.logger.addHandler(handler)

    def get_logger(self) -> logging.Logger:
        self.apply_handlers()
        return self.logger


def log_factory(name: Optional[str] = None) -> logging.Logger:
    logger = Log(name)
    logger.add_stream_handler()
    logger.add_file_handler()
    return logger.get_logger()
