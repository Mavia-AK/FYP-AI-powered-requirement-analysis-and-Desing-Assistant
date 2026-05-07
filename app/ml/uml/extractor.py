# app/ml/uml/extractor.py
from __future__ import annotations
import re

KNOWN_ACTORS: list[str] = [
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
]

NFR_SIGNALS: list[str] = [
    r"\bperformance\b", r"\blatency\b", r"\bthroughput\b",
    r"\bresponse time\b", r"\buptime\b", r"\bavailability\b",
    r"\bscalabilit", r"\breliabilit",
    r"\bencrypt", r"\bcompress", r"\bcache\b",
    r"\b\d+\s*(?:ms|seconds?|minutes?|hours?|%)\b",
    r"\bSLA\b", r"\bRTO\b", r"\bRPO\b",
    r"\bconcurrent\s+users?\b", r"\bload\s+balance",
    r"\bfault.toleran", r"\bdisaster.recover",
    r"\buser.friendly\b", r"\bscalable\b", r"\bbackup mechanism",
    r"\bdata integrity\b", r"\bfuture growth\b",
    r"\bsecure\b", r"\breliable\b",
]
_NFR_RE = re.compile("|".join(NFR_SIGNALS), re.IGNORECASE)
_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')
_COORD_SPLIT = re.compile(r"\s+(?:and|or|as well as)\s+", re.IGNORECASE)

# ── Predefined domain use-case rules ─────────────────────────────────────────
# Format: (actor, use_case) triggered by keyword patterns in sentence
DOMAIN_RULES: list[tuple[str, str, str]] = [
    # (actor, use_case, keyword_pattern)
    # Admin
    ("Administrator", "Manage Users",             r"\b(?:manage|manage user|user account)\b"),
    ("Administrator", "Send Notifications",        r"\bnotif(?:y|ication)\b"),
    ("Administrator", "Generate Reports",          r"\bgenerate\s+report\b"),
    ("Administrator", "Resolve Feedback",          r"\b(?:review|address|resolve).*(?:feedback|complaint|issue)\b"),
    ("Administrator", "Manage Doctors",            r"\b(?:manage|maintain).*doctor\b"),
    ("Administrator", "View Patient Records",      r"\bview.*patient\b"),
    ("Administrator", "Manage Appointments",       r"\bmanage.*appointment\b"),
    # Doctor
    ("Doctor",        "Record Diagnosis",          r"\b(?:record|diagnos)\b"),
    ("Doctor",        "Create Prescription",       r"\bprescri(?:be|ption)\b"),
    ("Doctor",        "Manage Medical Records",    r"\bmedical\s+record\b"),
    ("Doctor",        "View Patient Records",      r"\bview.*patient\b"),
    ("Doctor",        "Manage Appointments",       r"\bappointment\b"),
    # Receptionist
    ("Receptionist",  "Manage Appointments",       r"\bappointment\b"),
    ("Receptionist",  "Manage Patient Records",    r"\bpatient\s+(?:record|information|info)\b"),
    ("Receptionist",  "Register/Login",            r"\b(?:register|log\s*in|login)\b"),
    # Patient
    ("Patient",       "Book Appointment",          r"\bbook\s+appointment\b"),
    ("Patient",       "Register/Login",            r"\b(?:register|log\s*in|login)\b"),
    ("Patient",       "View Prescription",         r"\bview.*prescri\b"),
    ("Patient",       "View Schedule",             r"\bview.*(?:schedule|slot|time)\b"),
    ("Patient",       "Submit Feedback/Complaint", r"\b(?:feedback|complaint|submit)\b"),
    ("Patient",       "View Payment History",      r"\bpayment.*histor\b"),
    ("Patient",       "Manage Profile",            r"\b(?:profile|personal)\b"),
    # Billing / shared
    ("Administrator", "Manage Payments",           r"\bpayment\b"),
    ("Administrator", "Generate Invoice",          r"\binvoice\b"),
    ("Doctor",        "Generate Invoice",          r"\binvoice\b"),
]

