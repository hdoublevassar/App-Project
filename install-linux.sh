#!/bin/bash
#
# Sleep Tracker Installation Script for Linux
# ============================================
# This script installs the Sleep Tracker application on Fedora/RHEL or Debian/Ubuntu.
#
# Usage:
#   ./install-linux.sh           # Install for current user only
#   sudo ./install-linux.sh      # Install system-wide (for all users)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "  ╔════════════════════════════════════════╗"
echo "  ║       Sleep Tracker Installer          ║"
echo "  ╚════════════════════════════════════════╝"
echo -e "${NC}"

# Determine installation type
if [ "$EUID" -eq 0 ]; then
    INSTALL_TYPE="system"
    INSTALL_DIR="/opt/sleep-tracker"
    BIN_DIR="/usr/local/bin"
    DESKTOP_DIR="/usr/share/applications"
    ICON_DIR="/usr/share/icons/hicolor/256x256/apps"
    echo -e "${GREEN}Installing system-wide...${NC}"
else
    INSTALL_TYPE="user"
    INSTALL_DIR="$HOME/.local/share/sleep-tracker/app"
    BIN_DIR="$HOME/.local/bin"
    DESKTOP_DIR="$HOME/.local/share/applications"
    ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
    echo -e "${GREEN}Installing for current user only...${NC}"
fi

# Get the directory where this script is located (source files)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"

# Copy application files
echo -e "${YELLOW}Copying application files...${NC}"
cp -r "$SCRIPT_DIR/app.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/database.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/templates" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/static" "$INSTALL_DIR/"

# Copy and setup launcher script
echo -e "${YELLOW}Setting up launcher...${NC}"
cp "$SCRIPT_DIR/linux/sleep-tracker.sh" "$BIN_DIR/sleep-tracker"
chmod +x "$BIN_DIR/sleep-tracker"

# Update the launcher with the correct install directory
sed -i "s|APP_DIR=\"\${SLEEP_TRACKER_DIR:-/opt/sleep-tracker}\"|APP_DIR=\"$INSTALL_DIR\"|g" "$BIN_DIR/sleep-tracker"

# Copy desktop entry
echo -e "${YELLOW}Installing desktop entry...${NC}"
cp "$SCRIPT_DIR/linux/sleep-tracker.desktop" "$DESKTOP_DIR/"

# Update desktop entry with correct exec path
sed -i "s|Exec=sleep-tracker|Exec=$BIN_DIR/sleep-tracker|g" "$DESKTOP_DIR/sleep-tracker.desktop"

# Copy icon if exists, otherwise create a placeholder
if [ -f "$SCRIPT_DIR/linux/sleep-tracker.png" ]; then
    cp "$SCRIPT_DIR/linux/sleep-tracker.png" "$ICON_DIR/"
    sed -i "s|Icon=sleep-tracker|Icon=$ICON_DIR/sleep-tracker.png|g" "$DESKTOP_DIR/sleep-tracker.desktop"
else
    echo -e "${YELLOW}Note: No icon found. Using default.${NC}"
fi

# Install Python dependencies
echo -e "${YELLOW}Checking Python dependencies...${NC}"

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed!${NC}"
    echo "Please install Python 3:"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi

# Install Flask
echo -e "${YELLOW}Installing Flask...${NC}"
if [ "$INSTALL_TYPE" = "system" ]; then
    # For system install, create a virtual environment
    python3 -m venv "$INSTALL_DIR/.venv"
    "$INSTALL_DIR/.venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
else
    # For user install, use pip with --user flag
    python3 -m pip install --user -r "$INSTALL_DIR/requirements.txt" 2>/dev/null || \
    python3 -m pip install --user flask
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$(dirname "$ICON_DIR")" 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Installation complete!                                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "You can now:"
echo -e "  1. Find '${BLUE}Sleep Tracker${NC}' in your applications menu"
echo -e "  2. Or run '${BLUE}sleep-tracker${NC}' from the terminal"
echo ""

if [ "$INSTALL_TYPE" = "user" ]; then
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo -e "${YELLOW}Note: Add ~/.local/bin to your PATH:${NC}"
        echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
        echo "  source ~/.bashrc"
        echo ""
    fi
fi

echo -e "To uninstall later, run: ${RED}./uninstall-linux.sh${NC}"
