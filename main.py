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
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStdio
import asyncio
import time
from pydantic import BaseModel
from typing import List, Optional

# Azure OpenAI imports
import os
from openai import AsyncAzureOpenAI
from agents import OpenAIChatCompletionsModel

# Configuration management
from config.config_manager import config_manager

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

azure_openai_model = OpenAIChatCompletionsModel(
    model=config_manager.get("azure_openai.model"),
    openai_client=azure_openai_client
)


class HasSensitiveInformation(BaseModel):
    """
    Model representing the result of a guardrail check.
    
    Attributes:
        has_sensitive_information (bool): True if sensitive information was detected
        reasoning (str): Explanation of why the content was flagged as sensitive
    """
    has_sensitive_information: bool
    reasoning: str


class ServiceNowQuery(BaseModel):
    """
    Model representing a ServiceNow query result.
    
    Attributes:
        query (str): The original query sent to ServiceNow
        result (str): The response from ServiceNow
        source (str): Source identifier, defaults to "ServiceNow"
    """
    query: str
    result: str
    source: str = "ServiceNow"


class GTIQuery(BaseModel):
    """
    Model representing a Google Threat Intelligence query result.
    
    Attributes:
        query (str): The original query sent to GTI
        result (str): The response from GTI
        source (str): Source identifier, defaults to "Google Threat Intelligence"
    """
    query: str
    result: str
    source: str = "Google Threat Intelligence"


class AggregatedResult(BaseModel):
    """
    Model representing the final aggregated result from multiple sources.
    
    Attributes:
        original_query (str): The original user query
        servicenow_results (Optional[List[ServiceNowQuery]]): Results from ServiceNow queries
        gti_results (Optional[List[GTIQuery]]): Results from GTI queries
        summary (str): Comprehensive summary of all results
        recommendations (Optional[List[str]]): Actionable recommendations based on findings
    """
    original_query: str
    servicenow_results: Optional[List[ServiceNowQuery]] = None
    gti_results: Optional[List[GTIQuery]] = None
    summary: str
    recommendations: Optional[List[str]] = None


class ServiceDecision(BaseModel):
    """
    Model representing the orchestrator's decision about which services to query.
    
    Attributes:
        servicenow (bool): Whether ServiceNow should be queried
        gti (bool): Whether Google Threat Intelligence should be queried
        reasoning (str): Explanation of the decision
    """
    servicenow: bool
    gti: bool
    reasoning: str


# Guardrail agent to check for sensitive information
guardrail_config = config_manager.get("agents.guardrail")
guardrail_agent = Agent(
    name=guardrail_config["name"],
    instructions=guardrail_config["instructions"],
    output_type=HasSensitiveInformation,
    model=azure_openai_model
)

# Orchestrator agent to determine which services to query
orchestrator_config = config_manager.get("agents.orchestrator")
orchestrator_agent = Agent(
    name=orchestrator_config["name"],
    instructions=orchestrator_config["instructions"],
    output_type=ServiceDecision,
    model=azure_openai_model
)

# Aggregator agent to process and combine results
aggregator_config = config_manager.get("agents.aggregator")
aggregator_agent = Agent(
    name=aggregator_config["name"],
    instructions=aggregator_config["instructions"],
    output_type=AggregatedResult,
    model=azure_openai_model
)

# Factory functions for specialist agents

def make_servicenow_agent(mcp_server):
    servicenow_config = config_manager.get("agents.servicenow")
    return Agent(
        name=servicenow_config["name"],
        instructions=servicenow_config["instructions"],
        model=azure_openai_model,
        mcp_servers=[mcp_server]
    )

def make_gti_agent(mcp_server):
    gti_config = config_manager.get("agents.gti")
    return Agent(
        name=gti_config["name"],
        instructions=gti_config["instructions"],
        model=azure_openai_model,
        mcp_servers=[mcp_server]
    )


async def check_guardrails(user_query: str) -> HasSensitiveInformation:
    """
    Check if the user query contains sensitive information that should be blocked.
    
    This function uses the guardrail agent to analyze the query for sensitive
    credentials, keys, or other secrets that should not be processed.
    
    Args:
        user_query (str): The user's query to be checked
        
    Returns:
        HasSensitiveInformation: Object containing the check result and reasoning
        
    Example:
        >>> result = await check_guardrails("find incidents for user john")
        >>> print(result.has_sensitive_information)  # False
        >>> print(result.reasoning)  # "Query contains only internal identifiers"
    """
    print("🔒 Checking guardrails for sensitive information...")
    result = await Runner.run(guardrail_agent, f"Check this query for sensitive information: {user_query}")
    return result.final_output


