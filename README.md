# LifeTracker

A privacy-focused personal wellness companion for GNOME.

## Features

- 😴 **Sleep & Mental Health** - Track sleep quality, mood, and energy levels
- 💪 **Fitness Tracker** - Log workouts and monitor progress
- 🌟 **Addiction Recovery** - Support for recovery with milestones and encouragement
- 💊 **Medications & Appointments** - Never miss a dose or appointment
- 💬 **Relationships** - Track interaction patterns and relationship health
- 🎯 **Goals** - Set and achieve long-term goals with milestone tracking
- 📊 **Lifestyle Insights** - Cross-module analytics and recommendations
- 🔒 **Privacy First** - All data stored locally, password protected

## Screenshots

*(Coming soon)*

## Installation

### Flatpak (Recommended)

```bash
flatpak install io.github.lifetracker
```

### From Source

Requirements:
- Python 3.10+
- GTK 4.10+
- libadwaita 1.4+
- meson & ninja
- SQLCipher (optional, for encrypted database)

```bash
# Clone the repository
git clone https://github.com/yourusername/lifetracker.git
cd lifetracker

# Build with meson
meson setup builddir
meson compile -C builddir
meson install -C builddir

# Run
lifetracker
```

### Development Run

For development without installing:

```bash
# On Linux with GTK4 and libadwaita installed:
cd src
python main.py
```

## Technology Stack

- **UI**: GTK4 + libadwaita (GNOME native)
- **Language**: Python 3
- **Database**: SQLite with optional SQLCipher encryption
- **Packaging**: Flatpak

## Privacy

LifeTracker is designed with privacy as a core principle:

- All data is stored locally on your device
- Optional encrypted database (SQLCipher)
- Password protection required to access the app
- No telemetry, no analytics, no cloud sync
- Your data never leaves your device

## License

GPL-3.0-or-later

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.
