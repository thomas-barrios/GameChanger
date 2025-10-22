import os
import sys
import shutil
import logging
from pathlib import Path

try:
    from utils import setup_logging
    from messaging import OutputManager, PathHelper
except Exception:
    # Fallback if messaging module not available
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
    
    class OutputManager:
        def __init__(self, logger, operation_type="RESTORE"):
            self.logger = logger
        def start_operation(self): pass
        def add_section(self, section_name, base_path): pass
        def add_operation(self, source_path, dest_path, section, success, error_type=None, error_message=None):
            if success:
                self.logger.info(f"Restored: {dest_path}")
            else:
                self.logger.error(f"Failed to restore {source_path} to {dest_path}: {error_message}")
        def finalize_operation(self, log_file_path=None): pass
    
    class PathHelper:
        @staticmethod
        def get_section_base_path(section, file_paths):
            return str(Path(file_paths[0]).parent) if file_paths else ""

def copy_with_permissions(src: Path, dst: Path, logger, dry_run: bool = False) -> tuple[bool, str, str]:
    """Safe copy with permission handling and dry-run support"""
    try:
        if dry_run:
            logger.debug(f"DRY RUN - Would copy: {src} -> {dst}")
            return True, "success", ""
            
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        logger.debug(f"Copied: {dst}")
        return True, "success", ""
        
    except PermissionError as e:
        error_msg = f"Permission denied: {dst}"
        logger.error(error_msg)
        return False, "Permission denied", str(e)
        
    except FileNotFoundError as e:
        error_msg = f"File not found: {src}"
        logger.error(error_msg)
        return False, "File not found", str(e)
        
    except Exception as e:
        error_msg = f"Failed to copy {src} to {dst}: {e}"
        logger.error(error_msg)
        return False, "Other error", str(e)

def group_files_by_destination_section(backup_path: Path) -> dict:
    """Group restored files by their destination base paths to create sections"""
    sections = {}
    
    # Walk through backup and group files by common destination bases
    for src in backup_path.rglob('*'):
        if not src.is_file():
            continue
            
        # Convert backup path to original path
        rel_path = src.relative_to(backup_path)
        dst = map_backup_to_original_path(backup_path, rel_path, logging.getLogger())
        
        if dst is None:  # Skip restore batch files
            continue
            
        # Determine section based on destination path patterns
        dst_str = str(dst).lower()
        section = "Unknown"
        
        if "saved games\\dcs" in dst_str:
            section = "DCS"
        elif any(vr_path in dst_str for vr_path in ["pitool", "pimax", "quad-views", "foveated"]):
            section = "VR"  
        elif any(sys_path in dst_str for sys_path in ["nvidia", "capframex", "discord", "programdata"]):
            section = "System"
        elif "appdata" in dst_str:
            section = "System"
        
        if section not in sections:
            sections[section] = []
        sections[section].append((src, dst))
    
    return sections

def map_backup_to_original_path(backup_path: Path, rel_path: Path, logger) -> Path:
    """Convert a backup path to its original location using backed up drive letter"""
    path_str = str(rel_path)
    
    # Skip restore batch files
    if path_str in ["Restore-This-Backup.bat", "RestoreBackup.bat"]:
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
    import time
    start_time = time.time()
    
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
    
    # Initialize messaging system  
    output_mgr = OutputManager(logger, "RESTORE")
    output_mgr.start_operation()

    if args.dry_run:
        logger.info("DRY RUN - No changes will be made")

    files_restored = 0
    files_failed = 0

    # Group files by sections for organized output
    sections = group_files_by_destination_section(backup_path)
    
    # Process each section
    for section_name, file_pairs in sections.items():
        if not file_pairs:
            continue
            
        # Get base path for this section (from destination paths)
        dest_paths = [str(dst) for src, dst in file_pairs]
        base_path = PathHelper.get_section_base_path(section_name, dest_paths)
        output_mgr.add_section(section_name, base_path)
        
        # Process files in this section
        for src, dst in file_pairs:
            # Check if destination exists and force not specified
            if dst.exists() and not args.force:
                logger.warning(f"File exists, skipping (use --force to override): {dst}")
                files_failed += 1
                output_mgr.add_operation(src, dst, section_name, False, "File exists", "Use --force to override")
                continue

            success, error_type, error_message = copy_with_permissions(src, dst, logger, args.dry_run)
            if success:
                files_restored += 1
                output_mgr.add_operation(src, dst, section_name, True)
            else:
                files_failed += 1
                output_mgr.add_operation(src, dst, section_name, False, error_type, error_message)

    duration = time.time() - start_time
    
    # Finalize messaging
    output_mgr.finalize_operation(log_file)

    return 0 if files_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())