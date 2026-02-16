"""
Serializers for the Project Trainer API.
Handles validation and serialization of input/output data.
"""
from rest_framework import serializers


# =============================================
# Input Serializers (ユーザー入力用)
# =============================================

class SegmentalLeanSerializer(serializers.Serializer):
    """部位別骨格筋量"""
    right_arm = serializers.FloatField(help_text="右腕の骨格筋量 (kg)")
    left_arm = serializers.FloatField(help_text="左腕の骨格筋量 (kg)")
    trunk = serializers.FloatField(help_text="体幹の骨格筋量 (kg)")
    right_leg = serializers.FloatField(help_text="右脚の骨格筋量 (kg)")
    left_leg = serializers.FloatField(help_text="左脚の骨格筋量 (kg)")



class UserProfileSerializer(serializers.Serializer):
    """ユーザープロフィール"""
    age = serializers.IntegerField(min_value=10, max_value=100, help_text="年齢")
    gender = serializers.ChoiceField(
        choices=['男性', '女性'],
        help_text="性別"
    )
    height_cm = serializers.FloatField(min_value=100, max_value=250, help_text="身長 (cm)")
    training_experience = serializers.ChoiceField(
        choices=['初級者', '中級者', '上級者'],
        help_text="トレーニング経験レベル"
    )
    injuries = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=[],
        help_text="既往歴・怪我のリスト"
    )


class InBodyMetricsSerializer(serializers.Serializer):
    """InBody測定データ"""
    weight_kg = serializers.FloatField(min_value=30, max_value=200, help_text="体重 (kg)")
    muscle_mass_kg = serializers.FloatField(min_value=10, max_value=100, help_text="筋肉量 (kg)")
    skeletal_muscle_mass_kg = serializers.FloatField(min_value=5, max_value=60, help_text="骨格筋量 (kg)")
    body_fat_percent = serializers.FloatField(min_value=3, max_value=60, help_text="体脂肪率 (%)")
    segmental_lean = SegmentalLeanSerializer(help_text="部位別骨格筋量")


class GoalSerializer(serializers.Serializer):
    """トレーニング目標"""
    type = serializers.CharField(help_text="目標タイプ（例: ダイエット、筋肥大）")
    days_per_week = serializers.CharField(
        required=False,
        default="",
        help_text="週のトレーニング日数",
        allow_blank=True,
    )


class PreferencesSerializer(serializers.Serializer):
    """ユーザーの好み・制約"""
    environment = serializers.ChoiceField(
        choices=['home', 'gym'],
        required=False,
        default='home',
        help_text="トレーニング環境"
    )
    training_time_minutes = serializers.ChoiceField(
        choices=['5', '10', '15', '30', '45', '60', '90', '120'],
        required=False,
        default='60',
        help_text="一日のトレーニング時間（分）"
    )
    equipment = serializers.CharField(
        required=False,
        default="",
        allow_blank=True,
        help_text="利用可能な器具"
    )
    schedule_notes = serializers.CharField(
        required=False,
        default="",
        allow_blank=True,
        help_text="スケジュールに関する注記"
    )
    specific_requests = serializers.CharField(
        required=False,
        default="",
        allow_blank=True,
        help_text="その他の要望"
    )


class TrainingRequestSerializer(serializers.Serializer):
    """トレーニングメニュー生成リクエスト（統合入力）"""
    user_profile = UserProfileSerializer()
    inbody_metrics = InBodyMetricsSerializer()
    goal = GoalSerializer()
    preferences = PreferencesSerializer(required=False)

    def validate(self, data):
        """追加のバリデーション"""
        # preferencesがない場合はデフォルト値を設定
        if 'preferences' not in data or data['preferences'] is None:
            data['preferences'] = {
                'environment': 'home',
                'equipment': '',
                'schedule_notes': '',
                'specific_requests': ''
            }
        return data


# =============================================
# Output Serializers (レスポンス用)
# =============================================

class ExerciseSerializer(serializers.Serializer):
    """エクササイズ詳細"""
    target_area = serializers.CharField(help_text="対象部位")
    exercise_name = serializers.CharField(help_text="エクササイズ名")
    sets = serializers.IntegerField(help_text="セット数")
    reps = serializers.CharField(help_text="レップ数")
    interval_seconds = serializers.IntegerField(required=False, default=60, help_text="セット間休憩（秒）")
    notes = serializers.CharField(required=False, default="", help_text="実施上の注意")
    instructions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=[],
        help_text="動作手順（ステップバイステップ）"
    )


class DayPlanSerializer(serializers.Serializer):
    """1日分のトレーニングプラン"""
    day_label = serializers.CharField(help_text="日のラベル（例: Day 1）")
    focus = serializers.CharField(help_text="その日のフォーカス")
    exercises = ExerciseSerializer(many=True, help_text="エクササイズリスト")


class TrainingPlanSerializer(serializers.Serializer):
    """トレーニングプラン全体"""
    split_method = serializers.CharField(help_text="分割法")
    split_rationale = serializers.CharField(help_text="分割法の選択理由")
    weekly_schedule = DayPlanSerializer(many=True, help_text="週間スケジュール")
    modifications = serializers.ListField(
        child=serializers.CharField(),
        help_text="リスク要因に基づく修正"
    )
    priority_points = serializers.ListField(
        child=serializers.CharField(),
        help_text="優先的に取り組むポイント"
    )
    nutrition_tips = serializers.ListField(
        child=serializers.CharField(),
        help_text="栄養に関するアドバイス"
    )


class AnalysisReportSerializer(serializers.Serializer):
    """分析レポート"""
    body_type = serializers.CharField(help_text="体型タイプ")
    body_fat_evaluation = serializers.CharField(help_text="体脂肪率評価")
    skeletal_muscle_evaluation = serializers.CharField(help_text="骨格筋量評価")
    arm_balance = serializers.CharField(help_text="腕の左右バランス")
    leg_balance = serializers.CharField(help_text="脚の左右バランス")
    upper_lower_balance = serializers.CharField(help_text="上下肢バランス")
    risk_factors = serializers.ListField(
        child=serializers.CharField(),
        help_text="リスク要因"
    )
    concerns = serializers.ListField(
        child=serializers.CharField(),
        help_text="懸念事項"
    )


class TrainingResponseSerializer(serializers.Serializer):
    """トレーニングメニュー生成レスポンス"""
    analysis_report = AnalysisReportSerializer(help_text="分析レポート")
    training_plan = TrainingPlanSerializer(help_text="トレーニングプラン")
