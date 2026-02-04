# Makefile for Sleep Tracker
# ==========================
# Standard Linux installation using make
#
# Usage:
#   make install          # Install for current user
#   sudo make install     # Install system-wide
#   make uninstall        # Uninstall
#   make run              # Run without installing
#

PREFIX ?= $(HOME)/.local
DESTDIR ?=

ifeq ($(shell id -u),0)
    # Running as root - install system-wide
    PREFIX = /usr/local
    APP_DIR = /opt/sleep-tracker
else
    APP_DIR = $(PREFIX)/share/sleep-tracker/app
endif

BIN_DIR = $(DESTDIR)$(PREFIX)/bin
DESKTOP_DIR = $(DESTDIR)$(PREFIX)/share/applications
ICON_DIR = $(DESTDIR)$(PREFIX)/share/icons/hicolor/256x256/apps

.PHONY: all install uninstall run clean help

all: help

help:
	@echo "Sleep Tracker - Makefile targets:"
	@echo ""
	@echo "  make install    - Install the application"
	@echo "  make uninstall  - Remove the application"
	@echo "  make run        - Run without installing"
	@echo "  make deps       - Install Python dependencies"
	@echo "  make clean      - Clean build files"
	@echo ""
	@echo "For system-wide installation, run with sudo:"
	@echo "  sudo make install"

deps:
	@echo "Installing Python dependencies..."
	python3 -m pip install --user -r requirements.txt

run: deps
	@echo "Starting Sleep Tracker..."
	@(sleep 2 && xdg-open "http://localhost:5000" 2>/dev/null) &
	python3 app.py

install:
	@echo "Installing Sleep Tracker..."
	
	# Create directories
	mkdir -p $(DESTDIR)$(APP_DIR)
	mkdir -p $(BIN_DIR)
	mkdir -p $(DESKTOP_DIR)
	mkdir -p $(ICON_DIR)
	
	# Copy application files
	cp app.py $(DESTDIR)$(APP_DIR)/
	cp database.py $(DESTDIR)$(APP_DIR)/
	cp requirements.txt $(DESTDIR)$(APP_DIR)/
	cp -r templates $(DESTDIR)$(APP_DIR)/
	cp -r static $(DESTDIR)$(APP_DIR)/
	
	# Install launcher
	cp linux/sleep-tracker.sh $(BIN_DIR)/sleep-tracker
	chmod +x $(BIN_DIR)/sleep-tracker
	sed -i 's|APP_DIR="$${SLEEP_TRACKER_DIR:-/opt/sleep-tracker}"|APP_DIR="$(APP_DIR)"|g' $(BIN_DIR)/sleep-tracker
	
	# Install desktop entry
	cp linux/sleep-tracker.desktop $(DESKTOP_DIR)/
	sed -i 's|Exec=sleep-tracker|Exec=$(BIN_DIR)/sleep-tracker|g' $(DESKTOP_DIR)/sleep-tracker.desktop
	
	# Install icon (if exists)
	@if [ -f linux/sleep-tracker.png ]; then \
		cp linux/sleep-tracker.png $(ICON_DIR)/; \
		sed -i 's|Icon=sleep-tracker|Icon=$(ICON_DIR)/sleep-tracker.png|g' $(DESKTOP_DIR)/sleep-tracker.desktop; \
	fi
	
	# Create virtual environment and install deps (for system install)
	@if [ $$(id -u) -eq 0 ]; then \
		python3 -m venv $(DESTDIR)$(APP_DIR)/.venv; \
		$(DESTDIR)$(APP_DIR)/.venv/bin/pip install -r requirements.txt; \
	else \
		python3 -m pip install --user -r requirements.txt 2>/dev/null || python3 -m pip install --user flask; \
	fi
	
	# Update desktop database
	@update-desktop-database $(DESKTOP_DIR) 2>/dev/null || true
	
	@echo ""
	@echo "Installation complete!"
	@echo "Run 'sleep-tracker' or find it in your applications menu."

uninstall:
	@echo "Uninstalling Sleep Tracker..."
	rm -rf $(DESTDIR)$(APP_DIR)
	rm -f $(BIN_DIR)/sleep-tracker
	rm -f $(DESKTOP_DIR)/sleep-tracker.desktop
	rm -f $(ICON_DIR)/sleep-tracker.png
	@update-desktop-database $(DESKTOP_DIR) 2>/dev/null || true
	@echo "Uninstallation complete!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -f sleep_tracker.db
