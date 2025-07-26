from agents import Agent
from models import VisualizationResult
from config.config_manager import config_manager
from agents import OpenAIChatCompletionsModel

def get_visualization_agent(openai_client):
    return Agent(
        name=config_manager.get("agents.visualization.name"),
        instructions=config_manager.get("agents.visualization.instructions"),
        output_type=VisualizationResult,
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        )
    ) 