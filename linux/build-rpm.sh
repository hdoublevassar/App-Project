#!/bin/bash
#
# Build RPM Package for Sleep Tracker
# ====================================
# This script builds an RPM package that can be installed with dnf/yum.
#
# Prerequisites:
#   sudo dnf install rpm-build rpmdevtools
#
# Usage:
#   ./linux/build-rpm.sh
#
# Output:
#   The RPM file will be in ~/rpmbuild/RPMS/noarch/
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

VERSION="1.0.0"
NAME="sleep-tracker"

echo -e "${BLUE}"
echo "  ╔════════════════════════════════════════╗"
echo "  ║    Sleep Tracker RPM Builder           ║"
echo "  ╚════════════════════════════════════════╝"
echo -e "${NC}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

# Check for required tools
if ! command -v rpmbuild &> /dev/null; then
    echo -e "${YELLOW}Installing required tools...${NC}"
    sudo dnf install -y rpm-build rpmdevtools
fi

# Setup RPM build environment
echo -e "${YELLOW}Setting up RPM build environment...${NC}"
rpmdev-setuptree 2>/dev/null || true

# Create source tarball
echo -e "${YELLOW}Creating source tarball...${NC}"
TEMP_DIR=$(mktemp -d)
mkdir -p "$TEMP_DIR/$NAME-$VERSION"

# Copy files to temp directory
cp -r app.py database.py requirements.txt templates static linux "$TEMP_DIR/$NAME-$VERSION/"

# Create LICENSE if it doesn't exist
if [ ! -f "LICENSE" ]; then
    echo "MIT License" > "$TEMP_DIR/$NAME-$VERSION/LICENSE"
fi
cp LICENSE "$TEMP_DIR/$NAME-$VERSION/" 2>/dev/null || echo "MIT License" > "$TEMP_DIR/$NAME-$VERSION/LICENSE"

# Create README if it doesn't exist
if [ ! -f "README.md" ]; then
    echo "# Sleep Tracker" > "$TEMP_DIR/$NAME-$VERSION/README.md"
fi
cp README.md "$TEMP_DIR/$NAME-$VERSION/" 2>/dev/null || echo "# Sleep Tracker" > "$TEMP_DIR/$NAME-$VERSION/README.md"

# Create tarball
cd "$TEMP_DIR"
tar czf "$NAME-$VERSION.tar.gz" "$NAME-$VERSION"
mv "$NAME-$VERSION.tar.gz" ~/rpmbuild/SOURCES/

# Copy spec file
cp "$SCRIPT_DIR/linux/sleep-tracker.spec" ~/rpmbuild/SPECS/

# Build RPM
echo -e "${YELLOW}Building RPM package...${NC}"
cd ~/rpmbuild/SPECS
rpmbuild -ba sleep-tracker.spec

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  RPM Build Complete!                                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Your RPM package is at:"
echo -e "  ${BLUE}~/rpmbuild/RPMS/noarch/$NAME-$VERSION-1.*.noarch.rpm${NC}"
echo ""
echo -e "To install:"
echo -e "  ${YELLOW}sudo dnf install ~/rpmbuild/RPMS/noarch/$NAME-$VERSION-1.*.noarch.rpm${NC}"
echo ""
echo -e "To share with others, upload the RPM file to GitHub Releases."
