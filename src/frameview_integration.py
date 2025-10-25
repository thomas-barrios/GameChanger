"""
GameChanger FrameView Integration
Parses FrameView CSV data and correlates with configuration backups for performance analysis
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import logging


@dataclass
class FrameViewSession:
    """Represents a single FrameView DCS performance session"""
    timestamp: datetime
    application: str
    avg_fps: float
    one_percent_low: float
    min_fps: float
    max_fps: float
    session_duration_ms: float
    resolution: str
    gpu_util: float
    gpu_temp: float
    cpu_util: float
    cpu_temp: float
    
    @property
    def session_duration_minutes(self) -> float:
        """Session duration in minutes"""
        return self.session_duration_ms / 1000 / 60
    
    @property
    def performance_stability_ratio(self) -> float:
        """Ratio of 1% low to average FPS (higher = more stable)"""
        return self.one_percent_low / self.avg_fps if self.avg_fps > 0 else 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class FrameViewParser:
    """Parses FrameView CSV data and correlates with GameChanger backups"""
    
    def __init__(self, csv_path: Path, logger=None):
        self.csv_path = csv_path
        self.logger = logger or logging.getLogger('FrameViewParser')
        self._sessions_cache = None
        self._last_modified = None
    
    def is_available(self) -> bool:
        """Check if FrameView CSV is available for parsing"""
        return self.csv_path.exists() and self.csv_path.is_file()
    
    def load_sessions(self, force_reload: bool = False) -> List[FrameViewSession]:
        """Load and parse all DCS sessions from CSV"""
        if not self.is_available():
            self.logger.warning(f"FrameView CSV not found: {self.csv_path}")
            return []
        
        # Check if we need to reload based on file modification time
        current_modified = self.csv_path.stat().st_mtime
        if (self._sessions_cache is None or 
            force_reload or 
            self._last_modified != current_modified):
            
            self._sessions_cache = self._parse_csv()
            self._last_modified = current_modified
            
        return self._sessions_cache
    
    def _parse_csv(self) -> List[FrameViewSession]:
        """Parse FrameView CSV into session objects"""
        sessions = []
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, 2):  # Start at 2 for header
                    try:
                        # Filter for DCS sessions only
                        if row.get('Application', '').strip() != 'DCS.exe':
                            continue
                        
                        # Parse timestamp - FrameView format: 2025-10-24T132935
                        timestamp_str = row.get('TimeStamp', '').strip()
                        if not timestamp_str:
                            continue
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H%M%S')
                        
                        # Extract and validate numeric metrics
                        def safe_float(value, default=0.0):
                            try:
                                return float(value) if value and value.strip() else default
                            except (ValueError, AttributeError):
                                return default
                        
                        # Create session object
                        session = FrameViewSession(
                            timestamp=timestamp,
                            application=row.get('Application', ''),
                            avg_fps=safe_float(row.get('Avg FPS')),
                            one_percent_low=safe_float(row.get('1% Low')),
                            min_fps=safe_float(row.get('Min FPS')),
                            max_fps=safe_float(row.get('Max FPS')),
                            session_duration_ms=safe_float(row.get('Time (ms)')),
                            resolution=row.get('Resolution', ''),
                            gpu_util=safe_float(row.get('GPU0 Util%')),
                            gpu_temp=safe_float(row.get('GPU0 Temp (C)')),
                            cpu_util=safe_float(row.get('CPU Util %')),
                            cpu_temp=safe_float(row.get('CPU Temp (C)'))
                        )
                        
                        # Validate session has reasonable data
                        if (session.avg_fps > 0 and 
                            session.session_duration_ms > 0 and
                            session.one_percent_low > 0):
                            sessions.append(session)
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to parse CSV row {row_num}: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Failed to parse FrameView CSV {self.csv_path}: {e}")
            return []
        
        # Sort by timestamp for easier correlation
        sessions.sort(key=lambda s: s.timestamp)
        self.logger.info(f"Loaded {len(sessions)} DCS sessions from FrameView CSV")
        return sessions
    
    def find_sessions_near_backup(self, backup_timestamp: datetime, 
                                window_minutes: int = 15,
                                min_duration_seconds: int = 30) -> List[FrameViewSession]:
        """Find DCS sessions within time window of backup creation"""
        sessions = self.load_sessions()
        
        if not sessions:
            return []
        
        start_window = backup_timestamp - timedelta(minutes=window_minutes)
        end_window = backup_timestamp + timedelta(minutes=window_minutes)
        
        matching_sessions = []
        for session in sessions:
            if (start_window <= session.timestamp <= end_window and 
                session.session_duration_ms >= min_duration_seconds * 1000):
                matching_sessions.append(session)
        
        self.logger.debug(f"Found {len(matching_sessions)} sessions within {window_minutes}min of {backup_timestamp}")
        return matching_sessions
    
    def get_best_session_for_backup(self, backup_timestamp: datetime,
                                  window_minutes: int = 15,
                                  min_duration_seconds: int = 30) -> Optional[FrameViewSession]:
        """Get the most representative session for performance correlation"""
        sessions = self.find_sessions_near_backup(backup_timestamp, window_minutes, min_duration_seconds)
        
        if not sessions:
            return None
        
        # Scoring function: prefer longer sessions closer to backup time
        def session_score(session):
            time_diff_minutes = abs((session.timestamp - backup_timestamp).total_seconds()) / 60
            duration_score = min(session.session_duration_minutes, 10)  # Cap at 10 min max benefit
            time_score = max(0, 1 - (time_diff_minutes / window_minutes))  # Closer = higher score
            
            # Bonus for sessions with good stability (1% low close to average)
            stability_bonus = session.performance_stability_ratio * 0.1
            
            return (duration_score * 0.6) + (time_score * 0.3) + stability_bonus
        
        best_session = max(sessions, key=session_score)
        self.logger.info(f"Selected best session: {best_session.timestamp} "
                        f"({best_session.avg_fps:.1f} FPS, {best_session.session_duration_minutes:.1f}min)")
        return best_session


class PerformanceCorrelator:
    """Correlates FrameView performance data with GameChanger configuration backups"""
    
    def __init__(self, config: dict, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger('PerformanceCorrelator')
        self.frameview_parser = FrameViewParser(config['frameview_csv_path'], logger)
    
    def correlate_with_frameview(self, backup_folder: Path) -> Optional[dict]:
        """Correlate backup with FrameView performance data"""
        
        # Extract backup timestamp from folder name
        backup_timestamp = self._extract_backup_timestamp(backup_folder)
        if not backup_timestamp:
            self.logger.warning(f"Could not extract timestamp from backup folder: {backup_folder.name}")
            return None
        
        # Check if FrameView correlation is enabled and available
        if not self.config.get('enable_performance_correlation', True):
            self.logger.debug("Performance correlation disabled in config")
            return None
            
        if not self.frameview_parser.is_available():
            if self.config.get('require_frameview_data', False):
                self.logger.error("FrameView data required but not available")
                return None
            else:
                self.logger.info("FrameView data not available - graceful degradation")
                return None
        
        # Find best matching session
        best_session = self.frameview_parser.get_best_session_for_backup(
            backup_timestamp,
            self.config.get('performance_correlation_window', 15),
            self.config.get('min_session_duration', 30)
        )
        
        if not best_session:
            self.logger.info("No matching FrameView sessions found for backup correlation")
            return None
        
        # Calculate correlation confidence based on time proximity
        time_offset_minutes = (best_session.timestamp - backup_timestamp).total_seconds() / 60
        confidence = self._calculate_correlation_confidence(abs(time_offset_minutes))
        
        # Build performance correlation data
        correlation_data = {
            "backup_info": {
                "timestamp": backup_timestamp.isoformat(),
                "backup_path": str(backup_folder)
            },
            "frameview_correlation": {
                "csv_source": str(self.frameview_parser.csv_path),
                "correlation_success": True,
                "session_found": True,
                "session_data": {
                    "timestamp": best_session.timestamp.isoformat(),
                    "time_offset_minutes": round(time_offset_minutes, 2),
                    "avg_fps": best_session.avg_fps,
                    "one_percent_low": best_session.one_percent_low,
                    "min_fps": best_session.min_fps,
                    "max_fps": best_session.max_fps,
                    "session_duration_minutes": round(best_session.session_duration_minutes, 2),
                    "resolution": best_session.resolution,
                    "gpu_utilization": best_session.gpu_util,
                    "gpu_temperature": best_session.gpu_temp,
                    "cpu_utilization": best_session.cpu_util,
                    "cpu_temperature": best_session.cpu_temp,
                    "performance_stability_ratio": round(best_session.performance_stability_ratio, 3)
                },
                "correlation_confidence": confidence
            }
        }
        
        # Try to add performance comparison with previous backup
        self._add_performance_comparison(correlation_data, backup_folder)
        
        return correlation_data
    
    def _extract_backup_timestamp(self, backup_folder: Path) -> Optional[datetime]:
        """Extract timestamp from backup folder name"""
        try:
            # Expected format: 2025-10-24-19-16-30-Config-Backup
            folder_name = backup_folder.name
            if '-Config-Backup' in folder_name:
                timestamp_part = folder_name.replace('-Config-Backup', '')
            elif '-Services-Backup' in folder_name:
                timestamp_part = folder_name.replace('-Services-Backup', '')
            else:
                # Try to extract first part that looks like timestamp
                parts = folder_name.split('-')
                if len(parts) >= 6:
                    timestamp_part = '-'.join(parts[:6])
                else:
                    return None
            
            return datetime.strptime(timestamp_part, '%Y-%m-%d-%H-%M-%S')
        except Exception as e:
            self.logger.warning(f"Failed to parse backup timestamp from {backup_folder.name}: {e}")
            return None
    
    def _calculate_correlation_confidence(self, time_offset_minutes: float) -> str:
        """Calculate correlation confidence based on time proximity"""
        if time_offset_minutes <= 2:
            return "HIGH"
        elif time_offset_minutes <= 5:
            return "MEDIUM"
        elif time_offset_minutes <= 15:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _add_performance_comparison(self, correlation_data: dict, current_backup_folder: Path):
        """Add performance comparison with previous backup if available"""
        try:
            # Find previous backup with performance data
            backup_root = current_backup_folder.parent
            previous_backup = self._find_previous_backup_with_performance(backup_root, current_backup_folder)
            
            if previous_backup:
                previous_perf_file = previous_backup / "performance_data.json"
                if previous_perf_file.exists():
                    with open(previous_perf_file, 'r') as f:
                        previous_data = json.load(f)
                    
                    previous_session = previous_data.get('frameview_correlation', {}).get('session_data', {})
                    current_session = correlation_data['frameview_correlation']['session_data']
                    
                    if previous_session and current_session:
                        fps_delta = current_session['avg_fps'] - previous_session['avg_fps']
                        stability_delta = current_session['one_percent_low'] - previous_session['one_percent_low']
                        
                        correlation_data['performance_comparison'] = {
                            "baseline_backup": previous_backup.name,
                            "has_baseline": True,
                            "fps_delta": round(fps_delta, 2),
                            "stability_delta": round(stability_delta, 2),
                            "performance_change_percent": round((fps_delta / previous_session['avg_fps']) * 100, 1) if previous_session['avg_fps'] > 0 else 0
                        }
                        return
            
            # No previous backup found
            correlation_data['performance_comparison'] = {
                "baseline_backup": None,
                "has_baseline": False,
                "fps_delta": 0,
                "stability_delta": 0,
                "performance_change_percent": 0
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to add performance comparison: {e}")
            correlation_data['performance_comparison'] = {
                "baseline_backup": None,
                "has_baseline": False,
                "fps_delta": 0,
                "stability_delta": 0,
                "performance_change_percent": 0
            }
    
    def _find_previous_backup_with_performance(self, backup_root: Path, current_backup: Path) -> Optional[Path]:
        """Find the most recent previous backup that has performance data"""
        try:
            current_timestamp = self._extract_backup_timestamp(current_backup)
            if not current_timestamp:
                return None
            
            backup_folders = []
            for folder in backup_root.iterdir():
                if folder.is_dir() and folder != current_backup:
                    timestamp = self._extract_backup_timestamp(folder)
                    if timestamp and timestamp < current_timestamp:
                        # Check if this backup has performance data
                        perf_file = folder / "performance_data.json"
                        if perf_file.exists():
                            backup_folders.append((timestamp, folder))
            
            if backup_folders:
                # Return the most recent backup with performance data
                backup_folders.sort(key=lambda x: x[0], reverse=True)
                return backup_folders[0][1]
                
        except Exception as e:
            self.logger.warning(f"Error finding previous backup: {e}")
        
        return None


def load_performance_data(backup_folder: Path) -> Optional[dict]:
    """Load performance correlation data from backup folder"""
    perf_file = backup_folder / "performance_data.json"
    if not perf_file.exists():
        return None
    
    try:
        with open(perf_file, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def save_performance_data(backup_folder: Path, performance_data: dict) -> bool:
    """Save performance correlation data to backup folder"""
    try:
        perf_file = backup_folder / "performance_data.json"
        with open(perf_file, 'w') as f:
            json.dump(performance_data, f, indent=2)
        return True
    except Exception:
        return False