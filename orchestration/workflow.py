"""
Enhanced MCP Orchestrator Workflow

This module implements the main workflow for the enhanced MCP orchestrator system.
It coordinates multiple AI agents to process user queries through ServiceNow, 
Google Threat Intelligence (GTI), and OpenSearch platforms with guardrail protection.

The workflow consists of:
1. Guardrail check to prevent sensitive information exposure
2. Service determination to route queries to appropriate platforms
3. Parallel execution of service queries for optimal performance
4. Data visualization and summarization of results

Key Features:
- Parallel execution of multiple service queries
- Comprehensive error handling and monitoring
- Performance timing and analytics
- Structured data validation with Pydantic models
"""

import time
import asyncio
from ai_agents import get_servicenow_agent, get_gti_agent, get_opensearch_agent, get_guardrail_agent, get_orchestrator_agent, get_visualization_agent
from models import HasSensitiveInformation, ServiceDecision, ServiceNowQuery, GTIQuery, OpenSearchQuery, VisualizationResult
from agents import Runner
from agents.mcp import MCPServer
from typing import List, Optional

async def check_guardrails(user_query: str, openai_client) -> HasSensitiveInformation:
    """
    Check if the user query contains sensitive information that should not be processed.
    
    This function uses the guardrail agent to analyze the query for potential
    security risks such as passwords, API keys, tokens, or other credentials.
    
    Args:
        user_query (str): The user's query to be checked for sensitive information
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        HasSensitiveInformation: A Pydantic model containing:
            - has_sensitive_information (bool): True if sensitive info detected
            - reasoning (str): Explanation of the guardrail decision
            
    Example:
        >>> result = await check_guardrails("Find incidents for user john", client)
        >>> print(result.has_sensitive_information)
        False
    """
    agent = get_guardrail_agent(openai_client)
    result = await Runner.run(agent, f"Check this query for sensitive information: {user_query}")
    return result.final_output

async def determine_required_services(user_query: str, openai_client) -> ServiceDecision:
    """
    Determine which services should be queried based on the user's request.
    
    This function uses the orchestrator agent to analyze the query and determine
    whether ServiceNow, GTI, OpenSearch, or multiple services should be queried.
    The decision is based on keywords, context, and the nature of the request.
    
    Args:
        user_query (str): The user's query to be analyzed
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        ServiceDecision: A Pydantic model containing:
            - servicenow (bool): Whether ServiceNow should be queried
            - gti (bool): Whether GTI should be queried
            - opensearch (bool): Whether OpenSearch should be queried
            - reasoning (str): Explanation of the service selection decision
            
    Example:
        >>> decision = await determine_required_services("Find security incidents", client)
        >>> print(f"ServiceNow: {decision.servicenow}, GTI: {decision.gti}")
        ServiceNow: True, GTI: False
    """
    agent = get_orchestrator_agent(openai_client)
    
    print("🎯 Determining required services...")
    prompt = f"""Analyze this user query and determine which services should be queried:\n\nQuery: {user_query}\n\nConsider the context and keywords in the query."""
    result = await Runner.run(agent, prompt)
    decision = result.final_output
    print(f"✅ Orchestrator decision:")
    print(f"   ServiceNow needed: {decision.servicenow}")
    print(f"   GTI needed: {decision.gti}")
    print(f"   OpenSearch needed: {decision.opensearch}")
    print(f"   Reasoning: {decision.reasoning}")
    return decision

async def query_servicenow(user_query: str, mcp_server: MCPServer, openai_client) -> List[ServiceNowQuery]:
    """
    Query the ServiceNow platform for incident and ticket information.
    
    This function uses the ServiceNow agent with MCP server integration to
    retrieve and analyze data from the ServiceNow platform.
    
    Args:
        user_query (str): The query to send to ServiceNow
        mcp_server (MCPServer): The ServiceNow MCP server instance
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        List[ServiceNowQuery]: A list of ServiceNow query results containing:
            - query (str): The original query
            - result (str): The response from ServiceNow
            - source (str): Source identifier ("ServiceNow")
            
    Example:
        >>> results = await query_servicenow("Find security incidents", server, client)
        >>> print(f"Found {len(results)} ServiceNow results")
    """
    servicenow_agent_with_mcp = get_servicenow_agent(mcp_server, openai_client)
    servicenow_result = await Runner.run(servicenow_agent_with_mcp, user_query)
    return [ServiceNowQuery(
        query=user_query,
        result=servicenow_result.final_output,
        source="ServiceNow"
    )]

