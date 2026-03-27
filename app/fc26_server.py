from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

APP_HOME = Path.home() / ".local/share/fc26-clubos"
RUNTIME = APP_HOME / "runtime"
DB_PATH = RUNTIME / "fc26_clubos.sqlite"
STATUS = RUNTIME / "status.json"
MANIFEST = RUNTIME / "fc26_image_manifest_v4.json"
DASHBOARD_DIR = RUNTIME / "dashboard"

app = Flask(__name__, static_folder=str(DASHBOARD_DIR), static_url_path="")


def rows(query: str, params: tuple = ()):
    if not DB_PATH.exists():
        return []
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute(query, params).fetchall()]


@app.get("/")
def root():
    return send_from_directory(DASHBOARD_DIR, "index.html")


@app.get("/api/summary")
def summary():
    if STATUS.exists():
        return jsonify(json.loads(STATUS.read_text()))
    return jsonify({})


@app.get("/api/players")
def players():
    q = request.args.get("q", "").strip()
    if q:
        like = f"%{q}%"
        data = rows("select * from players where name like ? or team like ? or rarity like ? order by rating desc", (like, like, like))
    else:
        data = rows("select * from players order by rating desc limit 500")
    return jsonify({"players": data})


@app.get("/api/history")
def history():
    return jsonify({"history": rows("select * from snapshots order by snapshot_id desc")})


@app.get("/api/history/<int:snapshot_id>/players")
def history_players(snapshot_id: int):
    return jsonify({"players": rows("select * from players where snapshot_id = ? order by rating desc limit 250", (snapshot_id,))})


@app.get("/api/resolver-queue")
def resolver_queue():
    return jsonify({"queue": rows("select * from resolver_queue order by id desc limit 250")})


@app.get("/api/manifest")
def manifest():
    if MANIFEST.exists():
        return jsonify(json.loads(MANIFEST.read_text()))
    return jsonify({"items": []})


@app.post("/api/refresh")
def refresh():
    from app import fc26_manager
    fc26_manager.refresh()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=43826, debug=False)
