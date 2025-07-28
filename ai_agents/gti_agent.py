from agents import Agent
from config.config_manager import config_manager
from agents import OpenAIChatCompletionsModel

def get_gti_agent(mcp_server, openai_client):
    return Agent(
        name=config_manager.get("agents.gti.name"),
        instructions=config_manager.get("agents.gti.instructions"),
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        ),
        mcp_servers=[mcp_server]
    ) 