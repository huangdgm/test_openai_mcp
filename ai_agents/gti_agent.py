from agents import Agent
from config.config_manager import config_manager
from agents import OpenAIChatCompletionsModel

def make_gti_agent(mcp_server, openai_client):
    gti_config = config_manager.get("agents.gti")
    return Agent(
        name=gti_config["name"],
        instructions=gti_config["instructions"],
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        ),
        mcp_servers=[mcp_server]
    ) 