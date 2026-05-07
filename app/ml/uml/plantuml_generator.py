from __future__ import annotations

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from typing import Dict, Any

from app.ml.uml.openrouter_client import call_openrouter as _call_openrouter


def _safe_id(text: str) -> str:
    """Alphanumeric + underscore identifier."""
    return re.sub(r"[^A-Za-z0-9]", "_", text.strip())


def _create_plantuml_prompt(graph: dict) -> str:
    """Create a detailed prompt for generating PlantUML code."""
    actors = graph.get("actors", [])
    use_cases = graph.get("use_cases", [])
    relationships = graph.get("relationships", [])
    include_edges = graph.get("include_edges", [])
    extend_edges = graph.get("extend_edges", [])

    prompt = f"""Generate a high-quality PlantUML Use Case diagram code based on the following data:

ACTORS:
{chr(10).join(f"- {actor}" for actor in actors)}

USE CASES:
{chr(10).join(f"- {uc}" for uc in use_cases)}

RELATIONSHIPS (Actor to Use Case):
{chr(10).join(f"- {rel['actor']} --> {rel['use_case']}" for rel in relationships)}

INCLUDE RELATIONSHIPS:
{chr(10).join(f"- {edge['from_uc']} includes {edge['to_uc']}" for edge in include_edges)}

EXTEND RELATIONSHIPS:
{chr(10).join(f"- {edge['from_uc']} extends {edge['to_uc']}" for edge in extend_edges)}

Requirements for the PlantUML code:
1. Start with @startuml and end with @enduml
2. Use proper PlantUML syntax for use case diagrams
3. Include a system boundary rectangle containing all use cases
4. Use actor icons (:Actor:) for actors
5. Use proper arrow notation for relationships
6. Use <<include>> and <<extend>> stereotypes for include/extend relationships
7. Include skinparam settings for professional appearance:
   - White background (PDF-safe)
   - Clean, modern styling
   - Proper colors for actors and use cases
   - No handwritten style
8. Make the diagram readable and well-organized
9. Use meaningful IDs for elements
10. Include proper spacing and organization

Generate only the PlantUML code, no explanations or additional text."""

    return prompt


# -----------------------------------------------------------------------------
# PlantUML
# -----------------------------------------------------------------------------

def generate_plantuml(graph: dict) -> str:
    """
    Generate PlantUML code using OpenRouter API for high-quality use case diagrams.
    Falls back to basic generation if API fails.
    """
    try:
        # Create prompt
        prompt = _create_plantuml_prompt(graph)

        # Generate PlantUML code using OpenRouter
        raw_response = _call_openrouter(prompt)

        if raw_response:
            # Clean up: strip markdown fences if present
            plantuml_code = raw_response.strip()
            if plantuml_code.startswith("```"):
                # Remove ```plantuml or ``` wrapper
                lines = plantuml_code.split("\n")
                lines = lines[1:]  # drop opening ```
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]  # drop closing ```
                plantuml_code = "\n".join(lines).strip()

            # Ensure it starts with @startuml
            if not plantuml_code.startswith('@startuml'):
                plantuml_code = '@startuml\n' + plantuml_code

            # Ensure it ends with @enduml
            if not plantuml_code.endswith('@enduml'):
                plantuml_code += '\n@enduml'

            return plantuml_code
        else:
            print("Warning: OpenRouter API returned empty response, falling back to basic generation")
            return _generate_plantuml_fallback(graph)

    except Exception as e:
        print(f"Warning: OpenRouter API failed ({str(e)}), falling back to basic generation")
        return _generate_plantuml_fallback(graph)


