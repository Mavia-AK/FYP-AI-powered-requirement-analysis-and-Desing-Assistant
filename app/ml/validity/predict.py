# app/ml/validity/predict.py
"""
Rule-based Requirement Validity Detection.

Classifies input text as Valid Requirement or various invalid types.
"""

import re
from typing import Dict, Any

# Known actors (from extractor)
KNOWN_ACTORS = [
    "system administrator", "system admin",
    "delivery staff", "delivery driver", "delivery person",
    "restaurant owner", "store manager", "store owner",
    "super admin", "super-admin",
    "end user", "new user", "registered user",
    "guest user", "anonymous user",
    "bank teller", "help desk",
    "administrator", "admin", "user", "customer", "client",
    "manager", "staff", "operator", "student", "teacher",
    "librarian", "employee", "driver", "vendor", "buyer",
    "seller", "agent", "moderator", "supervisor", "owner",
    "guest", "member", "patient", "doctor", "nurse",
    "cashier", "receptionist", "instructor", "professor",
    "supplier", "courier", "reader", "author", "editor",
    "viewer", "subscriber", "tenant", "landlord",
    "system", "application", "platform", "software", "server", "api", "database", "ui", "interface"
]

# Modal verbs
MODALS = ["shall", "must", "should", "can", "will", "may", "might", "could"]

# Action verbs (subset)
ACTION_VERBS = [
    "add", "remove", "delete", "create", "edit", "update", "manage", "browse",
    "search", "filter", "sort", "display", "show", "select", "choose", "pick",
    "place", "submit", "upload", "download", "export", "import", "login",
    "register", "authenticate", "view", "access", "retrieve", "store", "save",
    "modify", "calculate", "compute", "process", "handle", "perform", "allow",
    "enable", "support", "provide", "facilitate", "print", "send", "receive",
    "transmit", "book", "reserve", "schedule", "track", "monitor", "assign",
    "approve", "reject", "cancel", "register", "login", "log in", "manage",
    "update", "view", "book", "schedule", "assign", "record", "generate",
    "track", "create", "submit", "download", "access", "reset", "change",
    "list", "log", "out", "sign", "in", "up", "out", "password", "profile",
    "email", "notification", "alert", "message", "report", "invoice", "payment",
    "billing", "diagnose", "prescribe", "appointment", "schedule", "reserve",
    "borrow", "return", "renew", "rate", "review", "comment", "feedback",
    "complaint", "issue", "problem", "error", "bug", "fix", "resolve", "load", "scale", "respond",
    "notify", "ensure", "keep", "protect", "authenticate", "encrypt", "decrypt", "handle", "maintain",
    "operate", "function", "execute", "render", "display", "navigate", "route", "redirect"
]

# Common personal names (subset)
PERSONAL_NAMES = [
    "john", "jane", "mike", "sarah", "david", "lisa", "mark", "anna",
    "paul", "emma", "chris", "olivia", "daniel", "sophia", "matthew", "ava",
    "luke", "isabella", "josh", "mia", "ryan", "charlotte", "adam", "amelia",
    "muhammad", "ahmed", "fatima", "omar", "ali", "zara", "hassan", "ayesha",
    "chemistry", "physics", "math", "biology", "history", "english", "science",
]

# Domain keywords (subset)
DOMAIN_KEYWORDS = [
    "pdf", "export", "reports", "dashboard", "login", "fast", "secure",
    "performance", "response", "time", "latency", "throughput", "availability",
    "reliability", "scalability", "security", "encryption", "backup", "recovery",
    "usability", "accessibility", "compatibility", "portability", "testability",
    "memory", "cpu", "storage", "bandwidth", "concurrent", "load", "fault",
    "tolerance", "data", "integrity", "consistency", "audit", "logging",
    "compliance", "privacy", "gdpr", "efficiency", "robustness", "resilience",
]


def _clean_text(text: str) -> str:
    """Clean and normalize text."""
    return re.sub(r'[^\w\s]', '', text.lower()).strip()


def _get_meaningful_words(text: str) -> list[str]:
    """Get meaningful words (exclude stop words)."""
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can", "shall"}
    words = _clean_text(text).split()
    return [w for w in words if w not in stop_words and len(w) > 2]


def _has_actor(text: str) -> bool:
    """Check if text contains known actors."""
    words = _clean_text(text).split()
    return any(actor in " ".join(words) for actor in KNOWN_ACTORS)


def _has_modal(text: str) -> bool:
    """Check if text contains modal verbs."""
    words = _clean_text(text).split()
    return any(m in words for m in MODALS)


def _has_action_verb(text: str) -> bool:
    """Check if text contains action verbs."""
    words = _clean_text(text).split()
    return any(v in words for v in ACTION_VERBS)


def _is_mostly_personal_names(text: str) -> bool:
    """Check if text is mostly personal names."""
    words = _clean_text(text).split()
    if not words:
        return False
    name_count = sum(1 for w in words if w in PERSONAL_NAMES)
    return name_count / len(words) > 0.5


def _is_mostly_nouns(text: str) -> bool:
    """Simple check: if no verbs, mostly nouns."""
    words = _clean_text(text).split()
    verb_count = sum(1 for w in words if w in ACTION_VERBS or w in MODALS)
    return verb_count == 0 and len(words) > 1


def _is_domain_keywords_only(text: str) -> bool:
    """Check if text is only domain keywords without structure."""
    words = _clean_text(text).split()
    if not words:
        return False
    keyword_count = sum(1 for w in words if w in DOMAIN_KEYWORDS)
    return keyword_count == len(words) and len(words) < 4


def predict_validity(text: str) -> Dict[str, Any]:
    """
    Predict requirement validity using rule-based approach.

    Returns:
        dict: {"label": str, "confidence": float, "reason": str}
    """
    if not text or not text.strip():
        return {"label": "Irrelevant / Noise", "confidence": 1.0, "reason": "Empty input"}

    cleaned = _clean_text(text)
    words = cleaned.split()
    meaningful_words = _get_meaningful_words(text)

    # Rule 1: Less than 4 meaningful words
    if len(meaningful_words) < 4:
        return {"label": "Incomplete Fragment", "confidence": 0.9, "reason": "Too few meaningful words"}

    # Rule 2: Mostly personal names
    if _is_mostly_personal_names(text):
        return {"label": "Personal Name / Random Text", "confidence": 0.95, "reason": "Mostly personal names"}

    # Rule 3: No action verb
    if not _has_action_verb(text):
        # Check if mostly nouns
        if _is_mostly_nouns(text):
            return {"label": "Incomplete Fragment", "confidence": 0.8, "reason": "No action verbs, mostly nouns"}
        else:
            return {"label": "Non-requirement Sentence", "confidence": 0.7, "reason": "No action verbs"}

    # Rule 4: No actor
    if not _has_actor(text):
        # Check if domain keywords only
        if _is_domain_keywords_only(text):
            return {"label": "Domain Keywords Only", "confidence": 0.8, "reason": "Only domain keywords without structure"}
        else:
            return {"label": "Irrelevant / Noise", "confidence": 0.6, "reason": "No recognized actor"}

    # Rule 5: No modal verbs (but has actor and verb)
    if not _has_modal(text):
        return {"label": "Non-requirement Sentence", "confidence": 0.7, "reason": "No modal verbs like shall, must"}

    # If passes all rules, likely valid
    return {"label": "Valid Requirement", "confidence": 0.9, "reason": "Passes validity checks"}