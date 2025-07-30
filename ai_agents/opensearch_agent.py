"""
OpenSearch Agent Module

This module provides the OpenSearch agent functionality for the enhanced MCP orchestrator.
The OpenSearch agent is responsible for querying the OpenSearch platform for log data,
metrics, and analytics through MCP server integration.

The agent uses Azure OpenAI to analyze OpenSearch responses and provide structured
insights from search results and log data.
"""

from typing import List
from openai import AsyncAzureOpenAI
from agents import Agent
from agents.mcp import MCPServer
from config.config_manager import config_manager
from agents import OpenAIChatCompletionsModel


def get_opensearch_agent(mcp_server: MCPServer, openai_client: AsyncAzureOpenAI) -> Agent:
    """
    Create an OpenSearch agent with MCP server integration.
    
    This function creates an agent that can query the OpenSearch platform for
    log data, metrics, and analytics. The agent is configured with MCP server
    integration to access OpenSearch functionality and uses Azure OpenAI to
    analyze and structure the responses.
    
    Args:
        mcp_server (MCPServer): The OpenSearch MCP server instance for platform access
        openai_client (AsyncAzureOpenAI): The Azure OpenAI client for agent communication
        
    Returns:
        Agent: A configured OpenSearch agent with:
            - Name: "OpenSearch Specialist"
            - Instructions: Detailed instructions for OpenSearch queries and analysis
            - MCP Servers: OpenSearch MCP server for platform integration
            - Model: Azure OpenAI GPT-4o
            
    Example:
        >>> agent = get_opensearch_agent(opensearch_server, openai_client)
        >>> result = await Runner.run(agent, "List all indices in the cluster")
        >>> print(result.final_output)
        # Returns structured analysis of OpenSearch indices
    """
    return Agent(
        name=config_manager.get("agents.opensearch.name"),
        instructions=config_manager.get("agents.opensearch.instructions"),
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        ),
        mcp_servers=[mcp_server]
    )