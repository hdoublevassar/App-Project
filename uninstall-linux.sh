#!/bin/bash
#
# Sleep Tracker Uninstallation Script for Linux
# ==============================================
#
# Usage:
#   ./uninstall-linux.sh           # Uninstall user installation
#   sudo ./uninstall-linux.sh      # Uninstall system-wide installation
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
echo "  ║      Sleep Tracker Uninstaller         ║"
echo "  ╚════════════════════════════════════════╝"
echo -e "${NC}"

# Determine installation type
if [ "$EUID" -eq 0 ]; then
    INSTALL_TYPE="system"
    INSTALL_DIR="/opt/sleep-tracker"
    BIN_DIR="/usr/local/bin"
    DESKTOP_DIR="/usr/share/applications"
    ICON_DIR="/usr/share/icons/hicolor/256x256/apps"
else
    INSTALL_TYPE="user"
    INSTALL_DIR="$HOME/.local/share/sleep-tracker/app"
    BIN_DIR="$HOME/.local/bin"
    DESKTOP_DIR="$HOME/.local/share/applications"
    ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
fi

DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/sleep-tracker"

echo -e "${YELLOW}Removing Sleep Tracker ($INSTALL_TYPE installation)...${NC}"

# Remove application files
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing application directory..."
    rm -rf "$INSTALL_DIR"
fi

# Remove launcher
if [ -f "$BIN_DIR/sleep-tracker" ]; then
    echo "Removing launcher..."
    rm -f "$BIN_DIR/sleep-tracker"
fi

# Remove desktop entry
if [ -f "$DESKTOP_DIR/sleep-tracker.desktop" ]; then
    echo "Removing desktop entry..."
    rm -f "$DESKTOP_DIR/sleep-tracker.desktop"
fi

# Remove icon
if [ -f "$ICON_DIR/sleep-tracker.png" ]; then
    echo "Removing icon..."
    rm -f "$ICON_DIR/sleep-tracker.png"
fi

# Ask about data directory
if [ -d "$DATA_DIR" ]; then
    echo ""
    echo -e "${YELLOW}Found user data directory: $DATA_DIR${NC}"
    echo "This contains your sleep tracking database."
    read -p "Do you want to remove your data? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$DATA_DIR"
        echo "Data removed."
    else
        echo "Data preserved at: $DATA_DIR"
    fi
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}Sleep Tracker has been uninstalled.${NC}"
