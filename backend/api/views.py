"""
API Views for Project Trainer.
Handles HTTP requests and responses for training menu generation.
"""
import sys
import os
from pathlib import Path

# Add core module to Python path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .serializers import TrainingRequestSerializer, TrainingResponseSerializer


def initialize_environment():
    """環境変数とコアモジュールを初期化"""
    from dotenv import load_dotenv
    
    # Load .env from project root (parent of backend)
    project_root = BACKEND_DIR.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    # Also load from backend directory if exists
    backend_env = BACKEND_DIR / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)


# Initialize environment on module load
initialize_environment()


class GenerateTrainingPlanView(APIView):
    """
    トレーニングプラン生成 API エンドポイント
    
    POST /api/generate/
    
    InBodyデータとユーザー情報を受け取り、
    分析レポートとトレーニングプランを生成して返す。
    """
    
    def post(self, request):
        # 入力データのバリデーション
        serializer = TrainingRequestSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"[API] Validation errors: {serializer.errors}")
            return Response(
                {"error": "Invalid input data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        input_data = serializer.validated_data
        
        try:
            # AIコアを呼び出してプランを生成
            result = self._generate_plan(input_data)
            
            # レスポンスのシリアライズ
            response_serializer = TrainingResponseSerializer(data=result)
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                # 内部エラー（コアからの出力が期待形式でない）
                return Response(
                    {"error": "Internal processing error", "details": response_serializer.errors},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            import traceback
            return Response(
                {"error": str(e), "traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_plan(self, input_data: dict) -> dict:
        """
        AIコアを呼び出してトレーニングプランを生成
        
        Args:
            input_data: バリデーション済みの入力データ
            
        Returns:
            分析レポートとトレーニングプランを含む辞書
        """
        import uuid
        from langchain_core.messages import HumanMessage
        
        # backend/core からインポート（src -> core にリネーム済み）
        from core.orchestrator.graph import build_orchestrator, create_initial_state
        
        print("[API] Building orchestrator...")
        app = build_orchestrator()
        initial_state = create_initial_state(input_data)
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        
        print("[API] Running pipeline...")
        final_state = None
        analysis_report = {}
        training_plan = {}
        
        for event in app.stream(initial_state, config=config, stream_mode="updates"):
            for node_name, node_output in event.items():
                print(f"[API] Node: {node_name}")
                
                if "analysis_report" in node_output and node_output["analysis_report"]:
                    analysis_report = node_output["analysis_report"]
                
                if "training_plan" in node_output and node_output["training_plan"]:
                    training_plan = node_output["training_plan"]
            
            final_state = event
        
        # 結果を取得
        
        if not analysis_report:
            raise ValueError("Analysis report was not generated")
        
        if not training_plan:
            raise ValueError("Training plan was not generated")
        
        return {
            "analysis_report": analysis_report,
            "training_plan": training_plan
        }


@api_view(['GET'])
def health_check(request):
    """
    ヘルスチェックエンドポイント
    
    GET /api/health/
    
    サーバーが正常に動作しているかを確認
    """
    return Response({"status": "healthy", "message": "Project Trainer API is running"})


@api_view(['GET'])
def api_info(request):
    """
    API情報エンドポイント
    
    GET /api/
    
    利用可能なエンドポイントの情報を返す
    """
    return Response({
        "name": "Project Trainer API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/generate/": "トレーニングプラン生成",
            "POST /api/extract-inbody/": "InBody画像からデータ抽出",
            "GET /api/health/": "ヘルスチェック",
            "GET /api/": "API情報"
        }
    })


class ExtractInBodyDataView(APIView):
    """
    InBody画像からデータを抽出するAPIエンドポイント
    
    POST /api/extract-inbody/
    
    InBody結果画像をアップロードすると、
    Gemini Vision APIで解析し、数値データを抽出して返す。
    """
    
    def post(self, request):
        # 画像ファイルの取得
        if 'image' not in request.FILES:
            return Response(
                {"error": "画像ファイルが必要です"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        
        # ファイルタイプの確認
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/heic']
        if image_file.content_type not in allowed_types:
            return Response(
                {"error": f"サポートされていないファイル形式です。対応形式: {', '.join(allowed_types)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 画像データを読み込み
            image_data = image_file.read()
            
            # Gemini Vision APIで解析
            result = self._extract_data_from_image(image_data, image_file.content_type)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            return Response(
                {"error": str(e), "traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _extract_data_from_image(self, image_data: bytes, content_type: str) -> dict:
        """
        Gemini Vision APIを使ってInBody画像からデータを抽出
        """
        from typing import Optional, Literal
        from pydantic import BaseModel, Field
        from google import genai
        from google.genai import types
        from langchain_google_genai import ChatGoogleGenerativeAI

        class SegmentalLean(BaseModel):
            right_arm: Optional[float] = Field(None, description="右腕の骨格筋量(kg)")
            left_arm: Optional[float] = Field(None, description="左腕の骨格筋量(kg)")
            trunk: Optional[float] = Field(None, description="体幹の骨格筋量(kg)")
            right_leg: Optional[float] = Field(None, description="右脚の骨格筋量(kg)")
            left_leg: Optional[float] = Field(None, description="左脚の骨格筋量(kg)")

        class InBodyData(BaseModel):
            weight_kg: Optional[float] = None
            muscle_mass_kg: Optional[float] = None
            skeletal_muscle_mass_kg: Optional[float] = None
            body_fat_percent: Optional[float] = None
            segmental_lean: Optional[SegmentalLean] = None
            confidence: Literal["high", "medium", "low"] = "low"
            notes: Optional[str] = None

        initialize_environment()

        # Step 1: Agentic Vision（Google GenAI SDK）で画像を解析
        client = genai.Client()
        image_part = types.Part.from_bytes(data=image_data, mime_type=content_type)

        prompt = """この画像はInBody（体成分分析装置）の測定結果シートです。
必要に応じて画像をズーム・クロップして、以下の数値データを正確に読み取ってください。

- 体重 (weight_kg) - kg単位
- 筋肉量 (muscle_mass_kg) - kg単位
- 骨格筋量 (skeletal_muscle_mass_kg) - kg単位
- 体脂肪率 (body_fat_percent) - %単位
- 部位別骨格筋量: 左腕、右腕、体幹、左脚、右脚（各kg）

読み取った数値をすべて報告してください。"""

        print("[API] Calling Gemini Agentic Vision for InBody data extraction...")
        vision_response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[image_part, prompt],
            config=types.GenerateContentConfig(
                tools=[types.Tool(code_execution=types.ToolCodeExecution)],
            ),
        )

        # レスポンスからテキスト部分を抽出
        vision_text = ""
        for part in vision_response.candidates[0].content.parts:
            if part.text:
                vision_text += part.text + "\n"

        print(f"[API] Agentic Vision result: {vision_text[:500]}...")

        # Step 2: structured outputで型付きデータに変換
        llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            temperature=0,
        )
        structured_llm = llm.with_structured_output(InBodyData)
        result = structured_llm.invoke(
            f"以下のInBody解析結果から数値を抽出してください:\n\n{vision_text}"
        )

        return result.model_dump()
