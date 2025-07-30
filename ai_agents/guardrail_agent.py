"""
Guardrail Agent Module

This module provides the guardrail agent functionality for the enhanced MCP orchestrator.
The guardrail agent is responsible for checking user queries for sensitive information
such as passwords, API keys, tokens, and other credentials before processing.

The agent uses Azure OpenAI to analyze queries and determine if they contain
sensitive information that should not be processed by the system.
"""

from agents import Agent, OpenAIChatCompletionsModel
from models import HasSensitiveInformation
from config.config_manager import config_manager

def get_guardrail_agent(openai_client):
    """
    Create a guardrail agent for checking sensitive information in user queries.
    
    This function creates an agent that analyzes user queries to detect potential
    security risks such as passwords, API keys, tokens, or other credentials.
    The agent is configured with specific instructions to be conservative and
    only flag clear security risks while allowing internal identifiers.
    
    Args:
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        Agent: A configured guardrail agent with:
            - Name: "Guardrail Check"
            - Instructions: Detailed instructions for sensitive information detection
            - Output Type: HasSensitiveInformation Pydantic model
            - Model: Azure OpenAI GPT-4o
            
    Example:
        >>> agent = get_guardrail_agent(openai_client)
        >>> result = await Runner.run(agent, "Check this query: Find incidents for user john")
        >>> print(result.final_output.has_sensitive_information)
        False
    """
    return Agent(
        name=config_manager.get("agents.guardrail.name"),
        instructions=config_manager.get("agents.guardrail.instructions"),
        output_type=HasSensitiveInformation,
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        )
    )