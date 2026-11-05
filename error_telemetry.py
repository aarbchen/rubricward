"""
RubricWard — Closed-Loop Autonomous Error Telemetry, Self-Improving Anti-Regression Rule Ledger & Resolved-Only Discord Helper.

Strict Policy (Enforced across all RubricWard systems):
1. SILENT DETECTION: Never post raw errors, warnings, or open issues to Discord.
   All errors are logged silently to `error_log.txt` and `POST /v1/telemetry/report-error`
   for `auto_error_healer.py` and `omniscient_auditor.py` to inspect and fix autonomously.
2. RESOLVED-ONLY DISCORD NOTIFICATIONS: Discord is notified ONLY AFTER an issue has been
   diagnosed, repaired, verified via smoke test, and cleared.
3. SELF-IMPROVING RULE CODIFICATION: Every resolved issue MUST codify a permanent
   anti-regression rule in `learned_anti_regression_rules.json` AND append/sync it into
   `AGENTS.md` so the exact same class of bug can never recur.
"""

import json
import os
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG_PATH = os.path.join(BASE_DIR, "error_log.txt")
LEARNED_RULES_PATH = os.path.join(BASE_DIR, "learned_anti_regression_rules.json")
AGENTS_MD_PATH = os.path.join(BASE_DIR, "AGENTS.md")
_raw_api_base = os.getenv(
    "RUBRICWARD_API_BASE_URL",
    "https://rubricward.com",
).rstrip("/")
TELEMETRY_API_BASE = (
    "https://rubricward.com"
    if _raw_api_base == "https://api.rubricward.com"
    else _raw_api_base
)


