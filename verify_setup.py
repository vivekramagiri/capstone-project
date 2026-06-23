#!/usr/bin/env python3
"""
Setup verification script for Loan Approval AI System

Checks:
- Python version
- Required packages
- Environment variables
- File structure
- API connectivity (optional)
"""

import sys
import os
import subprocess
from pathlib import Path

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text):
    print(f"\n{BOLD}{text}{RESET}")
    print("-" * 60)


def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text):
    print(f"{RED}✗{RESET} {text}")


def print_warning(text):
    print(f"{YELLOW}⚠{RESET} {text}")


def check_python_version():
    """Check Python version"""
    print_header("Python Version")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.9+ required (found {version.major}.{version.minor})")
        return False


def check_required_packages():
    """Check if required packages are installed"""
    print_header("Required Packages")

    required = [
        "anthropic",
        "langgraph",
        "langchain",
        "fastapi",
        "uvicorn",
        "streamlit",
        "pydantic",
        "python-dotenv",
        "requests",
    ]

    all_ok = True
    for package in required:
        try:
            __import__(package)
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} (not installed)")
            all_ok = False

    if not all_ok:
        print(f"\n{YELLOW}Install missing packages:{RESET}")
        print("  pip install -r requirements.txt")

    return all_ok


def check_environment_variables():
    """Check environment variables"""
    print_header("Environment Variables")

    if os.path.exists(".env"):
        print_success(".env file found")

        # Check for API key
        if "ANTHROPIC_API_KEY" in open(".env").read():
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            if api_key and len(api_key) > 10:
                print_success("ANTHROPIC_API_KEY set and appears valid")
                return True
            else:
                print_error("ANTHROPIC_API_KEY not set or too short")
                return False
        else:
            print_error("ANTHROPIC_API_KEY not found in .env")
            return False
    else:
        print_warning(".env file not found")
        print(f"  Create it: cp .env.template .env")
        print(f"  Then edit with your ANTHROPIC_API_KEY")
        return False


def check_file_structure():
    """Check project file structure"""
    print_header("Project Structure")

    required_dirs = [
        "src",
        "src/agents",
        "src/mcp_servers",
        "src/orchestration",
        "src/api",
        "src/ui",
        "tests",
    ]

    required_files = [
        "main.py",
        "src/config.py",
        "src/schemas.py",
        "src/orchestration/workflow.py",
        "README.md",
    ]

    all_ok = True

    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"Directory: {dir_path}/")
        else:
            print_error(f"Directory missing: {dir_path}/")
            all_ok = False

    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"File: {file_path}")
        else:
            print_error(f"File missing: {file_path}")
            all_ok = False

    return all_ok


def test_imports():
    """Test basic imports"""
    print_header("Module Imports")

    try:
        from src.config import settings

        print_success("src.config")
    except Exception as e:
        print_error(f"src.config: {str(e)}")
        return False

    try:
        from src.schemas import LoanApplication

        print_success("src.schemas")
    except Exception as e:
        print_error(f"src.schemas: {str(e)}")
        return False

    try:
        from src.orchestration.workflow import get_workflow

        print_success("src.orchestration.workflow")
    except Exception as e:
        print_error(f"src.orchestration.workflow: {str(e)}")
        return False

    try:
        from src.api.main import app

        print_success("src.api.main")
    except Exception as e:
        print_error(f"src.api.main: {str(e)}")
        return False

    return True


def main():
    """Run all checks"""
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}Loan Approval AI System - Setup Verification{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")

    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("Environment Variables", check_environment_variables),
        ("Project Structure", check_file_structure),
        ("Module Imports", test_imports),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Check failed: {str(e)}")
            results.append((name, False))

    # Summary
    print_header("Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {status} - {name}")

    print(f"\n{BOLD}Result: {passed}/{total} checks passed{RESET}")

    if passed == total:
        print(f"\n{GREEN}✓ System is ready to run!{RESET}")
        print(f"\nTo start the system:")
        print(f"  {BOLD}python main.py{RESET}")
        print(f"\nAccess at:")
        print(f"  Web UI: http://localhost:8501")
        print(f"  API: http://localhost:8000")
        return 0
    else:
        print(f"\n{RED}✗ Fix the above issues before running{RESET}")
        print(f"\nFor help, see:")
        print(f"  QUICKSTART.md - Quick setup guide")
        print(f"  README.md - Full documentation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
