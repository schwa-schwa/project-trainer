from langchain_core.tools import tool
from core.common.retriever import search_knowledge


@tool
def retriever_tool(query: str) -> str:
    """
    体組成分析の専門知識ベースから関連情報を検索するツール。

    【重要】このツールは1回のターンで1度だけ呼び出してください。
    複数の検索項目がある場合は、クエリをスペース区切り等で1つにまとめてください。

    【対応カテゴリ (v3.1)】
    1. 体型分類/詳細（10タイプ）:
       痩せ, やや痩せ, スリム, 筋肉型スリム, 適正,
       筋肉型, アスリート, 隠れ肥満, やや肥満, 肥満
       ※各タイプに「代謝特性」「栄養戦略」「有酸素運動ガイド」が含まれます。
    2. 指標判定基準: 体脂肪率(11-14), 筋肉量(15)
    3. リスク・進行モデル:
       - 体型別リスク: 関節, 代謝, ホルモン(16-18)
       - 進行モデル: 線形, ダブルプログレッション, ピリオダイゼーション(19-21)
    4. トレーニング種目ライブラリ:
       - 部位別: 下半身, 胸, 背中, 肩, 腕・コア(25-40)
       - 特性: 家トレ可, ダンベル種目, 初心者向け(定番)
    5. その他: 左右差(22), リカバリー(23), サプリメント(24)

    Args:
        query: 検索クエリ（複数の場合はまとめて入力）
            例: "隠れ肥満型 アドバイス 骨格筋量 評価 基準 リカバリー サプリメント"

    Returns:
        str: 検索された専門知識のテキスト
    """
    return search_knowledge(query, k=3, fetch_k=10)


@tool
def calculate_smm_ratio(skeletal_muscle_mass_kg: float, weight_kg: float, gender: str) -> str:
    """
    体重比骨格筋量（SMM/Weight）を計算し、評価を返すツール。
    """
    if skeletal_muscle_mass_kg <= 0 or weight_kg <= 0:
        return "エラー: 骨格筋量と体重は正の値を入力してください。"

    smm_ratio = (skeletal_muscle_mass_kg / weight_kg) * 100

    if gender == "男性":
        if smm_ratio >= 45: evaluation = "優秀"
        elif smm_ratio >= 39: evaluation = "標準"
        else: evaluation = "不足"
    elif gender == "女性":
        if smm_ratio >= 40: evaluation = "優秀"
        elif smm_ratio >= 34: evaluation = "標準"
        else: evaluation = "不足"
    else:
        evaluation = "判定不可（性別を確認してください）"

    return f"体重比骨格筋量: {smm_ratio:.1f}%（{gender}：{evaluation}）"


@tool
def evaluate_body_type(weight_kg: float, height_cm: float, body_fat_percent: float, gender: str) -> str:
    """
    体重・身長・体脂肪率から体型タイプを判定するツール。
    InBodyの体型評価マトリックスに基づき判定します。
    """
    if weight_kg <= 0 or height_cm <= 0 or body_fat_percent < 0:
        return "エラー: 体重、身長、体脂肪率は正の値を入力してください。"

    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)

    if gender == "男性":
        if bmi >= 25:
            if body_fat_percent < 15: body_type = "アスリート"
            elif body_fat_percent < 20: body_type = "やや肥満"
            else: body_type = "肥満"
        elif bmi >= 21.75:
            if body_fat_percent < 15: body_type = "筋肉型"
            elif body_fat_percent < 20: body_type = "適正"
            else: body_type = "やや肥満"
        elif bmi >= 18.5:
            if body_fat_percent < 10: body_type = "筋肉型スリム"
            elif body_fat_percent < 15: body_type = "スリム"
            elif body_fat_percent < 20: body_type = "適正"
            else: body_type = "隠れ肥満"
        else:
            if body_fat_percent < 10: body_type = "痩せ"
            elif body_fat_percent < 20: body_type = "やや痩せ"
            else: body_type = "隠れ肥満"

    elif gender == "女性":
        if bmi >= 25:
            if body_fat_percent < 23: body_type = "アスリート"
            elif body_fat_percent < 28: body_type = "やや肥満"
            else: body_type = "肥満"
        elif bmi >= 21.75:
            if body_fat_percent < 23: body_type = "筋肉型"
            elif body_fat_percent < 28: body_type = "適正"
            else: body_type = "やや肥満"
        elif bmi >= 18.5:
            if body_fat_percent < 18: body_type = "筋肉型スリム"
            elif body_fat_percent < 23: body_type = "スリム"
            elif body_fat_percent < 28: body_type = "適正"
            else: body_type = "隠れ肥満"
        else:
            if body_fat_percent < 18: body_type = "痩せ"
            elif body_fat_percent < 28: body_type = "やや痩せ"
            else: body_type = "隠れ肥満"
    else:
        return "エラー: 性別は「男性」または「女性」を指定してください。"

    return f"体型タイプ: {body_type}（BMI: {bmi:.1f}, 体脂肪率: {body_fat_percent:.1f}%）"