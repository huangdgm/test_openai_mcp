import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, gen_trace_id, trace


"""This example uses a custom provider for a specific agent. Steps:
1. Create a custom OpenAI client.
2. Create a `Model` that uses the custom client.
3. Set the `model` on the Agent.

Note that in this example, we disable tracing under the assumption that you don't have an API key
from platform.openai.com. If you do have one, you can either set the `OPENAI_API_KEY` env var
or call set_tracing_export_api_key() to set a tracing specific key.
"""

load_dotenv()

azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
if azure_endpoint is None:
    raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")

azure_openai_client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2025-01-01-preview",
    azure_endpoint=azure_endpoint,
    azure_deployment="gpt-4o"
)


async def main():
    # This agent will use the custom LLM provider
    agent = Agent(
        name="Helpful Assistant",
        instructions="You are a helpful assistant. Be concise and professional.",
        model=OpenAIChatCompletionsModel(
            model="gpt-4o",
            openai_client=azure_openai_client
        )
    )

    trace_id = gen_trace_id()
    with trace(workflow_name="1_helloworld_custom_model", trace_id=trace_id):
        print(f"🔍 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
        result = await Runner.run(agent, "What is the capital city of USA?")
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())