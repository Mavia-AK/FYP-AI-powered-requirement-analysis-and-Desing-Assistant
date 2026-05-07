"""
Test the AI refiner with sample requirements.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from pathlib import Path

# Load .env
load_dotenv(Path(__file__).resolve().parent / ".env")

from app.ml.uml.parser import parse_requirements
from app.ml.uml.graph_builder import build_graph
from app.ml.uml.ai_refiner import refine_graph

# Sample requirements
requirements = [
    "1: The system shall allow users to upload documents (TXT, DOCX, PDF).",
    "2: The system shall extract text content from uploaded documents.",
    "3: The system shall preprocess text content (tokenization, stopword removal, lemmatization).",
    "1: The system shall identify vague/ambiguous terms (e.g., fast, user-friendly).",
    "2: The system shall suggest clearer alternatives for vague requirements.",
    "3: The system shall classify requirements into Functional and Non-Functional.",
    "4: The system shall provide a report of unclear vs. clear requirements.",
    "1: The system shall recommend design patterns/architectures based on requirement types.",
    "The administrator can manage user accounts and roles.",
    "The user shall be able to login with username and password.",
    "The customer can view order history and track deliveries.",
]

print("=" * 60)
print("STEP 1: Rule-based extraction")
print("=" * 60)

parsed = parse_requirements(requirements)
graph = build_graph(parsed)

print(f"\nActors:    {graph['actors']}")
print(f"Use Cases: {graph['use_cases']}")
print(f"Relations: {len(graph['relationships'])}")
for r in graph["relationships"]:
    print(f"  {r['actor']} --> {r['use_case']}")

print("\n" + "=" * 60)
print("STEP 2: AI Refinement")
print("=" * 60)

refined = refine_graph(requirements, graph)

print(f"\nActors:    {refined['actors']}")
print(f"Use Cases: {refined['use_cases']}")
print(f"Relations: {len(refined['relationships'])}")
for r in refined["relationships"]:
    print(f"  {r['actor']} --> {r['use_case']}")

if refined.get("include_edges"):
    print(f"\nIncludes:")
    for e in refined["include_edges"]:
        print(f"  {e['from_uc']} --include--> {e['to_uc']}")

if refined.get("extend_edges"):
    print(f"\nExtends:")
    for e in refined["extend_edges"]:
        print(f"  {e['from_uc']} --extend--> {e['to_uc']}")

print("\n[OK] AI refinement complete!")
