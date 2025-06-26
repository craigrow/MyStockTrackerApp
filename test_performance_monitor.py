#!/usr/bin/env python3
"""
Test performance monitoring and reporting tool.
Tracks test execution times and identifies slow tests.
"""
import subprocess
import json
import time
import sys
from datetime import datetime


def run_tests_with_timing():
    """Run tests and collect timing information."""
    print("📊 Test Performance Monitor")
    print("=" * 40)
    
    # Run tests with timing
    start_time = time.time()
    
    # Fast tests timing
    print("\n🏃 Running Fast Tests...")
    fast_start = time.time()
    fast_result = subprocess.run([
        'python', '-m', 'pytest', '-m', 'fast', 
        '--tb=short', '-q', '--durations=10'
    ], capture_output=True, text=True)
    fast_duration = time.time() - fast_start
    
    # All tests timing (sample)
    print("\n🐌 Running Sample of All Tests...")
    all_start = time.time()
    all_result = subprocess.run([
        'python', '-m', 'pytest', 
        '--tb=short', '-q', '--durations=10', '--maxfail=5'
    ], capture_output=True, text=True)
    all_duration = time.time() - all_start
    
    total_duration = time.time() - start_time
    
    # Generate report
    report = {
        'timestamp': datetime.now().isoformat(),
        'fast_tests': {
            'duration': round(fast_duration, 2),
            'status': 'PASSED' if fast_result.returncode == 0 else 'FAILED',
            'output': fast_result.stdout
        },
        'all_tests_sample': {
            'duration': round(all_duration, 2),
            'status': 'PASSED' if all_result.returncode == 0 else 'FAILED',
            'output': all_result.stdout
        },
        'total_duration': round(total_duration, 2)
    }
    
    # Display summary
    print(f"\n📈 Performance Summary")
    print(f"Fast Tests: {fast_duration:.2f}s ({report['fast_tests']['status']})")
    print(f"All Tests Sample: {all_duration:.2f}s ({report['all_tests_sample']['status']})")
    print(f"Total Monitoring Time: {total_duration:.2f}s")
    
    # Performance targets
    print(f"\n🎯 Performance Targets")
    fast_target = 30  # seconds
    fast_status = "✅" if fast_duration < fast_target else "⚠️"
    print(f"Fast Tests Target: <{fast_target}s {fast_status}")
    
    # Save detailed report
    with open('test_performance_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: test_performance_report.json")
    
    # Extract slow tests from output
    if '--durations=10' in fast_result.stdout or '--durations=10' in all_result.stdout:
        print(f"\n🐌 Slowest Tests (from pytest --durations output above)")
    
    return report


def analyze_performance_trends():
    """Analyze performance trends over time."""
    try:
        with open('test_performance_report.json', 'r') as f:
            current_report = json.load(f)
        
        # Simple trend analysis (could be expanded)
        fast_duration = current_report['fast_tests']['duration']
        
        if fast_duration < 10:
            print("🚀 Excellent performance!")
        elif fast_duration < 30:
            print("✅ Good performance")
        elif fast_duration < 60:
            print("⚠️  Performance needs attention")
        else:
            print("🚨 Performance issues detected")
            
    except FileNotFoundError:
        print("No previous performance data found")


if __name__ == "__main__":
    report = run_tests_with_timing()
    analyze_performance_trends()
    
    # Exit with error if tests failed
    if (report['fast_tests']['status'] == 'FAILED' or 
        report['all_tests_sample']['status'] == 'FAILED'):
        sys.exit(1)