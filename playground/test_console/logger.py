import os
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL
from time import strftime, localtime
from typing import Optional


class Logger:
    def __init__(self, level: Optional[str] = "INFO", logger_name: Optional[str] = "logger"):
        self.logger = None
        self.level = level
        self.logger_name = logger_name
        self.set_logger()

    # use dict
    def set_logger(self):
        if self.level and self.level == "INFO":
            self.level = INFO
        elif self.level and self.level == "DEBUG":
            self.level = DEBUG
        elif self.level and self.level == "WARNING":
            self.level = WARNING
        elif self.level and self.level == "ERROR":
            self.level = ERROR
        elif self.level and self.level == "WARN":
            self.level = WARN
        elif self.level and self.level == "CRITICAL":
            self.level = CRITICAL

        try:
            os.makedirs(os.path.join(os.path.realpath(os.path.dirname(__file__)), "logs"))
        except (FileExistsError, OSError):
            pass

        self.logger = getLogger(self.logger_name)
        self.logger.setLevel(self.level)
        stream_handler = StreamHandler()
        stream_handler.setLevel(self.level)
        file_handler = FileHandler(
            filename=os.path.join(os.path.realpath(os.path.dirname(__file__)), "logs",
                                  "{log_time}.log".format(log_time=strftime("%Y-%m-%d", localtime()))),
            mode="a",
            encoding="utf-8",
        )
        file_handler.setLevel(self.level)
        formatter = Formatter(fmt="%(asctime)s - [%(levelname)s] %(message)s")
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        self.logger.handlers.clear()
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        return

    def get_logger(self):
        return self.logger
