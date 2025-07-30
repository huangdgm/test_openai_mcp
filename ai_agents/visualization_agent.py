"""
Visualization Agent Module

This module provides the visualization agent functionality for the enhanced MCP orchestrator.
The visualization agent is responsible for analyzing data from multiple sources (ServiceNow,
GTI, OpenSearch) and generating appropriate visualizations and summaries for presentation.

The agent uses Azure OpenAI to analyze data and determine the best visualization types
and generate Python code snippets for creating visualizations.
"""

from agents import Agent
from models import VisualizationResult
from config.config_manager import config_manager
from agents import OpenAIChatCompletionsModel

def get_visualization_agent(openai_client):
    """
    Create a visualization agent for generating data visualizations and summaries.
    
    This function creates an agent that analyzes data from ServiceNow, GTI, and OpenSearch
    sources to generate appropriate visualizations and summaries. The agent determines
    the best visualization type and provides Python code snippets for creating the
    visualizations.
    
    Args:
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        Agent: A configured visualization agent with:
            - Name: "Visualization Agent"
            - Instructions: Detailed instructions for data visualization
            - Output Type: VisualizationResult Pydantic model
            - Model: Azure OpenAI GPT-4o
            
    Example:
        >>> agent = get_visualization_agent(openai_client)
        >>> result = await Runner.run(agent, "Analyze this data and create visualization...")
        >>> viz_result = result.final_output
        >>> print(f"Summary: {viz_result.summary}")
        >>> print(f"Visualization Type: {viz_result.visualization_type}")
    """
    return Agent(
        name=config_manager.get("agents.visualization.name"),
        instructions=config_manager.get("agents.visualization.instructions"),
        output_type=VisualizationResult,
        model=OpenAIChatCompletionsModel(
            model=config_manager.get("azure_openai.model"),
            openai_client=openai_client
        )
    )