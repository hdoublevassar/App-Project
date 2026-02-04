# Sleep Tracker

A locally-hosted web application for tracking sleep patterns, mood, and energy levels.

![Sleep Tracker](linux/sleep-tracker.svg)

## Features

- 📝 Log daily sleep entries (bed time, wake time)
- 💊 Track sleep aids (melatonin, etc.)
- 😊 Rate your mood and energy levels
- 📊 View trends and patterns over time
- 📅 Calendar view of your sleep history
- 🔒 All data stays on your computer

## Installation

### Windows

1. Download or clone this repository
2. Double-click `Sleep Tracker.bat` to run (first time will set up the virtual environment)
3. Or use the `Start Sleep Tracker.pyw` for a no-console-window experience

### Linux (Fedora, Ubuntu, etc.)

#### Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/sleep-tracker.git
cd sleep-tracker

# Install for current user
./install-linux.sh

# Or install system-wide (for all users)
sudo ./install-linux.sh
```

After installation, find "Sleep Tracker" in your applications menu or run `sleep-tracker` from the terminal.

#### Using Make

```bash
# Clone and enter directory
git clone https://github.com/yourusername/sleep-tracker.git
cd sleep-tracker

# Install for current user
make install

# Or install system-wide
sudo make install

# Run without installing
make run
```

#### DNF/RPM Installation (Fedora)

If you have the RPM package:

```bash
# Install from local RPM file
sudo dnf install sleep-tracker-1.0.0-1.fc*.noarch.rpm
```

To build the RPM yourself:

```bash
# Install build tools
sudo dnf install rpm-build rpmdevtools

# Build the RPM
./linux/build-rpm.sh

# Install the built RPM
sudo dnf install ~/rpmbuild/RPMS/noarch/sleep-tracker-*.rpm
```

#### Manual Installation

```bash
# Install Python 3 and Flask
sudo dnf install python3 python3-pip    # Fedora
# OR
sudo apt install python3 python3-pip    # Ubuntu/Debian

# Clone and run
git clone https://github.com/yourusername/sleep-tracker.git
cd sleep-tracker
pip3 install --user flask
python3 app.py
```

Then open http://localhost:5000 in your browser.

## Uninstallation

### Linux

```bash
# User installation
./uninstall-linux.sh

# System-wide installation
sudo ./uninstall-linux.sh

# Or using make
make uninstall
sudo make uninstall
```

### Windows

Simply delete the folder. Your sleep data is stored in `sleep_tracker.db` in the app folder.

## Data Storage

- **Windows**: Data is stored in `sleep_tracker.db` in the application folder
- **Linux (installed)**: Data is stored in `~/.local/share/sleep-tracker/sleep_tracker.db`
- **Linux (manual run)**: Data is stored in `sleep_tracker.db` in the application folder

## Development

### Requirements

- Python 3.8+
- Flask

### Running in Development Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

The app will be available at http://localhost:5000

### Project Structure

```
sleep-tracker/
├── app.py              # Main Flask application
├── database.py         # Database operations
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
├── static/            
│   ├── css/           # Stylesheets
│   └── js/            # JavaScript
├── linux/             # Linux packaging files
│   ├── sleep-tracker.desktop
│   ├── sleep-tracker.sh
│   ├── sleep-tracker.spec
│   └── sleep-tracker.svg
├── install-linux.sh   # Linux installer
├── uninstall-linux.sh # Linux uninstaller
├── Makefile           # Make targets
├── Sleep Tracker.bat  # Windows launcher
└── Start Sleep Tracker.pyw  # Windows GUI launcher
```

## GitHub Releases

Pre-built packages are available on the [Releases](../../releases) page:

- **RPM package** - For Fedora, RHEL, CentOS
- **Source archive** - For manual installation

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