async def query_gti(user_query: str, mcp_server: MCPServer, openai_client) -> List[GTIQuery]:
    """
    Query the Google Threat Intelligence platform for threat information.
    
    This function uses the GTI agent with MCP server integration to
    retrieve and analyze threat intelligence data.
    
    Args:
        user_query (str): The query to send to GTI
        mcp_server (MCPServer): The GTI MCP server instance
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        List[GTIQuery]: A list of GTI query results containing:
            - query (str): The original query
            - result (str): The response from GTI
            - source (str): Source identifier ("Google Threat Intelligence")
            
    Example:
        >>> results = await query_gti("Search for APT28", server, client)
        >>> print(f"Found {len(results)} GTI results")
    """
    gti_agent_with_mcp = get_gti_agent(mcp_server, openai_client)
    gti_result = await Runner.run(gti_agent_with_mcp, user_query)
    return [GTIQuery(
        query=user_query,
        result=gti_result.final_output,
        source="Google Threat Intelligence"
    )]

async def query_opensearch(user_query: str, mcp_server: MCPServer, openai_client) -> List[OpenSearchQuery]:
    """
    Query the OpenSearch platform for log data and analytics.
    
    This function uses the OpenSearch agent with MCP server integration to
    retrieve and analyze data from the OpenSearch platform.
    
    Args:
        user_query (str): The query to send to OpenSearch
        mcp_server (MCPServer): The OpenSearch MCP server instance
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        List[OpenSearchQuery]: A list of OpenSearch query results containing:
            - query (str): The original query
            - result (str): The response from OpenSearch
            - source (str): Source identifier ("OpenSearch")
            
    Example:
        >>> results = await query_opensearch("Find authentication failures", server, client)
        >>> print(f"Found {len(results)} OpenSearch results")
    """
    opensearch_agent_with_mcp = get_opensearch_agent(mcp_server, openai_client)
    opensearch_result = await Runner.run(opensearch_agent_with_mcp, user_query)
    return [OpenSearchQuery(
        query=user_query,
        result=opensearch_result.final_output,
        source="OpenSearch"
    )]

async def visualize_results(user_query: str, servicenow_results: Optional[List[ServiceNowQuery]], gti_results: Optional[List[GTIQuery]], opensearch_results: Optional[List[OpenSearchQuery]], openai_client) -> VisualizationResult:
    """
    Generate visualizations and summaries from multiple data sources.
    
    This function uses the visualization agent to analyze data from ServiceNow,
    GTI, and OpenSearch sources and generate appropriate visualizations and
    summaries for presentation.
    
    Args:
        user_query (str): The original user query
        servicenow_results (Optional[List[ServiceNowQuery]]): Results from ServiceNow queries
        gti_results (Optional[List[GTIQuery]]): Results from GTI queries
        opensearch_results (Optional[List[OpenSearchQuery]]): Results from OpenSearch queries
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        VisualizationResult: A Pydantic model containing:
            - summary (str): Natural language summary of findings
            - visualization_type (str): Recommended visualization type
            - code_snippet (str): Python code for generating the visualization
            
    Example:
        >>> result = await visualize_results("Find security incidents", sn_results, gti_results, os_results, client)
        >>> print(f"Summary: {result.summary}")
        >>> print(f"Visualization: {result.visualization_type}")
    """
    agent = get_visualization_agent(openai_client)
    
    print("📊 Generating visualization...")
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
    if opensearch_results:
        context += "OpenSearch Results:\n"
        for result in opensearch_results:
            context += f"- {result.result}\n"
        context += "\n"
    result = await Runner.run(agent, context)
    return result.final_output

