project('lifetracker',
  version: '1.0.0',
  meson_version: '>= 0.59.0',
  default_options: ['warning_level=2', 'werror=false']
)

# Application ID
APPLICATION_ID = 'io.github.lifetracker'

# Python module
python = import('python')
py_installation = python.find_installation('python3')

# GLib schema compiler
gnome = import('gnome')

# Dependencies
dependency('gtk4', version: '>= 4.10')
dependency('libadwaita-1', version: '>= 1.4')

# Subdirectories
subdir('data')
subdir('src')

# Post install
gnome.post_install(
  gtk_update_icon_cache: true,
  update_desktop_database: true
)
