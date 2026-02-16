import axios from 'axios';

// API Base URL - Django backend (Nginx経由)
const API_BASE_URL = 'http://localhost/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * トレーニングプランを生成するAPI呼び出し
 * @param {Object} inputData - ユーザープロフィール、InBodyデータ、目標、好み
 * @returns {Promise<Object>} - 分析レポートとトレーニングプラン
 */
export const generateTrainingPlan = async (inputData) => {
  try {
    const response = await apiClient.post('/generate/', inputData);
    return response.data;
  } catch (error) {
    if (error.response) {
      // サーバーからのエラーレスポンス
      throw new Error(error.response.data.error || 'サーバーエラーが発生しました');
    } else if (error.request) {
      // リクエストは送信されたがレスポンスがない
      throw new Error('サーバーに接続できません。バックエンドが起動しているか確認してください。');
    } else {
      // リクエスト設定時のエラー
      throw new Error('リクエストの作成中にエラーが発生しました');
    }
  }
};

/**
 * ヘルスチェックAPI
 * @returns {Promise<Object>} - ヘルスステータス
 */
export const healthCheck = async () => {
  try {
    const response = await apiClient.get('/health/');
    return response.data;
  } catch (error) {
    throw new Error('APIサーバーに接続できません');
  }
};

/**
 * InBody画像からデータを抽出するAPI呼び出し
 * @param {File} imageFile - InBody結果画像ファイル
 * @returns {Promise<Object>} - 抽出されたInBodyデータ
 */
export const extractInBodyDataFromImage = async (imageFile) => {
  try {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await axios.post(`${API_BASE_URL}/extract-inbody/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.error || '画像の解析に失敗しました');
    } else if (error.request) {
      throw new Error('サーバーに接続できません。バックエンドが起動しているか確認してください。');
    } else {
      throw new Error('画像のアップロード中にエラーが発生しました');
    }
  }
};

export default apiClient;
