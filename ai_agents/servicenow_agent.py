"""
ServiceNow Agent Module

This module provides the ServiceNow agent functionality for the enhanced MCP orchestrator.
The ServiceNow agent is responsible for querying the ServiceNow platform for incident
and ticket information through MCP server integration.

The agent uses Azure OpenAI to analyze ServiceNow responses and provide structured
insights from incident and ticket data.
"""

from agents import Agent
from config.config_manager import config_manager
from agents import OpenAIChatCompletionsModel

def get_servicenow_agent(mcp_server, openai_client):
    """
    Create a ServiceNow agent with MCP server integration.
    
    This function creates an agent that can query the ServiceNow platform for
    incident and ticket information. The agent is configured with MCP server
    integration to access ServiceNow functionality and uses Azure OpenAI to
    analyze and structure the responses.
    
    Args:
        mcp_server: The ServiceNow MCP server instance for platform access
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        Agent: A configured ServiceNow agent with:
            - Name: "ServiceNow Specialist"
            - Instructions: Detailed instructions for ServiceNow queries and analysis
            - MCP Servers: ServiceNow MCP server for platform integration
            - Model: Azure OpenAI GPT-4o
            
    Example:
        >>> agent = get_servicenow_agent(servicenow_server, openai_client)
        >>> result = await Runner.run(agent, "Find security incidents")
        >>> print(result.final_output)
        # Returns structured analysis of ServiceNow incidents
    """
    return Agent(
        name=config_manager.get("agents.servicenow.name"),
        instructions=config_manager.get("agents.servicenow.instructions"),
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        ),
        mcp_servers=[mcp_server]
    ) 