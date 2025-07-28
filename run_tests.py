#!/usr/bin/env python3
"""
Test Runner Script for MyStockTrackerApp

This script provides convenient commands for running different test suites
based on development needs and CI/CD requirements.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle output."""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Runner for MyStockTrackerApp")
    parser.add_argument(
        "mode", 
        choices=["dev", "fast", "full", "performance", "smoke", "ci"],
        help="Test mode to run"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose output"
    )
    parser.add_argument(
        "--durations", 
        type=int, 
        default=0,
        help="Show N slowest test durations"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    if args.durations > 0:
        base_cmd.extend(["--durations", str(args.durations)])
    
    # Test mode configurations
    test_configs = {
        "dev": {
            "cmd": base_cmd + ["-c", "pytest_dev.ini"],
            "description": "Development Tests (Fast - No Performance Tests)"
        },
        "fast": {
            "cmd": base_cmd + ["-m", "fast"],
            "description": "Fast Unit Tests Only"
        },
        "full": {
            "cmd": base_cmd + ["-c", "pytest_ci.ini"],
            "description": "Full Test Suite (All Tests Including Performance)"
        },
        "performance": {
            "cmd": base_cmd + ["-m", "performance"],
            "description": "Performance Tests Only"
        },
        "smoke": {
            "cmd": base_cmd + ["-m", "smoke"],
            "description": "Smoke Tests Only"
        },
        "ci": {
            "cmd": base_cmd + ["-c", "pytest_ci.ini", "--tb=short"],
            "description": "CI/CD Test Suite"
        }
    }
    
    config = test_configs.get(args.mode)
    if not config:
        print(f"❌ Unknown test mode: {args.mode}")
        return 1
    
    # Run the tests
    success = run_command(config["cmd"], config["description"])
    
    if success:
        print(f"\n🎉 All tests passed for mode: {args.mode}")
        return 0
    else:
        print(f"\n💥 Some tests failed for mode: {args.mode}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
