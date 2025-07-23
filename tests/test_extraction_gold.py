# tests/test_extraction_gold.py
import json, pathlib, pytest
from AI_Chatbot.nodes import extract_node

GOLD = pathlib.Path("data/gold/gold_calls.jsonl")
@pytest.mark.parametrize("row", [json.loads(l) for l in GOLD.open()])
def test_extract(row):
    state = {"user_input": row["text"], "slots": {}}
    out   = extract_node(state)
    assert out["slots"] == row["slots"]      # simple equality check
