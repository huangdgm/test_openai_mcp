from dotenv import load_dotenv
from agents import Agent, Runner, agent, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStdio
import os
import asyncio


load_dotenv()


async def run(mcp_server: MCPServer):
    print("Creating agent with MCP server...")
    agent=Agent(
        name="Assistant",
        instructions="You are a helpful assistant that can answer questions about the thread hunting information.",
        model="gpt-4o-mini",
        mcp_servers=[mcp_server]
    )
    
    print("Agent created successfully!")
    
    # message = "Use search_threat_actors('APT28') to find the threat actor"
    message = "please summarize the latest news from Google threat intelligence platform that are related to Scattered Spider"
    print(f"Sending message: {message}")
    result = await Runner.run(agent, message)
    print(result.final_output)


async def main():
    print("Starting MCP server...")
    async with MCPServerStdio(
        name="GTI Server",
        params={
            "command": "***REMOVED***/.local/bin/uv",
            "args": [
                "--directory",
                "***REMOVED***/repo/mcp-security/server/gti/",
                "run",
                "--env-file",
                "***REMOVED***/.env",
                "gti_mcp/server.py"
            ]
        }
    ) as server:
        print("MCP server started successfully!")
        trace_id = gen_trace_id()
        with trace(workflow_name="MCP GTI example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)



if __name__ == "__main__":
    asyncio.run(main())
        