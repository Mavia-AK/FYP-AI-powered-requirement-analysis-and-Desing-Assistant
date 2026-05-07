"""
Test with the exact requirements from the user's screenshot.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent / ".env")

from app.ml.uml.parser import parse_requirements
from app.ml.uml.graph_builder import build_graph
from app.ml.uml.ai_refiner import refine_graph

# Exact requirements from the user's screenshot
requirements = [
    "1: The system shall allow users to upload documents (TXT, DOCX, PDF).",
    "2: The system shall extract text content from uploaded documents.",
    "3: The system shall preprocess text content (tokenization, stopword removal, lemmatization).",
    "1: The system shall identify vague/ambiguous terms (e.g., fast, user-friendly).",
    "2: The system shall suggest clearer alternatives for vague requirements.",
    "3: The system shall classify requirements into Functional and Non-Functional.",
    "4: The system shall provide a report of unclear vs. clear requirements.",
    "1: The system shall recommend design patterns/architectures based on requirement types.",
    "1: The system shall automatically generate UML Use Case Diagrams from structured requirements.",
    "2: The system shall automatically generate UML Class Diagrams for functional requirements.",
    "1: The system shall provide a web interface where users can upload documents.",
    "3: The system shall display recommended design patterns.",
]

print("=" * 60)
print("RULE-BASED EXTRACTION:")
print("=" * 60)
parsed = parse_requirements(requirements)
graph = build_graph(parsed)
print(f"Actors: {graph['actors']}")
print(f"Use Cases: {graph['use_cases']}")
for r in graph["relationships"]:
    print(f"  {r['actor']} --> {r['use_case']}")

print("\n" + "=" * 60)
print("AI-REFINED EXTRACTION:")
print("=" * 60)
refined = refine_graph(requirements, graph)
print(f"Actors: {refined['actors']}")
print(f"Use Cases: {refined['use_cases']}")
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

print(f"\nMapping table entries: {len(refined.get('parsed', []))}")
for p in refined.get("parsed", []):
    print(f"  #{p['id']}: {p['actor']} -> {p['action']}")
