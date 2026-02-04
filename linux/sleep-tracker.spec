# RPM Spec File for Sleep Tracker
# ================================
# Build with: rpmbuild -ba sleep-tracker.spec
#
# Prerequisites (Fedora):
#   sudo dnf install rpm-build rpmdevtools
#   rpmdev-setuptree
#

Name:           sleep-tracker
Version:        1.0.0
Release:        1%{?dist}
Summary:        Track your sleep patterns, mood, and energy

License:        MIT
URL:            https://github.com/yourusername/sleep-tracker
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python3
Requires:       python3-flask
Requires:       python3-pip

%description
Sleep Tracker is a locally-hosted web application for tracking sleep patterns,
mood, and energy levels. It provides an easy-to-use interface for logging
daily sleep data and viewing trends over time.

%prep
%autosetup

%install
# Create directories
mkdir -p %{buildroot}/opt/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps

# Copy application files
cp -r app.py %{buildroot}/opt/%{name}/
cp -r database.py %{buildroot}/opt/%{name}/
cp -r requirements.txt %{buildroot}/opt/%{name}/
cp -r templates %{buildroot}/opt/%{name}/
cp -r static %{buildroot}/opt/%{name}/

# Install launcher script
install -m 755 linux/sleep-tracker.sh %{buildroot}%{_bindir}/%{name}

# Install desktop entry
install -m 644 linux/sleep-tracker.desktop %{buildroot}%{_datadir}/applications/

# Install icon (if exists)
if [ -f linux/sleep-tracker.png ]; then
    install -m 644 linux/sleep-tracker.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/
fi

%post
# Update desktop database
update-desktop-database %{_datadir}/applications &> /dev/null || :
# Update icon cache
gtk-update-icon-cache %{_datadir}/icons/hicolor &> /dev/null || :

%postun
# Update desktop database
update-desktop-database %{_datadir}/applications &> /dev/null || :
# Update icon cache
gtk-update-icon-cache %{_datadir}/icons/hicolor &> /dev/null || :

%files
%license LICENSE
%doc README.md
/opt/%{name}/
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/256x256/apps/%{name}.png

%changelog
* Mon Feb 03 2026 Your Name <your.email@example.com> - 1.0.0-1
- Initial RPM release
