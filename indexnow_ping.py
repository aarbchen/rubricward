"""
indexnow_ping.py — Automated IndexNow Instant Search Engine Submission for RubricWard (https://rubricward.com)

Reads all live URLs from D:\\RubricWard\\sitemap.xml and submits them in a single
batch POST to https://api.indexnow.org/indexnow so Bing, Microsoft Copilot,
DuckDuckGo, Yandex, ChatGPT Search, and Perplexity index all RubricWard pages
(index.html, apis.html, /lettings/index.html, and /lettings/project/<slug>.html)
immediately.
"""

from __future__ import annotations

import os
import re
import requests
from dotenv import load_dotenv
from error_telemetry import configure_utf8_stdio

configure_utf8_stdio()
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITEMAP_PATH = os.path.join(BASE_DIR, "sitemap.xml")

INDEXNOW_HOST = "rubricward.com"
INDEXNOW_KEY = os.getenv("RUBRICWARD_INDEXNOW_KEY", "a4f8e2c91b7d3056e8a12f4c9d0b3e71").strip()
INDEXNOW_KEY_LOCATION = f"https://{INDEXNOW_HOST}/{INDEXNOW_KEY}.txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"


def extract_sitemap_urls(sitemap_path: str = SITEMAP_PATH) -> list[str]:
    if not os.path.exists(sitemap_path):
        return []
    with open(sitemap_path, "r", encoding="utf-8") as f:
        xml_txt = f.read()
    urls = [u.strip() for u in re.findall(r"<loc>(.*?)</loc>", xml_txt, flags=re.I) if u.strip()]
    seen: set[str] = set()
    ordered: list[str] = []
    for url in urls:
        if url not in seen and url.startswith(f"https://{INDEXNOW_HOST}"):
            seen.add(url)
            ordered.append(url)
    return ordered


def submit_indexnow_urls(urls: list[str] | None = None) -> dict:
    """
    Submits all URLs from sitemap.xml to https://api.indexnow.org/indexnow
    using keyLocation https://rubricward.com/<key>.txt.
    Never raises so pipeline runs are never blocked.
    """
    for p in (
        os.path.join(BASE_DIR, f"{INDEXNOW_KEY}.txt"),
        os.path.join(BASE_DIR, "lettings", f"{INDEXNOW_KEY}.txt"),
    ):
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as kf:
                kf.write(INDEXNOW_KEY)
        except Exception:
            pass

    target_urls = urls if urls is not None else extract_sitemap_urls()
    if not target_urls:
        print("[RubricWard IndexNow] No URLs found in sitemap.xml to submit.", flush=True)
        return {"submitted": 0, "status_code": 0}

    payload = {
        "host": INDEXNOW_HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": INDEXNOW_KEY_LOCATION,
        "urlList": target_urls[:10000],
    }

    try:
        resp = requests.post(
            INDEXNOW_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=12,
        )
        status = resp.status_code
        if status in (200, 202):
            print(
                f"[RubricWard IndexNow] [+] Submitted {len(target_urls)} live RubricWard URLs to IndexNow (HTTP {status}).",
                flush=True,
            )
        else:
            print(
                f"[RubricWard IndexNow] [!] IndexNow returned HTTP {status}: {resp.text[:160]}",
                flush=True,
            )
        return {"submitted": len(target_urls), "status_code": status}
    except Exception as exc:
        print(f"[RubricWard IndexNow] [!] Non-blocking IndexNow ping warning: {exc}", flush=True)
        return {"submitted": 0, "status_code": 0, "error": str(exc)}


if __name__ == "__main__":
    submit_indexnow_urls()
