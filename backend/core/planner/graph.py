from langchain_core.messages import ToolMessage

from core.common.state import AgentState, TrainingPlan
from core.common.llm import get_llm
from core.common.graph_builder import build_tool_agent_graph
from core.planner.tools import training_retriever_tool, risk_modification_tool


SYSTEM_PROMPT = """あなたは運動生理学とスポーツ医学の専門家パーソナルトレーナーです。

## タスク
ユーザーのInBody分析結果を元に、パーソナライズされたトレーニングメニューを作成してください。

## 入力情報
1. ユーザープロフィール（年齢、性別、トレーニング経験、既往歴）
2. InBody測定データ（体重、筋肉量、体脂肪率、部位別骨格筋量）
3. 目標（ダイエット、筋肥大、基礎体力向上など）
4. 分析レポート（体型タイプ、バランス評価、リスク要因）

## 手順
1. training_retriever_toolで以下を検索（1回のクエリにまとめること）:
   - 体型タイプに適したトレーニング方針
   - 目標に合った戦略
   - トレーニング経験レベルに適した分割法
2. risk_modification_toolでリスク要因に対する対策を検索
3. 検索結果を元に週間トレーニングプランを設計

## 設計原則
- 【最優先】ユーザーの「preferences」（環境・器具・要望・トレーニング時間）を絶対に遵守すること
  - 家トレ(home)希望ならジムマシンは除外
  - 器具がダンベルのみならバーベルは除外
  - 指定されたトレーニング時間に合わせて種目数を調整する
- 【種目数の目安】トレーニング時間に応じて十分な種目数を提案する
  - 5〜15分: 2〜4種目（ウォームアップ含む）
  - 30分: 5〜7種目
  - 45分: 7〜9種目
  - 60分: 8〜12種目
  - 90分以上: 12〜15種目
  - 各種目の説明・セット間休憩も考慮して種目数を決める
- 【セット間休憩時間】各種目の強度に応じて適切な休憩時間（interval_seconds）を設定する
  - ストレッチ・軽い種目: 30秒
  - 通常の種目（腕立て伏せ、スクワット、腹筋など）: 60秒
  - 高強度・複合種目: 90〜120秒
- 【初心者の場合は特に重要】誰でも知っているなじみ深いエクササイズのみを使う
  - スクワット、腕立て伏せ、腹筋、背筋、プランク、もも上げ、かかと上げ、ストレッチなど
  - 専門用語や英語名は避け、日本語で分かりやすい名前を使う
  - 複雑なフォームが必要な種目は避ける
- 中級者・上級者には専門的な種目も提案可能
- 【動作手順】各種目には必ず3ステップ程度の具体的な動作手順（instructions）を含めること
  - 初心者でもわかるよう平易な言葉で説明
  - 「1. ○○する」「2. △△する」「3. □□する」の形式で記述
- ユーザーが「週のトレーニング日数」を指定している場合はそれに従う。指定がない（おまかせ）場合は、ユーザーの経験レベル・目標・体型を考慮して最適な日数をAIが判断する
- リスク要因がある部位は代替種目を提案
- 左右バランスに問題があればユニラテラル種目を含める"""

TOOLS = [training_retriever_tool, risk_modification_tool]


def create_planner_message(input_data: dict, analysis_report: dict) -> str:
    """分析結果からプランナー用のメッセージを生成"""
    user_profile = input_data.get("user_profile", {})
    inbody_metrics = input_data.get("inbody_metrics", {})
    goal = input_data.get("goal", {})

    return f"""以下の分析結果を元に、トレーニングメニューを作成してください。

## ユーザープロフィール
- 年齢: {user_profile.get('age', '不明')}歳
- 性別: {user_profile.get('gender', '不明')}
- トレーニング経験: {user_profile.get('training_experience', '不明')}
- 既往歴・怪我: {', '.join(user_profile.get('injuries', ['なし']))}

## InBodyデータサマリー
- 体重: {inbody_metrics.get('weight_kg', '不明')}kg
- 骨格筋量: {inbody_metrics.get('skeletal_muscle_mass_kg', '不明')}kg
- 体脂肪率: {inbody_metrics.get('body_fat_percent', '不明')}%

## 目標
- 目標タイプ: {goal.get('type', '不明')}
- 週のトレーニング日数: {goal.get('days_per_week', '不明')}日

## ユーザーの要望 (Preferences)
- 環境: {input_data.get('preferences', {}).get('environment', '指定なし')}
- 一日のトレーニング時間: {input_data.get('preferences', {}).get('training_time_minutes', '60')}分
- 器具: {input_data.get('preferences', {}).get('equipment', '指定なし')}
- スケジュール: {input_data.get('preferences', {}).get('schedule_notes', 'なし')}
- その他要望: {input_data.get('preferences', {}).get('specific_requests', 'なし')}

## 分析レポート（analyzer_nodeの出力）
- 体型タイプ: {analysis_report.get('body_type', '不明')}
- 体脂肪率評価: {analysis_report.get('body_fat_evaluation', '不明')}
- 骨格筋量評価: {analysis_report.get('skeletal_muscle_evaluation', '不明')}
- 腕の左右バランス: {analysis_report.get('arm_balance', '不明')}
- 脚の左右バランス: {analysis_report.get('leg_balance', '不明')}
- 上下肢バランス: {analysis_report.get('upper_lower_balance', '不明')}
- リスク要因: {', '.join(analysis_report.get('risk_factors', ['なし']))}
- 懸念事項: {', '.join(analysis_report.get('concerns', ['なし']))}

トレーニング分割法と具体的なメニューを提案してください。"""


def _generate_training_plan(state: AgentState) -> dict:
    """最終応答を生成するノード（TrainingPlan構造化出力を使用）"""
    input_data = state["input_data"]
    analysis_report = state["analysis_report"]
    messages = state["messages"]

    tool_results = [msg.content for msg in messages if isinstance(msg, ToolMessage)]
    context_text = "\n\n".join(tool_results) if tool_results else "専門知識なし"

    user_profile = input_data.get("user_profile", {})
    goal = input_data.get("goal", {})

    prompt = f"""以下の情報を元に、トレーニングプランを作成してください。

## 専門知識（検索結果）
{context_text}

## ユーザー情報サマリー
- 年齢: {user_profile.get('age')}歳、性別: {user_profile.get('gender')}
- トレーニング経験: {user_profile.get('training_experience')}
- 目標: {goal.get('type')}、週{goal.get('days_per_week')}回
- 要望: {input_data.get('preferences', {})}

## 分析結果
- 体型タイプ: {analysis_report.get('body_type')}
- リスク要因: {', '.join(analysis_report.get('risk_factors', []))}
- バランス: 腕={analysis_report.get('arm_balance')}, 脚={analysis_report.get('leg_balance')}

上記を踏まえ、具体的な週間トレーニングプランを構造化して出力してください。"""

    llm = get_llm(temperature=0.3)
    structured_llm = llm.with_structured_output(TrainingPlan)
    result = structured_llm.invoke(prompt)

    print("   [Planner] トレーニングプラン（構造化出力）を生成しました")
    return {"training_plan": result.model_dump()}


def build_planner_graph():
    """トレーニングプラン生成ワークフローを構築"""
    return build_tool_agent_graph(
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        final_node_fn=_generate_training_plan,
        temperature=0.3,
    )
