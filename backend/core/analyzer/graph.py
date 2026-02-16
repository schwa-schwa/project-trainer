from typing import List
from pydantic import BaseModel, Field
from langchain_core.messages import ToolMessage

from core.common.state import AgentState
from core.common.llm import get_llm
from core.common.graph_builder import build_tool_agent_graph
from core.analyzer.tools import retriever_tool, calculate_smm_ratio, evaluate_body_type


class AnalysisResult(BaseModel):
    """InBody分析結果の構造化出力モデル（分析専用）"""
    body_type: str = Field(description="体型タイプ（筋肉質型/標準型/隠れ肥満型/肥満型/痩せ型）")
    body_fat_evaluation: str = Field(description="体脂肪率の評価（低い/標準/軽度肥満/肥満）と数値根拠")
    skeletal_muscle_evaluation: str = Field(description="骨格筋量の評価（優秀/標準/やや低い/低い）と数値根拠")
    arm_balance: str = Field(description="腕の左右バランス（正常/軽度アンバランス/要注意）と差分%")
    leg_balance: str = Field(description="脚の左右バランス（正常/軽度アンバランス/要注意）と差分%")
    upper_lower_balance: str = Field(description="上下肢バランスの評価")
    risk_factors: List[str] = Field(description="リスク要因のリスト（既往歴・数値から導出）")
    concerns: List[str] = Field(description="注意すべき点・懸念事項")


SYSTEM_PROMPT = """あなたは運動生理学とスポーツ医学の専門家です。

## タスク
ユーザーのInBodyデータを詳細に分析し、体組成の現状を客観的に評価してください。
※トレーニング推奨は行わず、純粋な分析結果のみを出力

## 手順
1. calculate_smm_ratioで体重比骨格筋量を計算
2. evaluate_body_typeで体重・身長・体脂肪率から体型タイプを判定（BMIは内部で自動計算）
3. retriever_toolで以下の項目を検索（※必ず**一度だけ**呼び出し、全項目を一つのクエリに含めること）:
   - 体型分類の詳細アドバイス
   - 体脂肪率判定（4段階: 低い/標準/軽度肥満/肥満）
   - 既往歴に関連するリスク対策
   - 上下肢バランスおよび左右差の評価基準
4. 左右バランスおよび上下肢バランスを評価（Knowledge Baseの基準を参照）
5. 既往歴とデータからリスク要因を特定

## 出力形式
- 体型タイプ（evaluate_body_typeの結果を使用）、体脂肪率評価、骨格筋量評価
- 腕・脚・上下肢のバランス評価（差分%を明記）
- リスク要因、注意すべき点"""

TOOLS = [retriever_tool, calculate_smm_ratio, evaluate_body_type]


def create_user_message(input_data: dict) -> str:
    """ユーザーデータからメッセージを生成"""
    user_profile = input_data.get("user_profile", {})
    inbody_metrics = input_data.get("inbody_metrics", {})
    goal = input_data.get("goal", {})

    return f"""以下のInBodyデータを分析してください。

## ユーザープロフィール
- 年齢: {user_profile.get('age', '不明')}歳
- 性別: {user_profile.get('gender', '不明')}
- 身長: {user_profile.get('height_cm', '不明')}cm
- トレーニング経験: {user_profile.get('training_experience', '不明')}
- 既往歴・怪我: {', '.join(user_profile.get('injuries', ['なし']))}

## InBody測定データ
- 体重: {inbody_metrics.get('weight_kg', '不明')}kg
- 筋肉量: {inbody_metrics.get('muscle_mass_kg', '不明')}kg
- 骨格筋量: {inbody_metrics.get('skeletal_muscle_mass_kg', '不明')}kg
- 体脂肪率: {inbody_metrics.get('body_fat_percent', '不明')}%
- 部位別骨格筋量:
  - 右腕: {inbody_metrics.get('segmental_lean', {}).get('right_arm', '不明')}kg
  - 左腕: {inbody_metrics.get('segmental_lean', {}).get('left_arm', '不明')}kg
  - 体幹: {inbody_metrics.get('segmental_lean', {}).get('trunk', '不明')}kg
  - 右脚: {inbody_metrics.get('segmental_lean', {}).get('right_leg', '不明')}kg
  - 左脚: {inbody_metrics.get('segmental_lean', {}).get('left_leg', '不明')}kg

## 目標
- 目標タイプ: {goal.get('type', '不明')}
- 週のトレーニング日数: {goal.get('days_per_week', '不明')}日

retriever_toolを使って専門知識を検索し、科学的根拠に基づいた分析を行ってください。"""


def _generate_final_response(state: AgentState) -> dict:
    """最終応答を生成するノード（AnalysisResult構造化出力を使用）"""
    messages = state["messages"]
    input_data = state["input_data"]

    tool_results = [msg.content for msg in messages if isinstance(msg, ToolMessage)]
    context_text = "\n\n".join(tool_results) if tool_results else "専門知識なし"

    user_profile = input_data.get("user_profile", {})
    inbody_metrics = input_data.get("inbody_metrics", {})

    prompt = f"""以下のInBodyデータと専門知識を元に、現状の体組成を詳細に分析してください。

## 専門知識（検索結果）
{context_text}

## ユーザーデータ
- 年齢: {user_profile.get('age')}歳、性別: {user_profile.get('gender')}
- 体重: {inbody_metrics.get('weight_kg')}kg、骨格筋量: {inbody_metrics.get('skeletal_muscle_mass_kg')}kg
- 体脂肪率: {inbody_metrics.get('body_fat_percent')}%
- 部位別骨格筋量: {inbody_metrics.get('segmental_lean')}
- 既往歴: {', '.join(user_profile.get('injuries', []))}

上記データを分析し、トレーニング推奨は含めず、客観的な分析結果のみを構造化して出力してください。"""

    llm = get_llm()
    structured_llm = llm.with_structured_output(AnalysisResult)
    result = structured_llm.invoke(prompt)

    print("   [Analyzer] 構造化出力を生成しました")
    return {"analysis_report": result.model_dump()}


def build_analyzer_graph():
    """カスタムRAGワークフローを構築"""
    return build_tool_agent_graph(
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        final_node_fn=_generate_final_response,
    )
