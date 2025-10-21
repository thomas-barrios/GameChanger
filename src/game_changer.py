import argparse
import logging
from pathlib import Path
from backup import main as backup_main
from restore import main as restore_main
from utils import setup_logging

def create_parser():
    parser = argparse.ArgumentParser(description="GameChanger - DCS Configuration Manager")
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable detailed logging')
    parser.add_argument('-c', '--config', type=Path, help='Custom config file path')
    parser.add_argument('-d', '--dry-run', action='store_true', help='Test run without making changes')
    parser.add_argument('-f', '--force', action='store_true', help='Override warnings')

    subparsers = parser.add_subparsers(dest='command', required=True)

    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create new backup')
    backup_parser.add_argument('--name', help='Custom backup name')

    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('--backup-folder', required=True, type=Path, help='Backup folder path')

    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Configure scheduled backups')
    schedule_parser.add_argument('--preset', choices=['atlogon', 'daily', 'weekly'], default='atlogon', help='Schedule preset')
    schedule_parser.add_argument('--time', help='Time for daily/weekly backups (HH:MM)')

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level=log_level)

    try:
        if args.command == 'backup':
            backup_main(args)
        elif args.command == 'restore':
            restore_main(args)
        elif args.command == 'schedule':
            schedule_backup(args)
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())