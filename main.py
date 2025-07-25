"""
Enhanced MCP Orchestrator with Guardrail Protection

This module implements a multi-agent orchestration system that can query both ServiceNow
and Google Threat Intelligence (GTI) platforms while providing guardrail protection
against sensitive information exposure.

The system consists of:
- Guardrail Agent: Checks for sensitive credentials and secrets
- Orchestrator Agent: Determines which services to query based on user input
- ServiceNow Agent: Queries ServiceNow platform via MCP server
- GTI Agent: Queries Google Threat Intelligence via MCP server
- Aggregator Agent: Combines and summarizes results from multiple sources
"""

from dotenv import load_dotenv
import os
import asyncio
from openai import AsyncAzureOpenAI
from agents import gen_trace_id, trace
from config.config_manager import config_manager
from agents.mcp import MCPServerStdio
from orchestration import run

# Load default .env file first to get the environment type, e.g. development, staging, production, etc.
load_dotenv(dotenv_path=os.path.expanduser(f"~/.env"))

if os.getenv("ENV") is None:
    raise ValueError("ENV environment variable is required, please set it in the .env file. It will be default to 'development' if not set.")

# Load configuration from yaml file(s) based on the environment type, and store the configs in config_manager
config_manager.load_config()

# Load environment-specific .env file based on the environment type
# The .env.{environment} contains the environment-specific API keys, etc.
load_dotenv(dotenv_path=os.path.expanduser(f"~/.env.{config_manager.environment}"), override=True)

# Initialize Azure OpenAI client
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

if azure_endpoint is None:
    raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
if api_key is None:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")

azure_openai_client = AsyncAzureOpenAI(
    api_key=api_key,
    api_version=config_manager.get("azure_openai.api_version"),
    azure_endpoint=azure_endpoint,
    azure_deployment=config_manager.get("azure_openai.azure_deployment")
)

async def main():
    """
    Main entry point that initializes and starts the MCP servers.
    
    This function:
    1. Starts both GTI and ServiceNow MCP servers with proper configuration
    2. Sets up tracing for monitoring and debugging
    3. Executes the main workflow with the configured servers
    
    The servers are configured with:
    - GTI: Uses uv to run the GTI MCP server
    - ServiceNow: Uses Python virtual environment with proxy settings
    
    Example:
        >>> asyncio.run(main())
        # Starts servers and processes queries
    """
    print("🔧 Starting MCP servers...")
    
    # Start both GTI and ServiceNow MCP servers
    async with MCPServerStdio(
        name=config_manager.get("mcp_servers.gti.name"),
        params={
            "command": config_manager.get("mcp_servers.gti.command"),
            "args": config_manager.get("mcp_servers.gti.args")
        }
    ) as gti_server, MCPServerStdio(
        name=config_manager.get("mcp_servers.servicenow.name"),
        params={
            "command": config_manager.get("mcp_servers.servicenow.command"),
            "args": config_manager.get("mcp_servers.servicenow.args")
        }
    ) as servicenow_server:
        print("✅ MCP servers started successfully!")
        trace_id = gen_trace_id()
        with trace(workflow_name="Enhanced MCP Orchestrator", trace_id=trace_id):
            print(f"🔍 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(gti_server, servicenow_server, azure_openai_client)

if __name__ == "__main__":
    asyncio.run(main())
