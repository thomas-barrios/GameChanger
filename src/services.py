"""
GameChanger Windows Services Management
Handles scanning, backup, optimization, and restoration of Windows services
"""

import os
import sys
import json
import logging
import subprocess
import ctypes
import configparser
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse

try:
    from utils import setup_logging
    from messaging import ServiceOutputManager
    from services_definitions import SERVICES_DATABASE, get_services_by_category, get_service_by_internal_name
except ImportError:
    # Fallback for standalone usage
    def setup_logging(log_path=None, log_level=logging.INFO):
        logger = logging.getLogger('GameChanger')
        logger.setLevel(log_level)
        return logger


class ServiceManager:
    """Manages Windows services operations"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.is_admin = self._check_admin_privileges()
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrative privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False
    
    def _ensure_admin_privileges(self):
        """Ensure administrative privileges are available"""
        if not self.is_admin:
            raise PermissionError(
                "Administrative privileges required for service operations. "
                "Please run GameChanger as Administrator."
            )
    
    def _run_powershell_command(self, command: str, timeout: int = 15) -> Tuple[bool, str, str]:
        """Execute PowerShell command and return result"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide PowerShell window
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)
    
    def get_current_service_states(self) -> Dict[str, Dict]:
        """Get current state of all services in our database"""
        services_state = {}
        
        # Get all services with their startup types
        command = "Get-WmiObject -Class Win32_Service | Select-Object Name, DisplayName, StartMode, State | ConvertTo-Json"
        success, stdout, stderr = self._run_powershell_command(command)
        
        if not success:
            self.logger.error(f"Failed to get service states: {stderr}")
            return services_state
        
        try:
            # Parse JSON output
            if stdout.strip():
                services_data = json.loads(stdout)
                if not isinstance(services_data, list):
                    services_data = [services_data]
                
                # Create lookup dictionary
                system_services = {}
                for service in services_data:
                    name = service.get('Name', '').lower()
                    system_services[name] = {
                        'name': service.get('Name', ''),
                        'display_name': service.get('DisplayName', ''),
                        'startup_type': service.get('StartMode', 'Unknown'),
                        'state': service.get('State', 'Unknown')
                    }
                
                # Match with our database
                for service_def in SERVICES_DATABASE:
                    service_key = service_def.internal_name.lower()
                    if service_key in system_services:
                        services_state[service_def.internal_name] = {
                            'display_name': service_def.display_name,
                            'current_startup_type': system_services[service_key]['startup_type'],
                            'current_state': system_services[service_key]['state'],
                            'category': service_def.category,
                            'gaming_rationale': service_def.gaming_rationale,
                            'group': service_def.group
                        }
                    else:
                        # Service not found on system
                        services_state[service_def.internal_name] = {
                            'display_name': service_def.display_name,
                            'current_startup_type': 'NotFound',
                            'current_state': 'NotInstalled',
                            'category': service_def.category,
                            'gaming_rationale': service_def.gaming_rationale,
                            'group': service_def.group
                        }
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse service data: {e}")
        except Exception as e:
            self.logger.error(f"Error processing service states: {e}")
        
        self.logger.info(f"Retrieved state for {len(services_state)} services")
        return services_state
    
    def scan_services(self, output_mgr: ServiceOutputManager) -> Dict[str, Dict]:
        """Scan system services and populate output manager"""
        services_state = self.get_current_service_states()
        
        # Group services by category for organized output
        categories = get_services_by_category()
        
        for category_name, services in categories.items():
            output_mgr.add_service_section(category_name, category_name)
            
            for service_def in services:
                service_name = service_def.internal_name
                if service_name in services_state:
                    service_info = services_state[service_name]
                    
                    # Add service operation (for scan, no target change)
                    output_mgr.add_service_operation(
                        service_name=service_name,
                        display_name=service_def.display_name,
                        current_startup=service_info['current_startup_type'],
                        target_startup=service_info['current_startup_type'],  # Same for scan
                        category=service_def.category,
                        gaming_rationale=service_def.gaming_rationale,
                        success=True
                    )
        
        return services_state
    
    def backup_service_states(self, backup_folder: Path, services_state: Dict[str, Dict]) -> tuple[bool, Path]:
        """Backup current service states to JSON file"""
        try:
            backup_folder.mkdir(parents=True, exist_ok=True)
            
            # Create backup file with same naming convention as config backup
            # backup_folder is already: "D:\GameChanger\Backup\2025-10-22-17-18-54-Services-Backup"
            backup_file_name = f"{backup_folder.name}.json"
            backup_file = backup_folder / backup_file_name
            
            # Create timestamp for backup data
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            # Prepare backup data
            backup_data = {
                "backup_timestamp": timestamp,
                "backup_type": "GameChanger_Services",
                "admin_required": True,
                "services": {}
            }
            
            # Only backup services that exist on the system
            for service_name, service_info in services_state.items():
                if service_info['current_startup_type'] != 'NotFound':
                    backup_data["services"][service_name] = {
                        "display_name": service_info['display_name'],
                        "startup_type": service_info['current_startup_type'],
                        "state": service_info['current_state'],
                        "category": service_info['category'],
                        "group": service_info['group']
                    }
            
            # Write backup file
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # Create restoration .bat file (same pattern as config backup)
            bat_file = backup_folder / "RestoreBackup.bat"
            
            # Calculate correct relative path to GameChanger.exe from backup folder
            # backup_folder is like: D:\GameChanger\Backup\2025-10-22-17-43-38-Services-Backup
            # GameChanger.exe is at: C:\Projects\GameChanger\dist\GameChanger.exe
            # For now, use absolute path to avoid path issues
            exe_path = Path(sys.executable).parent / "GameChanger.exe" if hasattr(sys, '_MEIPASS') else Path(__file__).parent.parent / "dist" / "GameChanger.exe"
            
            bat_content = f'''@echo off
echo GameChanger Services Restoration
echo ================================
echo This will restore Windows services from backup
echo Backup: {backup_file}
echo.
echo WARNING: This requires Administrator privileges
echo Press Ctrl+C to cancel, or
pause

echo Restoring services...
"{exe_path}" services restore --backup-file "%~dp0{backup_file_name}" --force

echo.
echo Services restoration completed!
pause
'''
            
            with open(bat_file, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            self.logger.info(f"Service states backed up to: {backup_file}")
            self.logger.info(f"Restoration script created: {bat_file}")
            return True, backup_file
            
        except Exception as e:
            self.logger.error(f"Failed to backup service states: {e}")
            return False, None
    
    def optimize_services(self, config: Dict, backup_folder: Path, 
                         output_mgr: ServiceOutputManager) -> tuple[bool, Path]:
        """Optimize services based on configuration"""
        self._ensure_admin_privileges()
        
        # Get current service states
        services_state = self.get_current_service_states()
        
        # Backup current states before making changes
        backup_success, backup_file = self.backup_service_states(backup_folder, services_state)
        if not backup_success:
            self.logger.error("Failed to backup service states - aborting optimization")
            return False, None
        
        # Get enabled categories from config
        enabled_categories = config.get('enabled_categories', [])
        if not enabled_categories:
            self.logger.info("No service categories enabled for optimization")
            return True, backup_file
        
        total_changes = 0
        successful_changes = 0
        
        # Process each enabled category
        for category_name in enabled_categories:
            if category_name == "DoNotDisable":
                continue  # Never modify these services
            
            output_mgr.add_service_section(category_name, category_name)
            
            # Get services for this category
            services_by_category = get_services_by_category()
            if category_name not in services_by_category:
                continue
            
            for service_def in services_by_category[category_name]:
                service_name = service_def.internal_name
                
                if service_name not in services_state:
                    continue
                
                service_info = services_state[service_name]
                current_startup = service_info['current_startup_type']
                
                # Skip if service not found on system
                if current_startup == 'NotFound':
                    output_mgr.add_service_operation(
                        service_name=service_name,
                        display_name=service_def.display_name,
                        current_startup=current_startup,
                        target_startup="NotFound",
                        category=service_def.category,
                        gaming_rationale=service_def.gaming_rationale,
                        success=False,
                        error_type="Service not found",
                        error_message="Service not installed on this system"
                    )
                    continue
                
                # Skip if already disabled
                if current_startup.lower() in ['disabled', 'manual']:
                    output_mgr.add_service_operation(
                        service_name=service_name,
                        display_name=service_def.display_name,
                        current_startup=current_startup,
                        target_startup=current_startup,
                        category=service_def.category,
                        gaming_rationale=service_def.gaming_rationale,
                        success=True
                    )
                    continue
                
                # Attempt to disable the service
                total_changes += 1
                success, error_message = self._disable_service(service_name)
                
                if success:
                    successful_changes += 1
                    output_mgr.add_service_operation(
                        service_name=service_name,
                        display_name=service_def.display_name,
                        current_startup=current_startup,
                        target_startup="Disabled",
                        category=service_def.category,
                        gaming_rationale=service_def.gaming_rationale,
                        success=True
                    )
                else:
                    output_mgr.add_service_operation(
                        service_name=service_name,
                        display_name=service_def.display_name,
                        current_startup=current_startup,
                        target_startup="Disabled",
                        category=service_def.category,
                        gaming_rationale=service_def.gaming_rationale,
                        success=False,
                        error_type="Permission denied" if "access" in error_message.lower() else "Service error",
                        error_message=error_message
                    )
        
        self.logger.info(f"Service optimization completed: {successful_changes}/{total_changes} successful")
        return successful_changes == total_changes, backup_file
    
    def _disable_service(self, service_name: str) -> Tuple[bool, str]:
        """Disable a specific service"""
        try:
            # Stop service first if running
            stop_command = f"Stop-Service -Name '{service_name}' -Force -ErrorAction SilentlyContinue"
            self._run_powershell_command(stop_command)
            
            # Set startup type to disabled
            disable_command = f"Set-Service -Name '{service_name}' -StartupType Disabled"
            success, stdout, stderr = self._run_powershell_command(disable_command)
            
            if success:
                return True, "Service disabled successfully"
            else:
                return False, stderr or "Unknown error disabling service"
                
        except Exception as e:
            return False, str(e)
    
    def restore_services(self, backup_file: Path, output_mgr: ServiceOutputManager) -> bool:
        """Restore services from backup file"""
        self._ensure_admin_privileges()
        
        if not backup_file.exists():
            self.logger.error(f"Backup file not found: {backup_file}")
            return False
        
        try:
            # Load backup data
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            if backup_data.get("backup_type") != "GameChanger_Services":
                self.logger.error("Invalid backup file format")
                return False
            
            services_backup = backup_data.get("services", {})
            if not services_backup:
                self.logger.warning("No services found in backup file")
                return True
            
            total_restorations = 0
            successful_restorations = 0
            
            # Group by category for organized output
            categories = {"SafeToDisable": [], "OptionalToDisable": [], "DoNotDisable": []}
            
            for service_name, service_info in services_backup.items():
                category = service_info.get('category', 'Unknown')
                if category in categories:
                    categories[category].append((service_name, service_info))
            
            failed_services = []
            print(f"Restoring {sum(len(services) for services in categories.values())} services...")
            print()
            
            # Process each category
            for category_name, services in categories.items():
                if not services:
                    continue
                    
                output_mgr.add_service_section(category_name, category_name)
                
                for service_name, service_info in services:
                    total_restorations += 1
                    
                    # Get service definition for rationale
                    service_def = get_service_by_internal_name(service_name)
                    gaming_rationale = service_def.gaming_rationale if service_def else "Service restoration"
                    display_name = service_info.get('display_name', service_name)
                    
                    try:
                        # Restore service startup type
                        original_startup = service_info['startup_type']
                        success, error_message = self._restore_service(service_name, original_startup)
                        
                        if success:
                            successful_restorations += 1
                            output_mgr.add_service_operation(
                                service_name=service_name,
                                display_name=display_name,
                                current_startup="Modified",  # Assumed current state
                                target_startup=original_startup,
                                category=category_name,
                                gaming_rationale=gaming_rationale,
                                success=True
                            )
                        else:
                            failed_services.append(f"{display_name}: {error_message}")
                            output_mgr.add_service_operation(
                                service_name=service_name,
                                display_name=display_name,
                                current_startup="Modified",
                                target_startup=original_startup,
                                category=category_name,
                                gaming_rationale=gaming_rationale,
                                success=False,
                                error_type="Restoration failed",
                                error_message=error_message
                            )
                    except KeyboardInterrupt:
                        print(f"\n\n⚠️  Restoration interrupted by user!")
                        print(f"Progress: {successful_restorations}/{total_restorations} services restored")
                        raise
                    except Exception as e:
                        failed_services.append(f"{display_name}: {str(e)}")
                        print(f" ✗ Error: {e}")
            
            print()
            print("=" * 60)
            print(f"Restoration completed: {successful_restorations}/{total_restorations} successful")
            
            if failed_services:
                print(f"Failed services ({len(failed_services)}):")
                for failure in failed_services[:5]:  # Show first 5 failures
                    print(f"  • {failure}")
                if len(failed_services) > 5:
                    print(f"  ... and {len(failed_services) - 5} more")
            
            print("=" * 60)
            
            self.logger.info(f"Service restoration completed: {successful_restorations}/{total_restorations} successful")
            return successful_restorations == total_restorations
            
        except Exception as e:
            self.logger.error(f"Failed to restore services: {e}")
            return False
    
    def _restore_service(self, service_name: str, startup_type: str) -> Tuple[bool, str]:
        """Restore a specific service to its original startup type"""
        try:
            # Get current service status before attempting restore
            status_command = f"Get-Service -Name '{service_name}' -ErrorAction SilentlyContinue | Select-Object StartType, Status | ConvertTo-Json"
            status_success, status_stdout, status_stderr = self._run_powershell_command(status_command)
            
            current_status = "Unknown"
            current_startup = "Unknown"
            if status_success and status_stdout.strip():
                try:
                    status_data = json.loads(status_stdout)
                    current_startup = status_data.get('StartType', 'Unknown')
                    current_status = status_data.get('Status', 'Unknown')
                except:
                    pass
            
            # Set startup type
            restore_command = f"Set-Service -Name '{service_name}' -StartupType {startup_type} -ErrorAction SilentlyContinue"
            success, stdout, stderr = self._run_powershell_command(restore_command)
            
            if not success:
                failure_reason = stderr or "Unknown error restoring service"
                print(f"ERROR: {service_name} to {startup_type}... Failed Restore {failure_reason}, Current {current_status}")
                return False, failure_reason
            
            # Start service if it was originally running and startup type is Auto
            if startup_type.lower() in ['auto', 'automatic']:
                start_command = f"Start-Service -Name '{service_name}' -ErrorAction SilentlyContinue"
                start_success, start_stdout, start_stderr = self._run_powershell_command(start_command)
                if start_success:
                    print(f"OK: {service_name} to {startup_type}... Restored and Started")
                else:
                    print(f"OK: {service_name} to {startup_type}... Restored (start failed)")
            else:
                print(f"OK: {service_name} to {startup_type}... Restored")
            
            return True, "Service restored successfully"
            
        except Exception as e:
            print(f"ERROR: {service_name} to {startup_type}... Failed Restore {str(e)}, Current {current_status}")
            return False, str(e)


def load_services_config(config_path: Path, logger: logging.Logger) -> Dict:
    """Load services configuration from config.ini"""
    import configparser
    
    config = {
        'enabled_categories': [],
        'backup_before_changes': True,
        'show_confirmation': True,
        'service_actions': {}  # Individual service settings
    }

    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return config

    try:
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(config_path, encoding='utf-8')
        
        # Check for legacy [WindowsServices] section first
        if parser.has_section('WindowsServices'):
            services_section = parser['WindowsServices']
            
            if 'EnabledCategories' in services_section:
                categories_str = services_section['EnabledCategories']
                config['enabled_categories'] = [cat.strip() for cat in categories_str.split(',') if cat.strip()]
            
            if 'BackupBeforeChanges' in services_section:
                config['backup_before_changes'] = services_section.getboolean('BackupBeforeChanges')
            
            if 'ShowConfirmation' in services_section:
                config['show_confirmation'] = services_section.getboolean('ShowConfirmation')
        
        # Check for individual service category sections
        service_sections = [s for s in parser.sections() if s.startswith('WindowsServices.')]
        if service_sections:
            # If we have individual service sections, consider all categories enabled
            # and load individual service settings
            categories = set()
            for section_name in service_sections:
                # Extract category from section name (e.g., 'WindowsServices.SafeToDisable' -> 'SafeToDisable')
                category = section_name.split('.', 1)[1] if '.' in section_name else section_name
                categories.add(category)
                
                # Load individual service settings
                section = parser[section_name]
                for service_name, action in section.items():
                    if action.strip() and action.strip() != 'Skip':
                        config['service_actions'][service_name] = action.strip()
            
            config['enabled_categories'] = list(categories)
        
        logger.info(f"Loaded services config: {len(config['enabled_categories'])} categories enabled, {len(config['service_actions'])} individual services configured")
        
    except Exception as e:
        logger.error(f"Error reading services config: {e}")
    
    return config


def services_scan_main(args=None):
    """Main function for services scan command"""
    if args is None:
        parser = argparse.ArgumentParser(description='Scan Windows services')
        parser.add_argument('--config', type=Path, help='Config file path')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level=log_level)
    
    try:
        # Initialize service manager
        service_mgr = ServiceManager(logger)
        
        # Initialize output manager
        output_mgr = ServiceOutputManager(logger, "SERVICES_SCAN")
        output_mgr.start_operation()
        
        # Scan services
        services_state = service_mgr.scan_services(output_mgr)
        
        # Finalize and output results
        output_mgr.finalize_scan_operation()
        
        return 0
        
    except Exception as e:
        logger.error(f"Services scan failed: {e}")
        return 1


