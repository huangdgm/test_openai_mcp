from agents import Agent, OpenAIChatCompletionsModel
from models import HasSensitiveInformation
from config.config_manager import config_manager

def get_guardrail_agent(openai_client):
    return Agent(
        name=config_manager.get("agents.guardrail.name"),
        instructions=config_manager.get("agents.guardrail.instructions"),
        output_type=HasSensitiveInformation,
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        )
    )