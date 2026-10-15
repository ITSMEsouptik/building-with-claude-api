"""Extraction prompts, versioned."""

EXTRACT_V1 = (
    "Extract a support ticket from the email inside <email> tags. "
    "category is one of: billing, bug, feature_request, other. "
    "urgency is an integer from 1 (low) to 5 (critical). "
    "summary is one sentence. Output only JSON."
)

EXTRACT_V2 = (
    "Extract a support ticket from the email inside <email> tags. "
    "Return JSON with exactly these keys: "
    "customer (string: the sender's name, or their company if given), "
    "category (one of: billing, bug, feature_request, other), "
    "urgency (integer from 1 low to 5 critical), "
    "summary (one sentence). Output only JSON."
)
