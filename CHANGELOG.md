# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-03-27

### Added

* `fc26-doctor` with preflight, dependency repair, Python repair, Go repair, systemd checks, desktop patch checks, and database maintenance flows
* Curl installer path in `installers/fc26-curl-installer.sh`
* SQLite checksum registry maintenance for persistent duplicate art cleanup across refreshes
* Resolver retry and backoff handling for public asset fetches
* Omarchy and Arch focused dependency bootstrap including `xdg-utils`, `git`, and `sqlite`
* Local server mode, CSV history browser, resolver queue, Waybar and Hyprland integration, and a local desktop web service layer from the previous packaging cycle, now documented as part of the repository baseline

### Changed

* Standardized repository versioning to semantic versioning
* Corrected package and documentation references from v3 to v4
* Improved bootstrap flow so dependency repair happens before the main install path
* Reframed the repository around source first publishing instead of a tarball first dump

### Fixed

* Packaging mismatch where the repository README still referenced the v3 package
* Missing explicit dependency coverage for common Omarchy and Arch desktop workflows
* Missing self-healing guidance for Go module, Python environment, and SQLite integrity issues
