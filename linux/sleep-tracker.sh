#!/bin/bash
#
# Sleep Tracker Launcher for Linux
# =================================
# This script launches the Sleep Tracker application
# and opens a browser window automatically.
#

# Get the directory where the app is installed
APP_DIR="${SLEEP_TRACKER_DIR:-/opt/sleep-tracker}"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/sleep-tracker"

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"

# Change to app directory
cd "$APP_DIR"

# Set the database path to user's data directory
export SLEEP_TRACKER_DB="$DATA_DIR/sleep_tracker.db"

# Check if virtual environment exists, if not use system Python
if [ -d "$APP_DIR/.venv" ]; then
    PYTHON="$APP_DIR/.venv/bin/python"
else
    PYTHON="python3"
fi

# Check if Flask is available
if ! $PYTHON -c "import flask" 2>/dev/null; then
    # Try to install Flask in user space
    echo "Flask not found. Installing dependencies..."
    $PYTHON -m pip install --user flask
fi

# Start browser after a short delay (in background)
(sleep 2 && xdg-open "http://localhost:5000" 2>/dev/null || \
    firefox "http://localhost:5000" 2>/dev/null || \
    chromium-browser "http://localhost:5000" 2>/dev/null || \
    google-chrome "http://localhost:5000" 2>/dev/null) &

# Run the Flask app
exec $PYTHON "$APP_DIR/app.py"
