"""
RubricWard — Programmatic SEO (pSEO) Static Lettings & Payer MRF/IDR Dossier Generator (`pseo_generator.py`).
Generates:
1. `/lettings/index.html` (52-Portal Commercial Payer TiC MRF, ERISA Appeal & Federal NSA IDR Hub)
2. `/lettings/project/<slug>.html` (Individual Payer MRF Rate Disparity & NSA IDR Dossier Pages with 1-Click 6-File .ZIP Compiler CTA)
3. `/sitemap.xml` and `/robots.txt`
Strictly enforces:
- Word-boundary `slugify()` (<= 65 chars) & portal-first `classify_jurisdiction()`
- Zero unescaped quotes inside generated `<script>` blocks
- Zero emojis & 100% Swiss Architectural Grid aesthetic
"""

from error_telemetry import configure_utf8_stdio, report_error
configure_utf8_stdio()

import html
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent
SEED_PATH = ROOT_DIR / "dot_lettings_seed.json"
LETTINGS_DIR = ROOT_DIR / "lettings"
PROJECTS_DIR = LETTINGS_DIR / "project"
from build_rubricward_site import build_social_and_favicon_head

LOGO_SVG = """<svg viewBox="0 0 64 64" class="w-[22px] h-[22px] shrink-0 -translate-y-[1px]" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path fill="#0A0D14" d="M12 10H32V54C19 48 12 37 12 22V10Z"/>
  <rect x="37" y="10" width="15" height="28" rx="2" fill="#059669"/>
</svg>"""


def slugify(text: str) -> str:
    """Word-boundary slugify (<= 65 chars, never cutting a word in half)."""
    cleaned = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    if len(cleaned) <= 65:
        return cleaned
    truncated = cleaned[:65]
    if "-" in truncated:
        truncated = truncated.rsplit("-", 1)[0]
    return truncated.strip("-")


def classify_jurisdiction(letting: Dict[str, Any]) -> str:
    """Portal-first jurisdiction classifier identical across pseo_generator, client_delivery, and rubricward_autopilot."""
    url = str(letting.get("source_url") or "").lower()
    if "cms.gov" in url or "nsa" in str(letting.get("letting_id") or "").lower():
        return "federal"
    if "uhc.com" in url or "multi-payer" in str(letting.get("agency") or "").lower():
        return "municipal"
    if "tdi.texas.gov" in url:
        return "tx"
    if "dmhc.ca.gov" in url:
        return "ca"
    if "floir.com" in url:
        return "fl"
    if "scc.virginia.gov" in url:
        return "va"
    if "pa.gov" in url:
        return "pa"
    if "dfs.ny.gov" in url:
        return "ny"
    if "idoi.illinois.gov" in url:
        return "il"
    if "insurance.ohio.gov" in url:
        return "oh"
    if "oci.georgia.gov" in url:
        return "ga"
    if "ncdoi.gov" in url:
        return "nc"
    st = str(letting.get("state_code") or "").lower().strip()
    if st == "us":
        return "federal"
    if st == "mu":
        return "municipal"
    return st or "tx"


