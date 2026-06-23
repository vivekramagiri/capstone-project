#!/usr/bin/env python3
"""
Main entry point for the Loan Approval AI System

This script starts all the necessary services:
1. FastAPI microservice (for API endpoints)
2. Streamlit UI (for web interface)
3. MCP servers (for agent communication)
"""

import subprocess
import sys
import time
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def start_fastapi_server():
    """Start FastAPI microservice"""
    logger.info(f"Starting FastAPI server on {settings.API_HOST}:{settings.API_PORT}")
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.api.main:app",
        "--host",
        settings.API_HOST,
        "--port",
        str(settings.API_PORT),
        "--reload",
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def start_streamlit_app():
    """Start Streamlit UI"""
    logger.info(f"Starting Streamlit app on port {settings.STREAMLIT_PORT}")
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "src/ui/app.py",
        f"--server.port={settings.STREAMLIT_PORT}",
        "--server.headless=true",
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def print_banner():
    """Print startup banner"""
    banner = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║            🏦 INTELLIGENT LOAN APPROVAL AI SYSTEM 🤖              ║
║                                                                    ║
║            Multi-Agent Agentic Architecture with LangGraph        ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main entry point"""
    print_banner()

    # Validate configuration
    logger.info("Validating configuration...")
    try:
        settings.validate()
        logger.info("✓ Configuration validated")
    except ValueError as e:
        logger.error(f"✗ Configuration error: {str(e)}")
        sys.exit(1)

    # Start services
    logger.info("Starting services...")

    processes = []

    try:
        # Start FastAPI server
        logger.info("Starting FastAPI microservice...")
        api_process = start_fastapi_server()
        processes.append(("FastAPI", api_process))
        time.sleep(2)  # Give API time to start

        # Start Streamlit app
        logger.info("Starting Streamlit UI...")
        streamlit_process = start_streamlit_app()
        processes.append(("Streamlit", streamlit_process))
        time.sleep(3)  # Give Streamlit time to start

        # Print service URLs
        print("\n" + "=" * 70)
        print("✓ All services started successfully!")
        print("=" * 70)
        print(f"\n📡 API Server: http://{settings.API_HOST}:{settings.API_PORT}")
        print(f"🌐 Web UI:    http://localhost:{settings.STREAMLIT_PORT}")
        print(f"\n🔗 API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
        print("\n" + "=" * 70)
        print("\nTo stop the system, press Ctrl+C")
        print("=" * 70 + "\n")

        # Keep processes running
        while True:
            time.sleep(1)

            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    logger.error(f"{name} process died with return code {process.returncode}")
                    # Don't exit here, let user see the error

    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        print("\n" + "=" * 70)
        print("Shutting down services...")
        print("=" * 70)

        for name, process in processes:
            try:
                process.terminate()
                logger.info(f"Terminated {name} process")
            except:
                pass

        time.sleep(1)

        # Force kill if needed
        for name, process in processes:
            try:
                if process.poll() is None:
                    process.kill()
            except:
                pass

        logger.info("Shutdown complete")
        print("✓ All services stopped")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        for name, process in processes:
            try:
                process.terminate()
            except:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main()
