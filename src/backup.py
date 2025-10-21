import os
import sys
import shutil
import logging
from datetime import datetime
from pathlib import Path
import argparse

try:
    from utils import setup_logging
except Exception:
    def setup_logging(log_path):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            handlers=[
                logging.FileHandler(log_path, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger()

def load_files_from_txt(config_path: Path, saved_games_path: Path, logger):
    """
    Load file list from a human-readable text file.
    - Lines starting with '#' are group headers (logged but ignored as paths).
    - Blank lines and lines starting with ';' or '//' are ignored.
    - Supports $SavedGamesPath or {SavedGamesPath} placeholders and Windows %ENV% vars.
    NOTE: This function does NOT create a template file — the backup_files.txt must exist.
    """
    if not config_path.exists():
        logger.error(f"Config missing: {config_path} — please create it (no template is auto-created).")
        return []

    try:
        raw = config_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read config {config_path}: {e}")
        return []

    files = []
    current_group = None
    for ln in raw.splitlines():
        s = ln.strip()
        if not s or s.startswith("//") or s.startswith(";"):
            continue
        if s.startswith("#"):
            current_group = s.lstrip("# ").strip()
            logger.info(f"Config group: {current_group}")
            continue
        # Replace placeholders and expand env vars
        s = s.replace("$SavedGamesPath", str(saved_games_path))
        s = s.replace("{SavedGamesPath}", str(saved_games_path))
        s = os.path.expandvars(s)
        files.append(s)
    return files

def load_config(config_path: Path, logger) -> dict:
    """Load configuration from config.txt"""
    config = {
        'backup_root': Path(r"C:\GameChanger\Backup"),  # default
        'saved_games_path': Path(rf"D:\Users\{os.environ.get('USERNAME')}\Saved Games")  # default
    }
    
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return config

    try:
        content = config_path.read_text(encoding='utf-8')
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip().lower()
                value = os.path.expandvars(value.strip())
                if key == 'backuproot':
                    config['backup_root'] = Path(value)
                elif key == 'savedgamespath':
                    config['saved_games_path'] = Path(value)
        logger.info(f"Loaded config from {config_path}")
    except Exception as e:
        logger.error(f"Error reading config {config_path}: {e}")
    
    return config

def main():
    parser = argparse.ArgumentParser(description="Config Backup for Games/GameChanger")
    args = parser.parse_args()

    # Load config before setting up logging
    config_path = Path(__file__).parent / "config.txt"
    username = os.environ.get('USERNAME') or (os.getlogin() if hasattr(os, "getlogin") else Path.home().name)
    
    # Initialize with defaults, then load config
    config = load_config(config_path, logging.getLogger())
    backup_root = config['backup_root']
    saved_games_path = config['saved_games_path']

    # Ensure the backup root exists before initializing logging
    backup_root.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    backup_folder = backup_root / f"{timestamp}-Backup"
    log_file = backup_root / "_BackupLog.txt"
    restore_batch_name = "Restore-This-Backup.bat"
    # call restore.py (next to this script) with the backup folder path as the single argument
    restore_script_path = Path(__file__).parent / "restore.py"

    logger = setup_logging(str(log_file))

    backup_folder.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created backup folder: {backup_folder}")

    # config file next to script (human-readable TXT)
    config_path = Path(__file__).parent / "backup_files.txt"
    files_to_backup = load_files_from_txt(config_path, saved_games_path, logger)

    backup_count = 0

    # Support files and directories listed in backup_files.txt.
    # If an entry is a folder, walk it recursively and back up all files inside.
    for file in files_to_backup:
        src = Path(file)
        if src.exists() and src.is_dir():
            logger.info(f"BACKUP FOLDER: {src} (recursing)")
            for p in src.rglob('*'):
                if not p.is_file():
                    continue
                dest_rel = Path(str(p).lstrip("\\/").replace(":", ""))
                dest_path = backup_folder / dest_rel
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(p, dest_path)
                    backup_count += 1
                    logger.info(f"{p} -> {dest_path}")
                except Exception as e:
                    logger.error(f"Failed to copy {p} -> {dest_path}: {e}")
        else:
            file_path = src
            if file_path.is_file():
                dest_rel = Path(str(file_path).lstrip("\\/").replace(":", ""))
                dest_path = backup_folder / dest_rel
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(file_path, dest_path)
                    backup_count += 1
                    logger.info(f"{file_path} -> {dest_path}")
                except Exception as e:
                    logger.error(f"Failed to copy {file_path} -> {dest_path}: {e}")
            else:
                logger.warning(f"MISSING: {file_path}")

    # Generate BAT that invokes restore.py with the backup folder path
    restore_batch_path = backup_folder / restore_batch_name
    restore_content = (
        '@echo off\r\n'
        'echo Checking for admin rights...\r\n'
        'net session >nul 2>&1\r\n'
        'if %errorLevel% neq 0 (\r\n'
        '    echo Requesting administrative privileges...\r\n'
        '    powershell -Command "Start-Process -FilePath \\"cmd\\" -ArgumentList \\"/c %~f0\\" -Verb RunAs"\r\n'
        '    exit /b\r\n'
        ')\r\n'
        f'echo Running restore from {backup_folder}...\r\n'
        f'"{sys.executable}" "{restore_script_path}" --backup_folder="{backup_folder}" > "%TEMP%\\restore_output.txt" 2>&1\r\n'
        'echo.\r\n'
        'echo --- Restore Output ---\r\n'
        'type "%TEMP%\\restore_output.txt"\r\n'
        'echo --- End Output ---\r\n'
        'echo.\r\n'
        'pause\r\n'
    )
    try:
        restore_batch_path.write_text(restore_content, encoding="utf-8")
        logger.info(f"Created: {restore_batch_path}")
    except Exception as e:
        logger.error(f"Failed to write restore batch {restore_batch_path}: {e}")

    logger.info("=== BACKUP COMPLETE ===")
    logger.info(f"Files backed up: {backup_count} / {len(files_to_backup)}")

if __name__ == "__main__":
    main()