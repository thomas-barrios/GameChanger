"""
GameChanger Configuration Comparison Engine
Analyzes and compares configuration files between backups to detect setting changes
"""

import os
import sys
import json
import re
import difflib
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

try:
    from utils import setup_logging
except ImportError:
    def setup_logging(log_level=logging.INFO):
        logging.basicConfig(level=log_level)
        return logging.getLogger('GameChanger')


@dataclass
class ConfigChange:
    """Represents a single configuration change"""
    file_path: str
    setting_name: str
    old_value: Any
    new_value: Any
    change_type: str  # 'modified', 'added', 'removed'
    category: str     # 'DCS', 'VR', 'System', etc.
    impact_level: str = 'UNKNOWN'  # 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'
    description: str = ""


@dataclass
class FileComparison:
    """Results of comparing a single file between backups"""
    file_path: str
    category: str
    exists_in_backup1: bool
    exists_in_backup2: bool
    binary_identical: bool
    size_change: int  # bytes difference
    changes: List[ConfigChange] = field(default_factory=list)
    parse_error: str = ""


@dataclass
class BackupComparison:
    """Complete comparison results between two backups"""
    backup1_path: Path
    backup2_path: Path
    backup1_timestamp: str
    backup2_timestamp: str
    file_comparisons: List[FileComparison] = field(default_factory=list)
    services_changes: List[Dict] = field(default_factory=list)
    summary_stats: Dict[str, int] = field(default_factory=dict)


