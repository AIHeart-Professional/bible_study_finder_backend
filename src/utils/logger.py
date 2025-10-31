"""
Professional colored logger for Bible Study Finder Backend.
Provides structured logging with colors, timestamps, and different log levels.
"""

import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels."""
    
    # Color mapping for different log levels
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        """Initialize the colored formatter."""
        if fmt is None:
            fmt = '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
        if datefmt is None:
            datefmt = '%Y-%m-%d %H:%M:%S'
        
        super().__init__(fmt, datefmt)
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        # Add color to the level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
        
        # Add color to the logger name
        record.name = f"{Fore.BLUE}{record.name}{Style.RESET_ALL}"
        
        # Add color to the timestamp
        formatted_time = datetime.fromtimestamp(record.created).strftime(self.datefmt)
        record.asctime = f"{Fore.MAGENTA}{formatted_time}{Style.RESET_ALL}"
        
        return super().format(record)

class BibleStudyLogger:
    """Professional logger for Bible Study Finder Backend."""
    
    _loggers: Dict[str, logging.Logger] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls, 
                   log_level: str = "INFO",
                   log_file: Optional[str] = None,
                   console_output: bool = True,
                   file_output: bool = False) -> None:
        """
        Initialize the logging system.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (optional)
            console_output: Enable console output
            file_output: Enable file output
        """
        if cls._initialized:
            return
        
        # Convert string level to logging constant
        level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler with colors
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_formatter = ColoredFormatter()
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # File handler (no colors)
        if file_output and log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance for the given name.
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Logger instance
        """
        if not cls._initialized:
            cls.initialize()
        
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def log_api_call(cls, 
                     logger: logging.Logger,
                     method: str,
                     url: str,
                     status_code: Optional[int] = None,
                     response_time: Optional[float] = None,
                     error: Optional[str] = None) -> None:
        """
        Log API calls with structured information.
        
        Args:
            logger: Logger instance
            method: HTTP method (GET, POST, etc.)
            url: API endpoint URL
            status_code: HTTP status code
            response_time: Response time in seconds
            error: Error message if any
        """
        if error:
            logger.error(f"API {method} {url} | Error: {error}")
        elif status_code:
            status_color = Fore.GREEN if 200 <= status_code < 300 else Fore.RED
            time_info = f" | Time: {response_time:.3f}s" if response_time else ""
            logger.info(f"API {method} {url} | Status: {status_color}{status_code}{Style.RESET_ALL}{time_info}")
        else:
            logger.info(f"API {method} {url}")
    
    @classmethod
    def log_database_operation(cls,
                               logger: logging.Logger,
                               operation: str,
                               table: str,
                               record_id: Optional[str] = None,
                               success: bool = True,
                               error: Optional[str] = None) -> None:
        """
        Log database operations.
        
        Args:
            logger: Logger instance
            operation: Database operation (INSERT, UPDATE, DELETE, SELECT)
            table: Table name
            record_id: Record ID if applicable
            success: Whether operation was successful
            error: Error message if any
        """
        id_info = f" | ID: {record_id}" if record_id else ""
        
        if error:
            logger.error(f"DB {operation} {table}{id_info} | Error: {error}")
        elif success:
            logger.info(f"DB {operation} {table}{id_info} | Success")
        else:
            logger.warning(f"DB {operation} {table}{id_info} | Failed")
    
    @classmethod
    def log_business_logic(cls,
                          logger: logging.Logger,
                          operation: str,
                          details: Optional[str] = None,
                          data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log business logic operations.
        
        Args:
            logger: Logger instance
            operation: Business operation name
            details: Additional details
            data: Data dictionary to log
        """
        details_str = f" | {details}" if details else ""
        data_str = f" | Data: {data}" if data else ""
        logger.info(f"BUSINESS {operation}{details_str}{data_str}")
    
    @classmethod
    def log_security_event(cls,
                           logger: logging.Logger,
                           event_type: str,
                           user_id: Optional[str] = None,
                           ip_address: Optional[str] = None,
                           details: Optional[str] = None) -> None:
        """
        Log security-related events.
        
        Args:
            logger: Logger instance
            event_type: Type of security event
            user_id: User ID if applicable
            ip_address: IP address if applicable
            details: Additional details
        """
        user_info = f" | User: {user_id}" if user_id else ""
        ip_info = f" | IP: {ip_address}" if ip_address else ""
        details_str = f" | {details}" if details else ""
        logger.warning(f"SECURITY {event_type}{user_info}{ip_info}{details_str}")
    
    @classmethod
    def log_performance(cls,
                       logger: logging.Logger,
                       operation: str,
                       duration: float,
                       memory_usage: Optional[float] = None) -> None:
        """
        Log performance metrics.
        
        Args:
            logger: Logger instance
            operation: Operation name
            duration: Duration in seconds
            memory_usage: Memory usage in MB
        """
        memory_info = f" | Memory: {memory_usage:.2f}MB" if memory_usage else ""
        logger.info(f"PERFORMANCE {operation} | Duration: {duration:.3f}s{memory_info}")

# Convenience function to get a logger
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return BibleStudyLogger.get_logger(name)

# Example usage and testing
if __name__ == "__main__":
    # Initialize the logger
    BibleStudyLogger.initialize(
        log_level="DEBUG",
        console_output=True,
        file_output=True,
        log_file="logs/bible_study_backend.log"
    )
    
    # Get a logger
    logger = get_logger(__name__)
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test structured logging
    BibleStudyLogger.log_api_call(
        logger, "GET", "https://api.scripture.api.bible/v1/bibles", 
        status_code=200, response_time=0.245
    )
    
    BibleStudyLogger.log_database_operation(
        logger, "SELECT", "bibles", record_id="123", success=True
    )
    
    BibleStudyLogger.log_business_logic(
        logger, "get_bibles", "Filtering by language", {"language": "English"}
    )
