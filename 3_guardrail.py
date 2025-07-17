# 3_guardrail.py
# 
# This example shows how to use guardrails to check if the user is asking about a math problem.
# It uses a guardrail agent to check if the user is asking about a math problem.
# It then uses the orchestrator agent to use the guardrail agent to check if the user is asking about a math problem.
# If the user is asking about a math problem, the orchestrator agent will output the result,
# otherwise it will fail early.

import asyncio
from agents import GuardrailFunctionOutput, Agent, Runner, input_guardrail, trace
from pydantic import BaseModel

class QuestionType(BaseModel):
    is_math_problem: bool
    is_historical_question: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about a math problem or a historical question.",
    output_type=QuestionType,
    model="gpt-4o-mini"
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

@input_guardrail
async def question_type_guardrail(ctx, agent, message):
    result = await Runner.run(guardrail_agent, message, context=ctx.context)
    final_output = result.final_output_as(QuestionType)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_math_problem and not final_output.is_historical_question,
    )

orchestrator_agent = Agent(
    name="Orchestrator",
    instructions="You determine which specialist agent to use based on the user's question. If the user is asking about a math problem, you will handoff to the math tutor agent. If the user is asking about a historical question, you will handoff to the history tutor agent.",
    handoffs=[math_tutor_agent, history_tutor_agent],
    model="gpt-4o-mini",
    input_guardrails=[question_type_guardrail]
)


async def main():
    message = "when does france become a republic?"
    result = await Runner.run(orchestrator_agent, message)
    print(result.final_output)


if __name__ == "__main__":
    with trace("3_guardrail.py"):
        asyncio.run(main())
        