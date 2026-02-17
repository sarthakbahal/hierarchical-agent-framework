"""
Logging Utility

LEARNING POINTS:
- Centralized logging configuration
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Colored output for better readability
- File logging option for production
- Context-aware logging (shows which component is logging)

Why proper logging?
- Essential for debugging async systems
- Track agent behavior and decisions
- Monitor tool execution
- Diagnose errors in production
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


# ANSI color codes for terminal output
# Makes logs easier to read by highlighting different levels
class Colors:
    """Terminal color codes for different log levels."""
    GREY = "\033[90m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD_RED = "\033[91;1m"
    RESET = "\033[0m"


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log levels.
    
    Why custom formatter?
    - Makes logs easier to scan visually
    - Highlights errors in red
    - Shows debug info in grey (less distracting)
    - Professional-looking output
    """
    
    # Map log level to color
    COLORS = {
        logging.DEBUG: Colors.GREY,
        logging.INFO: Colors.BLUE,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BOLD_RED,
    }
    
    def format(self, record):
        """
        Format log record with colors.
        
        Format: [TIME] LEVEL     LOGGER_NAME: MESSAGE
        Example: [12:34:56] INFO     OrchestratorAgent: Starting task execution
        """
        # Get color for this log level
        color = self.COLORS.get(record.levelno, Colors.RESET)
        
        # Format level name (padded to 8 chars for alignment)
        level = f"{color}{record.levelname:8s}{Colors.RESET}"
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        
        # Format message
        message = record.getMessage()
        
        # Combine into final format
        return f"[{timestamp}] {level} {record.name}: {message}"


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Create and configure a logger.
    
    Args:
        name: Logger name (usually module name or class name)
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        
    Returns:
        Configured logger instance
        
    Usage:
        logger = setup_logger("OrchestratorAgent")
        logger.info("Task started")
        logger.error("Something went wrong")
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    logger.propagate = False  # Don't pass to parent loggers
    
    # Console handler (stdout) with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # File handler (optional) - no colors in files
    if log_file:
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        
        # Simple format for files (colors don't work in text files)
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Create default logger for general use
logger = setup_logger("HierarchicalAgents", level=logging.INFO)


# LEARNING QUESTIONS:
# Q1: Why use logging instead of print()?
# A1: Logging provides:
#     - Different levels (debug, info, error, etc.)
#     - Filtering by level or module
#     - Multiple outputs (console + file)
#     - Timestamps and context
#     - Can be disabled in production

# Q2: What does logger.propagate = False do?
# A2: Prevents logs from being passed to parent loggers
#     Avoids duplicate log messages
#     Gives us full control over output

# Q3: Why separate console and file formatting?
# A3: Console can use colors (ANSI codes)
#     Files should be plain text (colors are garbage in files)
#     Different formatting for different use cases

# Q4: When would you use different log levels?
# A4: DEBUG: Detailed info for debugging (variable values, flow)
#     INFO: Normal operation milestones (agent started, task complete)
#     WARNING: Something unexpected but not critical
#     ERROR: Something failed that needs attention
#     CRITICAL: System-breaking errors
