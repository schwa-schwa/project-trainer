from typing import List, Literal, Callable
from pydantic import BaseModel
from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from core.common.state import AgentState
from core.common.llm import get_llm


def build_tool_agent_graph(
    tools: List[BaseTool],
    system_prompt: str,
    final_node_fn: Callable[[AgentState], dict],
    temperature: float = 0.5,
):
    """
    ツール呼び出し→最終生成の共通グラフを構築する。

    Args:
        tools: バインドするツールのリスト
        system_prompt: システムプロンプト
        final_node_fn: 最終ノードの処理関数（structured output等）
        temperature: LLMのtemperature
    """

    def call_model(state: AgentState) -> dict:
        messages = state["messages"]
        llm = get_llm(temperature=temperature)
        llm_with_tools = llm.bind_tools(tools)
        full_messages = [SystemMessage(content=system_prompt)] + messages
        response = llm_with_tools.invoke(full_messages)
        return {"messages": [response]}

    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"

    tool_node = ToolNode(tools)

    workflow = StateGraph(AgentState)
    workflow.add_node("call_model", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("generate_final", final_node_fn)

    workflow.add_edge(START, "call_model")
    workflow.add_conditional_edges(
        "call_model",
        should_continue,
        {"tools": "tools", "end": "generate_final"},
    )
    workflow.add_edge("tools", "call_model")
    workflow.add_edge("generate_final", END)

    return workflow.compile()