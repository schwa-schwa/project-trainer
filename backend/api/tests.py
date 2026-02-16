"""
API Tests for Project Trainer Backend.

Tests cover:
- Health check endpoint
- API info endpoint
- Training plan generation endpoint (validation + mock response)
- InBody image extraction endpoint (validation only, as actual extraction requires LLM)

テスト実行方法:
================

# 全テスト実行（LLM呼び出しを含むため時間がかかります）
python manage.py test api.tests --verbosity=2

# 高速テストのみ（LLM呼び出しを除く、推奨）
python manage.py test api.tests.HealthCheckTests api.tests.APIInfoTests api.tests.GenerateTrainingPlanMockTests api.tests.ExtractInBodyValidationTests --verbosity=2

# 特定のテストクラスのみ実行
python manage.py test api.tests.HealthCheckTests --verbosity=2

# 特定のテストメソッドのみ実行
python manage.py test api.tests.HealthCheckTests.test_health_check_returns_200 --verbosity=2
"""
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
import json


class HealthCheckTests(APITestCase):
    """ヘルスチェックエンドポイントのテスト"""
    
    def test_health_check_returns_200(self):
        """GET /api/health/ が 200 OK を返すこと"""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
    
    def test_health_check_response_structure(self):
        """ヘルスチェックのレスポンス構造が正しいこと"""
        response = self.client.get('/api/health/')
        self.assertIn('status', response.data)
        self.assertIn('message', response.data)


class APIInfoTests(APITestCase):
    """API情報エンドポイントのテスト"""
    
    def test_api_info_returns_200(self):
        """GET /api/ が 200 OK を返すこと"""
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_api_info_contains_endpoints(self):
        """API情報にエンドポイント一覧が含まれること"""
        response = self.client.get('/api/')
        self.assertIn('endpoints', response.data)
        self.assertIn('name', response.data)
        self.assertIn('version', response.data)


