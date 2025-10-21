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

def load_config(config_path: Path, logger) -> dict:
    """Load configuration from config.txt"""
    config = {
        'backup_root': Path(r"D:\GameChanger\Backup"),  # default
        'saved_games_path': Path(rf"D:\Users\{os.environ.get('USERNAME')}\Saved Games"),  # default
        'max_backups': 10,
        'compress_backups': False,
        'log_level': 'INFO'
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
                elif key == 'maxbackups':
                    config['max_backups'] = int(value)
                elif key == 'compressbackups':
                    config['compress_backups'] = value.lower() == 'true'
                elif key == 'loglevel':
                    config['log_level'] = value.upper()
                    
        logger.info(f"Loaded config from {config_path}")
    except Exception as e:
        logger.error(f"Error reading config {config_path}: {e}")
    
    return config

def load_files_from_txt(config_path: Path, saved_games_path: Path, logger) -> list:
    """Load file paths from backup_files.txt and expand placeholders"""
    files_to_backup = []
    
    if not config_path.exists():
        logger.warning(f"Backup files config not found: {config_path}")
        return files_to_backup
    
    try:
        content = config_path.read_text(encoding='utf-8')
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Expand placeholders
            expanded_line = line.replace('$SavedGamesPath', str(saved_games_path))
            expanded_line = expanded_line.replace('{SavedGamesPath}', str(saved_games_path))
            expanded_line = os.path.expandvars(expanded_line)
            
            files_to_backup.append(expanded_line)
            
        logger.info(f"Loaded {len(files_to_backup)} file paths from {config_path}")
    except Exception as e:
        logger.error(f"Error reading backup files config {config_path}: {e}")
    
    return files_to_backup

def main(args=None):
    """Main backup function supporting both CLI and module usage"""
    if args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument('--name', help='Custom backup name')
        parser.add_argument('--config', type=Path, help='Config file path')
        parser.add_argument('--dry-run', action='store_true', help='Test run')
        args = parser.parse_args()

    # Load config
    config_path = args.config if args.config else Path(__file__).parent / "config.txt"
    config = load_config(config_path, logging.getLogger())

    # Setup backup folder and logging
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    backup_name = f"{timestamp}-{args.name}" if args.name else f"{timestamp}-Backup"
    backup_folder = config['backup_root'] / backup_name
    log_file = config['backup_root'] / "_BackupLog.txt"

    # Initialize logging
    logger = setup_logging(log_file)
    logger.info(f"=== BACKUP STARTED to {backup_folder} ===")

    if args.dry_run:
        logger.info("DRY RUN - No changes will be made")
        return 0

    # config file next to script (human-readable TXT)
    backup_files_config = Path(__file__).parent / "backup_files.txt"
    # If running as executable, look in the current directory
    if not backup_files_config.exists():
        backup_files_config = Path("backup_files.txt")
    files_to_backup = load_files_from_txt(backup_files_config, config['saved_games_path'], logger)

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

    logger.info("=== BACKUP COMPLETE ===")
    logger.info(f"Files backed up: {backup_count} / {len(files_to_backup)}")

    return 0

if __name__ == "__main__":
    sys.exit(main())