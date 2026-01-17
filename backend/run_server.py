#!/usr/bin/env python
"""
Production server startup script.
"""
import os
import subprocess
import sys

def main():
    # Run migrations
    print("Running migrations...")
    subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], check=True)
    
    # Get port from environment, default to 8000
    port = os.environ.get("PORT", "8000")
    print(f"Starting gunicorn on port {port}...")
    
    # Start gunicorn
    os.execvp("gunicorn", [
        "gunicorn",
        "config.wsgi:application",
        "--bind", f"0.0.0.0:{port}",
        "--workers", "2",
        "--log-file", "-",
    ])

if __name__ == "__main__":
    main()