class GenerateTrainingPlanValidationTests(APITestCase):
    """トレーニングプラン生成エンドポイントの入力バリデーションテスト"""
    
    def setUp(self):
        """テスト用の有効な入力データを準備"""
        self.valid_input = {
            "user_profile": {
                "age": 30,
                "gender": "男性",
                "height_cm": 170.0,
                "training_experience": "初級者",
                "injuries": []
            },
            "inbody_metrics": {
                "weight_kg": 70.0,
                "muscle_mass_kg": 30.0,
                "skeletal_muscle_mass_kg": 28.0,
                "body_fat_percent": 20.0,
                "segmental_lean": {
                    "right_arm": 3.0,
                    "left_arm": 2.9,
                    "trunk": 25.0,
                    "right_leg": 9.0,
                    "left_leg": 8.8
                }
            },
            "goal": {
                "type": "ダイエット",
                "days_per_week": "3"
            },
            "preferences": {
                "environment": "home",
                "training_time_minutes": "30",
                "equipment": "ダンベル",
                "schedule_notes": "",
                "specific_requests": ""
            }
        }
    
    def test_missing_user_profile_returns_400(self):
        """user_profile がない場合は 400 エラーを返すこと"""
        data = self.valid_input.copy()
        del data['user_profile']
        response = self.client.post('/api/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_inbody_metrics_returns_400(self):
        """inbody_metrics がない場合は 400 エラーを返すこと"""
        data = self.valid_input.copy()
        del data['inbody_metrics']
        response = self.client.post('/api/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_goal_returns_400(self):
        """goal がない場合は 400 エラーを返すこと"""
        data = self.valid_input.copy()
        del data['goal']
        response = self.client.post('/api/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_age_returns_400(self):
        """age が範囲外の場合は 400 エラーを返すこと"""
        data = self.valid_input.copy()
        data['user_profile']['age'] = 5  # 10未満
        response = self.client.post('/api/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_gender_returns_400(self):
        """gender が無効な値の場合は 400 エラーを返すこと"""
        data = self.valid_input.copy()
        data['user_profile']['gender'] = '不明'
        response = self.client.post('/api/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_training_experience_returns_400(self):
        """training_experience が無効な値の場合は 400 エラーを返すこと"""
        data = self.valid_input.copy()
        data['user_profile']['training_experience'] = 'プロ'
        response = self.client.post('/api/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_preferences_is_optional(self):
        """preferences がなくてもバリデーションを通過すること（内部エラーは許容）"""
        data = self.valid_input.copy()
        del data['preferences']
        # Note: This will likely fail at the AI step, but should pass validation
        response = self.client.post('/api/generate/', data, format='json')
        # 400 (validation error) ではないことを確認
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GenerateTrainingPlanMockTests(APITestCase):
    """トレーニングプラン生成エンドポイントのモックテスト"""
    
    def setUp(self):
        """テスト用の有効な入力データを準備"""
        self.valid_input = {
            "user_profile": {
                "age": 30,
                "gender": "男性",
                "height_cm": 170.0,
                "training_experience": "初級者",
                "injuries": []
            },
            "inbody_metrics": {
                "weight_kg": 70.0,
                "muscle_mass_kg": 30.0,
                "skeletal_muscle_mass_kg": 28.0,
                "body_fat_percent": 20.0,
                "segmental_lean": {
                    "right_arm": 3.0,
                    "left_arm": 2.9,
                    "trunk": 25.0,
                    "right_leg": 9.0,
                    "left_leg": 8.8
                }
            },
            "goal": {
                "type": "ダイエット",
                "days_per_week": "3"
            },
            "preferences": {
                "environment": "home",
                "training_time_minutes": "30",
                "equipment": "ダンベル"
            }
        }
        
        self.mock_response = {
            "analysis_report": {
                "body_type": "適正",
                "body_fat_evaluation": "標準（20%）",
                "skeletal_muscle_evaluation": "標準",
                "arm_balance": "正常（差分3%）",
                "leg_balance": "正常（差分2%）",
                "upper_lower_balance": "正常",
                "risk_factors": [],
                "concerns": []
            },
            "training_plan": {
                "split_method": "全身法",
                "split_rationale": "初級者に最適な分割法",
                "weekly_schedule": [
                    {
                        "day_label": "Day 1",
                        "focus": "全身トレーニング",
                        "exercises": [
                            {
                                "target_area": "脚",
                                "exercise_name": "スクワット",
                                "sets": 3,
                                "reps": "10-15",
                                "interval_seconds": 60,
                                "notes": "",
                                "instructions": ["足を肩幅に開く", "膝を曲げてしゃがむ", "立ち上がる"]
                            }
                        ]
                    }
                ],
                "modifications": [],
                "priority_points": ["正しいフォームを意識"],
                "nutrition_tips": ["タンパク質を十分に摂取"]
            }
        }
    
    @patch('api.views.GenerateTrainingPlanView._generate_plan')
    def test_successful_generation_returns_200(self, mock_generate):
        """正常なリクエストで 200 OK とトレーニングプランを返すこと"""
        mock_generate.return_value = self.mock_response
        
        response = self.client.post('/api/generate/', self.valid_input, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('analysis_report', response.data)
        self.assertIn('training_plan', response.data)
    
    @patch('api.views.GenerateTrainingPlanView._generate_plan')
    def test_response_contains_expected_fields(self, mock_generate):
        """レスポンスに期待するフィールドが含まれること"""
        mock_generate.return_value = self.mock_response
        
        response = self.client.post('/api/generate/', self.valid_input, format='json')
        
        # Analysis report fields
        analysis = response.data['analysis_report']
        self.assertIn('body_type', analysis)
        self.assertIn('body_fat_evaluation', analysis)
        self.assertIn('risk_factors', analysis)
        
        # Training plan fields
        plan = response.data['training_plan']
        self.assertIn('split_method', plan)
        self.assertIn('weekly_schedule', plan)
        self.assertIn('nutrition_tips', plan)


class ExtractInBodyValidationTests(APITestCase):
    """InBody画像抽出エンドポイントの入力バリデーションテスト"""
    
    def test_missing_image_returns_400(self):
        """画像がない場合は 400 エラーを返すこと"""
        response = self.client.post('/api/extract-inbody/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