def services_backup_main(args=None):
    """Main function for services backup command"""
    if args is None:
        parser = argparse.ArgumentParser(description='Backup Windows services state')
        parser.add_argument('--backup-folder', type=Path, help='Custom backup folder')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level=log_level)
    
    try:
        # Get config path for backup location
        if hasattr(args, 'config') and args.config:
            config_path = args.config
        else:
            # When running from PyInstaller executable, use executable's directory
            if hasattr(sys, '_MEIPASS'):  # Running from PyInstaller bundle
                exe_dir = Path(sys.executable).parent
            else:
                # Development mode - use script directory
                exe_dir = Path(__file__).parent
            config_path = exe_dir / "config.ini"
        
        # Setup backup folder - use configured backup root
        if args.backup_folder:
            backup_folder = args.backup_folder
        else:
            # Read backup root from config.ini (same as backup.py)
            backup_root = Path(r"D:\GameChanger\Backup")  # default
            try:
                if config_path.exists():
                    parser = configparser.ConfigParser(interpolation=None)
                    parser.read(config_path, encoding='utf-8')
                    if parser.has_section('Paths') and 'BackupRoot' in parser['Paths']:
                        backup_root = Path(os.path.expandvars(parser['Paths']['BackupRoot']))
            except:
                pass  # Use default if config reading fails
            
            # Create timestamped backup folder following same pattern as config backup
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            backup_name = f"{timestamp}-Services-Backup"
            backup_folder = backup_root / backup_name
        
        # Initialize service manager
        service_mgr = ServiceManager(logger)
        
        # Check admin privileges
        if not service_mgr.is_admin:
            print("ERROR: Administrative privileges required for services backup.")
            print("Please run GameChanger as Administrator.")
            return 1
        
        print("=== WINDOWS SERVICES BACKUP ===")
        print("Creating backup of current Windows services state...")
        print(f"Backup location: {backup_folder}")
        print()
        
        # Get current service states
        services_state = service_mgr.get_current_service_states()
        
        # Create backup
        backup_success, backup_file = service_mgr.backup_service_states(backup_folder, services_state)
        if not backup_success:
            print("ERROR: Failed to create services backup.")
            return 1
        
        # Display success message
        bat_file_path = backup_file.parent / "RestoreBackup.bat"
        print("✅ Services backup completed successfully!")
        print()
        print(f"Backup file: {backup_file}")
        print(f"Backup size: {backup_file.stat().st_size:,} bytes")
        if bat_file_path.exists():
            print(f"Restore script: {bat_file_path}")
        print()
        print("To restore services later, use either:")
        print(f"1. Run the restore script: {bat_file_path}")
        print(f"2. Or use CLI: GameChanger.exe services restore --backup-file \"{backup_file}\"")
        print()
        print("NOTE: This backup is also created automatically before each")
        print("      'services optimize' operation for safety.")
        
        return 0
        
    except Exception as e:
        logger.error(f"Services backup failed: {e}")
        return 1


