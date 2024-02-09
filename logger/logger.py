from typing import Optional
from datetime import datetime

class Logger:
    _instance = None
    _is_initialized = False

    def __new__(cls, *args, **kwargs):
        if not Logger._instance:
            obj = Logger._instance = super(Logger, cls).__new__(cls)
            obj.__init__(*args, **kwargs)
        return Logger._instance


    def __init__(self, include_timestamp : bool, log_file_path : Optional[str] = None):
        if Logger._is_initialized:
            return

        self.include_timestamp : bool = include_timestamp
        self.log_file_path = log_file_path

        if log_file_path:
            try:
                open(log_file_path, "w").close()
            except:
                raise ValueError(f"File {log_file_path} could not be created")
        Logger._is_initialized = True


    def log(self, msg : str):
        if self.include_timestamp:
            current_timestamp = datetime.now()
            timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            msg = f"[{timestamp}]:{msg}"
        if self.log_file_path:
            self.log_to_file(msg=msg)
        self.log_to_console(msg=msg)

    def log_to_file(self, msg : str):
        with open(self.log_file_path, "a") as log_file:
            log_file.write(f"{msg}\n")

    @staticmethod
    def log_to_console(msg : str):
        print(msg)

    @classmethod
    def get(cls):
        return cls._instance


def initialize_logger(include_timestamp : bool, log_file_path : Optional[str] = None):
    Logger(include_timestamp=include_timestamp, log_file_path=log_file_path)


def log(msg : str):
    logger = Logger.get()
    if logger is None:
        raise ValueError("Logger not initialized")
    logger.log(msg=msg)



if __name__ == "__main__":
    initialize_logger(include_timestamp=True)
    log(msg='hi')