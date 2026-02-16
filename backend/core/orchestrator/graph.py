from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from core.common.state import AgentState
from core.analyzer.graph import build_analyzer_graph, create_user_message
from core.planner.graph import build_planner_graph, create_planner_message

def build_orchestrator():
    """
    analyzer_node と planner_node を統合したオーケストレーターグラフを構築
    
    フロー:
    START -> analyzer -> adapter -> planner -> END
    """
    workflow = StateGraph(AgentState)
    
    # サブグラフをノードとして追加
    workflow.add_node("analyzer", build_analyzer_graph())
    workflow.add_node("planner", build_planner_graph())
    
    # Adapter Node: メッセージの橋渡し
    # analyzerの出力messagesとplannerの入力messagesは文脈が違うため
    # ここでplanner向けの新しいHumanMessageを注入する
    def adapter_node(state: AgentState) -> dict:
        print("\n[Orchestrator] Connecting Analyzer to Planner...")
        input_data = state["input_data"]
        analysis_report = state.get("analysis_report", {})
        
        # Plannerへの指示を作成
        planner_msg = create_planner_message(input_data, analysis_report)
        
        # 既存のメッセージ（Analyzerの会話履歴）を保持するか、クリアするか？
        # ここではPlannerは独立したタスクとしてクリーンなコンテキストで開始させるため
        # messagesを上書き（または追加）するアプローチをとる
        
        return {
            "messages": [HumanMessage(content=planner_msg)]
        }

    workflow.add_node("adapter", adapter_node)
    
    # エッジを定義: START -> analyzer -> adapter -> planner -> END
    workflow.add_edge(START, "analyzer")
    workflow.add_edge("analyzer", "adapter")
    workflow.add_edge("adapter", "planner")
    workflow.add_edge("planner", END)
    
    return workflow.compile()

def create_initial_state(input_data: dict) -> dict:
    """入力データからオーケストレーター用の初期状態を作成"""
    user_message = create_user_message(input_data)
    
    return {
        "messages": [HumanMessage(content=user_message)],
        "input_data": input_data,
        "analysis_report": {},
        "training_plan": {}
    }
