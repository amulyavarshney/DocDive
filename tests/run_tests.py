#!/usr/bin/env python3
"""
Test runner script for document search API.
This script provides utilities to run both e2e tests and load tests.
"""

import os
import sys
import argparse
import subprocess
import time
import webbrowser
from pathlib import Path

# Configure paths
BASE_DIR = Path(__file__).parent.parent
E2E_DIR = BASE_DIR / "tests" / "e2e"
LOAD_DIR = BASE_DIR / "tests" / "load_tests"


def run_e2e_tests(args):
    """Run end-to-end tests with pytest"""
    print("\n=== Running E2E Tests ===\n")
    
    # Ensure the test document exists
    test_doc_script = E2E_DIR / "create_test_doc.py"
    if test_doc_script.exists():
        print("Creating test document for E2E tests...")
        try:
            subprocess.run([sys.executable, str(test_doc_script)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to create test document: {e}")
            print("Tests may still run if the document already exists.")
    
    # Build the pytest command
    cmd = ["pytest", str(E2E_DIR), "-v"]
    
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term", "--cov-report=html:coverage_report"])
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ E2E Tests completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ E2E Tests failed with exit code {e.returncode}")
        return e.returncode


def run_load_tests(args):
    """Run load tests with Locust"""
    print("\n=== Running Load Tests ===\n")
    
    host = f"http://{args.host}:{args.port}"
    
    if args.headless:
        # Run in headless mode with specified parameters
        cmd = [
            "locust", 
            "-f", str(LOAD_DIR / "locustfile.py"),
            "--host", host,
            "--headless",
            "--users", str(args.users),
            "--spawn-rate", str(args.spawn_rate),
            "--run-time", args.run_time
        ]
        
        try:
            result = subprocess.run(cmd, check=True)
            print("\n✅ Load Tests completed successfully!")
            return 0
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Load Tests failed with exit code {e.returncode}")
            return e.returncode
    else:
        # Run with web UI
        cmd = [
            "locust", 
            "-f", str(LOAD_DIR / "locustfile.py"),
            "--host", host
        ]
        
        process = subprocess.Popen(cmd)
        
        # Open browser to Locust web UI
        time.sleep(1)  # Give locust time to start
        webbrowser.open(f"http://localhost:8089")
        
        print("\n🔍 Locust web UI started at http://localhost:8089")
        print("Press Ctrl+C to stop the load tests")
        
        try:
            process.wait()
            return 0
        except KeyboardInterrupt:
            process.terminate()
            print("\n⏱️ Load Tests stopped by user")
            return 0


def run_all_tests(args):
    """Run both e2e and load tests"""
    e2e_result = run_e2e_tests(args)
    
    if e2e_result != 0 and not args.force:
        print("\n⚠️ Skipping load tests due to E2E test failures")
        return e2e_result
    
    return run_load_tests(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests for document search API")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # E2E tests parser
    e2e_parser = subparsers.add_parser("e2e", help="Run end-to-end tests")
    e2e_parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    
    # Load tests parser
    load_parser = subparsers.add_parser("load", help="Run load tests")
    load_parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    load_parser.add_argument("--host", default="localhost", help="Host to test")
    load_parser.add_argument("--port", type=int, default=8000, help="Port to test")
    load_parser.add_argument("--users", type=int, default=50, help="Number of users to simulate")
    load_parser.add_argument("--spawn-rate", type=int, default=10, help="Rate of user spawning")
    load_parser.add_argument("--run-time", default="1m", help="Test duration (e.g., 30s, 5m, 1h)")
    
    # All tests parser
    all_parser = subparsers.add_parser("all", help="Run both e2e and load tests")
    all_parser.add_argument("--coverage", action="store_true", help="Generate coverage report for e2e tests")
    all_parser.add_argument("--headless", action="store_true", help="Run load tests in headless mode")
    all_parser.add_argument("--host", default="localhost", help="Host to test")
    all_parser.add_argument("--port", type=int, default=8000, help="Port to test")
    all_parser.add_argument("--users", type=int, default=50, help="Number of users to simulate")
    all_parser.add_argument("--spawn-rate", type=int, default=10, help="Rate of user spawning")
    all_parser.add_argument("--run-time", default="1m", help="Test duration (e.g., 30s, 5m, 1h)")
    all_parser.add_argument("--force", action="store_true", help="Run load tests even if e2e tests fail")
    
    args = parser.parse_args()
    
    if args.command == "e2e":
        sys.exit(run_e2e_tests(args))
    elif args.command == "load":
        sys.exit(run_load_tests(args))
    elif args.command == "all":
        sys.exit(run_all_tests(args))
    else:
        parser.print_help()
        sys.exit(1) 