ACTION_VERBS: dict[str, str] = {
    "log in":              "Login",
    "login":               "Login",
    "log-in":              "Login",
    "log out":             "Logout",
    "logout":              "Logout",
    "sign in":             "Login",
    "sign up":             "Register",
    "sign out":            "Logout",
    "register":            "Register",
    "authenticate":        "Authenticate",
    "reset password":      "Reset Password",
    "change password":     "Change Password",
    "update profile":      "Update Profile",
    "edit profile":        "Update Profile",
    "create":              "Create {OBJ}",
    "add":                 "Add {OBJ}",
    "update":              "Update {OBJ}",
    "edit":                "Edit {OBJ}",
    "modify":              "Edit {OBJ}",
    "delete":              "Delete {OBJ}",
    "remove":              "Remove {OBJ}",
    "manage":              "Manage {OBJ}",
    "view":                "View {OBJ}",
    "display":             "View {OBJ}",
    "show":                "View {OBJ}",
    "browse":              "Browse {OBJ}",
    "search":              "Search",
    "filter":              "Filter {OBJ}",
    "book appointment":    "Book Appointment",
    "schedule appointment":"Schedule Appointment",
    "book":                "Book Appointment",
    "schedule":            "Schedule {OBJ}",
    "prescribe":           "Create Prescription",
    "record":              "Record {OBJ}",
    "diagnose":            "Record Diagnosis",
    "billing":             "Generate Invoice",
    "invoice":             "Generate Invoice",
    "payment":             "Make Payment",
    "appointment":         "Book Appointment",
    "assign":              "Assign {OBJ}",
    "approve":             "Approve {OBJ}",
    "reject":              "Reject {OBJ}",
    "cancel":              "Cancel {OBJ}",
    "track":               "Track {OBJ}",
    "monitor":             "Monitor {OBJ}",
    "report":              "Generate Report",
    "generate report":     "Generate Report",
    "generate":            "Generate {OBJ}",
    "upload":              "Upload {OBJ}",
    "download":            "Download {OBJ}",
    "submit":              "Submit {OBJ}",
    "send":                "Send Notification",
    "notify":              "Send Notification",
    "feedback":            "Submit Feedback",
    "complaint":           "Submit Complaint",
    "access":              "Access {OBJ}",
    "select":              "Select {OBJ}",
    "verify":              "Verify {OBJ}",
    "confirm":             "Confirm {OBJ}",
    "calculate":           "Calculate {OBJ}",
    "process":             "Process {OBJ}",
    "check":               "Check {OBJ}",
    "share":               "Share {OBJ}",
    "save":                "Save {OBJ}",
    "retrieve":            "Retrieve {OBJ}",
    "borrow":              "Borrow Book",
    "return":              "Return Book",
    "renew":               "Renew Book",
    "rate":                "Rate {OBJ}",
    "review":              "Write Review",
}

_OBJ_RE = re.compile(
    r"""
    (?:(?:a|an|the|their|his|her|its|this|that|all|any|new|existing)\s+)*
    ((?:[A-Za-z]+\s+){0,2}[A-Za-z]+)
    (?=\s*(?:and|or|,|\.|\?|!|$|
             \bto\b|\bfor\b|\bwith\b|\busing\b|\bvia\b|
             \bwhen\b|\bwhere\b|\bwhich\b|\bthat\b|
             \bshall\b|\bmust\b|\bwill\b|
             \bcan\b|\bcould\b|\bshould\b|
             \bmay\b|\bmight\b))
    """,
    re.VERBOSE | re.IGNORECASE,
)
_SKIP_OBJECTS: set[str] = {
    "the", "a", "an", "able", "system", "application", "platform",
    "it", "this", "that", "they", "user", "users", "when", "where",
    "which", "needed", "required", "possible", "allowed",
}

_SYSTEM_DELEGATE_RE = re.compile(
    r'(?:the\s+)?system\s+(?:allows?|enables?|permits?)\s+'
    r'(?:the\s+)?(?P<actor>' +
    "|".join(re.escape(a) for a in sorted(KNOWN_ACTORS, key=len, reverse=True)) +
    r')\s+to\s',
    re.IGNORECASE,
)


def _actor_alt() -> str:
    return "|".join(
        re.escape(a) for a in sorted(KNOWN_ACTORS, key=len, reverse=True)
    )


def _clean_label(label: str) -> str:
    filler = {"a", "an", "the", "to", "their", "its", "when",
               "needed", "required", "if", "where", "which"}
    words = [w for w in label.split() if w.lower() not in filler]
    return " ".join(w.capitalize() for w in words) if words else label.title()


def _capture_object(after: str) -> str | None:
    m = _OBJ_RE.match(after.strip())
    if not m:
        return None
    obj = m.group(1).strip()
    obj = re.sub(
        r'\s+(?:when|where|which|that|if|needed|required|allowed|possible)\s*$',
        '', obj, flags=re.IGNORECASE
    ).strip()
    if obj.lower() in _SKIP_OBJECTS or len(obj) < 2:
        return None
    obj = re.sub(r'^(?:a|an|the)\s+', '', obj, flags=re.IGNORECASE).strip()
    return _clean_label(obj) if obj else None


