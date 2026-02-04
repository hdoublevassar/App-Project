# Linux Installation Guide for Sleep Tracker

This guide explains how to install Sleep Tracker on Fedora Linux (and other distributions).

## Quick Start (Easiest Method)

### Download and Install

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/sleep-tracker.git
cd sleep-tracker

# 2. Run the installer
./install-linux.sh
```

That's it! Find "Sleep Tracker" in your applications menu.

---

## Installation Methods

### Method 1: Install Script (Recommended for Users)

The install script handles everything automatically:

```bash
# For personal use (installs to ~/.local)
./install-linux.sh

# For all users (installs to /opt and /usr/local)
sudo ./install-linux.sh
```

**What it does:**
- Copies app files to the appropriate location
- Installs Python dependencies
- Creates a desktop entry (app menu icon)
- Creates a command-line launcher

### Method 2: Using Make (For Developers)

```bash
# Install for current user
make install

# Install system-wide
sudo make install

# Just run without installing
make run

# Uninstall
make uninstall
```

### Method 3: RPM Package (For Fedora/RHEL)

If you have the RPM file (from GitHub Releases or self-built):

```bash
# Install with dnf
sudo dnf install sleep-tracker-1.0.0-1.fc*.noarch.rpm

# Uninstall
sudo dnf remove sleep-tracker
```

#### Building the RPM Yourself

```bash
# Install build tools
sudo dnf install rpm-build rpmdevtools

# Run the build script
./linux/build-rpm.sh

# Install the result
sudo dnf install ~/rpmbuild/RPMS/noarch/sleep-tracker-*.rpm
```

### Method 4: Manual Run (No Installation)

Just run directly without installing:

```bash
# Install Flask
pip3 install --user flask

# Run the app
python3 app.py

# Open browser to http://localhost:5000
```

---

## After Installation

### Running the App

**From Applications Menu:**
Look for "Sleep Tracker" in your applications menu (usually under Utilities or Accessories).

**From Terminal:**
```bash
sleep-tracker
```

### Where is My Data?

Your sleep data is stored in:
- **User install**: `~/.local/share/sleep-tracker/sleep_tracker.db`
- **System install**: `~/.local/share/sleep-tracker/sleep_tracker.db` (per-user data)
- **Manual run**: `./sleep_tracker.db` (in the app directory)

### Backup Your Data

```bash
cp ~/.local/share/sleep-tracker/sleep_tracker.db ~/sleep_tracker_backup.db
```

---

## Uninstallation

### Using the Uninstall Script

```bash
# User installation
./uninstall-linux.sh

# System installation
sudo ./uninstall-linux.sh
```

### Using DNF (if installed via RPM)

```bash
sudo dnf remove sleep-tracker
```

### Manual Cleanup

```bash
# Remove app files
rm -rf ~/.local/share/sleep-tracker/app  # user install
sudo rm -rf /opt/sleep-tracker           # system install

# Remove launcher
rm ~/.local/bin/sleep-tracker            # user install
sudo rm /usr/local/bin/sleep-tracker     # system install

# Remove desktop entry
rm ~/.local/share/applications/sleep-tracker.desktop
```

---

## Troubleshooting

### "Command not found" after installation

Add `~/.local/bin` to your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Flask/Python not found

Install Python and Flask:

```bash
# Fedora
sudo dnf install python3 python3-pip
pip3 install --user flask

# Ubuntu/Debian
sudo apt install python3 python3-pip
pip3 install --user flask
```

### Browser doesn't open automatically

Manually open http://localhost:5000 in your browser, or install xdg-utils:

```bash
sudo dnf install xdg-utils  # Fedora
sudo apt install xdg-utils  # Ubuntu
```

### Port 5000 already in use

Edit the launcher script to use a different port, or stop the conflicting service.

---

## For Your Friend

The easiest way to share with your friend:

1. **GitHub Release**: Upload the tarball to GitHub Releases
   ```bash
   # Your friend downloads and runs:
   tar xzf sleep-tracker-1.0.0-linux.tar.gz
   cd sleep-tracker-1.0.0
   ./install-linux.sh
   ```

2. **Direct clone**: Have them clone your GitHub repo
   ```bash
   git clone https://github.com/yourusername/sleep-tracker.git
   cd sleep-tracker
   ./install-linux.sh
   ```

3. **RPM file**: Build an RPM and share it directly
   ```bash
   # They run:
   sudo dnf install sleep-tracker-1.0.0-1.fc*.noarch.rpm
   ```
