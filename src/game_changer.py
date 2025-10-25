import argparse
import logging
from pathlib import Path
from backup import main as backup_main
from restore import main as restore_main
from services import services_scan_main, services_backup_main, services_list_backups_main, services_optimize_main, services_restore_main
from utils import setup_logging

def create_parser():
    parser = argparse.ArgumentParser(description="GameChanger - DCS Configuration Manager with Performance Impact Analysis")
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable detailed logging')
    parser.add_argument('-c', '--config', type=Path, help='Custom config file path')
    parser.add_argument('-d', '--dry-run', action='store_true', help='Test run without making changes')
    parser.add_argument('-f', '--force', action='store_true', help='Override warnings')

    subparsers = parser.add_subparsers(dest='command')

    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create new configuration backup for performance tracking')
    backup_parser.add_argument('--name', help='Custom backup name')

    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore configuration from backup')
    restore_parser.add_argument('backup_index', nargs='?', type=int, help='Backup index (1=newest, 2=second newest, etc.)')
    restore_parser.add_argument('--backup-folder', type=Path, help='Specific backup folder path')
    restore_parser.add_argument('--last', action='store_true', help='Restore from the most recent backup')

    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Configure scheduled backups for continuous performance monitoring')
    schedule_parser.add_argument('--preset', choices=['atlogon', 'daily', 'weekly'], default='atlogon', help='Schedule preset')
    schedule_parser.add_argument('--time', help='Time for daily/weekly backups (HH:MM)')

    # Services command
    services_parser = subparsers.add_parser('services', help='Optimize Windows services for gaming performance')
    services_subparsers = services_parser.add_subparsers(dest='services_command', required=True)

    # Services scan subcommand
    services_scan_parser = services_subparsers.add_parser('scan', help='Scan Windows services for gaming optimization opportunities')

    # Services backup subcommand  
    services_backup_parser = services_subparsers.add_parser('backup', help='Backup current Windows services state before optimization')
    services_backup_parser.add_argument('--backup-folder', type=Path, help='Custom backup folder')

    # Services list-backups subcommand
    services_list_parser = services_subparsers.add_parser('list-backups', help='List available service backup states')

    # Services optimize subcommand
    services_optimize_parser = services_subparsers.add_parser('optimize', help='Apply gaming performance optimizations to Windows services')
    services_optimize_parser.add_argument('--backup-folder', type=Path, help='Custom backup folder')

    # Services restore subcommand
    services_restore_parser = services_subparsers.add_parser('restore', help='Restore services from backup state')
    services_restore_parser.add_argument('--backup-file', required=True, type=Path, help='Services backup file')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Analyze performance impact of configuration changes between backups')
    compare_parser.add_argument('--backup1', type=Path, help='First backup folder (older)')
    compare_parser.add_argument('--backup2', type=Path, help='Second backup folder (newer)')
    compare_parser.add_argument('--latest', action='store_true', help='Compare against latest backup automatically')
    compare_parser.add_argument('--output', type=Path, help='Custom output file path')

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    # If no command provided, show help
    if not args.command:
        parser.print_help()
        return 0

    # Setup logging only once at the main entry point
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level=log_level)

    try:
        if args.command == 'backup':
            backup_main(args)
        elif args.command == 'restore':
            restore_main(args)
        elif args.command == 'schedule':
            logger.error("Schedule command not implemented yet")
            return 1
        elif args.command == 'services':
            if args.services_command == 'scan':
                return services_scan_main(args)
            elif args.services_command == 'backup':
                return services_backup_main(args)
            elif args.services_command == 'list-backups':
                return services_list_backups_main(args)
            elif args.services_command == 'optimize':
                return services_optimize_main(args)
            elif args.services_command == 'restore':
                return services_restore_main(args)
            else:
                logger.error(f"Unknown services command: {args.services_command}")
                return 1
        elif args.command == 'compare':
            from comparison import compare_main
            return compare_main(args)
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())