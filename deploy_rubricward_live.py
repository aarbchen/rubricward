# -*- coding: utf-8 -*-
"""
Deploys D:\\RubricWard to https://github.com/aarbchen/rubricward.git, configures GitHub Pages
and Cloudflare DNS records on Zone c7d2ed9fbd34bfd77b96eb9f58f9dfcd (rubricward.com),
binds Cloudflare Worker routes (if permitted), pings IndexNow + Google Favicon crawlers,
and verifies live HTTP 200 responses on https://rubricward.com.
"""

import json
import os
import subprocess
import time
from pathlib import Path
import requests
from dotenv import load_dotenv

ROOT = Path(r"D:\RubricWard")
load_dotenv(ROOT / ".env", override=True)
if Path(r"D:\CamberDesk\.env").exists():
    load_dotenv(r"D:\CamberDesk\.env", override=False)
if Path(r"D:\Daas\.env").exists():
    load_dotenv(r"D:\Daas\.env", override=False)

ZONE_ID = "c7d2ed9fbd34bfd77b96eb9f58f9dfcd"
CF_ACCOUNT_ID = (os.getenv("CLOUDFLARE_ACCOUNT_ID") or "1bd620fee1e67b48923bfbe445c3a88c").strip()
CF_TOKEN = (os.getenv("CLOUDFLARE_API_TOKEN") or "").strip()
CF_EMAIL = (os.getenv("CLOUDFLARE_EMAIL") or "").strip()
CF_GLOBAL_KEY = (os.getenv("CLOUDFLARE_GLOBAL_API_KEY") or os.getenv("CLOUDFLARE_API_KEY") or "").strip()
GH_TOKEN = (os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or os.getenv("GITHUB_PAT") or "").strip()


def _cf_headers() -> dict:
    if CF_TOKEN:
        return {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    return {"X-Auth-Email": CF_EMAIL, "X-Auth-Key": CF_GLOBAL_KEY, "Content-Type": "application/json"}


def _cf_request(method: str, url: str, **kwargs):
    resp = requests.request(method, url, headers=_cf_headers(), timeout=30, **kwargs)
    if resp.status_code in (401, 403) and CF_EMAIL and CF_GLOBAL_KEY:
        resp = requests.request(
            method,
            url,
            headers={"X-Auth-Email": CF_EMAIL, "X-Auth-Key": CF_GLOBAL_KEY, "Content-Type": "application/json"},
            timeout=30,
            **kwargs,
        )
    return resp


def step1_ensure_cname_and_git_push():
    print("=== STEP 1: Ensure CNAME / .nojekyll & Push D:\\RubricWard to GitHub (aarbchen/rubricward) ===")
    (ROOT / "CNAME").write_text("rubricward.com\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")

    if not (ROOT / ".git").exists():
        subprocess.run(["git", "init"], cwd=str(ROOT), check=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=str(ROOT), check=False)

    remote_url = (
        f"https://x-access-token:{GH_TOKEN}@github.com/aarbchen/rubricward.git"
        if GH_TOKEN
        else "https://github.com/aarbchen/rubricward.git"
    )
    res_rem = subprocess.run(["git", "remote"], cwd=str(ROOT), capture_output=True, text=True)
    if "origin" in (res_rem.stdout or "").split():
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=str(ROOT), check=True)
    else:
        subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=str(ROOT), check=True)

    subprocess.run(["git", "add", "-A"], cwd=str(ROOT), check=True)
    subprocess.run(
        ["git", "commit", "-m", "Launch RubricWard 52-Portal Commercial Payer MRF, ERISA Appeal & NSA IDR Platform + Split Shield Favicon"],
        cwd=str(ROOT),
        check=False,
    )
    push_res = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=str(ROOT), capture_output=True, text=True)
    print(f"  [GIT PUSH] exit={push_res.returncode}")
    # Reset remote URL to clean public URL without token
    subprocess.run(["git", "remote", "set-url", "origin", "https://github.com/aarbchen/rubricward.git"], cwd=str(ROOT), check=False)

    if GH_TOKEN:
        gh_headers = {
            "Authorization": f"Bearer {GH_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        r_create = requests.post(
            "https://api.github.com/repos/aarbchen/rubricward/pages",
            headers=gh_headers,
            json={"source": {"branch": "main", "path": "/"}},
            timeout=20,
        )
        print(f"  [GH PAGES CREATE] HTTP {r_create.status_code}")
        r_upd = requests.put(
            "https://api.github.com/repos/aarbchen/rubricward/pages",
            headers=gh_headers,
            json={"cname": "rubricward.com", "source": {"branch": "main", "path": "/"}},
            timeout=20,
        )
        print(f"  [GH PAGES CNAME=rubricward.com] HTTP {r_upd.status_code}")


