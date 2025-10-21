import logging
import os
import sys
import re
import shutil
import subprocess
from pathlib import Path
import argparse
import ctypes
from utils import setup_logging

def copy_with_permissions(src: Path, dst: Path, logger) -> bool:
    """Safe copy with permission handling and robocopy fallback"""
    try:
        # Ensure parent exists
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        # Try directS
        if dst.exists():
            dst.chmod(0o666)  # Make writable
        shutil.copy2(src, dst)
        return True
    except PermissionError:
        # Fall back to robocopy for difficult files
        logger.info(f"Using robocopy fallback for {src}")
        try:
            cmd = [
                "robocopy",
                str(src.parent),
                str(dst.parent),
                src.name,
                "/COPYALL",  # Copy all file info
                "/R:1",      # Retry once
                "/W:1"       # Wait 1 second between retries
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            success = result.returncode < 8  # Robocopy codes 0-7 are OK
            if not success:
                logger.error(f"Robocopy failed: {result.stderr}")
            return success
        except Exception as e:
            logger.error(f"Robocopy failed: {e}")
            return False
    except Exception as e:
        logger.error(f"Copy failed: {e}")
        return False

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def map_backup_to_original_path(backup_path: Path, rel_path: Path, logger) -> Path:
    """
    Convert a backup path to its original location using backed up drive letter.
    If no drive letter found, defaults to C:
    """
    path_str = str(rel_path)
    
    # Skip restore batch
    if path_str == "Restore-This-Backup.bat":
        return None
        
    # Split path into parts using os-independent separator
    path_parts = path_str.split(os.sep)
    
    # Check if first part matches a drive letter pattern (single letter)
    if len(path_parts[0]) == 1 and path_parts[0].isalpha():
        drive = f"{path_parts[0]}:\\"  # Use backed up drive letter with separator
        path_parts.pop(0)  # Remove it from parts
    else:
        # No drive letter in backup path, default to C:
        drive = 'C:\\'
        
    # Reconstruct path with proper Windows separators
    return Path(drive + '\\'.join(path_parts))

def main():
    # Require admin rights
    if not is_admin():
        logger = logging.getLogger()
        logger.error("This script requires administrator privileges")
        if sys.platform == 'win32':
            # Re-run with elevation
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{__file__}" {" ".join(sys.argv[1:])}', None, 1
            )
        sys.exit(1)

    parser = argparse.ArgumentParser(description="PC Restore for DCS/GameChanger")
    parser.add_argument("--backup_folder", required=True, help="Path to backup folder")
    args = parser.parse_args()

    backup_path = Path(args.backup_folder)
    if not backup_path.is_dir():
        print(f"Error: Backup folder not found: {backup_path}")
        sys.exit(1)

    # Setup logging
    log_file = Path(r"D:\GameChanger\Backup\_RestoreLog.txt")
    logger = setup_logging(str(log_file))
    logger.info(f"=== RESTORE STARTED from {backup_path} ===")

    # Track statistics
    files_restored = 0
    files_failed = 0

    # Walk the backup folder and restore files
    for src in backup_path.rglob('*'):
        if not src.is_file():
            continue
            
        # Get path relative to backup root and map to original location
        rel_path = src.relative_to(backup_path)
        dst = map_backup_to_original_path(backup_path, rel_path, logger)
        
        if dst is None:  # Skip restore batch
            continue
            
        logger.info(f"Restoring: {dst}")
        if copy_with_permissions(src, dst, logger):
            files_restored += 1
        else:
            files_failed += 1

    logger.info(f"=== RESTORE COMPLETE ===")
    logger.info(f"Files restored: {files_restored}")
    logger.info(f"Files failed: {files_failed}")

if __name__ == "__main__":
    main()