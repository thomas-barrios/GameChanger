"""
GameChanger Messaging System
Provides hierarchical, organized messaging for backup and restore operations
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class FileOperation:
    """Represents a single file operation (backup/restore)"""
    source_path: Path
    dest_path: Path
    relative_path: str
    section: str
    success: bool = False
    error_type: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ServiceOperation:
    """Represents a single service state change operation"""
    service_name: str
    display_name: str
    current_startup_type: str
    target_startup_type: str
    category: str  # SafeToDisable, OptionalToDisable, DoNotDisable
    gaming_rationale: str  # Why this matters for gaming performance
    success: bool = False
    error_type: Optional[str] = None
    error_message: Optional[str] = None


@dataclass 
class SectionStats:
    """Statistics for a config section"""
    name: str
    base_path: str
    files_ok: int = 0
    files_error: int = 0
    operations: List[FileOperation] = field(default_factory=list)


@dataclass 
class ServiceSectionStats:
    """Statistics for a service category section"""
    name: str
    category: str
    services_ok: int = 0
    services_error: int = 0
    operations: List[ServiceOperation] = field(default_factory=list)


class ErrorTracker:
    """Track and categorize errors by type"""
    
    def __init__(self):
        self.errors_by_type: Dict[str, List[str]] = defaultdict(list)
        self.total_errors = 0
    
    def add_error(self, error_type: str, file_path: str, section: str = ""):
        """Add an error with categorization"""
        # Normalize error types
        normalized_type = self._normalize_error_type(error_type)
        
        # Store with section context if provided
        display_path = f"{section}\\{file_path}" if section else file_path
        self.errors_by_type[normalized_type].append(display_path)
        self.total_errors += 1
    
    def _normalize_error_type(self, error_type: str) -> str:
        """Normalize error types to standard categories"""
        error_lower = error_type.lower()
        
        if "permission" in error_lower or "access" in error_lower:
            return "Permission denied"
        elif "not found" in error_lower or "no such file" in error_lower:
            return "File not found"
        elif "space" in error_lower:
            return "Disk space"
        elif "exists" in error_lower:
            return "File exists"
        else:
            return "Other errors"
    
    def get_error_summary(self) -> Dict[str, List[str]]:
        """Get categorized error summary"""
        return dict(self.errors_by_type)


class PathHelper:
    """Handle path manipulation and base path detection"""
    
    @staticmethod
    def get_section_base_path(section: str, file_paths: List[str]) -> str:
        """Determine base path for a config section"""
        if not file_paths:
            return ""
        
        # Convert to Path objects for easier manipulation
        paths = [Path(p) for p in file_paths]
        
        # Find common parent directory
        try:
            common_parent = Path(os.path.commonpath([str(p.parent) for p in paths]))
            return str(common_parent)
        except ValueError:
            # No common path, use first file's parent
            return str(paths[0].parent)
    
    @staticmethod
    def get_relative_path(file_path: str, base_path: str) -> str:
        """Get relative path from base path"""
        try:
            file_p = Path(file_path)
            base_p = Path(base_path)
            
            # Try to get relative path
            if file_p.is_relative_to(base_p):
                return str(file_p.relative_to(base_p))
            else:
                # Fall back to just filename if not under base
                return file_p.name
        except (ValueError, AttributeError):
            # Fallback to filename
            return Path(file_path).name
    
    @staticmethod
    def group_files_by_section(files_with_sections: List[Tuple[str, str]]) -> Dict[str, List[str]]:
        """Group file paths by config section"""
        sections = defaultdict(list)
        for file_path, section in files_with_sections:
            sections[section].append(file_path)
        return dict(sections)


class MessageFormatter:
    """Core formatting logic for hierarchical messages"""
    
    def __init__(self, operation_type: str = "BACKUP"):
        self.operation_type = operation_type.upper()
        self.sections: Dict[str, SectionStats] = {}
        self.error_tracker = ErrorTracker()
        
    def add_section(self, section_name: str, base_path: str):
        """Add a new section for grouping"""
        self.sections[section_name] = SectionStats(
            name=section_name,
            base_path=base_path
        )
    
    def add_operation(self, operation: FileOperation):
        """Add a file operation to the appropriate section"""
        if operation.section not in self.sections:
            # Auto-create section if not exists
            self.add_section(operation.section, str(operation.source_path.parent))
        
        section_stats = self.sections[operation.section]
        section_stats.operations.append(operation)
        
        if operation.success:
            section_stats.files_ok += 1
        else:
            section_stats.files_error += 1
            if operation.error_type and operation.relative_path:
                self.error_tracker.add_error(
                    operation.error_type, 
                    operation.relative_path,
                    operation.section
                )
    
    def format_console_output(self) -> str:
        """Generate formatted console output"""
        lines = []
        lines.append(f"=== {self.operation_type} STARTED ===")
        
        # Process each section
        for section_name, stats in self.sections.items():
            if not stats.operations:
                continue
                
            lines.append(f"Base: {stats.base_path}")
            
            # Add tree structure for files
            for i, op in enumerate(stats.operations):
                is_last = (i == len(stats.operations) - 1)
                prefix = "└─" if is_last else "├─"
                
                if op.success:
                    lines.append(f"{prefix} OK: {op.relative_path}")
                else:
                    error_msg = f" ({op.error_message})" if op.error_message else ""
                    lines.append(f"{prefix} ERROR: {op.relative_path}{error_msg}")
            
            lines.append("")  # Empty line between sections
        
        # Add summary
        lines.extend(self._format_summary())
        
        return "\n".join(lines)
    
    def _format_summary(self) -> List[str]:
        """Generate summary section"""
        lines = []
        
        total_ok = sum(s.files_ok for s in self.sections.values())
        total_errors = sum(s.files_error for s in self.sections.values())
        total_files = total_ok + total_errors
        
        lines.append(f"=== {self.operation_type} SUMMARY ===")
        lines.append(f"Files processed: {total_ok}/{total_files} successful ({total_errors} errors)")
        
        # Add error breakdown if there are errors
        if total_errors > 0:
            lines.append("")
            lines.append("ERROR BREAKDOWN:")
            
            error_summary = self.error_tracker.get_error_summary()
            for error_type, file_list in error_summary.items():
                count = len(file_list)
                lines.append(f"{error_type}: {count} file{'s' if count != 1 else ''}")
                
                # Show file list with proper indentation
                for file_path in file_list:
                    lines.append(f"  - {file_path}")
        
        return lines


class ServiceMessageFormatter:
    """Specialized formatting for Windows services operations"""
    
    def __init__(self, operation_type: str = "SERVICES_SCAN"):
        self.operation_type = operation_type.upper()
        self.service_sections: Dict[str, ServiceSectionStats] = {}
        self.error_tracker = ErrorTracker()
        
    def add_service_section(self, section_name: str, category: str):
        """Add a new service category section"""
        self.service_sections[section_name] = ServiceSectionStats(
            name=section_name,
            category=category
        )
    
    def add_service_operation(self, operation: ServiceOperation):
        """Add a service operation to the appropriate category section"""
        section_name = operation.category
        if section_name not in self.service_sections:
            self.add_service_section(section_name, operation.category)
        
        section_stats = self.service_sections[section_name]
        section_stats.operations.append(operation)
        
        if operation.success:
            section_stats.services_ok += 1
        else:
            section_stats.services_error += 1
            if operation.error_type:
                self.error_tracker.add_error(
                    operation.error_type, 
                    operation.service_name,
                    operation.category
                )
    
    def format_service_scan_output(self) -> str:
        """Generate formatted output for service scan results"""
        lines = []
        lines.append(f"=== WINDOWS SERVICES SCAN ===")
        lines.append("")
        
        # Process each category in specific order
        category_order = ["DoNotDisable", "SafeToDisable", "OptionalToDisable"]
        
        for category in category_order:
            if category not in self.service_sections:
                continue
                
            stats = self.service_sections[category]
            if not stats.operations:
                continue
            
            # Category header with description
            category_descriptions = {
                "DoNotDisable": "Essential services - NEVER modify these",
                "SafeToDisable": "Safe to disable - No impact on gaming",
                "OptionalToDisable": "Optional - May improve performance (user choice)"
            }
            
            lines.append(f"[{category}] - {category_descriptions.get(category, '')}")
            lines.append("─" * 60)
            
            for i, op in enumerate(stats.operations):
                is_last = (i == len(stats.operations) - 1)
                prefix = "└─" if is_last else "├─"
                
                # Format: Service Name (Current: Status) - Gaming Impact
                status_info = f"Current: {op.current_startup_type}"
                lines.append(f"{prefix} {op.display_name} ({status_info})")
                lines.append(f"   └─ Impact: {op.gaming_rationale}")
            
            lines.append("")  # Empty line between categories
        
        return "\n".join(lines)
    
    def format_service_optimization_output(self) -> str:
        """Generate formatted output for service optimization results"""
        lines = []
        lines.append(f"=== SERVICES OPTIMIZATION RESULTS ===")
        
        # Process each category
        for category_name, stats in self.service_sections.items():
            if not stats.operations or category_name == "DoNotDisable":
                continue
                
            lines.append(f"[{category_name}]")
            
            for i, op in enumerate(stats.operations):
                is_last = (i == len(stats.operations) - 1)
                prefix = "└─" if is_last else "├─"
                
                if op.success:
                    lines.append(f"{prefix} OK: {op.display_name} ({op.current_startup_type} → {op.target_startup_type})")
                else:
                    error_msg = f" ({op.error_message})" if op.error_message else ""
                    lines.append(f"{prefix} ERROR: {op.display_name}{error_msg}")
            
            lines.append("")
        
        # Add summary
        lines.extend(self._format_service_summary())
        
        return "\n".join(lines)
    
    def _format_service_summary(self) -> List[str]:
        """Generate service operation summary"""
        lines = []
        
        total_ok = sum(s.services_ok for s in self.service_sections.values())
        total_errors = sum(s.services_error for s in self.service_sections.values())
        total_services = total_ok + total_errors
        
        lines.append(f"=== SERVICES SUMMARY ===")
        lines.append(f"Services processed: {total_ok}/{total_services} successful ({total_errors} errors)")
        
        # Add error breakdown if there are errors
        if total_errors > 0:
            lines.append("")
            lines.append("ERROR BREAKDOWN:")
            
            error_summary = self.error_tracker.get_error_summary()
            for error_type, service_list in error_summary.items():
                count = len(service_list)
                lines.append(f"{error_type}: {count} service{'s' if count != 1 else ''}")
                
                for service_name in service_list:
                    lines.append(f"  - {service_name}")
        
        return lines


class OutputManager:
    """Manage dual output formatting - console vs log"""
    
    def __init__(self, logger: logging.Logger, operation_type: str = "BACKUP"):
        self.logger = logger
        self.formatter = MessageFormatter(operation_type)
        self.start_time = None
        
    def start_operation(self):
        """Mark operation start"""
        import time
        self.start_time = time.time()
        
    def add_section(self, section_name: str, base_path: str):
        """Add a section for grouping"""
        self.formatter.add_section(section_name, base_path)
        
    def add_operation(self, source_path: Path, dest_path: Path, section: str, 
                     success: bool, error_type: str = None, error_message: str = None):
        """Add a file operation"""
        # Calculate relative path from section base
        section_stats = self.formatter.sections.get(section)
        if section_stats:
            relative_path = PathHelper.get_relative_path(str(source_path), section_stats.base_path)
        else:
            relative_path = source_path.name
            
        operation = FileOperation(
            source_path=source_path,
            dest_path=dest_path,
            relative_path=relative_path,
            section=section,
            success=success,
            error_type=error_type,
            error_message=error_message
        )
        
        self.formatter.add_operation(operation)
        
    def finalize_operation(self, log_file_path: Path = None):
        """Complete operation and output final messages"""
        import time
        
        # Calculate duration
        duration = time.time() - self.start_time if self.start_time else 0
        
        # CONSOLE OUTPUT: Clean tree view for user
        console_output = self.formatter.format_console_output()
        print(console_output)
        
        # Add duration and log file info to console
        if duration > 0:
            print(f"Duration: {duration:.1f} seconds")
        if log_file_path:
            print(f"Log file: {log_file_path}")
        print("=" * 50)
        
        # LOG FILE OUTPUT: Detailed technical logging (different from console)
        self._log_technical_details()
        
        # Log duration to file
        if duration > 0:
            self.logger.info(f"Operation completed in {duration:.2f} seconds")
    
    def _log_technical_details(self):
        """Log detailed technical information to file (different from console)"""
        import time
        
        # Log detailed operation start with full context
        self.logger.info(f"=== {self.formatter.operation_type} TECHNICAL LOG ===")
        self.logger.info(f"Operation timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        total_sections = len(self.formatter.sections)
        total_operations = sum(len(stats.operations) for stats in self.formatter.sections.values())
        self.logger.info(f"Processing {total_operations} file operations across {total_sections} sections")
        
        # Log each file operation with full paths and technical details
        for section_name, stats in self.formatter.sections.items():
            if not stats.operations:
                continue
                
            self.logger.info(f"--- Section: {section_name} ---")
            self.logger.info(f"Base directory: {stats.base_path}")
            self.logger.info(f"Files in section: {len(stats.operations)} (Success: {stats.files_ok}, Errors: {stats.files_error})")
            
            for op in stats.operations:
                if op.success:
                    # Log successful operations with full source and destination paths
                    self.logger.info(f"SUCCESS: '{op.source_path}' -> '{op.dest_path}'")
                else:
                    # Log failed operations with full error context
                    self.logger.error(f"FAILED: '{op.source_path}' | Error: {op.error_type} | Details: {op.error_message or 'No additional details'}")
        
        # Log final statistics
        total_ok = sum(s.files_ok for s in self.formatter.sections.values())
        total_errors = sum(s.files_error for s in self.formatter.sections.values())
        success_rate = (total_ok / (total_ok + total_errors) * 100) if (total_ok + total_errors) > 0 else 0
        
        self.logger.info(f"=== OPERATION STATISTICS ===")
        self.logger.info(f"Total files processed: {total_ok + total_errors}")
        self.logger.info(f"Successful operations: {total_ok}")
        self.logger.info(f"Failed operations: {total_errors}")
        self.logger.info(f"Success rate: {success_rate:.1f}%")
        
        # Log detailed error analysis if there are errors
        if total_errors > 0:
            self.logger.info("=== ERROR ANALYSIS ===")
            error_summary = self.formatter.error_tracker.get_error_summary()
            for error_type, file_list in error_summary.items():
                self.logger.warning(f"{error_type}: {len(file_list)} occurrences")
                for file_path in file_list:
                    self.logger.warning(f"  -> {file_path}")
        
        self.logger.info(f"=== END {self.formatter.operation_type} TECHNICAL LOG ===")


class ServiceOutputManager:
    """Specialized output manager for Windows services operations"""
    
    def __init__(self, logger: logging.Logger, operation_type: str = "SERVICES_SCAN"):
        self.logger = logger
        self.formatter = ServiceMessageFormatter(operation_type)
        self.start_time = None
        
    def start_operation(self):
        """Mark operation start"""
        import time
        self.start_time = time.time()
        
    def add_service_section(self, section_name: str, category: str):
        """Add a service category section"""
        self.formatter.add_service_section(section_name, category)
        
    def add_service_operation(self, service_name: str, display_name: str, current_startup: str,
                             target_startup: str, category: str, gaming_rationale: str,
                             success: bool, error_type: str = None, error_message: str = None):
        """Add a service operation"""
        operation = ServiceOperation(
            service_name=service_name,
            display_name=display_name,
            current_startup_type=current_startup,
            target_startup_type=target_startup,
            category=category,
            gaming_rationale=gaming_rationale,
            success=success,
            error_type=error_type,
            error_message=error_message
        )
        
        self.formatter.add_service_operation(operation)
        
    def finalize_scan_operation(self, log_file_path: Path = None):
        """Complete service scan and output results"""
        import time
        
        # Calculate duration
        duration = time.time() - self.start_time if self.start_time else 0
        
        # CONSOLE OUTPUT: Service scan results
        console_output = self.formatter.format_service_scan_output()
        print(console_output)
        
        # Add duration and log info
        if duration > 0:
            print(f"Scan duration: {duration:.1f} seconds")
        if log_file_path:
            print(f"Log file: {log_file_path}")
        print("=" * 60)
        
        # LOG FILE OUTPUT: Technical details
        self._log_service_technical_details()
        
        if duration > 0:
            self.logger.info(f"Service scan completed in {duration:.2f} seconds")
    
    def finalize_optimization_operation(self, log_file_path: Path = None):
        """Complete service optimization and output results"""
        import time
        
        # Calculate duration
        duration = time.time() - self.start_time if self.start_time else 0
        
        # CONSOLE OUTPUT: Optimization results
        console_output = self.formatter.format_service_optimization_output()
        print(console_output)
        
        # Add important notices
        print("\n" + "=" * 60)
        print("IMPORTANT NOTICES:")
        print("• A system restart is recommended for all changes to take effect")
        print("• Service states have been backed up to the backup folder")
        print("• Use 'services restore' command to revert changes if needed")
        print("=" * 60)
        
        # Add duration and log info
        if duration > 0:
            print(f"Optimization duration: {duration:.1f} seconds")
        if log_file_path:
            print(f"Log file: {log_file_path}")
        print("=" * 60)
        
        # LOG FILE OUTPUT: Technical details
        self._log_service_technical_details()
        
        if duration > 0:
            self.logger.info(f"Service optimization completed in {duration:.2f} seconds")
    
    def _log_service_technical_details(self):
        """Log detailed service operation information"""
        import time
        
        self.logger.info(f"=== {self.formatter.operation_type} TECHNICAL LOG ===")
        self.logger.info(f"Operation timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        total_sections = len(self.formatter.service_sections)
        total_operations = sum(len(stats.operations) for stats in self.formatter.service_sections.values())
        self.logger.info(f"Processing {total_operations} service operations across {total_sections} categories")
        
        # Log each service operation with full details
        for category_name, stats in self.formatter.service_sections.items():
            if not stats.operations:
                continue
                
            self.logger.info(f"--- Category: {category_name} ---")
            self.logger.info(f"Services in category: {len(stats.operations)} (Success: {stats.services_ok}, Errors: {stats.services_error})")
            
            for op in stats.operations:
                if op.success:
                    self.logger.info(f"SUCCESS: '{op.service_name}' ({op.display_name}) | {op.current_startup_type} -> {op.target_startup_type} | Rationale: {op.gaming_rationale}")
                else:
                    self.logger.error(f"FAILED: '{op.service_name}' ({op.display_name}) | Error: {op.error_type} | Details: {op.error_message or 'No additional details'}")
        
        # Log final statistics
        total_ok = sum(s.services_ok for s in self.formatter.service_sections.values())
        total_errors = sum(s.services_error for s in self.formatter.service_sections.values())
        success_rate = (total_ok / (total_ok + total_errors) * 100) if (total_ok + total_errors) > 0 else 0
        
        self.logger.info(f"=== SERVICE OPERATION STATISTICS ===")
        self.logger.info(f"Total services processed: {total_ok + total_errors}")
        self.logger.info(f"Successful operations: {total_ok}")
        self.logger.info(f"Failed operations: {total_errors}")
        self.logger.info(f"Success rate: {success_rate:.1f}%")
        
        # Log detailed error analysis
        if total_errors > 0:
            self.logger.info("=== SERVICE ERROR ANALYSIS ===")
            error_summary = self.formatter.error_tracker.get_error_summary()
            for error_type, service_list in error_summary.items():
                self.logger.warning(f"{error_type}: {len(service_list)} occurrences")
                for service_name in service_list:
                    self.logger.warning(f"  -> {service_name}")
        
        self.logger.info(f"=== END {self.formatter.operation_type} TECHNICAL LOG ===")