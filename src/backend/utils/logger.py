import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

ENV = os.getenv("ENV", "development")
LOG_LEVEL = logging.DEBUG if ENV == "development" else logging.INFO

LOGS_DIR = Path(__file__).parent.parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / f"mentormetrics_{datetime.now().strftime('%Y%m%d')}.log"

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class StructuredFormatter(logging.Formatter):
    
    def format(self, record):
        if hasattr(record, 'levelno'):
            if record.levelno >= logging.ERROR:
                record.levelname = f"\033[91m{record.levelname}\033[0m"  # Red
            elif record.levelno >= logging.WARNING:
                record.levelname = f"\033[93m{record.levelname}\033[0m"  # Yellow
            elif record.levelno >= logging.INFO:
                record.levelname = f"\033[92m{record.levelname}\033[0m"  # Green
            else:
                record.levelname = f"\033[94m{record.levelname}\033[0m"  # Blue
        
        return super().format(record)

def setup_logger(name: str = "mentormetrics") -> logging.Logger:
    
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = StructuredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(LOG_LEVEL)
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create log file: {str(e)}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    
    return setup_logger(name)

_stage_logger = setup_logger("pipeline.stages")

def log_stage_start(stage_name: str, session_id: str, metadata: Optional[dict] = None):
    
    msg = f"[{stage_name.upper()}] STARTED | Session: {session_id}"
    
    if metadata:
        safe_metadata = {
            k: v for k, v in metadata.items() 
            if not isinstance(v, (bytes, bytearray)) and k.lower() not in ["password", "token", "key"]
        }
        if safe_metadata:
            msg += f" | Metadata: {safe_metadata}"
    
    _stage_logger.info(msg)

def log_stage_success(stage_name: str, session_id: str, result_summary: Optional[dict] = None):
    
    msg = f"[{stage_name.upper()}] SUCCESS | Session: {session_id}"
    
    if result_summary:
        safe_summary = {
            k: v for k, v in result_summary.items() 
            if not isinstance(v, (bytes, bytearray))
        }
        if safe_summary:
            msg += f" | Results: {safe_summary}"
    
    _stage_logger.info(msg)

def log_stage_error(stage_name: str, session_id: str, error_message: str, error_details: Optional[dict] = None):
    
    msg = f"[{stage_name.upper()}] FAILED | Session: {session_id} | Error: {error_message}"
    
    if error_details:
        safe_details = {
            k: v for k, v in error_details.items() 
            if not isinstance(v, (bytes, bytearray))
        }
        if safe_details:
            msg += f" | Details: {safe_details}"
    
    _stage_logger.error(msg)

def log_stage_skip(stage_name: str, session_id: str, reason: str):
    
    msg = f"[{stage_name.upper()}] SKIPPED | Session: {session_id} | Reason: {reason}"
    _stage_logger.info(msg)

__all__ = [
    'setup_logger',
    'get_logger',
    'log_stage_start',
    'log_stage_success',
    'log_stage_error',
    'log_stage_skip'
]
