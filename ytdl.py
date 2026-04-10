"""
ytdl.py — yt-dlp helpers: search, audio download, video download.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from typing import Optional

import yt_dlp

import config


# ── helpers ────────────────────────────────────────────────────────────────────

def _ydl_opts_base(extra: dict) -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "extractor_args": {
            "youtube": {
                "skip": ["dash", "hls"],
                "player_client": ["android", "ios"],
            }
        },
        "socket_timeout": 30,
        "nocheckcertificate": True,
        **extra,
    }
    # Load cookies if the user has provided a cookies.txt in the root
    if os.path.exists("cookies.txt"):
        opts["cookiefile"] = "cookies.txt"
    return opts


# ── search ─────────────────────────────────────────────────────────────────────

async def search_youtube(query: str, max_results: int = 5) -> list[dict]:
    """
    Return a list of dicts with keys: title, url, duration, thumbnail.
    Runs in a thread so it doesn't block the event loop.
    """
    def _search():
        opts = _ydl_opts_base({
            "extract_flat": "in_playlist",
            "default_search": f"ytsearch{max_results}",
        })
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(query, download=False)
            entries = info.get("entries", [])
            results = []
            for e in entries:
                results.append({
                    "title": e.get("title", "Unknown"),
                    "url": e.get("url") or e.get("webpage_url", ""),
                    "duration": e.get("duration") or 0,
                    "thumbnail": e.get("thumbnail") or e.get("thumbnails", [{}])[-1].get("url", ""),
                })
            return results

    return await asyncio.to_thread(_search)


# ── URL info ───────────────────────────────────────────────────────────────────

async def get_info(url: str) -> Optional[dict]:
    """Fetch metadata for a single URL (no download)."""
    def _info():
        opts = _ydl_opts_base({"noplaylist": False})
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    return await asyncio.to_thread(_info)


async def get_playlist_entries(url: str, limit: int) -> list[dict]:
    """
    Expand a playlist URL and return up to *limit* entries.
    Each entry has: title, url, duration, thumbnail.
    """
    def _pl():
        opts = _ydl_opts_base({
            "extract_flat": "in_playlist",
            "noplaylist": False,
            "playlistend": limit,
        })
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get("entries", [])
            results = []
            for e in entries:
                if not e:
                    continue
                results.append({
                    "title": e.get("title", "Unknown"),
                    "url": e.get("url") or e.get("webpage_url", ""),
                    "duration": e.get("duration") or 0,
                    "thumbnail": (e.get("thumbnail") or
                                  (e.get("thumbnails") or [{}])[-1].get("url", "")),
                })
            return results

    return await asyncio.to_thread(_pl)


# ── download ───────────────────────────────────────────────────────────────────

async def download_audio(url: str) -> tuple[str, dict]:
    """
    Download best audio as opus/m4a, returning (file_path, info_dict).
    """
    uid = uuid.uuid4().hex
    tmpl = os.path.join(config.DOWNLOAD_DIR, f"{uid}.%(ext)s")

    def _dl():
        opts = _ydl_opts_base({
            "format": "bestaudio/best",
            "outtmpl": tmpl,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "opus",
                "preferredquality": "128",
            }],
            "noplaylist": True,
        })
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info

    info = await asyncio.to_thread(_dl)
    # Find the actual file on disk (ext might vary)
    base = os.path.join(config.DOWNLOAD_DIR, uid)
    for ext in ("opus", "m4a", "webm", "mp3", "ogg"):
        path = f"{base}.{ext}"
        if os.path.exists(path):
            return path, info

    raise FileNotFoundError(f"Audio download succeeded but file not found for {url}")


async def download_video(url: str) -> tuple[str, dict]:
    """
    Download best video up to 480p as mp4, returning (file_path, info_dict).
    """
    uid = uuid.uuid4().hex
    tmpl = os.path.join(config.DOWNLOAD_DIR, f"{uid}.%(ext)s")

    def _dl():
        opts = _ydl_opts_base({
            # Prefer 480p or lower, fall back to best
            "format": "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
            "outtmpl": tmpl,
            "merge_output_format": "mp4",
            "noplaylist": True,
        })
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info

    info = await asyncio.to_thread(_dl)
    base = os.path.join(config.DOWNLOAD_DIR, uid)
    for ext in ("mp4", "mkv", "webm"):
        path = f"{base}.{ext}"
        if os.path.exists(path):
            return path, info

    raise FileNotFoundError(f"Video download succeeded but file not found for {url}")


# ── utility ────────────────────────────────────────────────────────────────────

def fmt_duration(seconds: int) -> str:
    if not seconds:
        return "Live"
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def is_url(text: str) -> bool:
    return text.startswith("http://") or text.startswith("https://")
