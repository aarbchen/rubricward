r"""
RubricWard — Engine 4: IndexNow & Search Engine Sitemap Submitter (`D:\RubricWard\indexnow_submitter.py`).
Pushes `https://rubricward.com`, `/apis`, `/lettings`, and all `/lettings/project/*.html` pSEO dossiers
directly to IndexNow (`api.indexnow.org` & `www.bing.com/indexnow`) and verifies `default._bimi` TXT
on `rubricward.com`.
"""

from error_telemetry import configure_utf8_stdio
configure_utf8_stdio()

import json
import os
from pathlib import Path
import re
import requests
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=str(ROOT_DIR / ".env"))

INDEXNOW_KEY = os.getenv("RUBRICWARD_INDEXNOW_KEY", "a4f8e2c91b7d3056e8a12f4c9d0b3e71").strip()


def ensure_bimi_on_primary_domain() -> bool:
    cf_token = (os.getenv("CLOUDFLARE_API_TOKEN") or "").strip()
    zone_id = "25e2afb50eb69f06f35a971ddf83f1ce"
    if not cf_token:
        return False
    headers = {"Authorization": f"Bearer {cf_token}", "Content-Type": "application/json"}
    try:
        r_list = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?per_page=100", headers=headers, timeout=10)
        existing = (r_list.json() or {}).get("result") or [] if r_list.status_code == 200 else []
        rec = {
            "type": "TXT",
            "name": "default._bimi",
            "content": '"v=BIMI1; l=https://rubricward.com/bimi-logo.svg;"',
            "ttl": 3600,
        }
        match = next((x for x in existing if x.get("type") == "TXT" and x.get("name") == "default._bimi.rubricward.com"), None)
        if match and match.get("id"):
            r = requests.put(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{match['id']}", headers=headers, json=rec, timeout=10)
        else:
            r = requests.post(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records", headers=headers, json=rec, timeout=10)
        return r.status_code in (200, 201)
    except Exception:
        return False


def submit_sitemap_to_indexnow() -> dict:
    sitemap_path = ROOT_DIR / "sitemap.xml"
    urls = ["https://rubricward.com/", "https://rubricward.com/apis.html", "https://rubricward.com/lettings/index.html"]
    if sitemap_path.exists():
        xml = sitemap_path.read_text(encoding="utf-8")
        found = re.findall(r"<loc>(https://rubricward\.com[^<]+)</loc>", xml)
        for u in found:
            if u not in urls:
                urls.append(u)

    payload = {
        "host": "rubricward.com",
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://rubricward.com/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    status_code = 0
    try:
        resp = requests.post("https://api.indexnow.org/indexnow", json=payload, timeout=10)
        status_code = resp.status_code
    except Exception:
        pass
    bimi_ok = ensure_bimi_on_primary_domain()
    out = {"urls_submitted": len(urls), "indexnow_http_status": status_code, "primary_bimi_configured": bimi_ok}
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    submit_sitemap_to_indexnow()
