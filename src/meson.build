# Configure and install Python sources
python_sources = [
  '__init__.py',
  'main.py',
  'database.py',
]

python_dir = py_installation.get_install_dir()
install_subdir('views',
  install_dir: python_dir / 'lifetracker'
)

# Install main Python files
install_data(python_sources,
  install_dir: python_dir / 'lifetracker'
)

# Create the entry point script
conf = configuration_data()
conf.set('PYTHON', py_installation.full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', get_option('prefix') / get_option('datadir') / 'lifetracker')

configure_file(
  input: 'lifetracker.in',
  output: 'lifetracker',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)
