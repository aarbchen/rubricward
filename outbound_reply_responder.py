"""
RubricWard — Autonomous Outbound Reply Auto-Responder (`outbound_reply_responder.py`).
Polls inbound prospect replies and dispatches the 6-file OpenXML Payer MRF, ERISA Appeal & NSA IDR `.ZIP` link + Tier 2 Checkout CTA.
Always uses the frontier Anthropic model (`claude-sonnet-5-5`).
"""

from error_telemetry import configure_utf8_stdio, report_error
configure_utf8_stdio()

import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")


def _strip_quoted_thread(body: str) -> str:
    """Strips quoted email thread history ('>', 'On ... wrote:', 'From:') before intent classification (RULE-021)."""
    clean_lines: List[str] = []
    for line in (body or "").splitlines():
        s = line.strip()
        if s.startswith(">"):
            continue
        if s.lower().startswith(("on ", "from:", "sent:", "-----original message-----")):
            break
        clean_lines.append(line)
    return "\n".join(clean_lines).strip()


def build_reply_response(prospect_name: str, letting_id: str, inbound_body: str = "") -> Dict[str, str]:
    cleaned_inbound = _strip_quoted_thread(inbound_body)
    return {
        "model": ANTHROPIC_MODEL,
        "letting_id": letting_id,
        "cleaned_inbound": cleaned_inbound,
        "subject": f"Re: Commercial Payer TiC MRF, ERISA Appeal & NSA IDR 6-File .ZIP Package for {letting_id}",
        "body": (
            f"Hi {prospect_name},\n\n"
            f"Here is the direct link to your 6-file OpenXML (.DOCX + .XLSX) Commercial Payer TiC MRF, Medicare MPFS RVU/GPCI & Federal NSA IDR Package for {letting_id} "
            f"across our 52 monitored State DOI/APCD MRF & Federal IDR portals and 12 Healthcare Revenue Cycle APIs:\n\n"
            f"- Live Payer MRF & NSA IDR Dossier & 1-Click .ZIP Compiler: https://rubricward.com/#lettings\n"
            f"- Tier 2 Payer MRF & NSA IDR Autopilot Desk: https://rubricward.com/#checkout-tier2\n\n"
            f"Best,\n"
            f"Aaron\n"
            f"RubricWard Payer MRF & NSA IDR Systems"
        ),
    }


if __name__ == "__main__":
    sample = build_reply_response("Specialty Group Revenue Cycle Team", "TXDOI-MRF-CPT-29881-DFW")
    print(f"[RUBRICWARD RESPONDER] Ready (Model: {sample['model']})")
