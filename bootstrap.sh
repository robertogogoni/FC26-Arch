#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_HOME="${HOME}/.local/share/fc26-clubos"
BIN_HOME="${HOME}/.local/bin"
STATE_HOME="${HOME}/.local/state/fc26-clubos"

mkdir -p "${APP_HOME}" "${BIN_HOME}" "${STATE_HOME}" "${APP_HOME}/app"

cp -f "${ROOT_DIR}/app/fc26_doctor.py" "${APP_HOME}/app/fc26_doctor.py"
chmod +x "${APP_HOME}/app/fc26_doctor.py"
python3 "${APP_HOME}/app/fc26_doctor.py" fix-deps || true
python3 "${APP_HOME}/app/fc26_doctor.py" preflight || true

python3 -m venv "${APP_HOME}/.venv"
source "${APP_HOME}/.venv/bin/activate"
python -m pip install --upgrade pip setuptools wheel
pip install -r "${ROOT_DIR}/requirements.txt"

mkdir -p "${APP_HOME}/app" "${APP_HOME}/runtime" "${APP_HOME}/imports" "${APP_HOME}/assets"
cp -r "${ROOT_DIR}/app"/* "${APP_HOME}/app/"
cp -r "${ROOT_DIR}/assets"/* "${APP_HOME}/assets/" 2>/dev/null || true

cd "${ROOT_DIR}"
export GO111MODULE=on
export GOPROXY="${GOPROXY:-https://proxy.golang.org,direct}"
python3 "${APP_HOME}/app/fc26_doctor.py" fix-go --root-dir "${ROOT_DIR}" || true
go mod download || true
go mod tidy || true
go build -o "${APP_HOME}/fc26-bootstrap" ./cmd/fc26-bootstrap

install -m 755 "${ROOT_DIR}/scripts/fc26-clubos" "${BIN_HOME}/fc26-clubos"
install -m 755 "${ROOT_DIR}/scripts/fc26-clubos-refresh" "${BIN_HOME}/fc26-clubos-refresh"
install -m 755 "${ROOT_DIR}/scripts/fc26-clubos-resolve" "${BIN_HOME}/fc26-clubos-resolve"
install -m 755 "${ROOT_DIR}/scripts/fc26-clubos-server" "${BIN_HOME}/fc26-clubos-server"
install -m 755 "${ROOT_DIR}/scripts/fc26-clubos-waybar" "${BIN_HOME}/fc26-clubos-waybar"
install -m 755 "${ROOT_DIR}/scripts/fc26-clubos-patch-desktop" "${BIN_HOME}/fc26-clubos-patch-desktop"
install -m 755 "${ROOT_DIR}/scripts/fc26-doctor" "${BIN_HOME}/fc26-doctor"

mkdir -p "${HOME}/.config/systemd/user"
cp "${ROOT_DIR}/systemd/fc26-clubos-refresh.service" "${HOME}/.config/systemd/user/"
cp "${ROOT_DIR}/systemd/fc26-clubos-refresh.timer" "${HOME}/.config/systemd/user/"
cp "${ROOT_DIR}/systemd/fc26-clubos-server.service" "${HOME}/.config/systemd/user/"

"${APP_HOME}/fc26-bootstrap"
fc26-clubos-patch-desktop || true
python3 "${APP_HOME}/app/fc26_doctor.py" fix-systemd || true
systemctl --user enable --now fc26-clubos-server.service || true
systemctl --user enable --now fc26-clubos-refresh.timer || true
fc26-clubos-refresh || true
python3 "${APP_HOME}/app/fc26_doctor.py" fix-db || true

echo "FC26 ClubOS v0.4.0 bootstrap completed"
