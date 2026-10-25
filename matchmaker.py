"""Snapchat Guntur Matchmaker AI — local, approval-only logic.

No network calls. No Snapchat login. No sending.
The system creates DRAFTS for shaik's approval; shaik sends manually
in Snapchat himself. Data is local JSON in this project only.
"""
import json, os
from dataclasses import dataclass, field, asdict

BASE = os.path.dirname(os.path.abspath(__file__))
OPENING = ("Assalamualaikum ji \U0001f60a Main Siraaj ki taraf se ek AI "
           "introduction assistant hoon. Agar aap comfortable ho toh kya "
           "hum thodi baat kar sakte hain?")
GUNTUR_Q = "Aap Guntur se ho kya?"
MARRIAGE_Q = ("Agar future mein hum dono shaadi karna chahein aur ghar "
              "wale raazi na hon, toh aap kya sochogi? Kya hum dono "
              "milkar unko samjha sakte hain?")
VALID_BASES = {"contacted_first", "mutual_accepted", "known_personally"}

@dataclass
class Candidate:
    username: str
    basis: str
    adult_confirmed: bool = False
    age_volunteered: str = "unknown"
    religion_volunteered: str = "unknown"
    location_volunteered: str = "unknown"
    ai_consent: str = "not_asked"  # not_asked | yes | no
    status: str = "pending_approval"  # pending_approval|draft_ready|active|closed|promising|paused
    incoming_messages: int = 0
    positive_signals: int = 0
    mutual_effort: bool = False
    mutual_romantic_interest: bool = False
    serious_intention: bool = False
    marriage_expectations: str = "unknown"
    intimacy_topic: str = "not_discussed"  # not_discussed | permission_given | declined
    drafts: list = field(default_factory=list)
    observations: list = field(default_factory=list)

def add_candidate(username, basis, adult_confirmed=False):
    """Manual add only. Never infer anything from name/photo."""
    if basis not in VALID_BASES:
        raise ValueError("basis must be contacted_first, mutual_accepted, or known_personally")
    if not adult_confirmed:
        raise ValueError("adult_confirmed is required before any romantic track")
    c = Candidate(username=username, basis=basis, adult_confirmed=True)
    c.drafts.append({"type": "opening", "text": OPENING, "sent_by_system": False})
    c.status = "draft_ready"
    return c

def record_ai_consent(c, answer):
    c.ai_consent = "yes" if answer else "no"
    c.status = "active" if answer else "closed"
    if not answer:
        c.observations.append("Declined AI-assisted conversation; track closed, no further drafts.")
    return c

def guntur_draft(c):
    if c.ai_consent != "yes":
        raise ValueError("Guntur question requires AI consent first")
    return {"type": "guntur_filter", "text": GUNTUR_Q, "sent_by_system": False}

def record_location(c, location_volunteered):
    c.location_volunteered = location_volunteered
    if location_volunteered.strip().lower() != "guntur":
        c.status = "closed"
        c.observations.append("Outside Guntur (volunteered); romantic track ended politely.")
    return c

def record_volunteered(c, field_name, value):
    """Only volunteered values. field_name in age/religion."""
    if field_name == "age":
        c.age_volunteered = value
    elif field_name == "religion":
        c.religion_volunteered = value
    else:
        raise ValueError("unknown field")
    return c

def evaluate(c):
    """Promising only on observed evidence + all volunteered confirmations."""
    promising = (
        c.adult_confirmed
        and c.religion_volunteered == "Muslim"
        and c.location_volunteered == "Guntur"
        and c.mutual_romantic_interest
        and c.serious_intention
        and c.incoming_messages >= 4
        and c.positive_signals >= 3
        and c.mutual_effort
        and c.ai_consent == "yes"
    )
    if promising:
        c.status = "promising"
    return promising

def promising_notification(c):
    if c.status != "promising":
        return None
    return (
        "\u2764\ufe0f PROMISING GUNTUR MATCH FOUND\n\n"
        f"Snapchat username: {c.username}\n"
        f"Age: {c.age_volunteered}\n"
        "Location: Guntur\n"
        "Religion: Muslim\n"
        f"Mutual romantic interest: {'yes - expressed' if c.mutual_romantic_interest else 'no'}\n"
        f"Compatibility observations: {c.incoming_messages} incoming messages, "
        f"{c.positive_signals} positive signals, mutual effort: {c.mutual_effort}\n"
        f"Marriage expectations: {c.marriage_expectations}\n"
        "Topics still unknown: anything not voluntarily disclosed\n"
        "Recommended next step: Open conversation to take over personally."
    )

def delete_all():
    return {"candidates": [], "conversations": []}

if __name__ == "__main__":
    print("Snapchat status: UNAVAILABLE (no permitted integration)")
    print("Opening draft:", OPENING)
