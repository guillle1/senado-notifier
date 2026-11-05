#!/usr/bin/env python3
"""Avisa por Telegram cuando @SenadoTVArgentina empieza una transmisión en vivo.

Uso:
    python senado_live_notifier.py            # una revisión (para cron / Task Scheduler)
    python senado_live_notifier.py --loop     # revisa cada CHECK_INTERVAL segundos
    python senado_live_notifier.py --test     # manda un mensaje de prueba a Telegram

Variables de entorno (o archivo .env junto al script):
    YOUTUBE_API_KEY      clave de YouTube Data API v3
    TELEGRAM_BOT_TOKEN   token del bot (de @BotFather)
    TELEGRAM_CHAT_ID     id del chat/grupo/canal destino
    CHECK_INTERVAL       segundos entre revisiones en modo --loop (por defecto 120)
"""
import argparse
import html
import json
import os
import sys
import time
from pathlib import Path

import requests

HANDLE = "SenadoTVArgentina"
YT_API = "https://www.googleapis.com/youtube/v3"
BASE = Path(__file__).resolve().parent
STATE_FILE = BASE / "state.json"


def load_env():
    env_file = BASE / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def need(name):
    value = os.environ.get(name)
    if not value:
        sys.exit(f"Falta la variable {name}. Revisá el archivo .env")
    return value


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"uploads_playlist": None, "notified": []}


def save_state(state):
    state["notified"] = state["notified"][-100:]
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def yt_get(endpoint, key, **params):
    params["key"] = key
    r = requests.get(f"{YT_API}/{endpoint}", params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def uploads_playlist(state, key):
    """Resuelve (y cachea) la playlist de 'uploads' del canal. Cuesta 1 unidad de cuota una sola vez."""
    if not state.get("uploads_playlist"):
        data = yt_get("channels", key, part="contentDetails", forHandle=f"@{HANDLE}")
        items = data.get("items")
        if not items:
            sys.exit(f"No se encontró el canal @{HANDLE}")
        state["uploads_playlist"] = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        save_state(state)
    return state["uploads_playlist"]


def current_lives(state, key):
    """Devuelve los videos que están en vivo ahora. Cuesta 2 unidades por revisión."""
    playlist = uploads_playlist(state, key)
    items = yt_get(
        "playlistItems", key, part="contentDetails", playlistId=playlist, maxResults=10
    ).get("items", [])
    ids = [i["contentDetails"]["videoId"] for i in items]
    if not ids:
        return []
    videos = yt_get("videos", key, part="snippet,liveStreamingDetails", id=",".join(ids))
    return [v for v in videos.get("items", []) if v["snippet"].get("liveBroadcastContent") == "live"]


def telegram_send(token, chat_id, text):
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=20,
    )
    r.raise_for_status()


def check_once():
    key = need("YOUTUBE_API_KEY")
    token = need("TELEGRAM_BOT_TOKEN")
    chat_id = need("TELEGRAM_CHAT_ID")
    state = load_state()

    for v in current_lives(state, key):
        vid = v["id"]
        if vid in state["notified"]:
            continue
        title = html.escape(v["snippet"]["title"])
        url = f"https://www.youtube.com/watch?v={vid}"
        telegram_send(token, chat_id, f"🔴 <b>Senado TV está en vivo</b>\n{title}\n{url}")
        state["notified"].append(vid)
        save_state(state)
        print(f"Notificado: {vid} - {v['snippet']['title']}")


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()

    if args.test:
        telegram_send(need("TELEGRAM_BOT_TOKEN"), need("TELEGRAM_CHAT_ID"),
                      "✅ Prueba: el notificador de Senado TV funciona.")
        print("Mensaje de prueba enviado.")
        return

    if not args.loop:
        check_once()
        return

    interval = int(os.environ.get("CHECK_INTERVAL", "120"))
    while True:
        try:
            check_once()
        except Exception as e:  # no cortar el loop por un error de red
            print(f"Error: {e}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    main()
