# FC26 Arch

A Linux desktop pack for FC26 club management on Arch and Omarchy, built around a local dashboard, image resolver pipeline, SQLite backbone, Go plus Charm onboarding, and a self-healing CLI.

## What this repo is

FC26 Arch turns a raw FC26 club export into a desktop workflow you can actually run daily.

It includes:

* a local dashboard and web service layer
* a consolidated SQLite database
* a resolver pipeline for card art and local image packs
* CSV history tracking and resolver queue plumbing
* Omarchy oriented Waybar and Hyprland integration
* a Go plus Charm first run wizard
* a `fc26-doctor` maintenance and repair command

## Release

Current version: `0.4.0`

Current tag target: `v0.4.0`

See [CHANGELOG.md](CHANGELOG.md) for release history and [docs/RELEASE.md](docs/RELEASE.md) for release notes.

## Repository layout

```text
app/
assets/
cmd/
docs/
hypr/
installers/
samples/
scripts/
systemd/
waybar/
bootstrap.sh
go.mod
requirements.txt
VERSION
CHANGELOG.md
```

## Core components

### App layer

* `app/fc26_manager.py`: ingestion, database refresh, snapshot history, duplicate logic, desktop patch orchestration
* `app/fc26_resolver_utility.py`: asset resolution, retries, local image pack building, manifest upgrade flows
* `app/fc26_server.py`: local web server and API layer
* `app/fc26_doctor.py`: preflight and auto repair command set

### Bootstrap layer

* `cmd/fc26-bootstrap/main.go`: Go plus Charm first run wizard
* `bootstrap.sh`: one-shot installer for Omarchy and Arch style setups
* `installers/fc26-curl-installer.sh`: curl driven install entrypoint for hosted installs

### Desktop integration

* `scripts/fc26-clubos`: launcher
* `scripts/fc26-clubos-refresh`: refresh pipeline entrypoint
* `scripts/fc26-clubos-resolve`: resolver entrypoint
* `scripts/fc26-clubos-server`: local server entrypoint
* `scripts/fc26-clubos-waybar`: Waybar status JSON producer
* `scripts/fc26-clubos-patch-desktop`: Waybar and Hyprland patch helper
* `scripts/fc26-doctor`: repair and diagnostics entrypoint

## Features

### Data pipeline

* continuous CSV ingestion from configured paths and import folders
* CSV snapshot history stored in SQLite
* consolidated player records across club and SBC exports
* persistent checksum registry for duplicate art cleanup

### Resolver pipeline

* FUT.GG first public provider strategy
* resolver queue for suspicious or incomplete matches
* confidence downgrade rules for collisions and risky variants
* local offline image pack mode after resolution

### Desktop workflow

* local server on `127.0.0.1:43826`
* systemd user services and timer
* Waybar friendly status output
* Hyprland and Omarchy aware patching with backups

### Maintenance

* dependency repair for Arch and Omarchy style systems
* Python environment repair
* Go module repair
* systemd user diagnostics
* SQLite maintenance and integrity checks

## Install

### Direct bootstrap

```bash
git clone https://github.com/robertogogoni/FC26-Arch.git
cd FC26-Arch
./bootstrap.sh
```

### Curl installer

The installer is included in `installers/`, ready to be hosted from this repository or a release asset.

Expected usage pattern after hosting:

```bash
export FC26_PACKAGE_URL="https://your-host/fc26_linux_desktop_pack_v4.tar.gz"
curl -fsSL https://your-host/fc26-curl-installer.sh | bash
```

## Main commands

```bash
fc26-clubos
fc26-clubos-refresh
fc26-clubos-resolve
fc26-clubos-server
fc26-clubos-waybar
fc26-doctor preflight
fc26-doctor fix-all
```

## Local paths

* app home: `~/.local/share/fc26-clubos`
* runtime: `~/.local/share/fc26-clubos/runtime`
* database: `~/.local/share/fc26-clubos/runtime/fc26_clubos.sqlite`
* imports: `~/.local/share/fc26-clubos/imports`
* images: `~/.local/share/fc26-clubos/runtime/images`
* config: `~/.config/fc26-clubos/config.json`
* logs: `~/.local/state/fc26-clubos`

## First run flow

On first run, the Go plus Charm wizard collects:

* club CSV path
* SBC CSV path
* browser launcher command
* refresh interval
* Waybar patch preference
* Hyprland patch preference

It then writes config automatically and hands off to the Python and systemd layers.

## Omarchy fit

This repository is tuned for:

* Arch based package installation
* Hyprland config patching with backups
* Waybar custom module insertion
* user space install layout under XDG friendly paths

## Current caveats

* Public card art resolution still depends on provider availability
* `go.sum` is not committed yet, so bootstrap still repairs the Go dependency graph at install time
* Release assets and hosted curl endpoints still need to be published from GitHub Releases or another host

## Next recommended release work

* commit `go.sum` after a local `go mod tidy` run on a networked machine
* publish `v0.4.0` as the first repository tag
* attach the packaged archive and curl installer to the GitHub Release
