"""
GameChanger Configuration Report Generator
Creates detailed reports of configuration changes between backups
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from comparison import BackupComparison, FileComparison, ConfigChange


class ReportGenerator:
    """Generate performance-focused comparison reports"""
    
    def __init__(self):
        # Simplified to single performance-focused report
        pass
    
    def generate_report(self, comparison: BackupComparison, 
                       report_type: str = 'performance',
                       output_path: Optional[Path] = None) -> str:
        """Generate a performance-focused comparison report"""
        
        # Always generate performance report (report_type kept for compatibility)
        report_content = self._generate_performance_report(comparison)
        
        # Save to file if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        return report_content
    
    def _generate_performance_report(self, comparison: BackupComparison) -> str:
        """Generate unified performance-focused report with comprehensive analysis"""
        lines = []
        
        # Load performance data from both backups
        baseline_perf = self._load_performance_data(comparison.backup1_path)
        current_perf = self._load_performance_data(comparison.backup2_path)
        
        # Header (Enhanced from detailed report)
        lines.extend([
            "GameChanger Performance Impact Analysis",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Comparison: {comparison.backup1_timestamp} → {comparison.backup2_timestamp}",
            f"Baseline: {comparison.backup1_path.name}",
            f"Current: {comparison.backup2_path.name}",
            ""
        ])
        
        # Executive Performance Summary with actual FrameView data integration
        stats = comparison.summary_stats
        total_changes = stats['settings_changed'] + stats['settings_added'] + stats['settings_removed']
        
        # Determine overall performance risk level - enhanced with actual performance data
        risk_level = "LOW RISK"
        risk_icon = "✅"
        performance_status = ""
        
        if baseline_perf and current_perf:
            # We have actual performance data - use it for risk assessment
            baseline_fps = baseline_perf.get('frameview_correlation', {}).get('session_data', {}).get('avg_fps', 0)
            current_fps = current_perf.get('frameview_correlation', {}).get('session_data', {}).get('avg_fps', 0)
            
            if baseline_fps > 0 and current_fps > 0:
                fps_change_percent = ((current_fps - baseline_fps) / baseline_fps) * 100
                baseline_stability = baseline_perf.get('frameview_correlation', {}).get('session_data', {}).get('one_percent_low', 0)
                current_stability = current_perf.get('frameview_correlation', {}).get('session_data', {}).get('one_percent_low', 0)
                stability_change_percent = ((current_stability - baseline_stability) / baseline_stability) * 100 if baseline_stability > 0 else 0
                
                if fps_change_percent >= 5 or stability_change_percent >= 5:
                    risk_icon = "⚡"
                    performance_status = f"PERFORMANCE IMPROVED (+{fps_change_percent:.1f}%)"
                elif fps_change_percent <= -5 or stability_change_percent <= -5:
                    risk_icon = "⚠️"
                    performance_status = f"PERFORMANCE DECREASED ({fps_change_percent:.1f}%)"
                else:
                    risk_icon = "✅"
                    performance_status = f"PERFORMANCE STABLE ({fps_change_percent:+.1f}%)"
        else:
            # Fall back to configuration-based risk assessment
            if stats['high_impact_changes'] > 0:
                risk_level = "HIGH RISK"
                risk_icon = "⚡"
            elif stats['medium_impact_changes'] > 0 or stats['services_changes'] > 0:
                risk_level = "MEDIUM RISK" 
                risk_icon = "⚠️"
        
        lines.extend([
            "PERFORMANCE IMPACT SUMMARY",
            "=" * 30,
        ])
        
        # Add performance correlation data if available
        if baseline_perf and current_perf:
            baseline_session = baseline_perf.get('frameview_correlation', {}).get('session_data', {})
            current_session = current_perf.get('frameview_correlation', {}).get('session_data', {})
            
            if baseline_session and current_session:
                lines.extend([
                    f"Gaming Performance Status: {risk_icon} {performance_status}",
                    f"Baseline Performance: {baseline_session['avg_fps']:.1f} FPS avg, {baseline_session['one_percent_low']:.1f} FPS 1% low",
                    f"Current Performance:  {current_session['avg_fps']:.1f} FPS avg, {current_session['one_percent_low']:.1f} FPS 1% low",
                    f"Performance Change: {current_session['avg_fps'] - baseline_session['avg_fps']:+.1f} FPS avg ({((current_session['avg_fps'] - baseline_session['avg_fps']) / baseline_session['avg_fps']) * 100:+.1f}%)",
                    f"Stability Change: {current_session['one_percent_low'] - baseline_session['one_percent_low']:+.1f} FPS 1% low ({((current_session['one_percent_low'] - baseline_session['one_percent_low']) / baseline_session['one_percent_low']) * 100:+.1f}%)",
                    ""
                ])
            else:
                lines.append(f"Gaming Performance Risk: {risk_icon} {risk_level}")
        else:
            lines.append(f"Gaming Performance Risk: {risk_icon} {risk_level}")
            if not current_perf:
                lines.append("FrameView Performance Data: Not available for current backup")
            if not baseline_perf:
                lines.append("FrameView Performance Data: Not available for baseline backup")
            lines.append("")
        
        lines.extend([
            f"Configuration Files: {stats['files_changed']} modified, {stats['files_unchanged']} unchanged",
            f"Total Setting Changes: {total_changes}",
            f"  ├─ High Impact (Performance Critical): {stats['high_impact_changes']}",
            f"  ├─ Medium Impact (Performance Relevant): {stats['medium_impact_changes']}",
            f"  └─ Low Impact (Minor Changes): {stats['low_impact_changes']}",
            f"Windows Services: {stats['services_changes']} optimizations applied",
            ""
        ])
        
        # Categorize changes by impact for detailed analysis
        high_impact_changes = []
        medium_impact_changes = []
        low_impact_changes = []
        
        for file_comp in comparison.file_comparisons:
            for change in file_comp.changes:
                # Skip ignored changes (joystick/input device changes)
                if change.impact_level == 'IGNORED':
                    continue
                elif change.impact_level == 'HIGH':
                    high_impact_changes.append((file_comp, change))
                elif change.impact_level == 'MEDIUM':
                    medium_impact_changes.append((file_comp, change))
                elif change.impact_level == 'LOW':
                    low_impact_changes.append((file_comp, change))
        
        # High Impact Changes (Critical Performance Analysis)
        if high_impact_changes:
            lines.extend([
                "CRITICAL PERFORMANCE CHANGES",
                "=" * 35,
            ])
            
            # Add measured vs predicted analysis if performance data available
            if baseline_perf and current_perf:
                baseline_session = baseline_perf.get('frameview_correlation', {}).get('session_data', {})
                current_session = current_perf.get('frameview_correlation', {}).get('session_data', {})
                
                if baseline_session and current_session:
                    measured_fps_change = current_session['avg_fps'] - baseline_session['avg_fps']
                    lines.extend([
                        f"⚡ PERFORMANCE MEASUREMENT: {measured_fps_change:+.1f} FPS change measured vs. configuration predictions",
                        "These changes are expected to significantly impact gaming performance:",
                        ""
                    ])
                else:
                    lines.extend([
                        "These changes are expected to significantly impact gaming performance:",
                        ""
                    ])
            else:
                lines.extend([
                    "These changes are expected to significantly impact gaming performance:",
                    ""
                ])
            
            # Group by category for better organization
            changes_by_category = {}
            for file_comp, change in high_impact_changes:
                category = file_comp.category
                if category not in changes_by_category:
                    changes_by_category[category] = []
                changes_by_category[category].append((file_comp, change))
            
            for category, category_changes in changes_by_category.items():
                lines.append(f"[{category} Configuration]")
                for file_comp, change in category_changes:
                    file_name = Path(file_comp.file_path).name
                    lines.append(f"├─ {file_name}")
                    lines.append(f"│  • {change.setting_name}: {change.old_value} → {change.new_value}")
                    
                    # Enhanced impact analysis with performance data correlation
                    impact_text = "⚡ PERFORMANCE IMPACT EXPECTED"
                    if baseline_perf and current_perf:
                        baseline_session = baseline_perf.get('frameview_correlation', {}).get('session_data', {})
                        current_session = current_perf.get('frameview_correlation', {}).get('session_data', {})
                        
                        if baseline_session and current_session:
                            measured_fps_change = current_session['avg_fps'] - baseline_session['avg_fps']
                            predicted_impact = self._predict_setting_impact(change.setting_name, change.old_value, change.new_value)
                            
                            if abs(measured_fps_change - predicted_impact) > 2.0:  # Significant difference
                                if measured_fps_change > predicted_impact:
                                    impact_text = f"⚡ UNEXPECTED PERFORMANCE GAIN (Predicted: {predicted_impact:+.1f} FPS, Measured: {measured_fps_change:+.1f} FPS)"
                                else:
                                    impact_text = f"⚠️ HIGHER IMPACT THAN EXPECTED (Predicted: {predicted_impact:+.1f} FPS, Measured: {measured_fps_change:+.1f} FPS)"
                            else:
                                impact_text = f"⚡ IMPACT AS EXPECTED (Predicted: {predicted_impact:+.1f} FPS, Measured: {measured_fps_change:+.1f} FPS)"
                    
                    lines.append(f"│  • Impact: {impact_text}")
                    
                    # Add performance rationale
                    rationale = self._get_performance_rationale(change.setting_name, change.old_value, change.new_value)
                    lines.append(f"│  └─ Analysis: {rationale}")
                    
                    # Add file size change if significant
                    if abs(file_comp.size_change) > 100:
                        lines.append(f"│     File size: {file_comp.size_change:+d} bytes")
                lines.append("")
        
        # Medium Impact Changes (Performance Relevant)
        if medium_impact_changes:
            lines.extend([
                "PERFORMANCE RELEVANT CHANGES", 
                "=" * 35,
                "These changes may affect gaming performance and should be monitored:",
                ""
            ])
            
            # Show top 10 medium impact changes to avoid overwhelming output
            for file_comp, change in medium_impact_changes[:10]:
                file_name = Path(file_comp.file_path).name
                lines.append(f"[{file_comp.category}] {file_name}")
                lines.append(f"• {change.setting_name}: {change.old_value} → {change.new_value} ⚠️")
                
                rationale = self._get_performance_rationale(change.setting_name, change.old_value, change.new_value)
                lines.append(f"  └─ {rationale}")
                lines.append("")
            
            if len(medium_impact_changes) > 10:
                lines.append(f"... and {len(medium_impact_changes) - 10} more medium impact changes")
                lines.append("")
        
        # Windows Services Performance Impact
        if comparison.services_changes:
            lines.extend([
                "WINDOWS SERVICES PERFORMANCE IMPACT",
                "=" * 40,
                "Service optimizations affecting system performance during gaming:",
                ""
            ])
            
            for service_change in comparison.services_changes:
                if service_change.get('type') == 'startup_type_changed':
                    old_type = service_change['old_startup_type']
                    new_type = service_change['new_startup_type']
                    service_name = service_change['service_name']
                    
                    if old_type in ['Automatic'] and new_type in ['Disabled', 'Manual']:
                        impact_icon = "⚡ PERFORMANCE GAIN EXPECTED"
                        rationale = "Reduces background service overhead during gaming"
                    elif old_type in ['Disabled', 'Manual'] and new_type in ['Automatic']:
                        impact_icon = "⚠️ MINOR PERFORMANCE COST"
                        rationale = "Additional background service may impact performance"
                    else:
                        impact_icon = "❓ PERFORMANCE IMPACT UNKNOWN"
                        rationale = "Service configuration change detected"
                    
                    lines.append(f"• {service_name}")
                    lines.append(f"  ├─ Change: {old_type} → {new_type}")
                    lines.append(f"  ├─ Impact: {impact_icon}")
                    lines.append(f"  └─ Analysis: {rationale}")
                    lines.append("")
        
        # Configuration Files Overview (From detailed report)
        if stats['files_changed'] > 0:
            lines.extend([
                "CONFIGURATION FILES OVERVIEW",
                "=" * 35,
                ""
            ])
            
            # Group files by category
            files_by_category = {}
            for file_comp in comparison.file_comparisons:
                if file_comp.changes:  # Only show files with changes
                    category = file_comp.category
                    if category not in files_by_category:
                        files_by_category[category] = []
                    files_by_category[category].append(file_comp)
            
            for category, files in files_by_category.items():
                lines.append(f"{category} Files Modified:")
                for file_comp in files[:5]:  # Top 5 files per category
                    file_name = Path(file_comp.file_path).name
                    change_count = len(file_comp.changes)
                    high_changes = len([c for c in file_comp.changes if c.impact_level == 'HIGH'])
                    
                    impact_summary = ""
                    if high_changes > 0:
                        impact_summary = f" ({high_changes} critical)"
                    
                    size_info = ""
                    if file_comp.size_change != 0:
                        size_info = f" [{file_comp.size_change:+d} bytes]"
                    
                    lines.append(f"• {file_name}: {change_count} changes{impact_summary}{size_info}")
                
                if len(files) > 5:
                    lines.append(f"• ... and {len(files) - 5} more {category} files")
                lines.append("")
        
        # Low Impact Changes Summary
        if low_impact_changes:
            lines.extend([
                "MINOR CONFIGURATION CHANGES",
                "=" * 35,
                f"• {len(low_impact_changes)} low-impact settings modified",
                "• Minimal performance impact expected",
                "• Monitor for any unexpected input/audio behavior changes",
                ""
            ])
        
        # Performance Testing Recommendations (Enhanced)
        lines.extend([
            "PERFORMANCE TESTING RECOMMENDATIONS",
            "=" * 40,
            "Recommended testing approach based on detected changes:",
            ""
        ])
        
        # Tailor recommendations based on changes detected
        if stats['high_impact_changes'] > 0:
            lines.extend([
                "PRIORITY TESTING (High Impact Changes Detected):",
                "1. 🎯 Capture baseline performance with NVIDIA FrameView or CapFrameX",
                "2. 🎯 Test graphics-intensive scenarios (DCS multiplayer, dense terrain)",
                "3. 🎯 Monitor GPU/CPU utilization and frame times closely",
                "4. 🎯 Document any stuttering, frame drops, or visual artifacts",
                ""
            ])
        
        if any('VR' in str(fc.category) for fc in comparison.file_comparisons if fc.changes):
            lines.extend([
                "VR SPECIFIC TESTING:",
                "• Test VR headset performance and comfort settings",
                "• Check for motion sickness or visual strain changes", 
                "• Verify head tracking smoothness and responsiveness",
                ""
            ])
        
        lines.extend([
            "STANDARD TESTING PROTOCOL:",
            "1. Run representative gaming sessions (30+ minutes)",
            "2. Test both VR and flat screen modes if applicable",
            "3. Compare results with previous performance baselines",
            "4. Log any performance anomalies with timestamps",
            "5. Correlate any issues with specific setting changes above",
            ""
        ])
        
        # Correlation Framework Status
        lines.extend([
            "PERFORMANCE CORRELATION FRAMEWORK",
            "=" * 40,
            "Current system capabilities for performance analysis:",
            "",
            "✅ Configuration change detection: ACTIVE",
            "✅ Service optimization tracking: ACTIVE", 
            "✅ Impact assessment system: ACTIVE",
            "✅ Performance rationale database: ACTIVE",
            "⏳ Performance metrics integration: READY FOR IMPLEMENTATION",
            "⏳ Automated correlation analysis: PLANNED",
            "⏳ Performance regression alerts: PLANNED",
            "⏳ Machine learning impact prediction: FUTURE DEVELOPMENT",
            ""
        ])
        
        # Footer with next steps
        lines.extend([
            "NEXT STEPS",
            "=" * 15,
            "1. Review critical performance changes above",
            "2. Run performance testing with recommended tools",
            "3. Document any performance differences observed", 
            "4. Correlate results with this analysis for future improvements",
            f"5. Keep this report for comparison with future changes",
            ""
        ])
        
        return "\n".join(lines)
    
    def _add_file_details(self, lines: List[str], file_comp: FileComparison):
        """Add detailed file comparison information to report"""
        file_name = Path(file_comp.file_path).name
        
        # File header
        lines.append(f"├─ {file_name}")
        
        # File metadata
        if file_comp.size_change != 0:
            size_info = f"({file_comp.size_change:+d} bytes)"
            lines.append(f"│  ├─ File Size: {size_info}")
        
        if file_comp.parse_error:
            lines.append(f"│  ├─ Parse Error: {file_comp.parse_error}")
            lines.append(f"│  └─ Binary comparison: {'IDENTICAL' if file_comp.binary_identical else 'DIFFERENT'}")
        else:
            # Settings changes
            if file_comp.changes:
                lines.append(f"│  └─ Configuration Changes:")
                for i, change in enumerate(file_comp.changes):
                    is_last_change = (i == len(file_comp.changes) - 1)
                    prefix = "     └─" if is_last_change else "     ├─"
                    
                    impact_icon = {
                        'HIGH': '🔥',
                        'MEDIUM': '⚠️',
                        'LOW': '💡',
                        'UNKNOWN': '❓'
                    }.get(change.impact_level, '❓')
                    
                    if change.change_type == 'added':
                        lines.append(f"{prefix} {change.setting_name}: ADDED = {change.new_value} {impact_icon}")
                    elif change.change_type == 'removed':
                        lines.append(f"{prefix} {change.setting_name}: REMOVED (was {change.old_value}) {impact_icon}")
                    else:
                        lines.append(f"{prefix} {change.setting_name}: {change.old_value} → {change.new_value} {impact_icon}")
        
        lines.append("│")
    
    def _get_performance_rationale(self, setting_name: str, old_value, new_value) -> str:
        """Get performance rationale for a specific setting change"""
        setting_lower = setting_name.lower()
        
        # Graphics performance settings
        if 'resolution' in setting_lower:
            return "Resolution changes directly impact GPU load and frame rates"
        elif any(term in setting_lower for term in ['msaa', 'ssaa', 'antialiasing']):
            return "Anti-aliasing settings significantly affect GPU performance"
        elif 'shadow' in setting_lower:
            return "Shadow quality impacts both GPU and CPU performance"
        elif 'texture' in setting_lower:
            return "Texture settings affect GPU memory usage and performance"
        elif 'visibility' in setting_lower or 'distance' in setting_lower:
            return "Visibility distance affects both CPU and GPU workload"
        elif 'forest' in setting_lower or 'vegetation' in setting_lower:
            return "Forest rendering is CPU intensive and affects frame rates"
        elif 'water' in setting_lower:
            return "Water effects can impact GPU performance significantly"
        elif 'effects' in setting_lower:
            return "Visual effects impact GPU performance and memory usage"
        elif 'preload' in setting_lower:
            return "Preloading affects memory usage and loading times"
        elif 'vsync' in setting_lower:
            return "V-Sync affects frame pacing and input latency"
        elif 'fullscreen' in setting_lower:
            return "Display mode affects performance and input latency"
        
        # Input settings
        elif any(term in setting_lower for term in ['input', 'control', 'sensitivity']):
            return "Input settings affect responsiveness and control precision"
        
        # Audio settings
        elif any(term in setting_lower for term in ['audio', 'sound']):
            return "Audio settings can impact CPU usage during gameplay"
        
        return "Configuration change may affect gaming performance"

    def _predict_setting_impact(self, setting_name: str, old_value, new_value) -> float:
        """Predict FPS impact of a specific setting change"""
        setting_lower = setting_name.lower()
        
        # Simple prediction model based on common DCS settings
        # Negative values = FPS loss, Positive = FPS gain
        
        if 'msaa' in setting_lower:
            try:
                old_val = int(old_value) if str(old_value).isdigit() else 0
                new_val = int(new_value) if str(new_value).isdigit() else 0
                # MSAA roughly costs 15-20% per level increase
                return (old_val - new_val) * 10  # Rough estimate
            except:
                return -5  # Default MSAA penalty
        
        elif 'shadow' in setting_lower:
            # Shadow quality changes
            if 'high' in str(new_value).lower() and 'medium' in str(old_value).lower():
                return -3  # High shadows cost ~3 FPS
            elif 'medium' in str(new_value).lower() and 'low' in str(old_value).lower():
                return -2  # Medium shadows cost ~2 FPS
            elif 'low' in str(new_value).lower() and 'high' in str(old_value).lower():
                return +5  # Lowering shadows gains ~5 FPS
            
        elif 'texture' in setting_lower:
            return -1  # Texture changes typically minor impact
            
        elif 'visibility' in setting_lower or 'distance' in setting_lower:
            return -2  # Visibility distance changes
            
        elif 'forest' in setting_lower:
            return -3  # Forest rendering is expensive
            
        elif 'water' in setting_lower:
            return -2  # Water effects impact
            
        elif 'resolution' in setting_lower:
            # Resolution has major impact but hard to predict without actual values
            return -10  # Assume resolution increase
        
        # Default for unknown high-impact settings
        return -2


    def _load_performance_data(self, backup_path: Path) -> Optional[dict]:
        """Load performance correlation data from backup folder"""
        try:
            perf_file = backup_path / "performance_data.json"
            if not perf_file.exists():
                return None
            
            with open(perf_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None


def create_default_report_path(backup1_name: str, backup2_name: str, report_format: str = 'performance') -> Path:
    """Create default report path following the specified format"""
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    filename = f"{timestamp}-Performance-Report.txt"
    
    # Create the specified directory structure
    gamechanger_root = Path("C:/Users/Thomas/Documents/GameChanger")
    reports_dir = gamechanger_root / "Reports"
    
    # Ensure reports directory exists
    try:
        reports_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Fall back to GameChanger root if Reports creation fails
        reports_dir = gamechanger_root
        try:
            reports_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Ultimate fallback to current directory
            reports_dir = Path.cwd()
    
    return reports_dir / filename


def main():
    """Test report generation"""
    import argparse
    from comparison import ConfigComparator
    
    parser = argparse.ArgumentParser(description='Generate GameChanger performance comparison report')
    parser.add_argument('backup1', type=Path, help='First backup folder')
    parser.add_argument('backup2', type=Path, help='Second backup folder')
    parser.add_argument('--output', type=Path, help='Output file path')
    
    args = parser.parse_args()
    
    # Perform comparison
    comparator = ConfigComparator()
    comparison = comparator.compare_backups(args.backup1, args.backup2)
    
    # Generate report
    generator = ReportGenerator()
    
    # Use default path if not specified
    output_path = args.output
    if not output_path:
        output_path = create_default_report_path(args.backup1.name, args.backup2.name)
    
    report_content = generator.generate_report(comparison, 'performance', output_path)
    
    print(f"Performance report generated: {output_path}")
    print(f"Report size: {len(report_content)} characters")


if __name__ == "__main__":
    main()