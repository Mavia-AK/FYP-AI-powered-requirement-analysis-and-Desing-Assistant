"""
Quick test for OpenRouter API with a free model.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent / ".env")

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("[ERROR] OPENROUTER_API_KEY not found in .env")
    exit(1)

print(f"[OK] Key loaded: {api_key[:12]}...{api_key[-4:]}")

# OpenRouter uses the OpenAI-compatible API
import urllib.request
import urllib.error
import json

url = "https://openrouter.ai/api/v1/chat/completions"
payload = json.dumps({
    "model": "inclusionai/ling-2.6-flash:free",
    "messages": [
        {"role": "user", "content": "Say 'Hello from OpenRouter!' and nothing else."}
    ]
}).encode("utf-8")

req = urllib.request.Request(url, data=payload, method="POST")
req.add_header("Authorization", f"Bearer {api_key}")
req.add_header("Content-Type", "application/json")

print("[...] Sending test request to OpenRouter (google/gemini-2.0-flash-exp:free)...")

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        reply = data["choices"][0]["message"]["content"]
        print(f"[OK] Response: {reply}")
        print("[OK] OpenRouter API is working!")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    print(f"[ERROR] HTTP {e.code}: {body}")
except Exception as e:
    print(f"[ERROR] {e}")
