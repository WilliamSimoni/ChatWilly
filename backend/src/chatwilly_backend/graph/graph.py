from typing import Annotated, List, TypedDict

from langchain.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from chatwilly_backend.graph.agents import guardrails_agent, response_agent


class ChatWillyState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    input_guardrail_passed: bool


async def guardrail_input(state: ChatWillyState):
    clean_messages = [
        m
        for m in state["messages"]
        if isinstance(m, (HumanMessage, AIMessage))
        and (isinstance(m, HumanMessage) or (isinstance(m, AIMessage) and m.content))
    ]
    recent_messages = clean_messages[-5:]
    response = await guardrails_agent.ainvoke({"messages": recent_messages})
    guardrail_result = response["structured_response"]
    return {"input_guardrail_passed": guardrail_result.passed}


def check_input_guardrail(state: ChatWillyState):
    if state["input_guardrail_passed"]:
        return "response_generation"
    else:
        return "guardrail_block"


async def response_generation(state: ChatWillyState, config: RunnableConfig):
    recent_messages = state["messages"][-10:]
    response = await response_agent.ainvoke(
        {"messages": recent_messages}, config=config
    )
    new_messages = response["messages"][len(recent_messages) :]
    return {"messages": new_messages}


def guardrail_block(state: ChatWillyState):
    return {
        "messages": [
            AIMessage(
                content="I can only respond to questions about my professional profile. Please ask me something related to my work experience, skills, or projects."
            )
        ]
    }


agent_builder = StateGraph(ChatWillyState)
agent_builder.add_node("guardrail_input", guardrail_input)
agent_builder.add_node("response_generation", response_generation)
agent_builder.add_node("guardrail_block", guardrail_block)

agent_builder.add_edge(START, "guardrail_input")
agent_builder.add_conditional_edges(
    "guardrail_input", check_input_guardrail, ["response_generation", "guardrail_block"]
)
agent_builder.add_edge("response_generation", END)
agent_builder.add_edge("guardrail_block", END)


def build_agent(checkpointer: AsyncPostgresSaver):
    return agent_builder.compile(checkpointer=checkpointer)
