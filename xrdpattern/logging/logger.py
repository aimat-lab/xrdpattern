from hollarek.logging import get_logger, LogSettings
from typing import Optional

def log_xrd_info(msg : str, log_file_path : Optional[str] = None):
    logger = get_logger(settings=LogSettings(timestamp=True, log_fpath=log_file_path ))
    logger.log(msg=msg, log_file_path=log_file_path)