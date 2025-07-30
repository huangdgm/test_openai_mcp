"""
Orchestrator Agent Module

This module provides the orchestrator agent functionality for the enhanced MCP orchestrator.
The orchestrator agent is responsible for analyzing user queries and determining which
specialized agents should handle the request (ServiceNow, GTI, OpenSearch, or multiple).

The agent uses Azure OpenAI to analyze query context and keywords to make intelligent
routing decisions for optimal service selection.
"""

from agents import Agent
from models import ServiceDecision
from config.config_manager import config_manager
from agents import OpenAIChatCompletionsModel

def get_orchestrator_agent(openai_client):
    """
    Create an orchestrator agent for determining which services to query.
    
    This function creates an agent that analyzes user queries to determine
    which specialized agents should handle the request. The agent considers
    keywords, context, and the nature of the request to make intelligent
    routing decisions.
    
    Args:
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        Agent: A configured orchestrator agent with:
            - Name: "Orchestrator"
            - Instructions: Detailed instructions for service determination
            - Output Type: ServiceDecision Pydantic model
            - Model: Azure OpenAI GPT-4o
            
    Example:
        >>> agent = get_orchestrator_agent(openai_client)
        >>> result = await Runner.run(agent, "Analyze this query: Find security incidents")
        >>> decision = result.final_output
        >>> print(f"ServiceNow: {decision.servicenow}, GTI: {decision.gti}")
        ServiceNow: True, GTI: False
    """
    return Agent(
        name=config_manager.get("agents.orchestrator.name"),
        instructions=config_manager.get("agents.orchestrator.instructions"),
        output_type=ServiceDecision,
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        )
    ) 