from agents import Agent
from models import ServiceDecision
from config.config_manager import config_manager
from agents import OpenAIChatCompletionsModel

def get_orchestrator_agent(openai_client):
    return Agent(
        name=config_manager.get("agents.orchestrator.name"),
        instructions=config_manager.get("agents.orchestrator.instructions"),
        output_type=ServiceDecision,
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        )
    ) 