async def run(gti_server: MCPServer, servicenow_server: MCPServer, opensearch_server: MCPServer, openai_client):
    """
    Main workflow function that orchestrates the entire query processing pipeline.
    
    This function implements the complete workflow:
    1. Guardrail check for sensitive information
    2. Service determination and routing
    3. Parallel execution of service queries
    4. Data visualization and result presentation
    
    The function processes a set of test queries and demonstrates the system's
    capabilities with comprehensive error handling and performance monitoring.
    
    Args:
        gti_server (MCPServer): The GTI MCP server instance
        servicenow_server (MCPServer): The ServiceNow MCP server instance
        opensearch_server (MCPServer): The OpenSearch MCP server instance
        openai_client: The Azure OpenAI client for agent communication
        
    Returns:
        None: The function prints results to console and handles all processing internally
        
    Example:
        >>> await run(gti_server, servicenow_server, opensearch_server, openai_client)
        🚀 Starting enhanced MCP agent workflow...
        Processing Query 1: List all the indices in the OpenSearch cluster.
        ✅ Guardrail passed: Query contains no sensitive information
        🎯 Determining required services...
        ...
    """
    print("🚀 Starting enhanced MCP agent workflow...")

    # "Analyze threat intelligence data from Google Threat Intelligence platform for cyber attacks targeting the telecommunications industry in New Zealand and Australia. Focus on gathering quantitative data such as the number of incidents, types of attack techniques used, threat actor groups involved, and the timeline of attacks. Present the data in a way that is suitable for creating visualizations like bar charts, timelines, or heatmaps."
    # "Search for log entries in OpenSearch related to authentication failures and security events from the last 24 hours. Look for patterns in failed login attempts, unusual access patterns, and any security alerts. Provide a summary of the findings and suggest potential security concerns."
    
    test_queries = [
        "List all the indices in the OpenSearch cluster."
    ]
    for i, message in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Processing Query {i}: {message}")
        print(f"{'='*60}")
        try:
            # Step 1: Guardrail check
            guardrail_check = await check_guardrails(message, openai_client)
            if guardrail_check.has_sensitive_information:
                print(f"❌ Guardrail triggered: {guardrail_check.reasoning}")
                print("Skipping this query due to sensitive information detected.")
                continue
            else:
                print(f"✅ Guardrail passed: {guardrail_check.reasoning}")
            
            # Step 2: Determine required services
            required_services = await determine_required_services(message, openai_client)
            print(f"📋 Required services: {required_services}")
            
            # Initialize result variables
            servicenow_results = None
            gti_results = None
            opensearch_results = None
            query_start_time = time.time()
            
            # Step 3: Prepare services to query
            services_to_query = []
            if required_services.servicenow:
                services_to_query.append(("servicenow", query_servicenow(message, servicenow_server, openai_client)))
            if required_services.gti:
                services_to_query.append(("gti", query_gti(message, gti_server, openai_client)))
            if required_services.opensearch:
                services_to_query.append(("opensearch", query_opensearch(message, opensearch_server, openai_client)))
            
            # Step 4: Execute queries (parallel or sequential)
            if len(services_to_query) > 1:
                print(f"🚀 Running {len(services_to_query)} queries in parallel...")
                tasks = [task for _, task in services_to_query]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results and handle exceptions
                for i, (service_name, _) in enumerate(services_to_query):
                    if isinstance(results[i], Exception):
                        print(f"❌ {service_name} query failed: {results[i]}")
                        if service_name == "servicenow":
                            servicenow_results = None
                        elif service_name == "gti":
                            gti_results = None
                        elif service_name == "opensearch":
                            opensearch_results = None
                    else:
                        if service_name == "servicenow":
                            servicenow_results = results[i]
                        elif service_name == "gti":
                            gti_results = results[i]
                        elif service_name == "opensearch":
                            opensearch_results = results[i]
                
                query_time = time.time() - query_start_time
                print(f"⏱️  Parallel queries completed in {query_time:.2f} seconds")
            elif len(services_to_query) == 1:
                service_name, task = services_to_query[0]
                print(f"🚀 Running {service_name} query...")
                result = await task
                if service_name == "servicenow":
                    servicenow_results = result
                elif service_name == "gti":
                    gti_results = result
                elif service_name == "opensearch":
                    opensearch_results = result
                query_time = time.time() - query_start_time
                print(f"⏱️  {service_name} query completed in {query_time:.2f} seconds")
            
            # Step 5: Generate visualization and final results
            final_result = await visualize_results(message, servicenow_results, gti_results, opensearch_results, openai_client)
            print(f"\n📋 Final Result:")
            print(f"Summary: {final_result.summary}")
            print(f"Visualization Type: {final_result.visualization_type}")
            if final_result.code_snippet:
                print(f"Code Snippet:\n{final_result.code_snippet}")
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}") 