"""
GameChanger Directory Management
Handles automatic creation and management of GameChanger directory structure
"""

import os
from pathlib import Path
import logging
from typing import Optional


def ensure_gamechanger_directories(config: dict, logger: Optional[logging.Logger] = None) -> bool:
    """
    Ensure GameChanger directory structure exists, creating it if necessary
    
    Args:
        config: Configuration dictionary containing paths
        logger: Optional logger for output
        
    Returns:
        bool: True if directories exist or were created successfully
    """
    if logger is None:
        logger = logging.getLogger('GameChanger')
    
    # Get the GameChanger root directory
    backup_root = config.get('backup_root', Path(r"C:\Users\Thomas\Documents\GameChanger\Backups"))
    gamechanger_root = backup_root.parent if backup_root.name == 'Backups' else backup_root.parent
    
    # Define required directory structure
    required_dirs = [
        gamechanger_root,
        gamechanger_root / "Backups",
        gamechanger_root / "Reports", 
        gamechanger_root / "Logs",
        gamechanger_root / "FrameView"  # For users who want to copy FrameView CSV here
    ]
    
    created_dirs = []
    failed_dirs = []
    
    try:
        for directory in required_dirs:
            if not directory.exists():
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(directory)
                    logger.info(f"Created directory: {directory}")
                except Exception as e:
                    failed_dirs.append((directory, str(e)))
                    logger.error(f"Failed to create directory {directory}: {e}")
            else:
                logger.debug(f"Directory already exists: {directory}")
        
        # Create a welcome file on first setup
        welcome_file = gamechanger_root / "README.txt"
        if not welcome_file.exists() and created_dirs:
            try:
                welcome_content = f"""GameChanger Directory Structure
=====================================

This directory contains all GameChanger data and configuration files.

Directory Structure:
├── Backups/        - Configuration backups with performance data
├── Reports/        - Generated comparison and analysis reports  
├── Logs/          - Application logs and operation history
└── FrameView/     - Optional: Copy FrameView CSV here for centralized management

FrameView Integration:
By default, GameChanger looks for FrameView data at:
C:\\Users\\Thomas\\Documents\\FrameView\\FrameView_Summary.csv

To use a different location, edit the FrameViewCSVPath setting in config.ini.

For support and documentation, visit:
https://github.com/thomas-barrios/GameChanger

Created: {gamechanger_root}
Version: GameChanger v1.0
"""
                welcome_file.write_text(welcome_content, encoding='utf-8')
                logger.info(f"Created welcome file: {welcome_file}")
            except Exception as e:
                logger.warning(f"Could not create welcome file: {e}")
        
        if failed_dirs:
            logger.warning(f"Failed to create {len(failed_dirs)} directories")
            for directory, error in failed_dirs:
                logger.warning(f"  - {directory}: {error}")
            return False
        
        if created_dirs:
            logger.info(f"GameChanger directory structure initialized at: {gamechanger_root}")
            logger.info(f"Created {len(created_dirs)} new directories")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to ensure GameChanger directories: {e}")
        return False


def create_backup_directory(backup_root: Path, backup_name: str, logger: Optional[logging.Logger] = None) -> Optional[Path]:
    """
    Create a new backup directory with proper error handling
    
    Args:
        backup_root: Root directory for backups
        backup_name: Name of the backup folder
        logger: Optional logger
        
    Returns:
        Path to created backup directory or None if failed
    """
    if logger is None:
        logger = logging.getLogger('GameChanger')
    
    backup_folder = backup_root / backup_name
    
    try:
        backup_folder.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created backup directory: {backup_folder}")
        return backup_folder
    except Exception as e:
        logger.error(f"Failed to create backup directory {backup_folder}: {e}")
        return None


def get_reports_directory(config: dict) -> Path:
    """Get the reports directory path from config"""
    backup_root = config.get('backup_root', Path(r"C:\Users\Thomas\Documents\GameChanger\Backups"))
    gamechanger_root = backup_root.parent if backup_root.name == 'Backups' else backup_root.parent
    return gamechanger_root / "Reports"


def get_logs_directory(config: dict) -> Path:
    """Get the logs directory path from config"""
    backup_root = config.get('backup_root', Path(r"C:\Users\Thomas\Documents\GameChanger\Backups"))
    gamechanger_root = backup_root.parent if backup_root.name == 'Backups' else backup_root.parent
    return gamechanger_root / "Logs"


def validate_directory_permissions(directory: Path, logger: Optional[logging.Logger] = None) -> bool:
    """
    Validate that we have read/write permissions to a directory
    
    Args:
        directory: Directory to validate
        logger: Optional logger
        
    Returns:
        bool: True if permissions are sufficient
    """
    if logger is None:
        logger = logging.getLogger('GameChanger')
    
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return False
    
    try:
        # Test write permission
        test_file = directory / ".gamechanger_test"
        test_file.touch()
        test_file.unlink()
        
        logger.debug(f"Directory permissions validated: {directory}")
        return True
        
    except Exception as e:
        logger.error(f"Insufficient permissions for directory {directory}: {e}")
        return False