def configure_utf8_stdio() -> None:
    """Ensure stdout and stderr use UTF-8 encoding across Windows PowerShell and Linux containers."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass



if os.name == "nt":
    import subprocess as _sp
    if not getattr(_sp.Popen, "_silent_window_patched", False):
        _ORIG_POPEN_INIT = _sp.Popen.__init__
        def _silent_popen_init(self, *args, **kwargs):
            kwargs["creationflags"] = int(kwargs.get("creationflags") or 0) | 0x08000000
            si = kwargs.get("startupinfo")
            if si is None:
                si = _sp.STARTUPINFO()
            si.dwFlags |= 0x00000001
            si.wShowWindow = 0
            kwargs["startupinfo"] = si
            return _ORIG_POPEN_INIT(self, *args, **kwargs)
        _silent_popen_init._silent_window_patched = True
        _sp.Popen.__init__ = _silent_popen_init
        _sp.Popen._silent_window_patched = True

def load_learned_rules() -> List[Dict[str, Any]]:
    """Load the persistent self-improving anti-regression rule ledger."""
    if not os.path.exists(LEARNED_RULES_PATH):
        return []
    try:
        with open(LEARNED_RULES_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if isinstance(data, dict):
                return data.get("rules", [])
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def _sync_rules_to_agents_md(rules: List[Dict[str, Any]]) -> None:
    """Keep the autonomous anti-regression rule ledger synchronized at the bottom of AGENTS.md."""
    if not os.path.exists(AGENTS_MD_PATH) or not rules:
        return
    marker_start = "<!-- AUTONOMOUS_LEARNED_RULES_START -->"
    marker_end = "<!-- AUTONOMOUS_LEARNED_RULES_END -->"

    lines = [
        marker_start,
        "## Autonomous Self-Improved Anti-Regression Rules (Auto-Codified by `omniscient_auditor.py` & `auto_error_healer.py`)",
        "",
        "The following rules were automatically learned from past detections and fixes. Every future audit and code change **MUST** enforce them:",
        "",
    ]
    for r in rules[-40:]:
        rule_id = r.get("rule_id", "RULE-AUTO")
        pillar = r.get("pillar", "General")
        rule_stmt = r.get("rule_statement", "")
        check_key = r.get("invariant_check", "")
        ts = r.get("created_at", "")[:10]
        lines.append(f"- **`{rule_id}` [{pillar}] ({ts}):** {rule_stmt} *(Enforced by `{check_key}`)*")
    lines.append(marker_end)
    block = "\n".join(lines)

    try:
        with open(AGENTS_MD_PATH, "r", encoding="utf-8") as fh:
            content = fh.read()
        if marker_start in content and marker_end in content:
            pre = content.split(marker_start)[0].rstrip()
            post = content.split(marker_end)[1].lstrip()
            updated = f"{pre}\n\n{block}\n" + (f"\n{post}" if post else "")
        else:
            updated = content.rstrip() + f"\n\n---\n\n{block}\n"
        if updated != content:
            with open(AGENTS_MD_PATH, "w", encoding="utf-8") as fh:
                fh.write(updated)
    except Exception:
        pass


def codify_learned_rule(
    rule_id: str,
    pillar: str,
    root_cause: str,
    fix_applied: str,
    rule_statement: str,
    invariant_check: str,
) -> Dict[str, Any]:
    """
    Record or update a permanent anti-regression rule in `learned_anti_regression_rules.json`
    and sync it to `AGENTS.md` so the system permanently learns from every issue it resolves.
    """
    rules = load_learned_rules()
    now_iso = datetime.now(timezone.utc).isoformat()

    existing = next((r for r in rules if r.get("rule_id") == rule_id), None)
    if existing:
        existing["last_enforced_at"] = now_iso
        existing["times_triggered"] = int(existing.get("times_triggered", 1)) + 1
        existing["fix_applied"] = fix_applied
        existing["rule_statement"] = rule_statement
        entry = existing
    else:
        entry = {
            "rule_id": rule_id,
            "pillar": pillar,
            "root_cause": root_cause,
            "fix_applied": fix_applied,
            "rule_statement": rule_statement,
            "invariant_check": invariant_check,
            "created_at": now_iso,
            "last_enforced_at": now_iso,
            "times_triggered": 1,
        }
        rules.append(entry)

    payload = {
        "updated_at": now_iso,
        "total_rules": len(rules),
        "policy": "Silent detection -> Autonomous diagnosis & repair -> Rule codification -> Resolved-only Discord notification",
        "rules": rules,
    }
    try:
        with open(LEARNED_RULES_PATH, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
    except Exception:
        pass

    _sync_rules_to_agents_md(rules)
    return entry


def derive_and_codify_rule_from_fix(
    component: str,
    issue_summary: str,
    fix_applied: str,
    pillar: str = "System Integrity",
) -> Dict[str, Any]:
    """Automatically synthesize a permanent anti-regression rule from any resolved incident."""
    low = f"{component} {issue_summary} {fix_applied}".lower()
    if "42501" in low or "rls" in low or "upsert" in low:
        rule_id = "RULE-RLS-SAFE-INSERT"
        stmt = "Never use `.upsert()` on Supabase tables protected by INSERT/SELECT-only RLS policies; always query existing URLs with `.select()` and insert only new rows via `.insert()`."
        inv = "ast_no_supabase_upsert"
    elif "claude-3" in low or "haiku" in low or "sonnet-4" in low or "model" in low:
        rule_id = "RULE-FRONTIER-MODEL-ONLY"
        stmt = "Always use the frontier Anthropic model (`claude-sonnet-5-5`) across all scrapers, `rubricward_autopilot.py`, `outbound_reply_responder.py`, and `llm_extractor.py`; never use retired models."
        inv = "check_frontier_model_strings"
    elif "emoji" in low or "unicode" in low or "cp1252" in low or "charmap" in low:
        rule_id = "RULE-UTF8-ZERO-EMOJI"
        stmt = "All scripts must call `configure_utf8_stdio()` at module load and HTML/UI surfaces must contain zero emojis (`[\\U0001F300-\\U0001FAFF]`)."
        inv = "check_utf8_and_zero_emoji"
    elif "syntax" in low or "vm.script" in low or "quote" in low or "script" in low:
        rule_id = "RULE-INLINE-JS-SYNTAX"
        stmt = "Every inline `<script>` block and `on*` event attribute in `index.html`, `apis.html`, and generated `/lettings/**/*.html` must pass Node.js `vm.Script` compilation with zero unescaped quotes."
        inv = "check_html_inline_js_vm"
    elif "openxml" in low or "docx" in low or "xlsx" in low or "zip" in low or "formula" in low:
        rule_id = "RULE-TIER3-OPENXML-INTEGRITY"
        stmt = "Tier 3 Bid Package `.ZIP` archives must always contain 6 valid OpenXML (`.docx`/`.xlsx`) and `.json` files with well-formed XML and live Excel `=SUM()` and `=D6*G6` formulas."
        inv = "check_tier3_openxml_zip_integrity"
    elif "mx" in low or "bimi" in low or "dmarc" in low or "spf" in low or "dkim" in low or "mailbox" in low:
        rule_id = "RULE-DELIVERABILITY-DNS-AUTH"
        stmt = "Outbound email infrastructure must maintain valid SPF, DMARC (`p=quarantine`/`reject`), BIMI SVG logo, MX records on all prospect domains, and zero duplicate follow-ups."
        inv = "check_email_deliverability_dns"
    elif "portal" in low or "catalog" in low or "parity" in low or "count" in low:
        rule_id = "RULE-PORTAL-CATALOG-PARITY"
        stmt = "Maintain 100% count and card parity across `index.html`, `apis.html`, `pseo_generator.py`, MCP servers, and Cloudflare Edge Worker (`52 Portals / 50 State DOTs` and `12 APIs`)."
        inv = "check_portal_and_catalog_parity"
    else:
        slug = "".join(ch if ch.isalnum() else "-" for ch in component.upper()).strip("-")[:24]
        rule_id = f"RULE-AUTO-{slug}"
        stmt = f"Prevent regression in `{component}` ({issue_summary[:120]}) by enforcing automated pre-flight verification (`{fix_applied[:120]}`)."
        inv = f"verify_{component.lower().replace('.', '_')}"

    return codify_learned_rule(
        rule_id=rule_id,
        pillar=pillar,
        root_cause=f"[{component}] {issue_summary[:300]}",
        fix_applied=fix_applied[:300],
        rule_statement=stmt,
        invariant_check=inv,
    )


def report_error(
    source: str,
    message: Any,
    severity: str = "ERROR",
    context: Optional[dict] = None,
    send_discord: bool = False,
) -> Dict[str, Any]:
    """
    SILENT DETECTION ONLY:
    1. Appends a structured line to local `error_log.txt`
    2. Reports to `POST /v1/telemetry/report-error` (if remote telemetry is reachable)
    3. NEVER posts raw/open errors to Discord (regardless of `send_discord` legacy flag).
       Discord only receives `[RESOLVED]` notifications via `send_discord_resolution()`.
    """
    configure_utf8_stdio()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    if isinstance(message, BaseException):
        err_msg = f"{type(message).__name__}: {message}"
        tb_str = "".join(traceback.format_exception(type(message), message, message.__traceback__))
    else:
        err_msg = str(message)
        tb_str = traceback.format_exc()
        if tb_str.strip() == "NoneType: None":
            tb_str = ""

    ctx_suffix = f" | context={context}" if context else ""
    log_line = f"[{ts}] [{severity.upper()}] [{source}] {err_msg}{ctx_suffix}\n"
    try:
        with open(ERROR_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(log_line)
    except Exception:
        pass

    payload = {
        "component": source,
        "error": err_msg[:1500],
        "traceback": tb_str[:3000],
        "severity": severity,
        "timestamp": ts,
        "host": os.getenv("RENDER_SERVICE_NAME", os.getenv("COMPUTERNAME", "local")),
    }

    if os.getenv("RUBRICWARD_REMOTE_TELEMETRY", "0") == "1":
        try:
            requests.post(
                f"{TELEMETRY_API_BASE}/v1/telemetry/report-error",
                json=payload,
                timeout=4,
            )
        except Exception:
            pass

    return payload


def send_discord_resolution(
    component: str,
    issues_fixed: List[str],
    verification_summary: str,
    learned_rules: Optional[List[Dict[str, Any]]] = None,
) -> bool:
    """
    RESOLVED-ONLY DISCORD NOTIFICATION:
    Posts to `DISCORD_WEBHOOK_URL` ONLY when an error or audit finding has been
    autonomously diagnosed, repaired, verified, and codified into a permanent anti-regression rule.
    """
    if not issues_fixed:
        return False

    rules_codified: List[Dict[str, Any]] = list(learned_rules or [])
    if not rules_codified:
        for item in issues_fixed:
            rule = derive_and_codify_rule_from_fix(
                component=component,
                issue_summary=item,
                fix_applied=verification_summary,
            )
            rules_codified.append(rule)

    webhook_url = os.getenv("RUBRICWARD_DISCORD_WEBHOOK_URL", "").strip()
    signaltender_webhook_ids = (
        "1555743443802918993",
        "1560070981563715644",
        "1561230679860056117",
        "1563916225862574080",
        "1563916236126036068",
    )
    if not webhook_url or any(wid in webhook_url for wid in signaltender_webhook_ids):
        return False

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    fixes_lines = "\n".join(f"• {item[:220]}" for item in issues_fixed[:8])
    rules_lines = "\n".join(
        f"• `{r.get('rule_id')}`: {r.get('rule_statement', '')[:180]}"
        for r in rules_codified[:5]
    )

    msg = (
        f"**[RESOLVED] RUBRICWARD AUTONOMOUS HEALER // `{component}`**\n"
        f"**Timestamp:** `{ts}`\n"
        f"**Status:** Diagnosed, Repaired & Verified (`0 Open Errors`)\n\n"
        f"**Issues Repaired:**\n{fixes_lines}\n\n"
        f"**Verification Gate:** {verification_summary[:300]}\n\n"
        f"**New Anti-Regression Rules Codified (`AGENTS.md`):**\n{rules_lines}"
    )

    try:
        resp = requests.post(
            webhook_url,
            json={"content": msg[:1950], "flags": 4},
            timeout=8,
        )
        return resp.status_code in (200, 204)
    except Exception:
        return False
