import logging
import os
from datetime import datetime

# Module-level logger so utility functions (like relaunch_as_admin) can log
# even if setup_logging() has not been called yet.
logger = logging.getLogger(__name__)

def setup_logging(log_file, level=logging.INFO):
    """Setup logging to file and console with colored output."""
    logging.basicConfig(level=level, format='%(asctime)s [%(levelname)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ])
    # Simple color hack (Windows-compatible via colorama if needed; skip for minimalism)
    return logging.getLogger(__name__)

def is_admin():
    """Check if running as admin (Windows-specific)."""
    import ctypes
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def relaunch_as_admin(script_path, args=None):
    """Relaunch script as admin if not already."""
    import sys
    import subprocess
    # ensure a logger exists even if caller didn't set one up
    logger = logging.getLogger()
    logger.warning("Relaunching as Administrator...")
    try:
        subprocess.call(['powershell', 'Start-Process', 'python', '-ArgumentList',
                             f'"{script_path}" {" ".join(args)}', '-Verb', 'RunAs'])
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to relaunch: {e}")