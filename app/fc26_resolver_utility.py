from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

APP_HOME = Path.home() / ".local/share/fc26-clubos"
RUNTIME = APP_HOME / "runtime"
MANIFEST_PATH = RUNTIME / "fc26_image_manifest_v4.json"
LOCAL_IMAGES = RUNTIME / "images"

HEADERS = {"User-Agent": "Mozilla/5.0 FC26-ClubOS"}


def load_manifest() -> dict[str, Any]:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {"items": []}


def save_manifest(data: dict[str, Any]) -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(data, indent=2))


def candidate_asset_page(item: dict[str, Any]) -> str:
    base = item.get("definitionId") or item.get("item_id") or "unknown"
    name = (item.get("name") or "player").lower().replace(" ", "-")
    return f"https://www.fut.gg/players/{base}-{name}/assets/"


def fetch_with_retry(url: str, timeout: int = 20, retries: int = 3) -> requests.Response | None:
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code in (403, 429, 500, 502, 503, 504):
                time.sleep(1.5 * (attempt + 1))
                continue
            return r
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None


def upgrade_direct() -> None:
    data = load_manifest()
    for item in data.get("items", []):
        if item.get("image_url"):
            continue
        page = candidate_asset_page(item)
        item["asset_page_url"] = page
        resp = fetch_with_retry(page)
        if not resp or not resp.ok:
            item["confidence"] = item.get("image_confidence", "low")
            continue
        soup = BeautifulSoup(resp.text, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            item["image_url"] = img.get("src")
            item["confidence"] = "high" if item.get("definitionId") else "medium"
        else:
            item["confidence"] = item.get("image_confidence", "low")
    save_manifest(data)
    print("Manifest upgraded")


def build_local_pack() -> None:
    data = load_manifest()
    LOCAL_IMAGES.mkdir(parents=True, exist_ok=True)
    for item in data.get("items", []):
        url = item.get("image_url")
        if not url:
            continue
        resp = fetch_with_retry(url)
        if not resp or not resp.ok:
            continue
        digest = hashlib.sha256(resp.content).hexdigest()[:16]
        name = f"{digest}.img"
        path = LOCAL_IMAGES / name
        path.write_bytes(resp.content)
        item["local_path"] = str(path)
        item["checksum"] = digest
    save_manifest(data)
    print("Local image pack built")


def main() -> None:
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "upgrade-direct"
    if action == "upgrade-direct":
        upgrade_direct()
    elif action == "build-local-pack":
        build_local_pack()
    else:
        raise SystemExit(f"Unknown action: {action}")


if __name__ == "__main__":
    main()
