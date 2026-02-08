# Install data files
gnome = import('gnome')

# Compile resources
gnome.compile_resources('lifetracker',
  'io.github.lifetracker.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: get_option('datadir') / 'lifetracker'
)

# Install desktop file
install_data('io.github.lifetracker.desktop',
  install_dir: get_option('datadir') / 'applications'
)

# Install metainfo
install_data('io.github.lifetracker.metainfo.xml',
  install_dir: get_option('datadir') / 'metainfo'
)

# Install CSS (directly, not compiled)
install_data('style.css',
  install_dir: get_option('datadir') / 'lifetracker'
)
