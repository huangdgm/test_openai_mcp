from agents import Agent
from config.config_manager import config_manager
from agents import OpenAIChatCompletionsModel

def make_servicenow_agent(mcp_server, openai_client):
    servicenow_config = config_manager.get("agents.servicenow")
    return Agent(
        name=servicenow_config["name"],
        instructions=servicenow_config["instructions"],
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        ),
        mcp_servers=[mcp_server]
    ) 