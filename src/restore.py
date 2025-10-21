import os
import sys
import shutil
import logging
from pathlib import Path
from utils import setup_logging

def copy_with_permissions(src: Path, dst: Path, logger, dry_run: bool = False) -> bool:
    """Safe copy with permission handling and dry-run support"""
    try:
        if dry_run:
            logger.info(f"DRY RUN - Would copy: {src} -> {dst}")
            return True
            
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        logger.debug(f"Copied: {dst}")
        return True
        
    except PermissionError:
        logger.error(f"Permission denied: {dst}")
        return False
        
    except Exception as e:
        logger.error(f"Failed to copy {src} to {dst}: {e}")
        return False

def map_backup_to_original_path(backup_path: Path, rel_path: Path, logger) -> Path:
    """Convert a backup path to its original location using backed up drive letter"""
    path_str = str(rel_path)
    
    # Skip restore batch
    if path_str == "Restore-This-Backup.bat":
        return None
        
    # Split path into parts
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

def main(args=None):
    """Main restore function supporting both CLI and module usage"""
    if args is None:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--backup-folder', required=True, type=Path)
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--force', action='store_true')
        args = parser.parse_args()

    backup_path = args.backup_folder
    if not backup_path.exists():
        print(f"Backup folder not found: {backup_path}")
        return 1

    # Setup logging
    log_file = backup_path.parent / "_RestoreLog.txt"
    logger = setup_logging(log_file)
    logger.info(f"=== RESTORE STARTED from {backup_path} ===")

    if args.dry_run:
        logger.info("DRY RUN - No changes will be made")

    files_restored = 0
    files_failed = 0

    # Walk the backup folder and restore files
    for src in backup_path.rglob('*'):
        if not src.is_file():
            continue
            
        # Convert backup path to original path
        rel_path = src.relative_to(backup_path)
        dst = map_backup_to_original_path(backup_path, rel_path, logger)
        
        if dst is None:  # Skip restore batch
            continue

        logger.info(f"Restoring: {dst}")
        
        # Check if destination exists and force not specified
        if dst.exists() and not args.force:
            logger.warning(f"File exists, skipping (use --force to override): {dst}")
            files_failed += 1
            continue

        if copy_with_permissions(src, dst, logger, args.dry_run):
            files_restored += 1
        else:
            files_failed += 1

    logger.info("=== RESTORE COMPLETE ===")
    logger.info(f"Files restored: {files_restored}")
    logger.info(f"Files failed: {files_failed}")

    return 0 if files_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())