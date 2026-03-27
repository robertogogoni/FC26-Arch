#!/usr/bin/env bash
set -euo pipefail

REPO_OWNER="robertogogoni"
REPO_NAME="FC26-Arch"
REF="${FC26_REF:-main}"
INSTALL_DIR="${FC26_INSTALL_DIR:-$HOME/Downloads/FC26-Arch}"
PACKAGE_URL="https://codeload.github.com/${REPO_OWNER}/${REPO_NAME}/tar.gz/refs/heads/${REF}"

mkdir -p "$INSTALL_DIR"
TMP_ARCHIVE="$(mktemp /tmp/fc26_arch_XXXXXX.tar.gz)"

curl -fL "$PACKAGE_URL" -o "$TMP_ARCHIVE"
tar -xzf "$TMP_ARCHIVE" -C "$INSTALL_DIR" --strip-components=1
cd "$INSTALL_DIR"
chmod +x bootstrap.sh
./bootstrap.sh