def services_list_backups_main(args=None):
    """Main function for listing services backups"""
    if args is None:
        parser = argparse.ArgumentParser(description='List available services backups')
        args = parser.parse_args()
    
    try:
        # Get config path for backup location
        if hasattr(args, 'config') and args.config:
            config_path = args.config
        else:
            # When running from PyInstaller executable, use executable's directory
            if hasattr(sys, '_MEIPASS'):  # Running from PyInstaller bundle
                exe_dir = Path(sys.executable).parent
            else:
                # Development mode - use script directory
                exe_dir = Path(__file__).parent
            config_path = exe_dir / "config.ini"
        
        # Read backup root from config.ini
        backup_root = Path(r"D:\GameChanger\Backup")  # default
        try:
            if config_path.exists():
                parser = configparser.ConfigParser(interpolation=None)
                parser.read(config_path, encoding='utf-8')
                if parser.has_section('Paths') and 'BackupRoot' in parser['Paths']:
                    backup_root = Path(os.path.expandvars(parser['Paths']['BackupRoot']))
        except:
            pass  # Use default if config reading fails
        
        print("=== AVAILABLE SERVICES BACKUPS ===")
        print(f"Backup location: {backup_root}")
        print()
        
        if not backup_root.exists():
            print("No backup directory found.")
            print(f"Expected location: {backup_root}")
            return 0
        
        # Find services backup folders
        services_backups = []
        for item in backup_root.iterdir():
            if item.is_dir() and "Services-Backup" in item.name:
                # Look for the JSON backup file
                json_file = item / f"{item.name}.json"
                bat_file = item / "RestoreBackup.bat"
                if json_file.exists():
                    services_backups.append({
                        'folder': item,
                        'json': json_file,
                        'bat': bat_file,
                        'size': json_file.stat().st_size,
                        'timestamp': item.name.split('-Services-Backup')[0]
                    })
        
        if not services_backups:
            print("No services backups found.")
            print("Create a backup with: GameChanger.exe services backup")
            return 0
        
        # Sort by timestamp (newest first)
        services_backups.sort(key=lambda x: x['timestamp'], reverse=True)
        
        print(f"Found {len(services_backups)} services backup(s):")
        print()
        
        for i, backup in enumerate(services_backups, 1):
            print(f"{i}. {backup['timestamp']}")
            print(f"   Folder: {backup['folder']}")
            print(f"   JSON file: {backup['json']}")
            print(f"   Size: {backup['size']:,} bytes")
            print(f"   Restore script: {'✓' if backup['bat'].exists() else '✗'}")
            print()
            print(f"   To restore: GameChanger.exe services restore --backup-file \"{backup['json']}\"")
            print(f"   Or run: {backup['bat']}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"Error listing backups: {e}")
        return 1


def services_optimize_main(args=None):
    """Main function for services optimization command"""
    if args is None:
        parser = argparse.ArgumentParser(description='Optimize Windows services')
        parser.add_argument('--config', type=Path, help='Config file path')
        parser.add_argument('--backup-folder', type=Path, help='Backup folder path')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        parser.add_argument('--force', action='store_true', help='Skip confirmation')
        args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level=log_level)
    
    try:
        # Load configuration
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
        services_config = load_services_config(config_path, logger)
        
        # Check if any categories are enabled
        if not services_config['enabled_categories']:
            print("No service categories enabled for optimization.")
            print("Edit the [WindowsServices] section in config.ini to enable optimization.")
            return 0
        
        # Setup backup folder - use configured backup root like config backup does
        if args.backup_folder:
            backup_folder = args.backup_folder
        else:
            # Read backup root from config.ini (same as backup.py)
            backup_root = Path(r"D:\GameChanger\Backup")  # default
            try:
                if config_path.exists():
                    parser = configparser.ConfigParser(interpolation=None)
                    parser.read(config_path, encoding='utf-8')
                    if parser.has_section('Paths') and 'BackupRoot' in parser['Paths']:
                        backup_root = Path(os.path.expandvars(parser['Paths']['BackupRoot']))
            except:
                pass  # Use default if config reading fails
            
            # Create timestamped backup folder following same pattern as config backup
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            backup_name = f"{timestamp}-Services-Backup"
            backup_folder = backup_root / backup_name
        
        # Initialize service manager
        service_mgr = ServiceManager(logger)
        
        # Handle dry-run mode - skip admin check and show what would happen
        if hasattr(args, 'dry_run') and args.dry_run:
            print("=== DRY RUN MODE - No changes will be made ===")
            print(f"Would optimize services in categories: {', '.join(services_config['enabled_categories'])}")
            
            # Show actual backup path that would be used
            if args.backup_folder:
                backup_folder_preview = args.backup_folder
            else:
                # Calculate the backup path the same way as the real operation
                backup_root = Path(r"D:\GameChanger\Backup")  # default
                try:
                    if config_path.exists():
                        parser = configparser.ConfigParser(interpolation=None)
                        parser.read(config_path, encoding='utf-8')
                        if parser.has_section('Paths') and 'BackupRoot' in parser['Paths']:
                            backup_root = Path(os.path.expandvars(parser['Paths']['BackupRoot']))
                except:
                    pass
                
                timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                backup_name = f"{timestamp}-Services-Backup"
                backup_folder_preview = backup_root / backup_name
            
            print(f"Would create backup in: {backup_folder_preview}")
            print(f"Backup file: {backup_folder_preview / f'{backup_folder_preview.name}.json'}")
            print(f"Restore script: {backup_folder_preview / 'RestoreBackup.bat'}")
            print("Would modify the following services based on config.ini:")
            
            # Show what services would be modified
            from services_definitions import get_services_by_category
            all_services_by_category = get_services_by_category()
            
            for category in services_config['enabled_categories']:
                if category in all_services_by_category:
                    category_services = all_services_by_category[category]
                    print(f"\n[{category}] - {len(category_services)} services:")
                    for svc in category_services[:5]:  # Show first 5 as example
                        action = services_config['service_actions'].get(svc.internal_name, 'Disabled' if category == 'SafeToDisable' else 'Skip')
                        if action != 'Skip':
                            print(f"  • {svc.display_name} -> {action}")
                    if len(category_services) > 5:
                        print(f"  ... and {len(category_services) - 5} more services")
            
            print("\nTo actually apply these changes, run without --dry-run and with Administrator privileges.")
            return 0
        
        # Check admin privileges for real execution
        if not service_mgr.is_admin:
            print("ERROR: Administrative privileges required for service optimization.")
            print("Please run GameChanger as Administrator.")
            return 1
        
        # Show confirmation if required
        if services_config['show_confirmation'] and not args.force:
            print(f"About to optimize services in categories: {', '.join(services_config['enabled_categories'])}")
            print("This will modify Windows service startup types.")
            print("A backup will be created automatically before making changes.")
            print()
            print("NOTE: You can create a manual backup anytime with:")
            print("      GameChanger.exe services backup")
            print()
            response = input("Continue? (y/N): ").strip().lower()
            if response != 'y':
                print("Operation cancelled.")
                return 0
        
        # Initialize output manager
        output_mgr = ServiceOutputManager(logger, "SERVICES_OPTIMIZATION")
        output_mgr.start_operation()
        
        # Optimize services
        success, backup_file_path = service_mgr.optimize_services(services_config, backup_folder, output_mgr)
        
        # Finalize and output results
        output_mgr.finalize_optimization_operation()
        
        # Display backup location to user
        if backup_file_path and backup_file_path.exists():
            bat_file_path = backup_file_path.parent / "RestoreBackup.bat"
            print()
            print("=" * 60)
            print("✅ SERVICE BACKUP CREATED")
            print("=" * 60)
            print(f"Backup file: {backup_file_path}")
            print(f"Backup size: {backup_file_path.stat().st_size:,} bytes")
            if bat_file_path.exists():
                print(f"Restore script: {bat_file_path}")
            print()
            print("To restore services later, use either:")
            print(f"1. Run the restore script: {bat_file_path}")
            print(f"2. Or use CLI: GameChanger.exe services restore --backup-file \"{backup_file_path}\"")
            print("=" * 60)
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Services optimization failed: {e}")
        return 1


