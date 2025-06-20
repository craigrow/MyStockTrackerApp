#!/usr/bin/env python3
"""
Test runner script for MyStockTrackerApp.

This script provides an easy way to run all tests or specific test categories.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle the output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for MyStockTrackerApp")
    parser.add_argument(
        "--category", 
        choices=["models", "services", "integration", "all"],
        default="all",
        help="Test category to run (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--specific", "-s",
        help="Run a specific test file or test function"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    if args.coverage:
        base_cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Determine which tests to run
    if args.specific:
        test_path = args.specific
        description = f"Specific test: {test_path}"
        cmd = base_cmd + [test_path]
        success = run_command(cmd, description)
        sys.exit(0 if success else 1)
    
    success_count = 0
    total_count = 0
    
    if args.category == "all":
        test_categories = [
            ("tests/test_models.py", "Model Tests"),
            ("tests/test_services.py", "Service Tests"),
            ("tests/test_integration.py", "Integration Tests")
        ]
    elif args.category == "models":
        test_categories = [("tests/test_models.py", "Model Tests")]
    elif args.category == "services":
        test_categories = [("tests/test_services.py", "Service Tests")]
    elif args.category == "integration":
        test_categories = [("tests/test_integration.py", "Integration Tests")]
    
    for test_file, description in test_categories:
        total_count += 1
        cmd = base_cmd + [test_file]
        if run_command(cmd, description):
            success_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Passed: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()