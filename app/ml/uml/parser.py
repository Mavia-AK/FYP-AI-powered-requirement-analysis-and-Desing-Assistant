# app/ml/uml/parser.py
"""
Parse a list of requirement strings into (id, requirement, actor, action) records.

Changes from v1
───────────────
• Calls extractor.extract_pairs() which returns a *list* — one requirement
  can now produce multiple actor-action rows (compound sentences).
• Global pair de-duplication: identical (actor, action) combinations that
  appear across several requirements are merged; the requirement text of the
  *first* occurrence is kept.
• Requirements where extraction fails are silently skipped (same as v1).
"""

from __future__ import annotations
from app.ml.uml.extractor import get_extractor


def parse_requirements(requirements: list[str]) -> list[dict]:
    """
    Parameters
    ----------
    requirements : list[str]
        Raw requirement strings (from the Streamlit text area or file upload).

    Returns
    -------
    list[dict]
        Each record: {"id": int, "requirement": str, "actor": str, "action": str}
    """
    if not requirements:
        return []

    extractor = get_extractor()
    parsed:     list[dict] = []
    seen_pairs: set[tuple]  = set()   # (actor_lower, action_lower)
    req_id:     int         = 0

    for req in requirements:
        text = str(req).strip()
        if not text or text.lower() in ("nan", "none", "null", ""):
            continue

        pairs = extractor.extract_pairs(text)

        for pair in pairs:
            actor  = pair["actor"]
            action = pair["action"]
            key    = (actor.lower(), action.lower())

            if key in seen_pairs:
                continue          # skip global duplicate

            seen_pairs.add(key)
            req_id += 1
            parsed.append({
                "id":          req_id,
                "requirement": text,
                "actor":       actor,
                "action":      action,
            })

    return parsed