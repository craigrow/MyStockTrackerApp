#!/usr/bin/env python3
"""
Fast test runner for development workflow.
Runs only fast tests to provide quick feedback during development.
"""
import subprocess
import sys
import time


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(cmd)}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"⏱️  Completed in {end_time - start_time:.2f} seconds")
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {description} - FAILED")
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout)
    
    return result.returncode == 0


def main():
    """Run fast tests with different configurations."""
    print("🚀 Fast Test Runner for MyStockTrackerApp")
    print("=" * 50)
    
    # Test configurations
    test_configs = [
        {
            "cmd": ["python", "-m", "pytest", "-m", "fast", "-v"],
            "description": "Fast tests only"
        },
        {
            "cmd": ["python", "-m", "pytest", "-m", "fast", "-n", "auto"],
            "description": "Fast tests in parallel"
        },
        {
            "cmd": ["python", "-m", "pytest", "-m", "not slow", "-v"],
            "description": "All tests except slow ones"
        }
    ]
    
    # Run each configuration
    results = []
    for config in test_configs:
        success = run_command(config["cmd"], config["description"])
        results.append((config["description"], success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{description}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All fast tests passed! Ready for development.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()