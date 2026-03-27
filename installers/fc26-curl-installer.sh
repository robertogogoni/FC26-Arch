#!/usr/bin/env bash
set -euo pipefail

PACKAGE_URL="${FC26_PACKAGE_URL:-}"
INSTALL_DIR="${FC26_INSTALL_DIR:-$HOME/Downloads/fc26_linux_desktop_pack_v4}"
ARCHIVE_NAME="fc26_linux_desktop_pack_v4.tar.gz"

if [ -z "$PACKAGE_URL" ]; then
  cat <<'EOF'
Set FC26_PACKAGE_URL to the tar.gz location before running this installer.
Example:
  export FC26_PACKAGE_URL="https://example.com/fc26_linux_desktop_pack_v4.tar.gz"
  curl -fsSL https://example.com/fc26-curl-installer.sh | bash
EOF
  exit 1
fi

mkdir -p "$INSTALL_DIR"
TMP_ARCHIVE="$(mktemp /tmp/fc26_v4_XXXXXX.tar.gz)"

curl -fL "$PACKAGE_URL" -o "$TMP_ARCHIVE"
tar -xzf "$TMP_ARCHIVE" -C "$INSTALL_DIR" --strip-components=1
cd "$INSTALL_DIR"
chmod +x bootstrap.sh
./bootstrap.sh

echo "FC26 ClubOS v4 installed from curl workflow"
