"""
Sleep Tracker Launcher
======================
Double-click this file to start the Sleep Tracker app.
A browser window will open automatically.

This script runs without showing a console window (.pyw extension).
"""

import subprocess
import webbrowser
import time
import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Path to the Python executable in the virtual environment
if sys.platform == 'win32':
    python_exe = os.path.join(script_dir, '.venv', 'Scripts', 'python.exe')
else:
    python_exe = os.path.join(script_dir, '.venv', 'bin', 'python')

# Path to the Flask app
app_path = os.path.join(script_dir, 'app.py')

# Start the Flask server
process = subprocess.Popen(
    [python_exe, app_path],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait a moment for the server to start, then open browser
time.sleep(2)
webbrowser.open('http://localhost:5000')

# Keep the script running (so the server stays alive)
try:
    process.wait()
except KeyboardInterrupt:
    process.terminate()
