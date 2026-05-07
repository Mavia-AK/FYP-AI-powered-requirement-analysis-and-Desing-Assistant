# app/ml/uml/graph_builder.py
from __future__ import annotations
from collections import defaultdict

_NOISE_USE_CASES: set[str] = {
    "Contact", "Enable", "Disable", "Access", "Store",
    "Process", "Future Growth", "Data Integrity",
}

_GENERIC_SINGLE: set[str] = {
    "create", "update", "manage", "view", "access",
    "store", "process", "enable", "disable", "it",
}

# Actor display order (most privileged first)
ACTOR_ORDER: list[str] = [
    "Administrator", "Admin", "System Administrator",
    "Manager", "Supervisor",
    "Doctor", "Nurse",
    "Receptionist", "Cashier", "Staff",
    "Teacher", "Instructor", "Professor", "Librarian",
    "Student", "Employee",
    "Customer", "Client", "Patient", "Member", "Guest",
    "User",
    "System",
]


def _actor_rank(actor: str) -> int:
    a = actor.strip().title()
    for i, name in enumerate(ACTOR_ORDER):
        if a == name or a.startswith(name):
            return i
    return len(ACTOR_ORDER)


def _is_noise(uc: str) -> bool:
    if uc in _NOISE_USE_CASES:
        return True
    if uc.lower() in _GENERIC_SINGLE:
        return True
    if len(uc.strip()) < 4:
        return True
    return False


def build_graph(parsed_requirements: list[dict]) -> dict:
    if not parsed_requirements:
        return {
            "actors": [], "use_cases": [], "relationships": [],
            "include_edges": [], "extend_edges": [],
            "actor_groups": {}, "uc_counts": {}, "parsed": [],
        }

    actors_set:    set[str]             = set()
    uc_set:        set[str]             = set()
    seen_pairs:    set[tuple[str, str]] = set()
    relationships: list[dict]           = []
    actor_groups:  dict[str, set[str]]  = defaultdict(set)
    uc_counts:     dict[str, int]       = defaultdict(int)

    for req in parsed_requirements:
        actor    = req.get("actor",  "").strip()
        use_case = req.get("action", "").strip()
        if not actor or not use_case:
            continue
        if _is_noise(use_case):
            continue

        actors_set.add(actor)
        uc_set.add(use_case)
        actor_groups[actor].add(use_case)
        uc_counts[use_case] += 1

        pair = (actor, use_case)
        if pair not in seen_pairs:
            relationships.append({"actor": actor, "use_case": use_case})
            seen_pairs.add(pair)

    # Remove System actor if real actors cover all its use-cases
    real_actors = {a for a in actors_set if a != "System"}
    if real_actors and "System" in actor_groups:
        real_ucs   = {uc for a in real_actors for uc in actor_groups[a]}
        system_ucs = actor_groups["System"]
        unique     = system_ucs - real_ucs
        if not unique:
            del actor_groups["System"]
            actors_set.discard("System")
            relationships = [r for r in relationships if r["actor"] != "System"]
        else:
            actor_groups["System"] = unique

    # Rebuild uc_set
    uc_set = {uc for ucs in actor_groups.values() for uc in ucs}

    # Sort actors by role priority
    sorted_actors = sorted(actor_groups.keys(), key=_actor_rank)

    # Sort use-cases per actor alphabetically
    sorted_groups: dict[str, list[str]] = {
        a: sorted(actor_groups[a]) for a in sorted_actors
    }

    # Global sorted use-cases (all unique)
    sorted_ucs = sorted(uc_set)

    return {
        "actors":        sorted_actors,
        "use_cases":     sorted_ucs,
        "relationships": relationships,
        "include_edges": [],
        "extend_edges":  [],
        "actor_groups":  sorted_groups,
        "uc_counts":     dict(uc_counts),
        "parsed":        parsed_requirements,
    }