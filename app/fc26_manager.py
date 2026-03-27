from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any

APP_HOME = Path.home() / ".local/share/fc26-clubos"
CONFIG_PATH = Path.home() / ".config/fc26-clubos/config.json"
RUNTIME = APP_HOME / "runtime"
DB_PATH = RUNTIME / "fc26_clubos.sqlite"
STATUS_PATH = RUNTIME / "status.json"
MANIFEST_PATH = RUNTIME / "fc26_image_manifest_v4.json"


def load_config() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {
        "csv_sources": [],
        "import_dir": str(APP_HOME / "imports"),
        "runtime_dir": str(RUNTIME),
        "images_dir": str(RUNTIME / "images"),
        "dashboard_dir": str(RUNTIME / "dashboard"),
        "status_json": str(STATUS_PATH),
        "sqlite_path": str(DB_PATH),
        "manifest_path": str(MANIFEST_PATH),
    }


def connect() -> sqlite3.Connection:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        create table if not exists snapshots (
            snapshot_id integer primary key autoincrement,
            source_name text,
            imported_at text default current_timestamp,
            player_count integer default 0
        );
        create table if not exists players (
            id integer primary key autoincrement,
            snapshot_id integer,
            definitionId text,
            item_id text,
            name text,
            rating integer,
            rarity text,
            team text,
            nation text,
            league text,
            role text,
            decision text,
            image_confidence text,
            image_url text,
            checksum text,
            reason text
        );
        create table if not exists resolver_queue (
            id integer primary key autoincrement,
            name text,
            rating integer,
            rarity text,
            reason text,
            confidence text,
            created_at text default current_timestamp
        );
        create table if not exists image_checksum_registry (
            checksum text primary key,
            path text,
            duplicate_count integer default 0,
            updated_at text default current_timestamp
        );
        """
    )
    return conn


def discover_csvs(cfg: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for src in cfg.get("csv_sources", []):
        p = Path(src).expanduser()
        if p.exists() and p.suffix.lower() == ".csv":
            paths.append(p)
    imp = Path(cfg.get("import_dir", APP_HOME / "imports")).expanduser()
    if imp.exists():
        for p in sorted(imp.glob("*.csv")):
            if p not in paths:
                paths.append(p)
    return paths


def normalize_row(row: dict[str, str], source: str) -> dict[str, Any]:
    def first(*keys: str) -> str:
        for k in keys:
            if k in row and row[k] not in (None, ""):
                return row[k]
        return ""

    name = first("Name", "Lastname")
    rating = first("Rating")
    rarity = first("Rarity")
    team = first("Team", "Club")
    nation = first("Nation", "Country")
    league = first("League")
    definition_id = first("DefinitionId")
    item_id = first("Id")

    return {
        "definitionId": definition_id,
        "item_id": item_id,
        "name": name,
        "rating": int(rating) if str(rating).isdigit() else None,
        "rarity": rarity,
        "team": team,
        "nation": nation,
        "league": league,
        "role": infer_role(row),
        "decision": infer_decision(row),
        "image_confidence": infer_confidence(definition_id, rarity, item_id),
        "image_url": "",
        "checksum": "",
        "reason": infer_reason(definition_id, rarity, item_id),
        "source": source,
    }


def infer_role(row: dict[str, str]) -> str:
    position = row.get("Preferred Position") or row.get("Position") or ""
    rating = int(row.get("Rating", 0) or 0)
    if rating >= 88:
        return f"Starter {position}".strip()
    if rating >= 84:
        return f"Bench {position}".strip()
    if rating >= 80:
        return f"Reserve {position}".strip()
    return "SBC Fodder"


def infer_decision(row: dict[str, str]) -> str:
    tradeable = row.get("Untradeable", "").lower()
    rating = int(row.get("Rating", 0) or 0)
    if "true" in tradeable or tradeable == "yes":
        return "Use"
    if rating >= 88:
        return "Keep"
    if rating <= 80:
        return "SBC"
    return "Use"


def infer_confidence(definition_id: str, rarity: str, item_id: str) -> str:
    if definition_id:
        return "high"
    if rarity and item_id:
        return "medium"
    return "low"


def infer_reason(definition_id: str, rarity: str, item_id: str) -> str:
    reasons = []
    if not definition_id:
        reasons.append("missing definitionId")
    if rarity.lower().startswith("rarity"):
        reasons.append("numeric rarity label")
    if item_id and item_id.isdigit() and int(item_id) < 1000:
        reasons.append("odd low id special")
    return ", ".join(reasons)


def refresh() -> None:
    cfg = load_config()
    csvs = discover_csvs(cfg)
    conn = connect()
    total = 0
    queue_total = 0
    manifest_items: list[dict[str, Any]] = []

    for csv_path in csvs:
        with csv_path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = [normalize_row(r, csv_path.name) for r in reader]
        cur = conn.execute("insert into snapshots(source_name, player_count) values (?, ?)", (csv_path.name, len(rows)))
        snapshot_id = cur.lastrowid
        for r in rows:
            conn.execute(
                "insert into players(snapshot_id, definitionId, item_id, name, rating, rarity, team, nation, league, role, decision, image_confidence, image_url, checksum, reason) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (snapshot_id, r["definitionId"], r["item_id"], r["name"], r["rating"], r["rarity"], r["team"], r["nation"], r["league"], r["role"], r["decision"], r["image_confidence"], r["image_url"], r["checksum"], r["reason"]),
            )
            total += 1
            manifest_items.append({k: r[k] for k in ["definitionId", "item_id", "name", "rating", "rarity", "team", "nation", "league", "image_confidence"]})
            if r["image_confidence"] != "high" or r["reason"]:
                conn.execute(
                    "insert into resolver_queue(name, rating, rarity, reason, confidence) values (?, ?, ?, ?, ?)",
                    (r["name"], r["rating"], r["rarity"], r["reason"] or "needs review", r["image_confidence"]),
                )
                queue_total += 1

    conn.commit()
    MANIFEST_PATH.write_text(json.dumps({"items": manifest_items}, indent=2))
    STATUS_PATH.write_text(json.dumps({"players_total": total, "queue_total": queue_total, "csv_sources": [p.name for p in csvs]}, indent=2))

    dashboard_dir = Path(cfg.get("dashboard_dir", RUNTIME / "dashboard"))
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    src_dashboard = Path(__file__).parent / "dashboard" / "index.html"
    if src_dashboard.exists():
        shutil.copy2(src_dashboard, dashboard_dir / "index.html")


def patch_waybar() -> None:
    src = Path.home() / ".config/waybar/config.jsonc"
    snippet = (Path(__file__).resolve().parents[1] / "waybar" / "fc26-clubos-module.jsonc")
    if not src.exists() or not snippet.exists():
        return
    backup = src.with_suffix(src.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(src, backup)
    text = src.read_text()
    inject = snippet.read_text().strip()
    if "custom/fc26-clubos" not in text:
        src.write_text(text.rstrip() + "\n\n" + inject + "\n")


def patch_hypr() -> None:
    src = Path.home() / ".config/hypr/hyprland.conf"
    snippet = (Path(__file__).resolve().parents[1] / "hypr" / "fc26-clubos.conf")
    if not src.exists() or not snippet.exists():
        return
    backup = src.with_suffix(src.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(src, backup)
    text = src.read_text()
    inject = snippet.read_text().strip()
    if "FC26 ClubOS" not in text:
        src.write_text(text.rstrip() + "\n\n" + inject + "\n")


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else "refresh"
    if action == "refresh":
        refresh()
    elif action == "patch-waybar":
        patch_waybar()
    elif action == "patch-hypr":
        patch_hypr()
    else:
        print(f"unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
