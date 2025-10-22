import os
import sys
import shutil
import logging
from datetime import datetime
from pathlib import Path
import argparse
import configparser

try:
    from utils import setup_logging
    from messaging import OutputManager, PathHelper
except Exception:
    def setup_logging(log_path):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s]: %(message)s",
            handlers=[
                logging.FileHandler(log_path, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('GameChanger')
    
    # Fallback if messaging module not available
    class OutputManager:
        def __init__(self, logger, operation_type="BACKUP"):
            self.logger = logger
        def start_operation(self): pass
        def add_section(self, section_name, base_path): pass
        def add_operation(self, source_path, dest_path, section, success, error_type=None, error_message=None):
            if success:
                self.logger.info(f"{source_path} -> {dest_path}")
            else:
                self.logger.error(f"Failed to copy {source_path} -> {dest_path}: {error_message}")
        def finalize_operation(self, log_file_path=None): pass
    
    class PathHelper:
        @staticmethod
        def get_section_base_path(section, file_paths):
            return str(Path(file_paths[0]).parent) if file_paths else ""

def load_config(config_path: Path, logger, log_to_file_only=None) -> dict:
    """Load configuration from config.ini"""
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
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(config_path, encoding='utf-8')
        
        # Load General settings
        if parser.has_section('General'):
            general = parser['General']
            if 'LogLevel' in general:
                config['log_level'] = general['LogLevel'].upper()
            if 'MaxBackups' in general:
                config['max_backups'] = general.getint('MaxBackups')
            if 'CompressBackups' in general:
                config['compress_backups'] = general.getboolean('CompressBackups')
        
        # Load Path settings
        if parser.has_section('Paths'):
            paths = parser['Paths']
            if 'BackupRoot' in paths:
                config['backup_root'] = Path(os.path.expandvars(paths['BackupRoot']))
            if 'SavedGamesPath' in paths:
                config['saved_games_path'] = Path(os.path.expandvars(paths['SavedGamesPath']))
                    
        if log_to_file_only:
            log_to_file_only(f"Loaded config from {config_path}")
        # No console logging for config loading
    except Exception as e:
        logger.error(f"Error reading config {config_path}: {e}")
    
    return config

def create_restore_batch(backup_folder: Path, logger) -> bool:
    """Create RestoreBackup.bat in the backup folder for silent restoration"""
    try:
        # Get the path to the GameChanger executable
        # When running from the built exe, sys.executable points to GameChanger.exe
        import sys
        if hasattr(sys, '_MEIPASS'):  # Running from PyInstaller bundle
            exe_path = Path(sys.executable)
        else:
            # Development mode - look for the built exe
            script_dir = Path(__file__).parent
            project_root = script_dir.parent
            exe_path = project_root / "dist" / "GameChanger.exe"
            
            # If exe doesn't exist in expected location, try to find it
            if not exe_path.exists():
                # Try to find GameChanger.exe in common locations
                possible_paths = [
                    Path.cwd() / "GameChanger.exe",
                    Path.cwd() / "dist" / "GameChanger.exe", 
                    project_root / "GameChanger.exe"
                ]
                for path in possible_paths:
                    if path.exists():
                        exe_path = path
                        break
                else:
                    exe_path = "GameChanger.exe"  # Fallback to relative path
        
        batch_content = f'''@echo off
title GameChanger - Configuration Restore
echo ================================================
echo GameChanger - Configuration Restore
echo ================================================
echo.
echo Restoring configuration from:
echo %~dp0
echo.
echo Log file: {backup_folder.parent / "_RestoreLog.txt"}
echo.

"{exe_path}" --verbose --force restore --backup-folder "%~dp0."

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================
    echo RESTORATION FAILED - Manual Instructions
    echo ================================================
    echo.
    echo 1. Open Command Prompt as Administrator
    echo 2. Navigate to: {exe_path.parent if isinstance(exe_path, Path) else Path(exe_path).parent}
    echo 3. Run: "{exe_path}" --verbose --force restore --backup-folder "%~dp0."
    echo 4. Check log file: {backup_folder.parent / "_RestoreLog.txt"}
    echo.
    echo Press any key to close...
    pause >nul
) else (
    echo.
    echo Restoration completed successfully!
    echo Check log file: {backup_folder.parent / "_RestoreLog.txt"}
    echo.
    echo Press any key to close...
    pause >nul
)
'''
        
        batch_file = backup_folder / "RestoreBackup.bat"
        batch_file.write_text(batch_content, encoding='utf-8')
        logger.info(f"Created restore batch file: {batch_file}")  # Changed back to info for file logging
        return True
        
    except Exception as e:
        logger.error(f"Failed to create restore batch file: {e}")
        return False

def load_files_from_config(config_path: Path, saved_games_path: Path, logger) -> dict:
    """Load file paths from config.ini file sections and expand placeholders"""
    files_by_section = {}
    
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return files_by_section
    
    try:
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(config_path, encoding='utf-8')
        
        # File sections to process (excluding General, Paths, WindowsServices)
        file_sections = ['DCS', 'VR', 'System']
        
        for section_name in file_sections:
            if parser.has_section(section_name):
                section_files = []
                section = parser[section_name]
                for key, value in section.items():
                    # Expand placeholders
                    expanded_path = value.replace('{SavedGamesPath}', str(saved_games_path))
                    expanded_path = os.path.expandvars(expanded_path)
                    section_files.append(expanded_path)
                
                if section_files:
                    files_by_section[section_name] = section_files
                    
        total_files = sum(len(files) for files in files_by_section.values())
        logger.info(f"Loaded {total_files} file paths from {config_path} across {len(files_by_section)} sections")  # Changed back to info for file logging
    except Exception as e:
        logger.error(f"Error reading config file {config_path}: {e}")
    
    return files_by_section

def main(args=None):
    """Main backup function supporting both CLI and module usage"""
    if args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument('--name', help='Custom backup name')
        parser.add_argument('--config', type=Path, help='Config file path')
        parser.add_argument('--dry-run', action='store_true', help='Test run')
        args = parser.parse_args()

    # Load config
    if args.config:
        config_path = args.config
    else:
        # When running from PyInstaller executable, use executable's directory
        if hasattr(sys, '_MEIPASS'):  # Running from PyInstaller bundle
            exe_dir = Path(sys.executable).parent
        else:
            # Development mode - use script directory
            exe_dir = Path(__file__).parent
        config_path = exe_dir / "config.ini"
    
    # Initialize logging first (to avoid duplicate setup)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    backup_name = f"{timestamp}-{args.name}" if args.name else f"{timestamp}-Backup"
    
    # Create a temp config to get backup root for logging setup
    temp_config = {'backup_root': Path(r"D:\GameChanger\Backup")}
    try:
        if config_path.exists():
            parser = configparser.ConfigParser(interpolation=None)
            parser.read(config_path, encoding='utf-8')
            if parser.has_section('Paths') and 'BackupRoot' in parser['Paths']:
                temp_config['backup_root'] = Path(os.path.expandvars(parser['Paths']['BackupRoot']))
    except:
        pass  # Use default if config reading fails
    
    backup_folder = temp_config['backup_root'] / backup_name
    log_file = temp_config['backup_root'] / "_BackupLog.txt"

    # Initialize logging (this will add file handler if not already present)
    logger = setup_logging(log_file)
    
    # Function to log only to file
    def log_to_file_only(message):
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                record = logging.LogRecord(
                    name=logger.name, level=logging.INFO, pathname="", lineno=0,
                    msg=message, args=(), exc_info=None
                )
                handler.emit(record)
    
    # Log backup start (file only)
    log_to_file_only("=== BACKUP OPERATION STARTED ===")
    log_to_file_only(f"Backup folder: {backup_folder}")
    log_to_file_only(f"Config file: {config_path}")
    
    # Now load full config with the logger
    config = load_config(config_path, logger, log_to_file_only)
    
    # Initialize messaging system
    output_mgr = OutputManager(logger, "BACKUP")
    output_mgr.start_operation()
    
    if args.dry_run:
        logger.info("DRY RUN - No changes will be made")
        return 0

    # Load files from config.ini grouped by section
    files_by_section = load_files_from_config(config_path, config['saved_games_path'], logger)

    backup_count = 0
    total_files = sum(len(files) for files in files_by_section.values())

    # Process each section
    for section_name, files_list in files_by_section.items():
        if not files_list:
            continue
            
        # Get base path for this section
        base_path = PathHelper.get_section_base_path(section_name, files_list)
        output_mgr.add_section(section_name, base_path)
        
        # Support files and directories listed in config.ini file sections.
        # If an entry is a folder, walk it recursively and back up all files inside.
        for file in files_list:
            src = Path(file)
            if src.exists() and src.is_dir():
                # Handle directory recursion
                for p in src.rglob('*'):
                    if not p.is_file():
                        continue
                    dest_rel = Path(str(p).lstrip("\\/").replace(":", ""))
                    dest_path = backup_folder / dest_rel
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.copy2(p, dest_path)
                        backup_count += 1
                        output_mgr.add_operation(p, dest_path, section_name, True)
                    except Exception as e:
                        error_type = "Permission denied" if "permission" in str(e).lower() else "Other error"
                        output_mgr.add_operation(p, dest_path, section_name, False, error_type, str(e))
            else:
                file_path = src
                if file_path.is_file():
                    dest_rel = Path(str(file_path).lstrip("\\/").replace(":", ""))
                    dest_path = backup_folder / dest_rel
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.copy2(file_path, dest_path)
                        backup_count += 1
                        output_mgr.add_operation(file_path, dest_path, section_name, True)
                    except Exception as e:
                        error_type = "Permission denied" if "permission" in str(e).lower() else "Other error"
                        output_mgr.add_operation(file_path, dest_path, section_name, False, error_type, str(e))
                else:
                    # File not found
                    output_mgr.add_operation(file_path, Path(""), section_name, False, "File not found", f"Missing: {file_path}")

    # Finalize messaging and create restore batch if successful
    output_mgr.finalize_operation(log_file)
    
    if backup_count > 0:
        create_restore_batch(backup_folder, logger)
    
    # Log backup completion (file only)
    log_to_file_only("=== BACKUP OPERATION COMPLETED ===")
    log_to_file_only(f"Files backed up: {backup_count}")
    log_to_file_only(f"Log file: {log_file}")

    return 0

if __name__ == "__main__":
    sys.exit(main())