import os
import sys
import logging
from pathlib import Path
from datetime import datetime

def setup_logging(log_path=None, log_level=logging.INFO):
    """Configure logging with file and console output"""
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Setup handlers
    handlers = [logging.StreamHandler()]
    
    if log_path:
        log_path = Path(log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    # Configure root logger
    logging.root.setLevel(log_level)
    
    # Apply formatter and handlers
    for handler in handlers:
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)

    return logging.getLogger()

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