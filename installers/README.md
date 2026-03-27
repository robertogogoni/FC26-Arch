# Curl installer

This installer expects a hosted tar.gz URL.

Usage:

```bash
export FC26_PACKAGE_URL="https://your-host/fc26_linux_desktop_pack_v4.tar.gz"
curl -fsSL https://your-host/fc26-curl-installer.sh | bash
```

It downloads the archive, extracts it into `FC26_INSTALL_DIR` or `~/Downloads/fc26_linux_desktop_pack_v4`, and runs `bootstrap.sh`.