def services_restore_main(args=None):
    """Main function for services restoration command"""
    if args is None:
        parser = argparse.ArgumentParser(description='Restore Windows services from backup')
        parser.add_argument('--backup-file', required=True, type=Path, help='Services backup file')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        parser.add_argument('--force', action='store_true', help='Skip confirmation')
        args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level=log_level)
    
    try:
        # Initialize service manager
        service_mgr = ServiceManager(logger)
        
        # Check admin privileges
        if not service_mgr.is_admin:
            print("ERROR: Administrative privileges required for service restoration.")
            print("Please run GameChanger as Administrator.")
            return 1
        
        # Validate backup file
        if not args.backup_file.exists():
            print(f"ERROR: Backup file not found: {args.backup_file}")
            return 1
        
        # Show confirmation if required
        if not args.force:
            print(f"About to restore services from: {args.backup_file}")
            print("This will modify Windows service startup types.")
            print()
            response = input("Continue? (y/N): ").strip().lower()
            if response != 'y':
                print("Operation cancelled.")
                return 0
        
        # Initialize output manager
        output_mgr = ServiceOutputManager(logger, "SERVICES_RESTORATION")
        output_mgr.start_operation()
        
        # Restore services
        success = service_mgr.restore_services(args.backup_file, output_mgr)
        
        # Finalize and output results
        output_mgr.finalize_optimization_operation()
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Services restoration failed: {e}")
        return 1


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] in ['scan', 'optimize', 'restore']:
        command = sys.argv[1]
        sys.argv = [sys.argv[0]] + sys.argv[2:]  # Remove command from args
        
        if command == 'scan':
            sys.exit(services_scan_main())
        elif command == 'optimize':
            sys.exit(services_optimize_main())
        elif command == 'restore':
            sys.exit(services_restore_main())
    else:
        print("Usage: python services.py {scan|optimize|restore} [options]")
        sys.exit(1)