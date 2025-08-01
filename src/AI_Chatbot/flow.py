import getpass
import os

if not os.environ.get("AZURE_OPENAI_API_KEY"):
  os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass("Enter API key for Azure: ")

from langchain_openai import AzureChatOpenAI

model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

def outbound_opening_flow(state):
    name_confirmed = state["slots"].get("customer_confirmed")
    someone_else = state["slots"].get("not_customer")
    callback_time = state["slots"].get("callback_time")

    if someone_else:
        return {"next_prompt": "Please let Matthew Monreal know they can call us back at (844) 810-2274. Thank you."}

    if name_confirmed is None:
        return {"next_prompt": "Hi, is this Matthew Monreal?"}

    if name_confirmed is True:
        if callback_time:
            return {"next_prompt": "Thank you. We’ll call you back then."}
        return {"next_prompt": "This is Amanda Xuuu from Dash Of Cash. I see you’ve been pre-approved for 800.00. Is now a good time to complete the process?"}

    return {"next_prompt": "No worries — when would be a better time for us to call back?"}
