from typing import List, Dict, Any, Optional, TypedDict
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field

# --- Pydantic Models for Structured Output ---

class Exercise(BaseModel):
    target_area: str = Field(description="対象部位（胸、背中、脚など）")
    exercise_name: str = Field(description="種目名")
    sets: int = Field(description="セット数")
    reps: str = Field(description="レップ数（例: '8-12'）")
    interval_seconds: int = Field(default=60, description="セット間休憩時間（秒）（例: 30, 60, 90）")
    notes: str = Field(default="", description="実施時の注意点")
    instructions: List[str] = Field(default=[], description="動作手順のステップリスト")

class DayPlan(BaseModel):
    day_label: str = Field(description="曜日ラベル（例: 'Day 1', '月曜日'）")
    focus: str = Field(description="その日のトレーニングの焦点")
    exercises: List[Exercise] = Field(description="種目リスト")

class TrainingPlan(BaseModel):
    split_method: str = Field(description="分割法（全身法、上下分割など）")
    split_rationale: str = Field(description="この分割法を選んだ理由")
    weekly_schedule: List[DayPlan] = Field(description="週間スケジュール")
    modifications: List[str] = Field(description="リスクに基づく種目変更・代替案")
    priority_points: List[str] = Field(description="優先的に取り組むべきポイント")
    nutrition_tips: List[str] = Field(description="栄養に関するアドバイス")

# --- Agent State ---

class AgentState(MessagesState):
    """
    Unified State for the entire pipeline (Analyzer -> Planner).
    """
    input_data: Dict[str, Any]      # User Profile, InBody Data, Goal, Preferences
    analysis_report: Dict[str, Any] # Output from Analyzer
    training_plan: Dict[str, Any]   # Output from Planner (as dict)
