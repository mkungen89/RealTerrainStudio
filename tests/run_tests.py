#!/usr/bin/env python3
# Copyright RealTerrain Studio. All Rights Reserved.

"""
Test runner script for RealTerrain Studio.

Usage:
    python run_tests.py               # Run all tests
    python run_tests.py --unit        # Run only unit tests
    python run_tests.py --integration # Run only integration tests
    python run_tests.py --coverage    # Run with coverage report
    python run_tests.py --performance # Run performance tests
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_pytest(args_list):
    """Run pytest with given arguments."""
    cmd = ['pytest'] + args_list
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Run RealTerrain Studio tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--parallel', '-n', type=int, help='Run tests in parallel (specify number of workers)')

    args = parser.parse_args()

    # Build pytest arguments
    pytest_args = []

    # Test selection
    if args.unit:
        pytest_args.extend(['backend/', '-m', 'not integration'])
    elif args.integration:
        pytest_args.extend(['integration/', '-m', 'integration'])
    elif args.performance:
        pytest_args.extend(['-m', 'performance'])
    else:
        # Run all tests by default
        pytest_args.append('.')

    # Coverage
    if args.coverage:
        pytest_args.extend([
            '--cov=../backend',
            '--cov=../qgis-plugin/src',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])

    # Verbosity
    if args.verbose:
        pytest_args.append('-v')

    # Parallel execution
    if args.parallel:
        pytest_args.extend(['-n', str(args.parallel)])

    # Change to tests directory
    tests_dir = Path(__file__).parent
    import os
    os.chdir(tests_dir)

    # Run tests
    exit_code = run_pytest(pytest_args)

    # Print summary
    if exit_code == 0:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
