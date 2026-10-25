import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from matchmaker import *

def test_opening_is_exact_and_never_sent():
    c = add_candidate("test_user", "contacted_first", adult_confirmed=True)
    assert c.drafts[0]["text"].startswith("Assalamualaikum ji")
    assert c.drafts[0]["sent_by_system"] is False
    assert c.age_volunteered == "unknown" and c.religion_volunteered == "unknown"

def test_no_adult_no_track():
    try:
        add_candidate("x", "mutual_accepted", adult_confirmed=False)
        raise AssertionError("should have raised")
    except ValueError:
        pass

def test_consent_gate():
    c = add_candidate("x", "mutual_accepted", adult_confirmed=True)
    try:
        guntur_draft(c); raise AssertionError("should require consent")
    except ValueError:
        pass
    record_ai_consent(c, False)
    assert c.status == "closed"

def test_guntur_outside_closes():
    c = add_candidate("x", "contacted_first", adult_confirmed=True)
    record_ai_consent(c, True)
    assert guntur_draft(c)["text"] == "Aap Guntur se ho kya?"
    record_location(c, "Hyderabad")
    assert c.status == "closed"

def test_promising_threshold():
    c = add_candidate("x", "contacted_first", adult_confirmed=True)
    record_ai_consent(c, True)
    record_location(c, "Guntur")
    record_volunteered(c, "religion", "Muslim")
    c.incoming_messages, c.positive_signals = 3, 3
    c.mutual_effort, c.mutual_romantic_interest, c.serious_intention = True, True, True
    assert evaluate(c) is False, "3 incoming must not be promising"
    c.incoming_messages = 4
    assert evaluate(c) is True
    note = promising_notification(c)
    assert note and "PROMISING GUNTUR MATCH FOUND" in note
    assert "Open conversation to take over personally" in note

def test_delete():
    assert delete_all() == {"candidates": [], "conversations": []}

if __name__ == "__main__":
    for fn in [test_opening_is_exact_and_never_sent, test_no_adult_no_track,
               test_consent_gate, test_guntur_outside_closes,
               test_promising_threshold, test_delete]:
        fn(); print("PASS", fn.__name__)
    print("ALL 6 TESTS PASSED")
