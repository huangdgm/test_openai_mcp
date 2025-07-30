"""
GTI (Google Threat Intelligence) Agent Module

This module provides the GTI agent functionality for the enhanced MCP orchestrator.
The GTI agent is responsible for querying the Google Threat Intelligence platform
for threat actor information, indicators, and intelligence through MCP server integration.

The agent uses Azure OpenAI to analyze GTI responses and provide structured
insights from threat intelligence data.
"""

from agents import Agent
from config.config_manager import config_manager
from agents import OpenAIChatCompletionsModel

def get_gti_agent(mcp_server, openai_client):
    """
    Create a GTI (Google Threat Intelligence) agent with MCP server integration.
    
    This function creates an agent that can query the Google Threat Intelligence
    platform for threat actor information, indicators, and intelligence. The agent
    is configured with MCP server integration to access GTI functionality and uses
    Azure OpenAI to analyze and structure the responses.
    
    Args:
        mcp_server: The GTI MCP server instance for platform access
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        Agent: A configured GTI agent with:
            - Name: "GTI Specialist"
            - Instructions: Detailed instructions for GTI queries and analysis
            - MCP Servers: GTI MCP server for platform integration
            - Model: Azure OpenAI GPT-4o
            
    Example:
        >>> agent = get_gti_agent(gti_server, openai_client)
        >>> result = await Runner.run(agent, "Search for APT28 threat actor")
        >>> print(result.final_output)
        # Returns structured analysis of GTI threat intelligence data
    """
    return Agent(
        name=config_manager.get("agents.gti.name"),
        instructions=config_manager.get("agents.gti.instructions"),
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        ),
        mcp_servers=[mcp_server]
    ) 