def _generate_plantuml_fallback(graph: dict) -> str:
    """
    Fallback PlantUML generation using the original method.
    Safe for PDF embedding (white background, no dark theme).
    """
    actors        = graph.get("actors",        [])
    use_cases     = graph.get("use_cases",     [])
    rels          = graph.get("relationships", [])
    include_edges = graph.get("include_edges", [])
    extend_edges  = graph.get("extend_edges",  [])

    lines: list[str] = [
        "@startuml",
        "",
        "' ── Skin ────────────────────────────────────────────────────────",
        "skinparam backgroundColor #FFFFFF",
        "skinparam handwritten false",
        "skinparam defaultFontName Segoe UI",
        "skinparam defaultFontSize 12",
        "",
        "skinparam actor {",
        "  BackgroundColor #DDEEFF",
        "  BorderColor     #1565C0",
        "  FontColor       #0D1B3E",
        "  FontStyle       bold",
        "}",
        "",
        "skinparam usecase {",
        "  BackgroundColor #FFFFFF",
        "  BorderColor     #455A64",
        "  FontColor       #1A237E",
        "  BorderThickness 1.5",
        "}",
        "",
        "skinparam ArrowColor  #37474F",
        "skinparam ArrowFontSize 10",
        "skinparam shadowing false",
        "",
    ]

    # Actor declarations
    for actor in actors:
        a_id = _safe_id(actor)
        lines.append(f'actor :{actor}: as {a_id}')

    lines.append("")

    # System boundary
    lines.append('rectangle "System" {')
    for uc in use_cases:
        uc_id = f"UC_{_safe_id(uc)}"
        lines.append(f'  ({uc}) as {uc_id}')
    lines.append("}")

    lines.append("")

    # Association edges
    for rel in rels:
        a_id  = _safe_id(rel["actor"])
        uc_id = f"UC_{_safe_id(rel['use_case'])}"
        lines.append(f"{a_id} --> {uc_id}")

    # «include» edges
    if include_edges:
        lines.append("")
        for edge in include_edges:
            src = f"UC_{_safe_id(edge['from_uc'])}"
            tgt = f"UC_{_safe_id(edge['to_uc'])}"
            lines.append(f"{src} .> {tgt} : <<include>>")

    # «extend» edges
    if extend_edges:
        lines.append("")
        for edge in extend_edges:
            src = f"UC_{_safe_id(edge['from_uc'])}"
            tgt = f"UC_{_safe_id(edge['to_uc'])}"
            lines.append(f"{src} .> {tgt} : <<extend>>")

    lines += ["", "@enduml"]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Mermaid
# ─────────────────────────────────────────────────────────────────────────────

def generate_mermaid(graph: dict) -> str:
    """
    Return Mermaid flowchart source (LR layout).

    Node shapes
    ───────────
    Actor    → ["label"]   rectangle
    Use Case → (("label")) stadium/oval  ← standard Mermaid oval syntax
    """
    actors        = graph.get("actors",        [])
    use_cases     = graph.get("use_cases",     [])
    rels          = graph.get("relationships", [])
    include_edges = graph.get("include_edges", [])
    extend_edges  = graph.get("extend_edges",  [])

    lines: list[str] = ["graph LR", ""]

    # Actor nodes  ── plain rectangle
    for actor in actors:
        nid   = _safe_id(actor)
        label = actor.replace('"', "'")
        lines.append(f'    {nid}["{label}"]')

    lines.append("")

    # Use-case nodes  ── oval / stadium
    for uc in use_cases:
        nid   = f"UC_{_safe_id(uc)}"
        label = uc.replace('"', "'")
        lines.append(f'    {nid}(("{label}"))')

    lines.append("")

    # Association edges  ── solid arrow
    for rel in rels:
        src = _safe_id(rel["actor"])
        tgt = f"UC_{_safe_id(rel['use_case'])}"
        lines.append(f"    {src} --> {tgt}")

    # «include» edges  ── dashed arrow with label
    if include_edges:
        lines.append("")
        for edge in include_edges:
            src = f"UC_{_safe_id(edge['from_uc'])}"
            tgt = f"UC_{_safe_id(edge['to_uc'])}"
            lines.append(f'    {src} -. "«include»" .-> {tgt}')

    # «extend» edges  ── dotted arrow with label
    if extend_edges:
        lines.append("")
        for edge in extend_edges:
            src = f"UC_{_safe_id(edge['from_uc'])}"
            tgt = f"UC_{_safe_id(edge['to_uc'])}"
            lines.append(f'    {src} -. "«extend»" .-> {tgt}')

    # ── Class styles ──────────────────────────────────────────────────────────
    lines += [
        "",
        "    classDef actor   fill:#DDEEFF,stroke:#1565C0,stroke-width:2px,"
        "color:#0D1B3E,font-weight:bold",
        "    classDef usecase fill:#FFFFFF,stroke:#455A64,stroke-width:1.5px,"
        "color:#1A237E",
        "    classDef include fill:#F9FBE7,stroke:#827717,stroke-width:1px,"
        "color:#33691E,font-style:italic",
    ]

    if actors:
        ids = ",".join(_safe_id(a) for a in actors)
        lines.append(f"    class {ids} actor")

    if use_cases:
        ids = ",".join(f"UC_{_safe_id(u)}" for u in use_cases)
        lines.append(f"    class {ids} usecase")

    return "\n".join(lines)