def _header_html(root_rel: str = "../", dir_href: str = "index.html") -> str:
    return f"""<header class="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-[#B4D6D0]">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between gap-4">
    <a href="{root_rel}index.html#overview" class="group inline-flex flex-col min-w-0 max-w-[calc(100%-88px)] sm:max-w-none">
      <div class="inline-flex items-center gap-2 flex-wrap">
        <span class="inline-flex items-center gap-[5px]">
          {LOGO_SVG}
          <span class="text-[22px] sm:text-[23px] font-extrabold tracking-[-0.03em] text-[#071C21] leading-none whitespace-nowrap">RubricWard</span>
        </span>
        <span class="px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider bg-[#DDF0EC] text-[#065F46] border border-[#7FB5AC] rounded">52 PAYER &amp; STATE PORTALS // 12 APIS</span>
      </div>
      <span class="text-[11px] font-mono font-semibold text-[#1E293B] mt-1 truncate max-w-full">50-State Commercial Payer TiC MRF, Medicare MPFS RVU/GPCI &amp; Federal NSA IDR Intelligence</span>
    </a>
    <nav class="hidden md:flex items-center gap-5 text-xs font-mono font-bold uppercase tracking-wider text-[#071C21]">
      <a href="{root_rel}index.html#overview" class="hover:text-[#065F46]">Overview</a>
      <a href="{dir_href}" class="text-[#065F46] font-extrabold">Live Payer MRF &amp; IDR Directory</a>
      <a href="{root_rel}apis.html" class="hover:text-[#065F46]">API Catalog</a>
      <a href="{root_rel}index.html#contact" class="hover:text-[#065F46]">Contact &amp; Support</a>
      <a href="{root_rel}index.html#checkout" class="px-3.5 py-1.5 bg-[#071C21] text-white rounded hover:bg-[#065F46] transition">Pricing &amp; Access</a>
    </nav>
    <a href="{root_rel}index.html#checkout" class="md:hidden shrink-0 px-3 py-1.5 rounded-lg bg-[#071C21] text-white text-xs font-mono font-bold">PRICING</a>
  </div>
</header>"""


