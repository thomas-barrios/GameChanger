#!/usr/bin/env python3
"""
Test script for the unified performance report functionality
This script validates that the performance report generation works correctly
with the merged format
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_report_generator_import():
    """Test that the ReportGenerator can be imported successfully"""
    try:
        from report_generator import ReportGenerator, create_default_report_path
        print("✅ ReportGenerator imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import ReportGenerator: {e}")
        return False

def test_comparison_import():
    """Test that the comparison module can be imported successfully"""
    try:
        from comparison import ConfigComparator, compare_main
        print("✅ Comparison module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import comparison module: {e}")
        return False

def test_report_generator_initialization():
    """Test that ReportGenerator can be initialized"""
    try:
        from report_generator import ReportGenerator
        generator = ReportGenerator()
        print("✅ ReportGenerator initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize ReportGenerator: {e}")
        return False

def test_unified_report_method():
    """Test that the unified performance report method exists"""
    try:
        from report_generator import ReportGenerator
        generator = ReportGenerator()
        
        # Check if the performance report method exists
        if hasattr(generator, '_generate_performance_report'):
            print("✅ Unified performance report method exists")
            return True
        else:
            print("❌ Unified performance report method not found")
            return False
    except Exception as e:
        print(f"❌ Error checking performance report method: {e}")
        return False

def test_format_argument_removed():
    """Test that format argument logic has been properly updated"""
    try:
        from report_generator import ReportGenerator
        generator = ReportGenerator()
        
        # Check if old report methods were removed
        old_methods = ['_generate_detailed_report', '_generate_summary_report']
        has_old_methods = any(hasattr(generator, method) for method in old_methods)
        
        if not has_old_methods:
            print("✅ Old report format methods successfully removed")
            return True
        else:
            print("❌ Old report format methods still exist")
            return False
    except Exception as e:
        print(f"❌ Error checking format argument removal: {e}")
        return False

def test_default_report_path():
    """Test that default report path uses performance format"""
    try:
        from report_generator import create_default_report_path
        
        path = create_default_report_path("backup1", "backup2")
        if "Performance-Report" in str(path):
            print("✅ Default report path uses Performance format")
            return True
        else:
            print(f"❌ Default report path doesn't use Performance format: {path}")
            return False
    except Exception as e:
        print(f"❌ Error testing default report path: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing GameChanger Performance Report Implementation")
    print("=" * 60)
    
    tests = [
        test_report_generator_import,
        test_comparison_import,
        test_report_generator_initialization,
        test_unified_report_method,
        test_format_argument_removed,
        test_default_report_path
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Performance report implementation looks good.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())