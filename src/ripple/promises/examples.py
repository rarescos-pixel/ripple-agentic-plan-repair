"""Domain data for the hero, never branches in the reconciliation engine."""
from __future__ import annotations


def fact(name): return {"fact": name}
def literal(value): return {"literal": value}
def eq(name, value): return {"eq": [fact(name), literal(value)]}
def both(a, b): return {"and": [a, b]}
def implies(a, b): return {"implies": [a, b]}


HERO_UTTERANCE = "Alexa, we're leaving for the airport at seven. Make sure the house is ready, but Mom is staying here tonight."


def household(start=1000):
    occupied = eq("guest_present", True)
    before_departure = {"lt": [fact("$now"), fact("departure_at")]}
    goal = both(eq("common_mode", "away"), both(
        implies(occupied, both(eq("guest_heat", "occupied"), eq("alarm_mode", "stay"))),
        implies({"not": [occupied]}, both(eq("guest_heat", "eco"), eq("alarm_mode", "full")))))
    contract = {
        "goal": goal, "goal_at": fact("departure_at"),
        "invariants": [
            {"id": "authorized_access", "label": "Mom keeps her access, even when she goes out", "predicate": eq("guest_access", True)},
            {"id": "occupied_comfort", "label": "Keep occupied areas comfortable", "predicate": implies(occupied, eq("guest_heat", "occupied"))},
            {"id": "occupied_security", "label": "Keep stay security while Mom is home or before departure", "predicate": implies({"or": [occupied, before_departure]}, eq("alarm_mode", "stay"))},
            {"id": "departure_timing", "label": "Keep the shared home active until departure", "predicate": implies(before_departure, eq("common_mode", "home"))},
        ],
        "assumptions": [{"id": "guest_stays", "predicate": occupied},
                        {"id": "departure_as_planned", "predicate": eq("departure_at", start + 60)}],
        "authority": {"common_mode": "APPROVAL_REQUIRED", "guest_heat": "APPROVAL_REQUIRED", "alarm_mode": "APPROVAL_REQUIRED", "guest_access": "FORBIDDEN"},
        "expiry": {"at": start + 200}, "completion": eq("departure_verified", True),
        "evidence": {"source": "household-twin", "max_age_seconds": 30},
        "meaning": "Prepare the house at your departure time. Keep Mom's access even if she goes out. Keep occupied areas comfortable and use stay security while she is home. Propose eco heat for empty guest areas. Full security and away transition also require independently observed family departure. Ask before every consequential change; stop after verified completion or expiry.",
        "questions": [],
    }
    catalog = {
        "common_mode": {"values": ["home", "away"], "times": ["goal"], "reversible": True,
                        "requires": implies(eq("common_mode", "away"), eq("family_departed", True))},
        "guest_heat": {"values": ["occupied", "eco"], "times": ["now", "goal"], "reversible": True},
        "alarm_mode": {"values": ["stay", "full"], "times": ["now", "goal"], "reversible": True,
                       "requires": implies(eq("alarm_mode", "full"), eq("family_departed", True))},
    }
    facts = {"common_mode": "home", "guest_present": True, "guest_heat": "occupied",
             "alarm_mode": "stay", "guest_access": True, "departure_at": start + 60,
             "departure_verified": False, "family_departed": False}
    return contract, catalog, facts