def build_project_dossier_html(letting: Dict[str, Any], slug: str) -> str:
    lid = html.escape(str(letting.get("letting_id") or letting.get("project_id") or ""))
    title = html.escape(str(letting.get("title") or ""))
    agency = html.escape(str(letting.get("agency") or ""))
    st = html.escape(str(letting.get("state_code") or "TX"))
    county = html.escape(str(letting.get("county") or ""))
    l_date = html.escape(str(letting.get("letting_date") or ""))
    est = float(letting.get("engineers_estimate_usd") or 0.0)
    dbe_pct = float(letting.get("dbe_goal_pct") or 215.0)
    wd_id = html.escape(str(letting.get("wage_determination_id") or letting.get("wage_decision_id") or ""))
    ld_day = int(letting.get("liquidated_damages_per_day_usd") or 180)
    src_url = html.escape(str(letting.get("source_url") or "https://www.cms.gov/nosurprises"))
    scope = html.escape(str(letting.get("description") or letting.get("scope_summary") or ""))

    pay_rows = []
    items = letting.get("key_pay_items") or letting.get("pay_items") or []
    for item in items:
        low_u = float(item.get("low_unit_usd") or item.get("hist_low_unit_usd") or item.get("hist_avg_unit_usd") or 0)
        med_u = float(item.get("median_unit_usd") or item.get("hist_median_unit_usd") or item.get("recommended_unit_usd") or 0)
        p75_u = float(item.get("p75_unit_usd") or item.get("recommended_unit_usd") or (med_u * 1.15) or 0)
        pay_rows.append(
            f"""<tr class="border-b border-[#B4D6D0] text-xs font-mono">
              <td class="py-2.5 px-3 font-bold text-[#065F46]">{html.escape(str(item.get('item_code', '')))}</td>
              <td class="py-2.5 px-3 text-[#071C21] font-semibold">{html.escape(str(item.get('description', '')))}</td>
              <td class="py-2.5 px-3 text-[#1E293B] font-semibold">{html.escape(str(item.get('unit', '')))}</td>
              <td class="py-2.5 px-3 text-right text-[#071C21] font-bold">{item.get('quantity', 0):,}</td>
              <td class="py-2.5 px-3 text-right text-[#1E293B] font-semibold">${low_u:,.2f}</td>
              <td class="py-2.5 px-3 text-right font-extrabold text-[#065F46]">${med_u:,.2f}</td>
              <td class="py-2.5 px-3 text-right font-bold text-[#0F766E]">${p75_u:,.2f}</td>
            </tr>"""
        )

    ph_badges = "".join(
        f'<span class="px-2.5 py-1 text-xs font-mono font-bold bg-[#DDF0EC] border border-[#7FB5AC] rounded text-[#071C21]">{html.escape(str(p))}</span>'
        for p in letting.get("planholders", [])
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{lid} — {title} | RubricWard Payer MRF &amp; NSA IDR Dossier</title>
  <meta name="description" content="Commercial Payer TiC MRF Rate-Disparity Dossier, Medicare MPFS RVU/GPCI Schedule, and Federal NSA 45 CFR 149.510 IDR Analysis for {lid} ({agency})." />
  {build_social_and_favicon_head(
      page_title=f"{lid} — {title} | RubricWard Payer MRF & NSA IDR Dossier",
      page_desc=f"Commercial Payer TiC MRF Rate-Disparity Dossier, Medicare MPFS RVU/GPCI Schedule, and Federal NSA IDR Analysis for {lid} ({agency}).",
      canonical_url=f"https://rubricward.com/lettings/project/{slug}.html",
      rel_prefix="../",
  )}
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    html, body {{ max-width: 100vw; overflow-x: hidden; color: #071C21; }}
    code, span, a, td, th {{ overflow-wrap: anywhere; word-break: break-word; }}
  </style>
</head>
<body class="bg-[#F2F9F8] text-[#071C21] antialiased min-h-screen flex flex-col">
  {_header_html(root_rel="../../", dir_href="../index.html")}
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full">
    <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
      <a href="../index.html" class="text-xs font-mono font-bold text-[#065F46] hover:underline">&larr; Back to 52-Portal Commercial Payer MRF &amp; NSA IDR Directory</a>
      <span class="px-2.5 py-1 text-[11px] font-mono font-bold bg-[#DDF0EC] border border-[#7FB5AC] rounded text-[#065F46]">RUBRICWARD AI DOSSIER // TIER 2 AUTOPILOT (#01–#06, #11)</span>
    </div>

    <section class="bg-white border border-[#B4D6D0] rounded-2xl p-6 sm:p-8 shadow-sm mb-8">
      <div class="flex flex-wrap items-center gap-2 text-xs font-mono font-bold text-[#1E293B] mb-2">
        <span class="px-2 py-0.5 bg-[#065F46] text-white rounded font-bold">{st}</span>
        <span>{lid}</span>
        <span>&bull;</span>
        <span>{agency}</span>
        <span>&bull;</span>
        <span>{county}</span>
        <span>&bull;</span>
        <span>Filing / IDR Window: {l_date}</span>
      </div>
      <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#071C21] mb-3">{title}</h1>
      <p class="text-sm font-medium text-[#111827] leading-relaxed mb-6">{scope}</p>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-b border-[#B4D6D0] py-4 mb-6 font-mono">
        <div>
          <div class="text-[11px] font-bold text-[#1E293B] uppercase">Cohort MRF 75th-Pct Value</div>
          <div class="text-lg font-extrabold text-[#071C21]">${est:,.0f}</div>
        </div>
        <div>
          <div class="text-[11px] font-bold text-[#1E293B] uppercase">Target % of Medicare</div>
          <div class="text-lg font-extrabold text-[#065F46]">{dbe_pct}% MPFS</div>
        </div>
        <div>
          <div class="text-[11px] font-bold text-[#1E293B] uppercase">Statutory Authority</div>
          <div class="text-sm font-extrabold text-[#0F766E]">{wd_id}</div>
        </div>
        <div>
          <div class="text-[11px] font-bold text-[#1E293B] uppercase">ERISA / Timely-Filing Window</div>
          <div class="text-lg font-extrabold text-[#071C21]">{ld_day} Days</div>
        </div>
      </div>

      <h2 class="text-sm font-mono uppercase tracking-wider text-[#065F46] font-extrabold mb-3">1. Commercial Payer TiC MRF Allowed-Amount Benchmarks (API #02)</h2>
      <div class="overflow-x-auto border border-[#B4D6D0] rounded-xl mb-6">
        <table class="w-full min-w-[680px] text-left border-collapse">
          <thead>
            <tr class="bg-[#DDF0EC] border-b border-[#7FB5AC] text-[11px] font-mono font-bold uppercase text-[#071C21]">
              <th class="py-2.5 px-3">CPT / DRG Code</th>
              <th class="py-2.5 px-3">Clinical Procedure Description</th>
              <th class="py-2.5 px-3">Unit</th>
              <th class="py-2.5 px-3 text-right">Cohort Claims</th>
              <th class="py-2.5 px-3 text-right">MRF 25th Pct</th>
              <th class="py-2.5 px-3 text-right">MRF Median (QPA)</th>
              <th class="py-2.5 px-3 text-right">MRF 75th Pct</th>
            </tr>
          </thead>
          <tbody>
            {''.join(pay_rows)}
          </tbody>
        </table>
      </div>

      <h2 class="text-sm font-mono uppercase tracking-wider text-[#065F46] font-extrabold mb-3">2. Regional Peer Specialty Groups &amp; EIN/NPI MRF Comparables (API #11)</h2>
      <div class="flex flex-wrap gap-2 mb-6">
        {ph_badges}
      </div>

      <div class="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-[#B4D6D0]">
        <div class="flex flex-wrap gap-3">
          <a href="../../index.html#checkout-tier2" class="px-4 py-2.5 bg-[#071C21] text-white text-xs font-mono font-bold uppercase tracking-wider rounded-lg hover:bg-[#065F46] transition">Compile 6-File OpenXML Claim &amp; IDR .ZIP Package (&rarr;)</a>
          <a href="../../apis.html#product-dot-unit-bid-tabs" class="px-4 py-2.5 bg-[#DDF0EC] text-[#071C21] border border-[#7FB5AC] text-xs font-mono font-bold uppercase tracking-wider rounded-lg hover:bg-[#C8E6E0] transition">Test API #02 Payer MRF Modeler</a>
        </div>
        <a href="{src_url}" target="_blank" rel="noopener noreferrer" class="text-xs font-mono font-bold text-[#065F46] hover:underline">Verify Official Payer MRF / Regulatory Portal &rarr;</a>
      </div>
    </section>
  </main>
</body>
</html>"""


def build_directory_index_html(lettings: List[Dict[str, Any]]) -> str:
    rows_html = []
    for item in lettings:
        lid_raw = item.get("letting_id") or item.get("project_id") or ""
        slug = slugify(f"{lid_raw}-{item.get('title', '')}")
        lid = html.escape(str(lid_raw))
        title = html.escape(str(item.get("title") or ""))
        agency = html.escape(str(item.get("agency") or ""))
        st = html.escape(str(item.get("state_code") or "TX"))
        est = float(item.get("engineers_estimate_usd") or 0.0)
        dbe_pct = float(item.get("dbe_goal_pct") or 215.0)
        l_date = html.escape(str(item.get("letting_date") or ""))

        rows_html.append(
            f"""<tr class="border-b border-[#B4D6D0] hover:bg-[#E8F4F2] transition text-xs font-mono">
              <td class="py-3 px-3 font-extrabold text-[#065F46]">{st}</td>
              <td class="py-3 px-3 font-bold text-[#0F766E]">{lid}</td>
              <td class="py-3 px-3 font-sans font-bold text-sm text-[#071C21]">
                <a href="project/{slug}.html" class="hover:text-[#065F46] underline">{title}</a>
                <div class="text-[11px] font-mono text-[#1E293B] font-semibold mt-0.5">{agency}</div>
              </td>
              <td class="py-3 px-3 text-right font-extrabold text-[#065F46]">${est:,.0f}</td>
              <td class="py-3 px-3 text-right font-bold text-[#0F766E]">{dbe_pct}% MPFS</td>
              <td class="py-3 px-3 text-right font-semibold text-[#071C21]">{l_date}</td>
              <td class="py-3 px-3 text-right">
                <a href="project/{slug}.html" class="inline-block whitespace-nowrap px-2.5 py-1 bg-[#071C21] text-white rounded text-[11px] font-bold hover:bg-[#065F46]">Open Dossier</a>
              </td>
            </tr>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>52-Portal Commercial Payer TiC MRF, ERISA Appeal &amp; Federal NSA IDR Directory | RubricWard</title>
  <meta name="description" content="Live 50-State Commercial Payer TiC MRF Rate Disparities, CMS Federal NSA IDR Arbitration Cohorts, and ERISA 29 CFR 2560.503-1 Underpayment Directory." />
  {build_social_and_favicon_head(
      page_title="52-Portal Commercial Payer TiC MRF, ERISA Appeal & Federal NSA IDR Directory | RubricWard",
      page_desc="Live 50-State Commercial Payer TiC MRF Rate Disparities, CMS Federal NSA IDR Arbitration Cohorts, and ERISA 29 CFR 2560.503-1 Underpayment Directory.",
      canonical_url="https://rubricward.com/lettings/index.html",
      rel_prefix="",
  )}
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    html, body {{ max-width: 100vw; overflow-x: hidden; color: #071C21; }}
    code, span, a, td, th {{ overflow-wrap: anywhere; word-break: break-word; }}
  </style>
</head>
<body class="bg-[#F2F9F8] text-[#071C21] antialiased min-h-screen flex flex-col">
  {_header_html(root_rel="../", dir_href="index.html")}
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full">
    <div class="mb-6">
      <div class="inline-flex items-center gap-2 px-2.5 py-1 bg-[#DDF0EC] border border-[#7FB5AC] rounded text-xs font-mono font-bold text-[#065F46] mb-2">
        52 PORTALS ACTIVE // FEDERAL CMS IDR &amp; 50-STATE COMMERCIAL PAYER MRF DIRECTORY
      </div>
      <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#071C21]">Live Commercial Payer TiC MRF, ERISA Appeal &amp; NSA IDR Directory</h1>
      <p class="text-sm font-medium text-[#111827] mt-1">Every cohort below includes pre-modeled 25th/50th/75th-percentile TiC MRF CPT/DRG benchmarks, CMS Medicare MPFS RVU/GPCI baselines, and 1-Click 6-File OpenXML (.DOCX + .XLSX) Claim &amp; IDR Package compilation.</p>
    </div>

    <div class="bg-white border border-[#B4D6D0] rounded-2xl overflow-x-auto shadow-sm">
      <table class="w-full min-w-[760px] text-left border-collapse">
        <thead>
          <tr class="bg-[#DDF0EC] border-b-2 border-[#7FB5AC] text-[11px] font-mono font-bold uppercase text-[#071C21]">
            <th class="py-3 px-3">State</th>
            <th class="py-3 px-3">Cohort / Case ID</th>
            <th class="py-3 px-3">Commercial Payer MRF Cohort &amp; Regulatory Portal</th>
            <th class="py-3 px-3 text-right">Cohort MRF Value</th>
            <th class="py-3 px-3 text-right">Target Multiple</th>
            <th class="py-3 px-3 text-right">Filing Window</th>
            <th class="py-3 px-3 text-right">Dossier</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows_html)}
        </tbody>
      </table>
    </div>
  </main>
</body>
</html>"""


def generate_pseo_pages() -> int:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    for stale_file in PROJECTS_DIR.glob("*.html"):
        try:
            stale_file.unlink()
        except Exception:
            pass
    raw = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    lettings = raw.get("lettings", [])

    urls = [
        "https://rubricward.com/",
        "https://rubricward.com/apis.html",
        "https://rubricward.com/lettings/index.html",
    ]

    for item in lettings:
        lid_raw = item.get("letting_id") or item.get("project_id") or ""
        slug = slugify(f"{lid_raw}-{item.get('title', '')}")
        out_file = PROJECTS_DIR / f"{slug}.html"
        out_file.write_text(build_project_dossier_html(item, slug), encoding="utf-8")
        urls.append(f"https://rubricward.com/lettings/project/{slug}.html")

    (LETTINGS_DIR / "index.html").write_text(build_directory_index_html(lettings), encoding="utf-8")

    sitemap_items = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_items}
</urlset>
"""
    (ROOT_DIR / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    (ROOT_DIR / "robots.txt").write_text(
        "User-agent: Google-Favicon\nAllow: /\n\nUser-agent: Googlebot-Image\nAllow: /\n\nUser-agent: Googlebot\nAllow: /\n\nUser-agent: *\nAllow: /\n\nSitemap: https://rubricward.com/sitemap.xml\n",
        encoding="utf-8",
    )
    print(f"[RUBRICWARD pSEO] Generated {len(lettings)} project dossiers, /lettings/index.html & sitemap.xml ({len(urls)} URLs)")
    return len(lettings)


if __name__ == "__main__":
    generate_pseo_pages()
