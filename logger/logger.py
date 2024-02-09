import datetime
from abc import abstractmethod, ABC
from datetime import datetime

class Logger(ABC):
    def __init__(self, include_timestamp : bool):
        self.include_timestamp : bool = include_timestamp

    def log(self, log_msg : str):
        if self.include_timestamp:
            current_timestamp = datetime.now()
            timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f"[{timestamp}]:{log_msg}"

        self._log(msg=log_msg)

    @abstractmethod
    def _log(self, msg : str):
        pass


class FileLogger(Logger):
    def __init__(self, log_file_path : str, include_timestamp : bool = True):
        super().__init__(include_timestamp=include_timestamp)

        try:
            open(log_file_path, "w").close()
        except:
            raise ValueError(f"File {log_file_path} could not be created")

        self.log_file_path = log_file_path


    def _log(self, msg : str):
        with open(self.log_file_path, "a") as log_file:
            log_file.write(f"{msg}\n")


class ConsoleLogger(Logger):
    def __init__(self, include_timestamp : bool = True):
        super().__init__(include_timestamp=include_timestamp)


    def _log(self, msg : str):
        print(msg)