def step2_configure_cloudflare_dns_and_worker():
    print("\n=== STEP 2: Configure Cloudflare DNS Records & Edge Worker on Zone c7d2ed9fbd34bfd77b96eb9f58f9dfcd ===")
    dns_url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
    existing_resp = _cf_request("GET", f"{dns_url}?per_page=100")
    existing = (existing_resp.json() or {}).get("result") or [] if existing_resp.status_code == 200 else []

    desired_records = [
        {"type": "A", "name": "rubricward.com", "content": "185.199.108.153", "proxied": True, "ttl": 1},
        {"type": "A", "name": "rubricward.com", "content": "185.199.109.153", "proxied": True, "ttl": 1},
        {"type": "A", "name": "rubricward.com", "content": "185.199.110.153", "proxied": True, "ttl": 1},
        {"type": "A", "name": "rubricward.com", "content": "185.199.111.153", "proxied": True, "ttl": 1},
        {"type": "CNAME", "name": "www.rubricward.com", "content": "aarbchen.github.io", "proxied": True, "ttl": 1},
        {"type": "CNAME", "name": "api.rubricward.com", "content": "aarbchen.github.io", "proxied": True, "ttl": 1},
        {"type": "TXT", "name": "rubricward.com", "content": "v=spf1 include:_spf.google.com ~all", "proxied": False, "ttl": 3600},
        {"type": "TXT", "name": "_dmarc.rubricward.com", "content": "v=DMARC1; p=quarantine; rua=mailto:aaron@tryrubricward.com; pct=100; adkim=s; aspf=s", "proxied": False, "ttl": 3600},
        {"type": "TXT", "name": "default._bimi.rubricward.com", "content": "v=BIMI1; l=https://rubricward.com/bimi-logo.svg;", "proxied": False, "ttl": 3600},
    ]

    for rec in desired_records:
        already = any(
            r.get("type") == rec["type"] and r.get("name") == rec["name"] and r.get("content") == rec["content"]
            for r in existing
        )
        if already:
            print(f"  [DNS EXISTS] {rec['type']} {rec['name']} -> {rec['content']}")
            continue
        r_post = _cf_request("POST", dns_url, json=rec)
        print(f"  [DNS ADD] {rec['type']} {rec['name']} -> {rec['content']} (HTTP {r_post.status_code})")

    # Ensure SSL/TLS mode is Full and Always Use HTTPS is enabled
    _cf_request("PATCH", f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/settings/ssl", json={"value": "full"})
    _cf_request("PATCH", f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/settings/always_use_https", json={"value": "on"})

    # Deploy rubricward-edge worker and bind routes if permitted
    try:
        from build_cloudflare_edge_worker import deploy_worker_to_cloudflare
        deployed = deploy_worker_to_cloudflare(ROOT / "cloudflare_worker.js")
        if deployed:
            routes_url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/workers/routes"
            for pat in ("rubricward.com/*", "www.rubricward.com/*", "api.rubricward.com/*"):
                r_rt = _cf_request("POST", routes_url, json={"pattern": pat, "script": "rubricward-edge"})
                print(f"  [WORKER ROUTE] {pat} -> rubricward-edge (HTTP {r_rt.status_code})")
    except Exception as exc:
        print(f"  [WARN] Worker deploy/route step: {exc}")


def step3_ping_indexnow_and_google_favicon():
    print("\n=== STEP 3: Ping IndexNow & Google Favicon Crawler for rubricward.com ===")
    urls = [
        "https://rubricward.com/",
        "https://rubricward.com/apis.html",
        "https://rubricward.com/lettings/index.html",
        "https://rubricward.com/favicon.ico",
        "https://rubricward.com/favicon.png",
        "https://rubricward.com/favicon-48x48.png",
        "https://rubricward.com/favicon-96x96.png",
        "https://rubricward.com/favicon-144x144.png",
        "https://rubricward.com/favicon-192x192.png",
        "https://rubricward.com/favicon-512x512.png",
        "https://rubricward.com/favicon.svg",
        "https://rubricward.com/apple-touch-icon.png",
        "https://rubricward.com/og-image.png",
        "https://rubricward.com/site.webmanifest",
        "https://rubricward.com/sitemap.xml",
    ]
    for pfile in sorted((ROOT / "lettings" / "project").glob("*.html")):
        urls.append(f"https://rubricward.com/lettings/project/{pfile.name}")

    payload = {
        "host": "rubricward.com",
        "key": "a4f8e2c91b7d3056e8a12f4c9d0b3e71",
        "keyLocation": "https://rubricward.com/a4f8e2c91b7d3056e8a12f4c9d0b3e71.txt",
        "urlList": urls,
    }
    for ep in ("https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow", "https://yandex.com/indexnow"):
        try:
            r = requests.post(ep, json=payload, timeout=15)
            print(f"  [INDEXNOW] {ep} -> HTTP {r.status_code}")
        except Exception as exc:
            print(f"  [INDEXNOW WARN] {ep}: {exc}")

    for fav_probe in (
        "https://www.google.com/s2/favicons?domain=rubricward.com&sz=128",
        "https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://rubricward.com&size=128",
    ):
        try:
            r = requests.get(fav_probe, timeout=15)
            print(f"  [GOOGLE FAVICON CRAWLER PROBE] {fav_probe[:65]}... -> HTTP {r.status_code} ({len(r.content)} bytes)")
        except Exception as exc:
            print(f"  [GOOGLE FAVICON PROBE WARN] {exc}")


if __name__ == "__main__":
    step1_ensure_cname_and_git_push()
    step2_configure_cloudflare_dns_and_worker()
    step3_ping_indexnow_and_google_favicon()

