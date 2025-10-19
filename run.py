#!/usr/bin/env python3
"""Simple startup script for Clinical Question Copilot."""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import chromadb
        import sentence_transformers
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main startup function."""
    print("🏥 Clinical Question Copilot")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if we want to run tests
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("\n🧪 Running tests...")
        subprocess.run([sys.executable, "test_copilot.py"])
        return
    
    # Start the web server
    print("\n🚀 Starting web server...")
    print("📱 Open your browser to: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
