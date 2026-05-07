import os
import json
import torch
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.ml.uml.openrouter_client import call_openrouter

AMBIGUITY_MODEL_PATH      = "models/ambiguity"
CLASSIFICATION_MODEL_PATH = "models/classification_final"

VAGUE_TERMS = [
    "fast","quick","slow","rapid","swift","efficient","effective",
    "optimal","optimized","good","bad","better","best","worse","worst",
    "high","low","superior","inferior","robust","reliable","stable",
    "user-friendly","easy","simple","intuitive","convenient","accessible",
    "straightforward","secure","safe","protected","flexible","scalable",
    "adaptable","extensible","many","few","several","multiple","large",
    "small","enough","sufficient","appropriate","suitable","adequate",
    "improved","enhanced","upgraded","properly","correctly","accurately",
    "reasonable","acceptable","satisfactory",
]
WEAK_MODALS = ["may","might","could","should","would","can"]

def load_ambiguity_model():
    try:
        tok   = AutoTokenizer.from_pretrained(AMBIGUITY_MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(
            AMBIGUITY_MODEL_PATH
        )
        dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(dev).float().eval()
        return tok, model, dev
    except Exception as exc:
        print(f"Ambiguity model error: {exc}")
        return None, None, None

def load_classification_model():
    if not os.path.exists(CLASSIFICATION_MODEL_PATH):
        return None, None, None, 0.30
    try:
        tok   = AutoTokenizer.from_pretrained(CLASSIFICATION_MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(
            CLASSIFICATION_MODEL_PATH
        )
        dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(dev).float().eval()
        threshold = 0.30
        meta_path = os.path.join(CLASSIFICATION_MODEL_PATH, "training_meta.json")
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                threshold = json.load(f).get("best_threshold", 0.30)
        return tok, model, dev, threshold
    except Exception as exc:
        print(f"Classification model error: {exc}")
        return None, None, None, 0.30

def extract_requirements(text: str) -> list[str]:
    if not text or not text.strip():
        return []

    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

    if len(lines) > 1:
        cleaned = [l for l in lines if len(l) >= 15]
        if cleaned:
            return cleaned

    reqs = re.split(
        r'(?<=[.!?])\s+(?=[A-Z])|'
        r'\n\n+|'
        r'^(?:REQ|FR|NFR|SRS|RS|UC|US)[-\s]*\d+\s*[:.]\s*|'
        r'(?:^|\n)\s*\d+[:.]\s+',
        text.strip(),
        flags=re.MULTILINE,
    )
    cleaned = [r.strip() for r in reqs if len(r.strip()) >= 15]
    return cleaned if cleaned else [text.strip()]

def detect_vague_terms(text: str):
    if not text:
        return [], []
    low = text.lower()
    vague  = sorted({
        t for t in VAGUE_TERMS
        if re.search(r'\b' + re.escape(t) + r'(?:ly)?\b', low)
    })
    modals = sorted({
        m for m in WEAK_MODALS
        if re.search(r'\b' + re.escape(m) + r'\b', low)
    })
    return vague, modals

def get_ambiguity_reason(text, vague, modals, status):
    if status == "Clear":
        return "✅ Specific and measurable"
    reasons = []
    if vague:  reasons.append(f"Vague: {', '.join(vague[:2])}")
    if modals: reasons.append(f"Weak modals: {', '.join(modals[:2])}")
    has_num  = bool(re.search(r'\d+', text))
    has_unit = bool(re.search(
        r'\b(seconds?|ms|%|users?|MB|GB|minutes?|hours?)\b', text, re.I
    ))
    if not (has_num or has_unit):
        reasons.append("No measurable criteria")
    return " | ".join(reasons) if reasons else "Missing acceptance criteria"

def calculate_rqi(prob_ambiguous: float, text: str) -> float:
    clarity      = round(1 - prob_ambiguous, 3)
    has_num      = bool(re.search(r'\d+', text))
    has_unit     = bool(re.search(r'\b(seconds?|ms|%|users?|MB|GB)\b', text, re.I))
    specificity  = round(min((int(has_num) + int(has_unit)) / 2, 1.0), 3)
    completeness = round(min(len(text.strip().split()) / 15, 1.0), 3)
    return round(0.5*clarity + 0.25*completeness + 0.25*specificity, 3)

def predict_ambiguity(text, tokenizer, model, device):
    """
    Two-stage Ambiguity Prediction:
    1. Local BERT inference
    2. Gemini API refinement
    """
    bert_label = "Unknown"
    bert_conf = 0.5
    
    # Stage 1: BERT Inference
    if tokenizer and model:
        try:
            inputs = tokenizer(
                text, return_tensors="pt",
                truncation=True, max_length=256, padding=True
            ).to(device)
            with torch.no_grad():
                probs = torch.softmax(model(**inputs).logits.float(), dim=1)
                pred  = torch.argmax(probs, dim=1).item()
            bert_label = "Ambiguous" if pred == 1 else "Clear"
            bert_conf = probs[0][pred].item()
        except Exception as e:
            print(f"BERT Ambiguity Error: {e}")

    # Stage 2: Gemini Refinement (DISABLED FOR PERFORMANCE)
    # The synchronous API calls were causing severe bottlenecks.
    # We now rely exclusively on the local fine-tuned BERT core.
    """
    try:
        prompt = f"..."
        resp = call_openrouter(prompt)
        ...
    except Exception as e:
        print(f"Gemini Ambiguity Refinement Error: {e}")
    """

    # Fallback to BERT only
    return {
        "label_text": bert_label,
        "confidence": bert_conf,
        "prob_ambiguous": 0.9 if bert_label == "Ambiguous" else 0.1
    }

class RuleBasedClassifier:
    def __init__(self):
        self.fr_verbs = [
            "add","remove","delete","create","edit","update","manage","browse",
            "search","filter","sort","display","show","select","choose","pick",
            "place","submit","upload","download","export","import","login",
            "register","authenticate","view","access","retrieve","store","save",
            "modify","calculate","compute","process","handle","perform","allow",
            "enable","support","provide","facilitate","print","send","receive",
            "transmit","book","reserve","schedule","track","monitor","assign",
            "approve","reject","cancel","register", "login", "log in", "manage",
            "update", "view", "book", "schedule",
            "assign", "record", "generate",
            "track", "create", "submit",
            "download", "access","reset","change","list",
        ]
        self.fr_patterns = [
            r'user.*(?:shall|can|should|must).*(?:add|remove|view|edit|place|select|create)',
            r'(?:system|user).*allows?.*(?:to|users?)',
            r'.*\b(?:add|remove|edit|view|place|select|browse|search|create|manage)\b',
            r'.*\b(?:screen|dialog|form|button|menu|interface|page|dashboard)\b',
        ]
        self.nfr_attrs = [
            "performance","response time","throughput","latency","speed",
            "security","secure","encryption","encrypted","ssl","tls",
            "reliability","reliable","availability","uptime","downtime",
            "scalability","scalable","maintainability","usability",
            "user-friendly","easy","simple","intuitive","convenient","accessible",
            "straightforward","secure","safe","protected","flexible","scalable",
            "adaptable","extensible","many","few","several","multiple","large",
            "small","enough","sufficient","appropriate","suitable","adequate",
            "improved","enhanced","upgraded","properly","correctly","accurately",
            "reasonable","acceptable","satisfactory",
            "testability","backup","recovery","resilience","load","concurrent",
            "capacity","efficient","efficiency","optimal","robustness",
            "data integrity","consistency","audit","logging","compliance",
            "privacy","gdpr","memory","cpu","storage","bandwidth",
        ]
        self.nfr_patterns = [
            r'(?:shall|must|should).*(?:respond|return|complete|load).*(?:within|in|less than)\s*\d+',
            r'(?:shall|must).*support.*\d+.*(?:user|concurrent|transaction)',
            r'(?:shall|must).*(?:be|ensure|maintain).*(?:secure|reliable|available|scalable)',
            r'\b(?:throughput|latency|bandwidth|memory|storage|cpu)\b',
            r'.*\bencrypt\b.*',
            r'.*\bbackup\b.*',
            r'.*\b(?:support|handle)\s+\d+\s*(?:user|transaction|request)',
        ]

    def classify(self, text: str) -> dict:
        low = text.lower()
        fr_score = nfr_score = 0.0
        for v in self.fr_verbs:
            if re.search(r'\b' + re.escape(v) + r'\b', low):
                fr_score += 1.0
        for p in self.fr_patterns:
            if re.search(p, low):
                fr_score += 2.0
        for a in self.nfr_attrs:
            if re.search(r'\b' + re.escape(a) + r'\b', low):
                nfr_score += 1.0
        for p in self.nfr_patterns:
            if re.search(p, low):
                nfr_score += 2.0
        total = fr_score + nfr_score
        if total == 0:
            return {"label": 0, "label_text": "Functional (FR)", "confidence": 0.5}
        if fr_score >= nfr_score:
            return {"label": 0, "label_text": "Functional (FR)", "confidence": min(fr_score / total, 0.99)}
        return {"label": 1, "label_text": "Non-Functional (NFR)", "confidence": min(nfr_score / total, 0.99)}

def predict_fr_nfr_hybrid(text, tok, model, dev, threshold=0.3):
    """
    Two-stage Classification:
    1. Local BERT inference (Fine-tuned)
    2. Gemini API refinement
    """
    # Stage 1: BERT Inference
    bert_label = "Functional (FR)"
    bert_conf = 0.5
    prob_nfr = 0.5
    
    if tok and model:
        try:
            inputs = tok(
                text, return_tensors="pt",
                truncation=True, max_length=128, padding=True
            ).to(dev)
            with torch.no_grad():
                probs = torch.softmax(model(**inputs).logits.float(), dim=1)
                prob_nfr = probs[0][1].item()
                label_idx = 1 if prob_nfr >= threshold else 0
                bert_label = "Non-Functional (NFR)" if label_idx == 1 else "Functional (FR)"
                bert_conf = probs[0][label_idx].item()
        except Exception as e:
            print(f"BERT Classification Error: {e}")

    # Stage 2: Gemini Refinement (DISABLED FOR PERFORMANCE)
    # We now rely on the optimized local BERT models to ensure
    # enterprise-grade latency (< 50ms per requirement).
    """
    try:
        prompt = f"..."
        resp = call_openrouter(prompt)
        ...
    except Exception as e:
        print(f"Gemini Classification Refinement Error: {e}")
    """

    return {
        "label_text": bert_label,
        "prob_fr": 1 - prob_nfr,
        "prob_nfr": prob_nfr,
        "confidence": bert_conf,
        "method_used": "bert_only"
    }

def batch_refine_requirements(results: list[dict], selected_modules: list[str]) -> None:
    """
    Takes the preliminary results (populated by BERT) and performs a SINGLE
    batch API call to refine Ambiguity and Classification. Updates the list in-place.
    """
    valid_items = [r for r in results if r.get("Validity") == "Valid Requirement"]
    if not valid_items:
        return

    # Build the payload
    payload = []
    for item in valid_items:
        payload_item = {"id": item["#"], "text": item["Requirement"]}
        if "ambiguity" in selected_modules:
            payload_item["bert_ambiguity"] = item.get("Ambiguity", "Unknown")
        if "classification" in selected_modules:
            payload_item["bert_type"] = item.get("Type", "Unknown")
        payload.append(payload_item)

    prompt = f"""You are an Expert Requirements Engineering AI.
I am providing a JSON array of software requirements.
Your task is to analyze each requirement for Classification (FR/NFR) and Ambiguity (Clear/Ambiguous) based on strict software engineering principles.

Definitions:
- Functional (FR): Describes WHAT the system should do (actions, behaviors, user interactions, data processing). Example: "The system shall allow users to log in."
- Non-Functional (NFR): Describes HOW the system should operate (performance, security, usability, reliability, constraints). Example: "The system must load within 2 seconds."
- Clear: The requirement is specific, measurable, and unambiguous. Developers know exactly what to build without making assumptions.
- Ambiguous: The requirement contains vague words (e.g., "fast", "user-friendly", "secure", "efficient", "robust") or lacks specific measurable metrics/details.

Input Requirements JSON:
{json.dumps(payload, indent=2)}

For each requirement, provide the refined values. Return EXACTLY a JSON array of objects with this strict schema:
[
  {{
    "id": <int>,
    "final_ambiguity": "Clear" | "Ambiguous",
    "final_type": "Functional (FR)" | "Non-Functional (NFR)",
    "reason": "<One concise, highly detailed sentence explaining the FR/NFR classification AND why it is Clear/Ambiguous>"
  }}
]
DO NOT wrap the JSON in Markdown formatting like ```json ... ```. Just return the raw JSON array.
"""
    try:
        resp = call_openrouter(prompt, timeout=120)
        # Find JSON array
        match = re.search(r"\[.*\]", resp, re.DOTALL)
        if match:
            refined_data = json.loads(match.group())
            # Create lookup dict
            refinements = {r["id"]: r for r in refined_data if "id" in r}
            
            for item in valid_items:
                ref = refinements.get(item["#"])
                if ref:
                    if "ambiguity" in selected_modules:
                        item["Ambiguity"] = ref.get("final_ambiguity", item.get("Ambiguity"))
                        # Keep the BERT confidence, but update reason
                        if item["Ambiguity"] == "Ambiguous":
                            item["RQI Score"] = calculate_rqi(0.9, item["Requirement"])
                        else:
                            item["RQI Score"] = calculate_rqi(0.1, item["Requirement"])
                    
                    if "classification" in selected_modules:
                        item["Type"] = ref.get("final_type", item.get("Type"))
                        item["Method"] = "bert+batch_llm"
                    
                    # Update reason
                    existing = item.get("Reason", "")
                    new_reason = ref.get("reason", "")
                    if new_reason:
                        if existing and "Vague:" in existing:
                            item["Reason"] = f"{existing} | Refined: {new_reason}"
                        else:
                            item["Reason"] = new_reason

    except Exception as e:
        print(f"Batch Refinement Error: {e}. Falling back to local BERT.")

