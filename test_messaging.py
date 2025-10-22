"""
Test script for the new GameChanger messaging system
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from messaging import OutputManager, PathHelper, ErrorTracker, MessageFormatter
    import logging
    
    def test_messaging_system():
        # Setup basic logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
        logger = logging.getLogger("test")
        
        # Test OutputManager
        print("=== Testing Backup Messaging ===")
        
        output_mgr = OutputManager(logger, "BACKUP")
        output_mgr.start_operation()
        
        # Add sections with sample operations
        output_mgr.add_section("DCS", r"C:\Users\thomas\Saved Games\DCS\Config")
        output_mgr.add_operation(
            Path(r"C:\Users\thomas\Saved Games\DCS\Config\autoexec.cfg"),
            Path(r"D:\GameChanger\Backup\2025-10-22\C\Users\thomas\Saved Games\DCS\Config\autoexec.cfg"),
            "DCS", True
        )
        output_mgr.add_operation(
            Path(r"C:\Users\thomas\Saved Games\DCS\Config\options.lua"),
            Path(r"D:\GameChanger\Backup\2025-10-22\C\Users\thomas\Saved Games\DCS\Config\options.lua"),
            "DCS", True
        )
        output_mgr.add_operation(
            Path(r"C:\Users\thomas\Saved Games\DCS\Config\nicknames.lua"),
            Path(r"D:\GameChanger\Backup\2025-10-22\C\Users\thomas\Saved Games\DCS\Config\nicknames.lua"),
            "DCS", False, "Permission denied", "Access is denied"
        )
        
        output_mgr.add_section("VR", r"C:\Users\thomas\AppData\Roaming")
        output_mgr.add_operation(
            Path(r"C:\Users\thomas\AppData\Roaming\PiTool\manifest\PiTool\beforeConfig.json"),
            Path(r"D:\GameChanger\Backup\2025-10-22\C\Users\thomas\AppData\Roaming\PiTool\manifest\PiTool\beforeConfig.json"),
            "VR", True
        )
        output_mgr.add_operation(
            Path(r"C:\Users\thomas\AppData\Roaming\discord\settings.json"),
            Path(r"D:\GameChanger\Backup\2025-10-22\C\Users\thomas\AppData\Roaming\discord\settings.json"),
            "VR", False, "File not found", "The system cannot find the file specified"
        )
        
        output_mgr.add_section("System", r"C:\ProgramData\NVIDIA Corporation\Drs")
        output_mgr.add_operation(
            Path(r"C:\ProgramData\NVIDIA Corporation\Drs\nvdrsdb0.bin"),
            Path(r"D:\GameChanger\Backup\2025-10-22\C\ProgramData\NVIDIA Corporation\Drs\nvdrsdb0.bin"),
            "System", False, "Permission denied", "Administrator access required"
        )
        
        # Finalize and display results
        output_mgr.finalize_operation(Path("test_backup.log"))
        
        print("\n=== Testing Individual Components ===")
        
        # Test PathHelper
        files = [
            r"C:\Users\thomas\Saved Games\DCS\Config\autoexec.cfg",
            r"C:\Users\thomas\Saved Games\DCS\Config\options.lua",
            r"C:\Users\thomas\Saved Games\DCS\Config\nicknames.lua"
        ]
        base_path = PathHelper.get_section_base_path("DCS", files)
        print(f"Base path for DCS: {base_path}")
        
        for file_path in files:
            rel_path = PathHelper.get_relative_path(file_path, base_path)
            print(f"  {file_path} -> {rel_path}")
        
        # Test ErrorTracker
        print("\n=== Testing ErrorTracker ===")
        error_tracker = ErrorTracker()
        error_tracker.add_error("Permission denied", "autoexec.cfg", "DCS")
        error_tracker.add_error("File not found", "missing.lua", "DCS")
        error_tracker.add_error("Access is denied", "nvdrsdb0.bin", "System")
        
        error_summary = error_tracker.get_error_summary()
        for error_type, files in error_summary.items():
            print(f"{error_type}: {len(files)} files")
            for file in files:
                print(f"  - {file}")
        
        print("\n=== Test Complete ===")
        
    if __name__ == "__main__":
        test_messaging_system()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure messaging.py is in the src directory")
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()