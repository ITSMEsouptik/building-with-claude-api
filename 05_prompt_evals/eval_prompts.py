"""Prompt versions under evaluation in lesson 05. Never edit a version in place: add a new one."""

V1_BARE = "Turn this support email into a ticket. Output JSON."

V2_SPEC = (
    "Extract a support ticket from the email inside <email> tags. "
    "Return only JSON with exactly these keys: "
    "customer (string: sender's name, or their company if given), "
    "category (one of: billing, bug, feature_request, other), "
    "urgency (integer 1 low to 5 critical), "
    "summary (one sentence). No prose, no code fences."
)