async def determine_required_services(user_query: str) -> ServiceDecision:
    """
    Determine which services need to be queried based on the user request.
    
    This function uses the orchestrator agent to analyze the query and decide
    whether to query ServiceNow, GTI, or both services.
    
    Args:
        user_query (str): The user's query to be analyzed
        
    Returns:
        ServiceDecision: Object containing which services to query and reasoning
        
    Example:
        >>> decision = await determine_required_services("find security incidents")
        >>> print(decision.servicenow)  # True
        >>> print(decision.gti)  # False
        >>> print(decision.reasoning)  # "Query asks for incident information..."
    """
    print("🎯 Determining required services...")
    
    prompt = f"""Analyze this user query and determine which services should be queried:
    
    Query: {user_query}
    
    Consider the context and keywords in the query.
    """
    
    result = await Runner.run(orchestrator_agent, prompt)
    decision = result.final_output
    
    print(f"✅ Orchestrator decision:")
    print(f"   ServiceNow needed: {decision.servicenow}")
    print(f"   GTI needed: {decision.gti}")
    print(f"   Reasoning: {decision.reasoning}")
    
    return decision


async def query_servicenow(user_query: str, mcp_server: MCPServer) -> List[ServiceNowQuery]:
    """
    Query ServiceNow for relevant information using the ServiceNow MCP server.
    
    This function creates a ServiceNow agent with access to the MCP server tools
    and executes the query against the ServiceNow platform.
    
    Args:
        user_query (str): The query to send to ServiceNow
        mcp_server (MCPServer): The ServiceNow MCP server instance
        
    Returns:
        List[ServiceNowQuery]: List of query results from ServiceNow
        
    Example:
        >>> results = await query_servicenow("find incidents", servicenow_server)
        >>> for result in results:
        >>>     print(result.result)  # ServiceNow response
    """
    print("🔍 Querying ServiceNow...")
    
    # Create ServiceNow agent with MCP server
    servicenow_agent_with_mcp = make_servicenow_agent(mcp_server)
    
    servicenow_result = await Runner.run(servicenow_agent_with_mcp, user_query)
    
    return [ServiceNowQuery(
        query=user_query,
        result=servicenow_result.final_output,
        source="ServiceNow"
    )]


async def query_gti(user_query: str, mcp_server: MCPServer) -> List[GTIQuery]:
    """
    Query Google Threat Intelligence platform for relevant information using the GTI MCP server.
    
    This function creates a GTI agent with access to the MCP server tools
    and executes the query against the Google Threat Intelligence platform.
    
    Args:
        user_query (str): The query to send to GTI
        mcp_server (MCPServer): The GTI MCP server instance
        
    Returns:
        List[GTIQuery]: List of query results from GTI
        
    Example:
        >>> results = await query_gti("search for APT28", gti_server)
        >>> for result in results:
        >>>     print(result.result)  # GTI response
    """
    print("🔍 Querying Google Threat Intelligence...")
    
    # Create GTI agent with MCP server
    gti_agent_with_mcp = make_gti_agent(mcp_server)
    
    gti_result = await Runner.run(gti_agent_with_mcp, user_query)
    
    return [GTIQuery(
        query=user_query,
        result=gti_result.final_output,
        source="Google Threat Intelligence"
    )]


async def aggregate_results(user_query: str, servicenow_results: Optional[List[ServiceNowQuery]], 
                          gti_results: Optional[List[GTIQuery]]) -> AggregatedResult:
    """
    Aggregate and process results from all agents into a comprehensive summary.
    
    This function combines results from ServiceNow and GTI queries and uses
    the aggregator agent to create a unified summary with recommendations.
    
    Args:
        user_query (str): The original user query
        servicenow_results (Optional[List[ServiceNowQuery]]): Results from ServiceNow queries
        gti_results (Optional[List[GTIQuery]]): Results from GTI queries
        
    Returns:
        AggregatedResult: Object containing summary and recommendations
        
    Example:
        >>> final_result = await aggregate_results("find threats", sn_results, gti_results)
        >>> print(final_result.summary)  # Combined summary
        >>> print(final_result.recommendations)  # Action items
    """
    print("📊 Aggregating results...")
    
    # Prepare context for aggregator
    context = f"Original Query: {user_query}\n\n"
    if servicenow_results:
        context += "ServiceNow Results:\n"
        for result in servicenow_results:
            context += f"- {result.result}\n"
        context += "\n"
    
    if gti_results:
        context += "GTI Results:\n"
        for result in gti_results:
            context += f"- {result.result}\n"
        context += "\n"
    
    context += "Please provide a comprehensive summary and recommendations based on all available information."
    
    result = await Runner.run(aggregator_agent, context)
    return result.final_output


