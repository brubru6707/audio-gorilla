#!/usr/bin/env python3
"""
Test runner script for unit tests.
Can run all tests or individual test files.
"""

import sys
import unittest
import os

def run_all_tests():
    """Run all test files in the unit_tests directory"""
    # Get the directory containing this script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_specific_test(test_file):
    """Run a specific test file"""
    if not test_file.endswith('.py'):
        test_file += '.py'
    
    # Get the full path to the test file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.join(test_dir, test_file)
    
    if not os.path.exists(test_path):
        print(f"Error: Test file '{test_file}' not found.")
        return False
    
    # Run the specific test file
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=test_file)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) == 1:
        # No arguments, run all tests
        print("Running all tests...")
        success = run_all_tests()
    elif len(sys.argv) == 2:
        # One argument, run specific test file
        test_file = sys.argv[1]
        print(f"Running tests from {test_file}...")
        success = run_specific_test(test_file)
    else:
        print("Usage:")
        print("  python run_tests.py                    # Run all tests")
        print("  python run_tests.py test_slack_api     # Run specific test file")
        print("  python run_tests.py test_netflix_api   # Run specific test file")
        return
    
    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 