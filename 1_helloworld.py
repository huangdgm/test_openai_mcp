from agents import Agent, Runner
import asyncio

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

async def main():
    result = await Runner.run(agent, "Write a joke about recursion in programming.")
    print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.

if __name__ == "__main__":
    asyncio.run(main())