async def run(gti_server: MCPServer, servicenow_server: MCPServer):
    """
    Main workflow function that orchestrates the entire query processing pipeline.
    
    This function implements the complete workflow:
    1. Guardrail check for sensitive information
    2. Service determination via orchestrator
    3. Query execution against relevant services (with parallel execution for efficiency)
    4. Result aggregation and summarization
    5. Final result display
    
    Performance Optimization:
    - When both ServiceNow and GTI queries are needed, they are executed in parallel
    - This significantly reduces total processing time compared to sequential execution
    - Timing information is logged to demonstrate the performance improvement
    
    Args:
        gti_server (MCPServer): The GTI MCP server instance
        servicenow_server (MCPServer): The ServiceNow MCP server instance
        
    Example:
        >>> await run(gti_server, servicenow_server)
        # Processes all test queries through the complete pipeline
    """
    print("🚀 Starting enhanced MCP agent workflow...")
    
    # Example queries for testing
    # test_queries = [
    #     "please summarize the latest news from Google threat intelligence platform that are related to Scattered Spider",
    #     "check ServiceNow for any recent incidents related to cybersecurity",
    #     "find all the security incident tickets that are assigned to 'coco liu' from both ServiceNow, check if those tickets have anything to do with 'scattered spider' according to google threat intelligence platform"
    # ]

    test_queries = [
        "find all the security incident tickets that are assigned to 'coco liu' from both ServiceNow, check if those tickets have anything to do with 'scattered spider' according to google threat intelligence platform"
    ]
    
    for i, message in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Processing Query {i}: {message}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Check guardrails
            guardrail_check = await check_guardrails(message)
            if guardrail_check.has_sensitive_information:
                print(f"❌ Guardrail triggered: {guardrail_check.reasoning}")
                print("Skipping this query due to sensitive information detected.")
                continue
            else:
                print(f"✅ Guardrail passed: {guardrail_check.reasoning}")
            
            # Step 2: Determine which services to query
            required_services = await determine_required_services(message)
            print(f"📋 Required services: {required_services}")
            
            # Step 3: Query relevant services in parallel when both are needed
            servicenow_results = None
            gti_results = None
            query_start_time = time.time()
            
            if required_services.servicenow and required_services.gti:
                # PERFORMANCE OPTIMIZATION: Run both queries in parallel instead of sequentially
                # This reduces total processing time from (ServiceNow_time + GTI_time) to max(ServiceNow_time, GTI_time)
                print("🚀 Running ServiceNow and GTI queries in parallel...")
                servicenow_task = query_servicenow(message, servicenow_server)
                gti_task = query_gti(message, gti_server)
                
                results = await asyncio.gather(
                    servicenow_task, 
                    gti_task,
                    return_exceptions=True
                )
                
                # Handle any exceptions that occurred during parallel execution
                if isinstance(results[0], Exception):
                    print(f"❌ ServiceNow query failed: {results[0]}")
                    servicenow_results: Optional[List[ServiceNowQuery]] = None
                else:
                    servicenow_results = results[0]  # type: ignore
                    
                if isinstance(results[1], Exception):
                    print(f"❌ GTI query failed: {results[1]}")
                    gti_results: Optional[List[GTIQuery]] = None
                else:
                    gti_results = results[1]  # type: ignore
                    
                query_time = time.time() - query_start_time
                print(f"⏱️  Parallel queries completed in {query_time:.2f} seconds")
                    
            elif required_services.servicenow:
                servicenow_results = await query_servicenow(message, servicenow_server)
                query_time = time.time() - query_start_time
                print(f"⏱️  ServiceNow query completed in {query_time:.2f} seconds")
            
            elif required_services.gti:
                gti_results = await query_gti(message, gti_server)
                query_time = time.time() - query_start_time
                print(f"⏱️  GTI query completed in {query_time:.2f} seconds")
            
            # Step 4: Aggregate results
            final_result = await aggregate_results(message, servicenow_results, gti_results)
            
            # Step 5: Display final result
            print(f"\n📋 Final Result:")
            print(f"Summary: {final_result.summary}")
            if final_result.recommendations:
                print(f"Recommendations:")
                for rec in final_result.recommendations:
                    print(f"- {rec}")
            
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")


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
    
    # Get MCP server configurations
    gti_server_config = config_manager.get("mcp_servers.gti")
    servicenow_server_config = config_manager.get("mcp_servers.servicenow")
    
    # Start both GTI and ServiceNow MCP servers
    async with MCPServerStdio(
        name=gti_server_config["name"],
        params={
            "command": gti_server_config["command"],
            "args": gti_server_config["args"]
        }
    ) as gti_server, MCPServerStdio(
        name=servicenow_server_config["name"],
        params={
            "command": servicenow_server_config["command"],
            "args": servicenow_server_config["args"]
        }
    ) as servicenow_server:
        print("✅ MCP servers started successfully!")
        trace_id = gen_trace_id()
        with trace(workflow_name="Enhanced MCP Orchestrator", trace_id=trace_id):
            print(f"🔍 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(gti_server, servicenow_server)


if __name__ == "__main__":
    asyncio.run(main())
