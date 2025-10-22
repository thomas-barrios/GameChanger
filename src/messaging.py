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
class SectionStats:
    """Statistics for a config section"""
    name: str
    base_path: str
    files_ok: int = 0
    files_error: int = 0
    operations: List[FileOperation] = field(default_factory=list)


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
    
    def format_log_output(self, logger: logging.Logger):
        """Generate detailed log output"""
        logger.info(f"=== {self.operation_type} STARTED ===")
        
        for section_name, stats in self.sections.items():
            if not stats.operations:
                continue
                
            logger.info(f"Processing section [{section_name}] - {len(stats.operations)} files")
            logger.info(f"Base path: {stats.base_path}")
            
            for op in stats.operations:
                if op.success:
                    logger.info(f"OK: {op.relative_path} -> {op.dest_path}")
                else:
                    error_detail = f" -> {op.error_message}" if op.error_message else ""
                    logger.error(f"ERROR: {op.relative_path} ({op.error_type}){error_detail}")
        
        # Log summary
        total_ok = sum(s.files_ok for s in self.sections.values())
        total_errors = sum(s.files_error for s in self.sections.values())
        logger.info(f"=== {self.operation_type} SUMMARY ===")
        logger.info(f"Files processed: {total_ok}/{total_ok + total_errors} successful ({total_errors} errors)")
    
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
        
        # Output to console
        console_output = self.formatter.format_console_output()
        print(console_output)
        
        # Add duration and log file info
        if duration > 0:
            print(f"Duration: {duration:.1f} seconds")
        if log_file_path:
            print(f"Log file: {log_file_path}")
        print("=" * 50)
        
        # Output to log file
        self.formatter.format_log_output(self.logger)
        
        if duration > 0:
            self.logger.info(f"Duration: {duration:.1f} seconds")