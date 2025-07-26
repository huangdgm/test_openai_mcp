from dotenv import load_dotenv
from agents import Agent, Runner, agent, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStdio
import os
import asyncio


load_dotenv()


async def run(mcp_server: MCPServer):
    agent=Agent(
        name="Assistant",
        instructions="You are a helpful assistant that can answer questions about the filesystem.",
        model="gpt-4o-mini",
        mcp_servers=[mcp_server]
    )
    
    message = "What is in the samples_files directory?"
    result = await Runner.run(agent, message)
    print(result.final_output)


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "samples_files")

    async with MCPServerStdio(
        name="Filesystem Server",
        params={
            "command": "***REMOVED***/.nvm/versions/node/v24.3.0/bin/node",
            "args": [
                "***REMOVED***/.nvm/versions/node/v24.3.0/lib/node_modules/@modelcontextprotocol/server-filesystem/dist/index.js",
                samples_dir
            ]
        }
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="MCP filesystem example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)



if __name__ == "__main__":
    asyncio.run(main())
        
