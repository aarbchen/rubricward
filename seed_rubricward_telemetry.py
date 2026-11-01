r"""
RubricWard 12-API Telemetry & Green-Badge Seeder (D:\RubricWard\seed_rubricward_telemetry.py)
Warms and verifies all 12 production RubricWard microservices across both:
  1. The RubricWard FastAPI Gateway (using RAPIDAPI_PROXY_SECRET from D:\RubricWard\.env)
  2. All 12 RapidAPI Marketplace Proxy Hosts (using RAPIDAPI_KEY from D:\RubricWard\.env),
     recording HTTP 200 OK responses and low-latency telemetry to maintain RapidAPI's
     green 100% Service Level badges across all 12 storefronts.
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List
import requests
from dotenv import load_dotenv

from generate_rapidapi_kit import RUBRICWARD_RAPIDAPI_CATALOG

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=str(ROOT_DIR / ".env"))

BASE_URL = os.getenv(
    "RUBRICWARD_API_BASE_URL",
    "https://api.rubricward.com",
).rstrip("/")
PROXY_SECRET = (os.getenv("RAPIDAPI_PROXY_SECRET") or "").split(",")[0].strip()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


def build_endpoints() -> List[Dict[str, Any]]:
    published_map: Dict[str, str] = {}
    pub_file = ROOT_DIR / "rapidapi_published_catalog.json"
    if pub_file.exists():
        try:
            for item in json.loads(pub_file.read_text(encoding="utf-8")):
                published_map[str(item.get("num"))] = item.get("rapid_host", "")
        except Exception:
            pass

    endpoints: List[Dict[str, Any]] = []
    for api in RUBRICWARD_RAPIDAPI_CATALOG:
        num = api["num"]
        rapid_host = published_map.get(num) or api.get("rapid_host", f"{api['slug']}.p.rapidapi.com")
        endpoints.append({
            "id": f"API {num}",
            "name": api["title"],
            "method": api["method"],
            "path": api["route"],
            "rapid_host": rapid_host,
            "payload": api["sample_request"] if api["method"] == "POST" else None,
            "params": api["sample_request"] if api["method"] == "GET" else None,
        })
    return endpoints


def run_telemetry_seeder(use_rapidapi_proxy: bool = True) -> Dict[str, Any]:
    endpoints = build_endpoints()
    results = {"direct_200": 0, "rapidapi_200": 0, "total": len(endpoints)}

    for ep in endpoints:
        url = f"{BASE_URL}{ep['path']}"
        headers = {"Content-Type": "application/json"}
        if PROXY_SECRET:
            headers["X-RapidAPI-Proxy-Secret"] = PROXY_SECRET
        try:
            if ep["method"] == "GET":
                resp = requests.get(url, params=ep["params"], headers=headers, timeout=25)
            else:
                resp = requests.post(url, json=ep["payload"], headers=headers, timeout=25)
            if resp.status_code == 200:
                results["direct_200"] += 1
            print(f"[DIRECT] {ep['id']} {ep['path']} -> HTTP {resp.status_code}")
        except Exception as exc:
            print(f"[DIRECT-ERR] {ep['id']} {ep['path']} -> {exc}")

        if use_rapidapi_proxy and RAPIDAPI_KEY:
            r_url = f"https://{ep['rapid_host']}{ep['path']}"
            r_headers = {
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": ep["rapid_host"],
                "Content-Type": "application/json",
            }
            try:
                if ep["method"] == "GET":
                    r_resp = requests.get(r_url, params=ep["params"], headers=r_headers, timeout=25)
                else:
                    r_resp = requests.post(r_url, json=ep["payload"], headers=r_headers, timeout=25)
                if r_resp.status_code == 200:
                    results["rapidapi_200"] += 1
                    print(f"[RAPIDAPI] {ep['id']} {ep['rapid_host']} -> HTTP {r_resp.status_code}")
                else:
                    print(f"[RAPIDAPI] {ep['id']} {ep['rapid_host']} -> HTTP {r_resp.status_code} ({r_resp.text[:140]})")
            except Exception as exc:
                print(f"[RAPIDAPI-ERR] {ep['id']} {ep['rapid_host']} -> {exc}")
            time.sleep(0.4)

    return results


if __name__ == "__main__":
    summary = run_telemetry_seeder()
    print(f"[RUBRICWARD TELEMETRY] Summary: {summary}")

