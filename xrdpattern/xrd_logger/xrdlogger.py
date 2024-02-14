from __future__ import annotations

import logging
from typing import Optional
from datetime import datetime


class XrdLogger:
    _instance = None
    _is_initialized = False

    def __new__(cls, *args, **kwargs):
        if not XrdLogger._instance:
            obj = XrdLogger._instance = super(XrdLogger, cls).__new__(cls)
            obj.__init__(*args, **kwargs)
        return XrdLogger._instance


    def __init__(self, include_timestamp : bool):
        if XrdLogger._is_initialized:
            return

        self.include_timestamp : bool = include_timestamp
        XrdLogger._is_initialized = True


    def log(self, msg : str, log_file_path : Optional[str] = None):
        if self.include_timestamp:
            current_timestamp = datetime.now()
            timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            msg = f"[{timestamp}]: {msg}"
        if log_file_path:
            self.log_to_file(msg=msg, log_file_path=log_file_path)
        self.log_to_console(msg=msg)


    @staticmethod
    def log_to_file(msg : str, log_file_path : str):
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{msg}\n")


    @staticmethod
    def log_to_console(msg : str):
        print(msg)


    @classmethod
    def get(cls) -> XrdLogger:
        return cls._instance



def log_xrd_info(msg : str, log_file_path : Optional[str] = None):
    logger = XrdLogger.get()
    if logger is None:
        logging.warning("XrdPattern Logger not initialized. Using defaults")
        logger = XrdLogger(include_timestamp=True)

    logger.log(msg=msg, log_file_path=log_file_path)


if __name__ == "__main__":
    log_xrd_info(msg='hi')