# AI_Chatbot/nodes.py
import os
from .schemas import Slots   # import your Pydantic model
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model = "gpt-4.1",
    api_key               = os.getenv("OPENAI_API_KEY"),   # ← env var, not literal
    temperature           = 0,
)

extract_llm = llm.with_structured_output(Slots)

def extract_node(state: dict) -> dict:
    """
    Pull slot values from state['user_input'] and merge into state['slots'].
    """
    slots = extract_llm.invoke(state["user_input"])
    state.setdefault("slots", {}).update(slots.model_dump())
    return state
