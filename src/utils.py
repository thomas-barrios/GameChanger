import os
import sys
import logging
from pathlib import Path
from datetime import datetime

def setup_logging(log_path=None, log_level=logging.INFO):
    """Configure logging with file and console output"""
    # Get or create the GameChanger logger (not root logger)
    logger = logging.getLogger('GameChanger')
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure the GameChanger logger level
    logger.setLevel(log_level)
    
    # Check if we already have handlers
    has_console_handler = any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) for h in logger.handlers)
    
    # DO NOT add console handler - we want clean console output from print statements only
    # Console output will be handled by the messaging system's print statements
    # All logger.info() calls should only go to the file
    
    # Add file handler if log_path is provided
    if log_path:
        # Check if we already have a file handler for this specific path
        log_path = Path(log_path)
        existing_file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_path:
                existing_file_handler = handler
                break
        
        if not existing_file_handler:
            try:
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_path, encoding="utf-8")
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                # File handler added successfully - no need to log this
            except Exception as e:
                # If file logging fails, at least log to console
                logger.error(f"Failed to initialize file logging to {log_path}: {e}")

    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False

    return logger

def is_admin():
    """Check if running with administrator privileges"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def relaunch_as_admin(script_path, args):
    """Relaunch the script with administrator privileges"""
    if is_admin():
        return True

    import ctypes
    ctypes.windll.shell32.ShellExecuteW(
        None, 
        "runas", 
        sys.executable,
        f'"{script_path}" {" ".join(args)}',
        None, 
        1
    )
    return False

def create_schedule_task(task_name, command, schedule_type, time=None):
    """Create Windows scheduled task"""
    import subprocess
    
    if schedule_type == "atlogon":
        schedule = "/SC ONLOGON"
    elif schedule_type in ["daily", "weekly"]:
        if not time:
            time = "12:00"
        schedule = f"/SC {schedule_type.upper()} /ST {time}"
    else:
        raise ValueError(f"Invalid schedule type: {schedule_type}")

    cmd = (
        f'schtasks /Create /TN "GameChanger\\{task_name}" '
        f'/TR "{command}" {schedule} /RU "%USERNAME%" /RL HIGHEST /F'
    )
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create task: {result.stderr}")

    return True