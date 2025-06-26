#!/usr/bin/env python3
"""
Smart test runner that selects tests based on changed files.
Analyzes git changes and runs only affected tests.
"""
import subprocess
import sys
import os
import re
from pathlib import Path


def get_changed_files():
    """Get list of changed files from git."""
    try:
        # Get changed files in current branch vs main
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1..HEAD'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            # Fallback to staged changes
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True, text=True
            )
        
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except Exception:
        return []


def determine_test_scope(changed_files):
    """Determine which tests to run based on changed files."""
    test_patterns = []
    
    for file_path in changed_files:
        if not file_path:
            continue
            
        # Model changes -> run model tests
        if file_path.startswith('app/models/'):
            test_patterns.extend(['-k', 'test_model', '-m', 'fast'])
            
        # Service changes -> run service and integration tests
        elif file_path.startswith('app/services/'):
            test_patterns.extend(['-k', 'service'])
            
        # View/template changes -> run UI tests
        elif file_path.startswith('app/views/') or file_path.startswith('app/templates/'):
            test_patterns.extend(['-m', 'ui'])
            
        # API changes -> run API tests
        elif 'api' in file_path.lower():
            test_patterns.extend(['-m', 'api'])
            
        # Test changes -> run specific test files
        elif file_path.startswith('tests/'):
            test_patterns.append(file_path)
            
        # Configuration changes -> run all tests
        elif file_path in ['requirements.txt', 'app/config.py', 'conftest.py']:
            return ['tests/']  # Run all tests
    
    # Remove duplicates and return
    return list(set(test_patterns)) if test_patterns else ['-m', 'fast']


def run_smart_tests():
    """Run tests based on changed files."""
    print("🧠 Smart Test Runner")
    print("=" * 40)
    
    changed_files = get_changed_files()
    
    if not changed_files:
        print("No changed files detected. Running fast tests...")
        test_args = ['-m', 'fast']
    else:
        print(f"Changed files detected: {len(changed_files)}")
        for file in changed_files[:5]:  # Show first 5
            print(f"  - {file}")
        if len(changed_files) > 5:
            print(f"  ... and {len(changed_files) - 5} more")
        
        test_args = determine_test_scope(changed_files)
        print(f"Test scope: {' '.join(test_args)}")
    
    # Run pytest with determined arguments
    cmd = ['python', '-m', 'pytest'] + test_args + ['-v']
    print(f"\nRunning: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_smart_tests())