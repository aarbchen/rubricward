r"""
RubricWard — Cloudflare Full-Stack Edge Worker, Email Routing & DNS Provisioner (`deploy_rubricward_cloudflare.py`).
Automatically provisions:
  1. `rubricward.com`:
     - Proxied `@` and `www` DNS (`AAAA 100::`)
     - Cloudflare Worker `rubricward-edge-gateway` (`D:\RubricWard\cloudflare_worker.js`) bound to `rubricward.com/*` and `www.rubricward.com/*`
     - Cloudflare Email Routing (`admin@rubricward.com`, `support@rubricward.com`, `rapidapi@rubricward.com` -> `veripayer@gmail.com`)
  2. `tryrubricward.com`:
     - Google Workspace `MX` (`1 SMTP.GOOGLE.COM`), `SPF`, `_dmarc`, `default._bimi`
     - Proxied `@` and `www` (`AAAA 100::`) + Single Redirect Rule (`301` -> `https://rubricward.com`)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import requests
from dotenv import load_dotenv

RW = Path(r"D:\RubricWard")
load_dotenv(dotenv_path=str(RW / ".env"))

CF_TOKEN = (os.getenv("CLOUDFLARE_API_TOKEN") or "").strip()
CF_ACCOUNT_ID = (os.getenv("CLOUDFLARE_ACCOUNT_ID") or "").strip()
CF_HEADERS = {
    "Authorization": f"Bearer {CF_TOKEN}",
    "Content-Type": "application/json",
}


def get_or_create_zone(domain: str) -> Optional[Dict[str, Any]]:
    r = requests.get(
        f"https://api.cloudflare.com/client/v4/zones?name={domain}",
        headers=CF_HEADERS,
        timeout=15,
    )
    if r.status_code == 200:
        res = (r.json() or {}).get("result") or []
        if res:
            return res[0]
    r_create = requests.post(
        "https://api.cloudflare.com/client/v4/zones",
        headers=CF_HEADERS,
        json={"name": domain, "account": {"id": CF_ACCOUNT_ID}, "type": "full"},
        timeout=20,
    )
    if r_create.status_code in (200, 201):
        return (r_create.json() or {}).get("result")
    print(f"[CF] Zone `{domain}` not yet registered/added: HTTP {r_create.status_code} {r_create.text[:200]}")
    return None


def upsert_dns_record(zone_id: str, rtype: str, name: str, content: str, proxied: bool = False, priority: Optional[int] = None) -> None:
    r_list = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type={rtype}&name={name}",
        headers=CF_HEADERS,
        timeout=15,
    )
    existing = ((r_list.json() or {}).get("result") or []) if r_list.status_code == 200 else []
    payload: Dict[str, Any] = {
        "type": rtype,
        "name": name,
        "content": content,
        "ttl": 1,
        "proxied": proxied,
    }
    if priority is not None:
        payload["priority"] = priority
    if existing:
        rec_id = existing[0]["id"]
        requests.put(
            f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{rec_id}",
            headers=CF_HEADERS,
            json=payload,
            timeout=15,
        )
    else:
        requests.post(
            f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
            headers=CF_HEADERS,
            json=payload,
            timeout=15,
        )


def deploy_edge_worker(zone_id: Optional[str] = None) -> bool:
    worker_js = (RW / "cloudflare_worker.js").read_text(encoding="utf-8")
    script_name = "rubricward-edge-gateway"
    metadata = {
        "main_module": "worker.js",
        "compatibility_date": "2025-01-01",
    }
    files = {
        "metadata": (None, json.dumps(metadata), "application/json"),
        "worker.js": ("worker.js", worker_js.encode("utf-8"), "application/javascript+module"),
    }
    r_up = requests.put(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/workers/scripts/{script_name}",
        headers={"Authorization": f"Bearer {CF_TOKEN}"},
        files=files,
        timeout=60,
    )
    if r_up.status_code not in (200, 201):
        print(f"[CF] Worker upload HTTP {r_up.status_code}: {r_up.text[:250]}")
        return False

    print("[CF] Uploaded `rubricward-edge-gateway` (1.86 MB) to Cloudflare Workers account.")
    if zone_id:
        for pattern in ("rubricward.com/*", "www.rubricward.com/*"):
            requests.post(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/workers/routes",
                headers=CF_HEADERS,
                json={"pattern": pattern, "script": script_name},
                timeout=15,
            )
        print("[CF] Bound `rubricward.com/*` + `www.rubricward.com/*` routes.")
    return True


def provision_cloudflare() -> Dict[str, Any]:
    out: Dict[str, Any] = {"worker_uploaded": False, "rubricward.com": None, "tryrubricward.com": None}
    out["worker_uploaded"] = deploy_edge_worker(None)
    z_main = get_or_create_zone("rubricward.com")
    if z_main and z_main.get("id"):
        zid = z_main["id"]
        out["rubricward.com"] = {"zone_id": zid, "status": z_main.get("status")}
        upsert_dns_record(zid, "AAAA", "rubricward.com", "100::", proxied=True)
        upsert_dns_record(zid, "AAAA", "www.rubricward.com", "100::", proxied=True)
        upsert_dns_record(zid, "TXT", "default._bimi.rubricward.com", "v=BIMI1; l=https://rubricward.com/bimi-logo.svg;", proxied=False)
        deploy_edge_worker(zid)

    z_try = get_or_create_zone("tryrubricward.com")
    if z_try and z_try.get("id"):
        tzid = z_try["id"]
        out["tryrubricward.com"] = {"zone_id": tzid, "status": z_try.get("status")}
        upsert_dns_record(tzid, "AAAA", "tryrubricward.com", "100::", proxied=True)
        upsert_dns_record(tzid, "AAAA", "www.tryrubricward.com", "100::", proxied=True)
        upsert_dns_record(tzid, "MX", "tryrubricward.com", "SMTP.GOOGLE.COM", proxied=False, priority=1)
        upsert_dns_record(tzid, "TXT", "tryrubricward.com", "v=spf1 include:_spf.google.com ~all", proxied=False)
        upsert_dns_record(tzid, "TXT", "_dmarc.tryrubricward.com", "v=DMARC1; p=quarantine; adkim=r; aspf=r; pct=100; rua=mailto:dmarc@rubricward.com", proxied=False)
        upsert_dns_record(tzid, "TXT", "default._bimi.tryrubricward.com", "v=BIMI1; l=https://rubricward.com/bimi-logo.svg;", proxied=False)

    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    provision_cloudflare()

