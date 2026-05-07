# app/ml/uml/ai_refiner.py
"""
AI-powered refinement of rule-based UML extraction.

Takes the raw requirements and the graph produced by the rule-based
extractor/graph_builder, sends both to OpenRouter, and returns a
corrected graph with proper actors, use cases, and relationships.
"""
from __future__ import annotations

import json
import re
from typing import Any

from app.ml.uml.openrouter_client import call_openrouter


def _build_refinement_prompt(
    requirements: list[str],
    graph: dict,
) -> str:
    """Build a prompt that gives the AI both the raw text and the
    current (possibly incorrect) extraction so it can correct it."""

    req_block = "\n".join(
        f"  {i}. {r}" for i, r in enumerate(requirements, 1)
    )

    current_actors    = graph.get("actors", [])
    current_ucs       = graph.get("use_cases", [])
    current_rels      = graph.get("relationships", [])
    current_includes  = graph.get("include_edges", [])
    current_extends   = graph.get("extend_edges", [])

    current_block = json.dumps({
        "actors":        current_actors,
        "use_cases":     current_ucs,
        "relationships": [
            {"actor": r["actor"], "use_case": r["use_case"]}
            for r in current_rels
        ],
        "include_edges": current_includes,
        "extend_edges":  current_extends,
    }, indent=2)

    return f"""You are a UML Use Case Diagram expert. I need you to extract actors, use cases, and relationships from software requirements.

A rule-based system already attempted an extraction but it may be WRONG. Your job is to produce the CORRECT extraction.

## RAW REQUIREMENTS:
{req_block}

## RULE-BASED EXTRACTION (may be incorrect):
{current_block}

## STRICT RULES - FOLLOW EXACTLY:

### Actors:
- An actor is a HUMAN ROLE that interacts with the system (e.g., "User", "Administrator", "Customer", "Doctor")
- If requirements say "the system shall allow users to..." then the actor is "User"
- If requirements say "the system shall..." without mentioning a specific role, the actor is "User" (the person using the system)
- NEVER use "System" as an actor - the system is what is BEING BUILT, not an actor
- NEVER INVENT actors that are not mentioned or implied in the requirements. Only use actors that the requirements text actually refers to
- If no specific roles are mentioned, just use "User" as the single actor
- Use title case: "User", "Administrator", "Customer"

### Use Cases:
- Extract use cases ONLY from functional requirements (things the system DOES for the user)
- Use clear verb-noun format: "Upload Document", "View Report", "Classify Requirements"
- NEVER use single-word use cases like "Upload" or "Generate" — always include the object
- Skip section headings, labels, numbering prefixes, and non-functional requirements
- Skip requirements about performance, security, scalability (these are NOT use cases)

### Relationships:
- Every use case MUST be connected to at least one actor
- Map each actor to the use cases they would actually interact with

### Include/Extend edges:
- Only add include/extend edges when the requirements EXPLICITLY state a dependency
- "include": Use case A ALWAYS requires use case B (e.g., "Place Order" always includes "Process Payment")
- "extend": Use case A OPTIONALLY triggers use case B
- Do NOT chain every use case into include edges just because they appear in sequence
- If unsure, leave include_edges and extend_edges as empty arrays []

## RESPOND WITH ONLY this JSON (no markdown fences, no explanation, no text before or after):
{{"actors":["Actor1"],"use_cases":["Use Case 1","Use Case 2"],"relationships":[{{"actor":"Actor1","use_case":"Use Case 1"}},{{"actor":"Actor1","use_case":"Use Case 2"}}],"include_edges":[],"extend_edges":[]}}"""


def _parse_json_response(text: str) -> dict | None:
    """Extract and parse JSON from the AI response, handling markdown
    fences and other wrapper text."""
    text = text.strip()

    # Try to extract from markdown code fences
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find the JSON object in the text
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass

    return None


def _validate_graph(data: dict) -> dict | None:
    """Validate that the parsed JSON has the expected structure."""
    if not isinstance(data, dict):
        return None

    actors = data.get("actors")
    use_cases = data.get("use_cases")
    relationships = data.get("relationships")

    if not isinstance(actors, list) or not actors:
        return None
    if not isinstance(use_cases, list) or not use_cases:
        return None
    if not isinstance(relationships, list) or not relationships:
        return None

    # Validate each relationship has required keys
    valid_rels = []
    for rel in relationships:
        if not isinstance(rel, dict):
            continue
        if "actor" not in rel or "use_case" not in rel:
            continue
        valid_rels.append(rel)

    if not valid_rels:
        return None

    # Ensure include/extend edges have proper structure
    include_edges = data.get("include_edges", [])
    extend_edges = data.get("extend_edges", [])

    if not isinstance(include_edges, list):
        include_edges = []
    if not isinstance(extend_edges, list):
        extend_edges = []

    # Clean include/extend edges
    valid_includes = [
        e for e in include_edges
        if isinstance(e, dict) and "from_uc" in e and "to_uc" in e
    ]
    valid_extends = [
        e for e in extend_edges
        if isinstance(e, dict) and "from_uc" in e and "to_uc" in e
    ]

    # Build actor_groups for compatibility with existing code
    actor_groups: dict[str, list[str]] = {}
    for rel in valid_rels:
        actor = rel["actor"]
        uc = rel["use_case"]
        if actor not in actor_groups:
            actor_groups[actor] = []
        if uc not in actor_groups[actor]:
            actor_groups[actor].append(uc)

    # Sort groups
    for actor in actor_groups:
        actor_groups[actor] = sorted(actor_groups[actor])

    # Build parsed records for the mapping table
    parsed_records = []
    for idx, rel in enumerate(valid_rels, 1):
        parsed_records.append({
            "id":          idx,
            "requirement": f"{rel['actor']} -> {rel['use_case']}",
            "actor":       rel["actor"],
            "action":      rel["use_case"],
        })

    return {
        "actors":        list(actors),
        "use_cases":     list(use_cases),
        "relationships": valid_rels,
        "include_edges": valid_includes,
        "extend_edges":  valid_extends,
        "actor_groups":  actor_groups,
        "uc_counts":     {},
        "parsed":        parsed_records,
    }


def refine_graph(
    requirements: list[str],
    graph: dict,
) -> dict:
    """
    Use OpenRouter AI to refine the rule-based UML extraction.

    Parameters
    ----------
    requirements : list[str]
        Raw requirement strings from the user.
    graph : dict
        The graph produced by `build_graph()`.

    Returns
    -------
    dict
        A corrected graph dict. Falls back to the original graph
        if the AI call fails.
    """
    # Don't bother refining if there are no requirements
    if not requirements:
        return graph

    try:
        prompt = _build_refinement_prompt(requirements, graph)
        response = call_openrouter(prompt, timeout=90)

        parsed = _parse_json_response(response)
        if parsed is None:
            print("Warning: AI refiner returned unparseable response, "
                  "keeping original extraction")
            return graph

        validated = _validate_graph(parsed)
        if validated is None:
            print("Warning: AI refiner returned invalid graph structure, "
                  "keeping original extraction")
            return graph

        return validated

    except Exception as e:
        print(f"Warning: AI refinement failed ({e}), "
              f"keeping original extraction")
        return graph