def _fill(template: str, obj: str | None) -> str:
    if "{OBJ}" not in template:
        return template
    if obj:
        return template.replace("{OBJ}", obj)
    return template.replace(" {OBJ}", "").replace("{OBJ}", "").strip()


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]


class RequirementExtractor:
    def __init__(self) -> None:
        actor_alt = _actor_alt()
        self._sorted_verbs = sorted(ACTION_VERBS.keys(), key=len, reverse=True)
        self._subject_patterns: list[re.Pattern] = [
            _SYSTEM_DELEGATE_RE,
            re.compile(
                rf'(?:the\s+)?({actor_alt})'
                rf'\s+(?:shall|can|must|will|should|may|is able to)\s',
                re.IGNORECASE,
            ),
            re.compile(rf'^(?:the\s+)?({actor_alt})\s+', re.IGNORECASE),
            re.compile(
                rf'(?:allow|enable|permit)\s+(?:the\s+)?({actor_alt})\s+to\s',
                re.IGNORECASE,
            ),
            re.compile(rf'as\s+an?\s+({actor_alt})[,\s]', re.IGNORECASE),
            re.compile(rf'({actor_alt})\'s\s', re.IGNORECASE),
        ]

    def extract_pairs(self, text: str) -> list[dict]:
        text = str(text).strip()
        if not text or text.lower() in {"nan", "none", "null"}:
            return []
        sentences = _split_sentences(text)
        if len(sentences) <= 1:
            return self._from_sentence(text)
        all_pairs: list[dict] = []
        prev_actor: str | None = None
        for sent in sentences:
            pairs = self._from_sentence(sent, fallback_actor=prev_actor)
            if pairs:
                prev_actor = pairs[0]["actor"]
                all_pairs.extend(pairs)
        return all_pairs

    def _from_sentence(
        self, sentence: str, fallback_actor: str | None = None
    ) -> list[dict]:
        if not sentence:
            return []
        if _NFR_RE.search(sentence):
            return []

        # ── Try domain rules first ────────────────────────────────────────────
        domain_pairs = self._apply_domain_rules(sentence)
        if domain_pairs:
            return domain_pairs

        actor = self._detect_actor(sentence)
        if actor is None and fallback_actor:
            if re.search(
                r'^(?:it|the system|this|the application)\s+',
                sentence, re.IGNORECASE
            ):
                actor = fallback_actor

        segments = _COORD_SPLIT.split(sentence)
        pairs: list[dict] = []
        seen: set[str] = set()
        for seg in segments:
            action = self._detect_action(seg)
            if action and action not in seen:
                seen.add(action)
                pairs.append({"actor": actor or "System", "action": action})

        if not pairs:
            action = self._detect_action(sentence)
            if action and action not in seen:
                pairs.append({"actor": actor or "System", "action": action})

        if actor is None and fallback_actor is None:
            noise = {"Search", "Filter", "Sort", "Access",
                     "View", "Enable", "Disable"}
            pairs = [p for p in pairs if p["action"] not in noise]

        return pairs

    def _apply_domain_rules(self, sentence: str) -> list[dict]:
        """Match sentence against predefined domain rules."""
        results: list[dict] = []
        seen: set[tuple] = set()
        for actor, use_case, pattern in DOMAIN_RULES:
            if re.search(pattern, sentence, re.IGNORECASE):
                key = (actor, use_case)
                if key not in seen:
                    seen.add(key)
                    results.append({"actor": actor, "action": use_case})
        return results

    def _detect_actor(self, text: str) -> str | None:
        for pat in self._subject_patterns:
            m = pat.search(text)
            if m:
                try:
                    raw = m.group("actor")
                except IndexError:
                    raw = m.group(1)
                return raw.strip().title()
        return None

    def _detect_action(self, text: str) -> str | None:
        low = text.lower()
        for key in self._sorted_verbs:
            m = re.search(r'\b' + re.escape(key) + r'\b', low)
            if not m:
                continue
            template = ACTION_VERBS[key]
            if "{OBJ}" in template:
                after = text[m.end():]
                obj   = _capture_object(after)
                return _fill(template, obj)
            return template
        return None


_instance: RequirementExtractor | None = None


def get_extractor() -> RequirementExtractor:
    global _instance
    if _instance is None:
        _instance = RequirementExtractor()
    return _instance