class ConfigurationParser:
    """Parsers for different configuration file formats"""
    
    @staticmethod
    def parse_lua_config(file_path: Path) -> Dict[str, Any]:
        """Parse DCS options.lua and similar Lua configuration files"""
        settings = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract options table settings
            # Pattern for: ["setting"] = value,
            pattern = r'\["([^"]+)"\]\s*=\s*([^,\n]+),?'
            matches = re.findall(pattern, content)
            
            for setting, value in matches:
                # Clean up the value
                value = value.strip()
                
                # Convert to appropriate type
                if value == 'true':
                    settings[setting] = True
                elif value == 'false':
                    settings[setting] = False
                elif value.startswith('"') and value.endswith('"'):
                    settings[setting] = value[1:-1]  # Remove quotes
                elif value.isdigit():
                    settings[setting] = int(value)
                elif '.' in value and value.replace('.', '').isdigit():
                    settings[setting] = float(value)
                else:
                    settings[setting] = value
            
            # Also look for nested tables
            # Pattern for complex structures like graphics settings
            nested_pattern = r'\["([^"]+)"\]\s*=\s*\{([^}]+)\}'
            nested_matches = re.findall(nested_pattern, content, re.DOTALL)
            
            for setting, table_content in nested_matches:
                nested_settings = {}
                inner_matches = re.findall(pattern, table_content)
                for inner_setting, inner_value in inner_matches:
                    inner_value = inner_value.strip()
                    if inner_value == 'true':
                        nested_settings[inner_setting] = True
                    elif inner_value == 'false':
                        nested_settings[inner_setting] = False
                    elif inner_value.startswith('"') and inner_value.endswith('"'):
                        nested_settings[inner_setting] = inner_value[1:-1]
                    else:
                        nested_settings[inner_setting] = inner_value
                
                settings[setting] = nested_settings
                
        except Exception as e:
            raise ValueError(f"Failed to parse Lua file {file_path}: {e}")
        
        return settings
    
    @staticmethod
    def parse_json_config(file_path: Path) -> Dict[str, Any]:
        """Parse JSON configuration files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON file {file_path}: {e}")
    
    @staticmethod
    def parse_cfg_config(file_path: Path) -> Dict[str, Any]:
        """Parse .cfg configuration files (simple key=value format)"""
        settings = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('--'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Convert to appropriate type
                        if value.lower() == 'true':
                            settings[key] = True
                        elif value.lower() == 'false':
                            settings[key] = False
                        elif value.isdigit():
                            settings[key] = int(value)
                        elif value.replace('.', '').isdigit() and value.count('.') == 1:
                            settings[key] = float(value)
                        else:
                            settings[key] = value
                            
        except Exception as e:
            raise ValueError(f"Failed to parse CFG file {file_path}: {e}")
        
        return settings
    
    @staticmethod
    def parse_file(file_path: Path) -> Dict[str, Any]:
        """Parse configuration file based on extension"""
        extension = file_path.suffix.lower()
        
        if extension == '.lua':
            return ConfigurationParser.parse_lua_config(file_path)
        elif extension == '.json':
            return ConfigurationParser.parse_json_config(file_path)
        elif extension in ['.cfg', '.ini']:
            return ConfigurationParser.parse_cfg_config(file_path)
        else:
            # For unknown formats, try to read as text and do simple analysis
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {'_raw_content': content, '_content_length': len(content)}
            except:
                return {}


class ConfigComparator:
    """Main comparison engine for configuration files"""
    
    def __init__(self, logger=None):
        self.logger = logger or setup_logging()
        self.parser = ConfigurationParser()
    
    def compare_backups(self, backup1_path: Path, backup2_path: Path) -> BackupComparison:
        """Compare two complete backups"""
        self.logger.info(f"Comparing backups: {backup1_path.name} vs {backup2_path.name}")
        
        comparison = BackupComparison(
            backup1_path=backup1_path,
            backup2_path=backup2_path,
            backup1_timestamp=self._extract_timestamp(backup1_path.name),
            backup2_timestamp=self._extract_timestamp(backup2_path.name)
        )
        
        # Find all configuration files in both backups
        config_files = self._find_config_files(backup1_path, backup2_path)
        
        # Compare each file
        for rel_path, (file1, file2, category) in config_files.items():
            file_comparison = self._compare_config_file(file1, file2, rel_path, category)
            comparison.file_comparisons.append(file_comparison)
        
        # Compare services if available
        services_comparison = self._compare_services(backup1_path, backup2_path)
        comparison.services_changes = services_comparison
        
        # Generate summary statistics
        comparison.summary_stats = self._generate_summary_stats(comparison)
        
        return comparison
    
    def _extract_timestamp(self, backup_name: str) -> str:
        """Extract timestamp from backup folder name"""
        # Extract timestamp from format like "2025-10-22-15-48-33-Backup"
        parts = backup_name.split('-')
        if len(parts) >= 6:
            return f"{parts[0]}-{parts[1]}-{parts[2]} {parts[3]}:{parts[4]}:{parts[5]}"
        return backup_name
    
    def _find_config_files(self, backup1_path: Path, backup2_path: Path) -> Dict[str, Tuple[Optional[Path], Optional[Path], str]]:
        """Find all configuration files in both backups"""
        config_files = {}
        
        # Extensions we can parse
        config_extensions = {'.lua', '.json', '.cfg', '.ini'}
        
        # Scan both backups
        all_files = set()
        
        # Get files from backup1
        if backup1_path.exists():
            for file_path in backup1_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in config_extensions:
                    rel_path = file_path.relative_to(backup1_path)
                    all_files.add(rel_path)
        
        # Get files from backup2
        if backup2_path.exists():
            for file_path in backup2_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in config_extensions:
                    rel_path = file_path.relative_to(backup2_path)
                    all_files.add(rel_path)
        
        # Create comparison pairs
        for rel_path in all_files:
            file1 = backup1_path / rel_path if (backup1_path / rel_path).exists() else None
            file2 = backup2_path / rel_path if (backup2_path / rel_path).exists() else None
            category = self._categorize_file(rel_path)
            config_files[str(rel_path)] = (file1, file2, category)
        
        return config_files
    
    def _categorize_file(self, rel_path: Path) -> str:
        """Categorize a file by its path"""
        path_str = str(rel_path).lower()
        
        if any(dcs_path in path_str for dcs_path in ['dcs', 'saved games']):
            return 'DCS'
        elif any(vr_path in path_str for vr_path in ['pimax', 'pitool', 'quad-views', 'foveated']):
            return 'VR'
        elif any(sys_path in path_str for sys_path in ['nvidia', 'capframex', 'discord', 'programdata']):
            return 'System'
        else:
            return 'Other'
    
    def _compare_config_file(self, file1: Optional[Path], file2: Optional[Path], 
                           rel_path: str, category: str) -> FileComparison:
        """Compare a single configuration file between backups"""
        comparison = FileComparison(
            file_path=rel_path,
            category=category,
            exists_in_backup1=file1 is not None and file1.exists(),
            exists_in_backup2=file2 is not None and file2.exists(),
            binary_identical=False,
            size_change=0
        )
        
        # If one file doesn't exist, it's a simple add/remove
        if not comparison.exists_in_backup1:
            comparison.changes.append(ConfigChange(
                file_path=rel_path,
                setting_name="FILE_ADDED",
                old_value=None,
                new_value="File added",
                change_type="added",
                category=category,
                impact_level="MEDIUM"
            ))
            return comparison
        
        if not comparison.exists_in_backup2:
            comparison.changes.append(ConfigChange(
                file_path=rel_path,
                setting_name="FILE_REMOVED",
                old_value="File existed",
                new_value=None,
                change_type="removed",
                category=category,
                impact_level="HIGH"
            ))
            return comparison
        
        # Both files exist - do detailed comparison
        try:
            # Check if files are binary identical
            comparison.binary_identical = self._files_identical(file1, file2)
            comparison.size_change = file2.stat().st_size - file1.stat().st_size
            
            if comparison.binary_identical:
                return comparison  # No changes
            
            # Parse and compare configurations
            try:
                config1 = self.parser.parse_file(file1)
                config2 = self.parser.parse_file(file2)
                
                changes = self._compare_configs(config1, config2, rel_path, category)
                comparison.changes = changes
                
            except Exception as e:
                comparison.parse_error = str(e)
                # Fall back to binary difference indication
                comparison.changes.append(ConfigChange(
                    file_path=rel_path,
                    setting_name="BINARY_CHANGE",
                    old_value=f"File size: {file1.stat().st_size} bytes",
                    new_value=f"File size: {file2.stat().st_size} bytes",
                    change_type="modified",
                    category=category,
                    impact_level="UNKNOWN",
                    description=f"Parse error: {e}"
                ))
                
        except Exception as e:
            comparison.parse_error = f"File comparison error: {e}"
        
        return comparison
    
    def _files_identical(self, file1: Path, file2: Path) -> bool:
        """Check if two files are binary identical"""
        try:
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                return hashlib.md5(f1.read()).hexdigest() == hashlib.md5(f2.read()).hexdigest()
        except:
            return False
    
    def _compare_configs(self, config1: Dict, config2: Dict, file_path: str, category: str) -> List[ConfigChange]:
        """Compare two parsed configuration dictionaries"""
        changes = []
        
        # Get all keys from both configs
        all_keys = set(config1.keys()) | set(config2.keys())
        
        for key in all_keys:
            old_value = config1.get(key)
            new_value = config2.get(key)
            
            if key not in config1:
                # Setting was added
                changes.append(ConfigChange(
                    file_path=file_path,
                    setting_name=key,
                    old_value=None,
                    new_value=new_value,
                    change_type="added",
                    category=category,
                    impact_level=self._assess_impact(key, None, new_value, category)
                ))
            elif key not in config2:
                # Setting was removed
                changes.append(ConfigChange(
                    file_path=file_path,
                    setting_name=key,
                    old_value=old_value,
                    new_value=None,
                    change_type="removed",
                    category=category,
                    impact_level=self._assess_impact(key, old_value, None, category)
                ))
            elif old_value != new_value:
                # Setting was modified
                if isinstance(old_value, dict) and isinstance(new_value, dict):
                    # Recursive comparison for nested settings
                    nested_changes = self._compare_configs(old_value, new_value, f"{file_path}::{key}", category)
                    changes.extend(nested_changes)
                else:
                    changes.append(ConfigChange(
                        file_path=file_path,
                        setting_name=key,
                        old_value=old_value,
                        new_value=new_value,
                        change_type="modified",
                        category=category,
                        impact_level=self._assess_impact(key, old_value, new_value, category)
                    ))
        
        return changes
    
    def _assess_impact(self, setting_name: str, old_value: Any, new_value: Any, category: str) -> str:
        """Assess the potential impact of a setting change"""
        setting_lower = setting_name.lower()
        
        # Filter out joystick/input device changes that don't affect performance
        joystick_patterns = [
            'joy', 'stick', 'button', 'axis', 'input_device', 'controller',
            'bind', 'key_', 'mouse_', 'joystick_', 'device_', 'keymap',
            'throttle', 'rudder', 'pedal', 'hat', 'pov', 'trigger'
        ]
        
        if any(pattern in setting_lower for pattern in joystick_patterns):
            return 'IGNORED'  # New impact level for filtered changes
        
        # High impact settings (performance critical)
        high_impact_patterns = [
            'resolution', 'msaa', 'ssaa', 'shadow', 'texture', 'visibility', 
            'preload', 'forest', 'water', 'effects', 'clouds', 'terrain',
            'fps', 'vsync', 'fullscreen', 'gamma', 'brightness'
        ]
        
        # Medium impact settings  
        medium_impact_patterns = [
            'audio', 'sound', 'voice', 'volume', 'comm', 'sensitivity'
        ]
        
        # Check patterns
        if any(pattern in setting_lower for pattern in high_impact_patterns):
            return 'HIGH'
        elif any(pattern in setting_lower for pattern in medium_impact_patterns):
            return 'MEDIUM'
        elif category == 'DCS' and 'option' in setting_lower:
            return 'MEDIUM'  # DCS options are generally important
        else:
            return 'LOW'
    
    def _compare_services(self, backup1_path: Path, backup2_path: Path) -> List[Dict]:
        """Compare Windows services between backups"""
        services_changes = []
        
        # Look for services backup files
        services1_file = None
        services2_file = None
        
        # Find services JSON files
        for file in backup1_path.rglob('*.json'):
            if 'Services-Backup' in file.name:
                services1_file = file
                break
        
        for file in backup2_path.rglob('*.json'):
            if 'Services-Backup' in file.name:
                services2_file = file
                break
        
        if services1_file and services2_file:
            try:
                with open(services1_file, 'r', encoding='utf-8') as f:
                    services1 = json.load(f).get('services', {})
                
                with open(services2_file, 'r', encoding='utf-8') as f:
                    services2 = json.load(f).get('services', {})
                
                # Compare service states
                all_services = set(services1.keys()) | set(services2.keys())
                
                for service_name in all_services:
                    svc1 = services1.get(service_name, {})
                    svc2 = services2.get(service_name, {})
                    
                    changes = {}
                    
                    if not svc1:
                        changes['type'] = 'service_added'
                        changes['service_name'] = service_name
                        changes['new_state'] = svc2
                    elif not svc2:
                        changes['type'] = 'service_removed'
                        changes['service_name'] = service_name
                        changes['old_state'] = svc1
                    else:
                        # Check for changes
                        if svc1.get('startup_type') != svc2.get('startup_type'):
                            changes['type'] = 'startup_type_changed'
                            changes['service_name'] = service_name
                            changes['old_startup_type'] = svc1.get('startup_type')
                            changes['new_startup_type'] = svc2.get('startup_type')
                            changes['display_name'] = svc1.get('display_name', service_name)
                        
                        if svc1.get('state') != svc2.get('state'):
                            if changes:
                                # Create separate change for state
                                state_change = {
                                    'type': 'state_changed',
                                    'service_name': service_name,
                                    'old_state': svc1.get('state'),
                                    'new_state': svc2.get('state'),
                                    'display_name': svc1.get('display_name', service_name)
                                }
                                services_changes.append(state_change)
                            else:
                                changes['type'] = 'state_changed'
                                changes['service_name'] = service_name
                                changes['old_state'] = svc1.get('state')
                                changes['new_state'] = svc2.get('state')
                                changes['display_name'] = svc1.get('display_name', service_name)
                    
                    if changes:
                        services_changes.append(changes)
                        
            except Exception as e:
                self.logger.error(f"Failed to compare services: {e}")
        
        return services_changes
    
    def _generate_summary_stats(self, comparison: BackupComparison) -> Dict[str, int]:
        """Generate summary statistics for the comparison"""
        stats = {
            'total_files_compared': len(comparison.file_comparisons),
            'files_changed': 0,
            'files_unchanged': 0,
            'files_added': 0,
            'files_removed': 0,
            'settings_changed': 0,
            'settings_added': 0,
            'settings_removed': 0,
            'high_impact_changes': 0,
            'medium_impact_changes': 0,
            'low_impact_changes': 0,
            'services_changes': len(comparison.services_changes)
        }
        
        for file_comp in comparison.file_comparisons:
            if not file_comp.exists_in_backup1:
                stats['files_added'] += 1
            elif not file_comp.exists_in_backup2:
                stats['files_removed'] += 1
            elif file_comp.changes:
                stats['files_changed'] += 1
            else:
                stats['files_unchanged'] += 1
            
            for change in file_comp.changes:
                # Skip ignored changes (joystick/input device changes)
                if change.impact_level == 'IGNORED':
                    continue
                    
                if change.change_type == 'added':
                    stats['settings_added'] += 1
                elif change.change_type == 'removed':
                    stats['settings_removed'] += 1
                elif change.change_type == 'modified':
                    stats['settings_changed'] += 1
                
                if change.impact_level == 'HIGH':
                    stats['high_impact_changes'] += 1
                elif change.impact_level == 'MEDIUM':
                    stats['medium_impact_changes'] += 1
                elif change.impact_level == 'LOW':
                    stats['low_impact_changes'] += 1
        
        return stats


def compare_main(args=None):
    """Main function for comparison command"""
    import configparser
    
    if args is None:
        import argparse
        parser = argparse.ArgumentParser(description='Analyze performance impact of GameChanger configuration changes')
        parser.add_argument('--backup1', type=Path, help='First backup folder (older baseline)')
        parser.add_argument('--backup2', type=Path, help='Second backup folder (newer configuration)')
        parser.add_argument('--latest', action='store_true', help='Compare against latest backup automatically')
        parser.add_argument('--output', type=Path, help='Custom output file path for performance report')
        parser.add_argument('--verbose', action='store_true', help='Verbose output for detailed analysis')
        args = parser.parse_args()
    
    # Setup logging - handle both global verbose and local verbose
    verbose = getattr(args, 'verbose', False) or getattr(args, 'v', False)
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create a simple logger since we don't need file logging for comparison
    logger = logging.getLogger('GameChanger')
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)
    
    try:
        # Get backup root from config
        config_path = Path(__file__).parent / "config.ini"
        backup_root = Path(r"D:\GameChanger\Backup")  # default
        
        try:
            if config_path.exists():
                parser = configparser.ConfigParser(interpolation=None)
                parser.read(config_path, encoding='utf-8')
                if parser.has_section('Paths') and 'BackupRoot' in parser['Paths']:
                    backup_root = Path(os.path.expandvars(parser['Paths']['BackupRoot']))
        except:
            pass  # Use default if config reading fails
        
        # Determine backup folders to compare
        if args.latest:
            # Find the two most recent backups
            backup_folders = []
            if backup_root.exists():
                for item in sorted(backup_root.iterdir(), key=lambda x: x.name, reverse=True):
                    if item.is_dir() and not item.name.endswith('-Services-Backup'):
                        backup_folders.append(item)
                        if len(backup_folders) >= 2:
                            break
            
            if len(backup_folders) < 2:
                logger.error("Need at least 2 backups for comparison. Use --backup1 and --backup2 to specify manually.")
                return 1
            
            backup2_path = backup_folders[0]  # Latest
            backup1_path = backup_folders[1]  # Previous
            
            logger.info(f"Auto-selected backups:")
            logger.info(f"  Older:  {backup1_path.name}")
            logger.info(f"  Newer:  {backup2_path.name}")
        
        else:
            # Use specified backup folders
            if not args.backup1 or not args.backup2:
                logger.error("Must specify both --backup1 and --backup2, or use --latest")
                return 1
            
            backup1_path = Path(args.backup1)
            backup2_path = Path(args.backup2)
            
            if not backup1_path.exists():
                logger.error(f"Backup 1 not found: {backup1_path}")
                return 1
            
            if not backup2_path.exists():
                logger.error(f"Backup 2 not found: {backup2_path}")
                return 1
        
        # Perform comparison
        logger.info("Starting configuration comparison...")
        comparator = ConfigComparator(logger)
        comparison = comparator.compare_backups(backup1_path, backup2_path)
        
        # Generate performance impact report
        from report_generator import ReportGenerator, create_default_report_path
        generator = ReportGenerator()
        
        # Determine output path
        if args.output:
            output_path = args.output
        else:
            output_path = create_default_report_path(backup1_path.name, backup2_path.name)
        
        # Generate and save performance report
        logger.info("Generating performance impact analysis...")
        report_content = generator.generate_report(comparison, 'performance', output_path)
        
        # Print performance summary to console
        stats = comparison.summary_stats
        print("\n" + "="*50)
        print("PERFORMANCE IMPACT ANALYSIS COMPLETE")
        print("="*50)
        print(f"Files analyzed: {stats['total_files_compared']}")
        print(f"Files changed: {stats['files_changed']}")
        print(f"Configuration changes: {stats['settings_changed'] + stats['settings_added'] + stats['settings_removed']}")
        print(f"Performance critical changes: {stats['high_impact_changes']}")
        print(f"Services optimizations: {stats['services_changes']}")
        
        # Performance risk assessment
        if stats['high_impact_changes'] > 0:
            risk_level = "HIGH RISK ⚡"
        elif stats['medium_impact_changes'] > 0 or stats['services_changes'] > 0:
            risk_level = "MEDIUM RISK ⚠️"
        else:
            risk_level = "LOW RISK ✅"
        
        print(f"Gaming Performance Risk: {risk_level}")
        print(f"\nPerformance report saved to: {output_path}")
        print(f"Report size: {len(report_content):,} characters")
        
        # Show sample performance-critical changes
        if stats['high_impact_changes'] > 0:
            print(f"\nCritical performance changes detected:")
            change_count = 0
            for file_comp in comparison.file_comparisons:
                if file_comp.changes and change_count < 3:
                    high_impact_changes = [c for c in file_comp.changes if c.impact_level == 'HIGH']
                    if high_impact_changes:
                        file_name = Path(file_comp.file_path).name
                        print(f"  [{file_comp.category}] {file_name}:")
                        for change in high_impact_changes[:2]:  # First 2 critical changes per file
                            print(f"    ⚡ {change.setting_name}: {change.old_value} → {change.new_value}")
                        change_count += 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        return 1


def main():
    """Test the performance impact analysis system with actual backups"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze GameChanger backup performance impact')
    parser.add_argument('backup1', type=Path, help='First backup folder (baseline)')
    parser.add_argument('backup2', type=Path, help='Second backup folder (current)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output with detailed analysis')
    
    args = parser.parse_args()
    
    logger = setup_logging(logging.DEBUG if args.verbose else logging.INFO)
    comparator = ConfigComparator(logger)
    
    comparison = comparator.compare_backups(args.backup1, args.backup2)
    
    # Print performance-focused results
    print(f"Performance Impact Analysis: {comparison.backup1_timestamp} → {comparison.backup2_timestamp}")
    print(f"Files analyzed: {comparison.summary_stats['total_files_compared']}")
    print(f"Configuration changes: {comparison.summary_stats['files_changed']}")
    print(f"Performance critical changes: {comparison.summary_stats['high_impact_changes']}")
    print(f"Gaming relevant changes: {comparison.summary_stats['medium_impact_changes']}")
    print(f"Services optimizations: {comparison.summary_stats['services_changes']}")
    
    # Performance risk assessment
    stats = comparison.summary_stats
    if stats['high_impact_changes'] > 0:
        print("⚡ HIGH PERFORMANCE IMPACT DETECTED")
    elif stats['medium_impact_changes'] > 0 or stats['services_changes'] > 0:
        print("⚠️ MEDIUM PERFORMANCE IMPACT DETECTED")
    else:
        print("✅ LOW PERFORMANCE IMPACT")
    
    # Show critical performance changes
    print("\nCritical Performance Changes:")
    for file_comp in comparison.file_comparisons[:3]:  # First 3 files
        if file_comp.changes:
            high_impact = [c for c in file_comp.changes if c.impact_level == 'HIGH']
            if high_impact:
                print(f"[{file_comp.category}] {file_comp.file_path}:")
                for change in high_impact[:3]:  # First 3 critical changes
                    print(f"  ⚡ {change.setting_name}: {change.old_value} → {change.new_value}")


if __name__ == "__main__":
    main()