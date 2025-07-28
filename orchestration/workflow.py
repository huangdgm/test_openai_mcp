import time
import asyncio
from ai_agents import get_servicenow_agent, get_gti_agent, get_guardrail_agent, get_orchestrator_agent, get_visualization_agent
from models import HasSensitiveInformation, ServiceDecision, ServiceNowQuery, GTIQuery, VisualizationResult
from agents import Runner
from agents.mcp import MCPServer
from typing import List, Optional

async def check_guardrails(user_query: str, openai_client) -> HasSensitiveInformation:
    agent = get_guardrail_agent(openai_client)
    result = await Runner.run(agent, f"Check this query for sensitive information: {user_query}")
    return result.final_output

async def determine_required_services(user_query: str, openai_client) -> ServiceDecision:
    agent = get_orchestrator_agent(openai_client)
    
    print("🎯 Determining required services...")
    prompt = f"""Analyze this user query and determine which services should be queried:\n\nQuery: {user_query}\n\nConsider the context and keywords in the query."""
    result = await Runner.run(agent, prompt)
    decision = result.final_output
    print(f"✅ Orchestrator decision:")
    print(f"   ServiceNow needed: {decision.servicenow}")
    print(f"   GTI needed: {decision.gti}")
    print(f"   Reasoning: {decision.reasoning}")
    return decision

async def query_servicenow(user_query: str, mcp_server: MCPServer, openai_client) -> List[ServiceNowQuery]:
    servicenow_agent_with_mcp = get_servicenow_agent(mcp_server, openai_client)
    servicenow_result = await Runner.run(servicenow_agent_with_mcp, user_query)
    return [ServiceNowQuery(
        query=user_query,
        result=servicenow_result.final_output,
        source="ServiceNow"
    )]

async def query_gti(user_query: str, mcp_server: MCPServer, openai_client) -> List[GTIQuery]:
    gti_agent_with_mcp = get_gti_agent(mcp_server, openai_client)
    gti_result = await Runner.run(gti_agent_with_mcp, user_query)
    return [GTIQuery(
        query=user_query,
        result=gti_result.final_output,
        source="Google Threat Intelligence"
    )]

async def visualize_results(user_query: str, servicenow_results: Optional[List[ServiceNowQuery]], gti_results: Optional[List[GTIQuery]], openai_client) -> VisualizationResult:
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
    result = await Runner.run(agent, context)
    return result.final_output

async def run(gti_server: MCPServer, servicenow_server: MCPServer, openai_client):
    print("🚀 Starting enhanced MCP agent workflow...")
    test_queries = [
        "Analyze threat intelligence data from Google Threat Intelligence platform for cyber attacks targeting the telecommunications industry in New Zealand and Australia. Focus on gathering quantitative data such as the number of incidents, types of attack techniques used, threat actor groups involved, and the timeline of attacks. Present the data in a way that is suitable for creating visualizations like bar charts, timelines, or heatmaps."
    ]
    for i, message in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Processing Query {i}: {message}")
        print(f"{'='*60}")
        try:
            guardrail_check = await check_guardrails(message, openai_client)
            if guardrail_check.has_sensitive_information:
                print(f"❌ Guardrail triggered: {guardrail_check.reasoning}")
                print("Skipping this query due to sensitive information detected.")
                continue
            else:
                print(f"✅ Guardrail passed: {guardrail_check.reasoning}")
            required_services = await determine_required_services(message, openai_client)
            print(f"📋 Required services: {required_services}")
            servicenow_results = None
            gti_results = None
            query_start_time = time.time()
            if required_services.servicenow and required_services.gti:
                print("🚀 Running ServiceNow and GTI queries in parallel...")
                servicenow_task = query_servicenow(message, servicenow_server, openai_client)
                gti_task = query_gti(message, gti_server, openai_client)
                results = await asyncio.gather(
                    servicenow_task, 
                    gti_task,
                    return_exceptions=True
                )
                if isinstance(results[0], Exception):
                    print(f"❌ ServiceNow query failed: {results[0]}")
                    servicenow_results = None
                else:
                    servicenow_results = results[0]
                if isinstance(results[1], Exception):
                    print(f"❌ GTI query failed: {results[1]}")
                    gti_results = None
                else:
                    gti_results = results[1]
                query_time = time.time() - query_start_time
                print(f"⏱️  Parallel queries completed in {query_time:.2f} seconds")
            elif required_services.servicenow:
                servicenow_results = await query_servicenow(message, servicenow_server, openai_client)
                query_time = time.time() - query_start_time
                print(f"⏱️  ServiceNow query completed in {query_time:.2f} seconds")
            elif required_services.gti:
                gti_results = await query_gti(message, gti_server, openai_client)
                query_time = time.time() - query_start_time
                print(f"⏱️  GTI query completed in {query_time:.2f} seconds")
            final_result = await visualize_results(message, servicenow_results, gti_results, openai_client)
            print(f"\n📋 Final Result:")
            print(f"Summary: {final_result.summary}")
            print(f"Visualization Type: {final_result.visualization_type}")
            if final_result.code_snippet:
                print(f"Code Snippet:\n{final_result.code_snippet}")
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}") 