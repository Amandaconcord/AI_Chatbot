import os
from .schemas import Slots
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    deployment_name="gpt-4.1",  # ← match your Azure model deployment name
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint="https://amanda-test-resource.cognitiveservices.azure.com/",
    api_version="2024-12-01-preview",
    temperature=0,
)

extract_llm = llm.with_structured_output(Slots)

def extract_node(state: dict) -> dict:
    slots = extract_llm.invoke(state["user_input"])
    state.setdefault("slots", {}).update(slots.model_dump())
    return state
