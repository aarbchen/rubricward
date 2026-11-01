"""
Compatibility shim forwarding `camberdesk_autopilot` imports to `rubricward_autopilot`.
"""

from rubricward_autopilot import (
    TIER2_AUTOPILOT_API_SUITE,
    classify_jurisdiction,
    generate_all_dossiers,
    slugify,
    synthesize_tier2_dossier,
)

if __name__ == "__main__":
    generate_all_dossiers(dispatch_discord=False)
