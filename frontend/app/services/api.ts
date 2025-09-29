const API_BASE_URL = __DEV__ 
  ? 'http://10.0.2.2:8080'  // Android emulator
  : 'http://localhost:8080'; // iOS simulator/web

interface StyleRequest {
  user_id: string;
  user_prompt: string;
  current_location: string;
}

interface StyleRecommendation {
  celebrity_twin: string;
  weather_info: string;
  final_recommendation: string;
  items_owned: Array<{
    item: string;
    owned_item: string;
    confidence: number;
    source: string;
  }>;
  items_to_buy: Array<{
    item: string;
    suggested_product: string;
    brand: string;
    link: string;
    confidence: number;
  }>;
  extracted_emotion: string;
}

interface UserStatus {
  user_exists: boolean;
  wardrobe_items_count: number;
  purchase_history_count: number;
  total_items: number;
  message: string;
}

class StyleSenseAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async healthCheck() {
    const response = await fetch(`${this.baseURL}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  async getUserStatus(userId: string): Promise<UserStatus> {
    const response = await fetch(`${this.baseURL}/user/${userId}/status`);
    if (!response.ok) {
      throw new Error(`Failed to get user status: ${response.statusText}`);
    }
    return response.json();
  }

  async uploadWardrobeBase64(userId: string, imageBase64: string): Promise<any> {
    const response = await fetch(`${this.baseURL}/user/styles/upload-base64`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        image_base64: imageBase64
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to upload image: ${response.statusText}`);
    }
    return response.json();
  }

  async loadOrderHistory(userId: string): Promise<any> {
    const formData = new FormData();
    formData.append('user_id', userId);

    const response = await fetch(`${this.baseURL}/user/styles/load-orders`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to load order history: ${response.statusText}`);
    }
    return response.json();
  }

  async getStyleRecommendation(request: StyleRequest): Promise<StyleRecommendation> {
    const response = await fetch(`${this.baseURL}/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorData.detail || `Recommendation failed: ${response.statusText}`);
    }
    return response.json();
  }
}

export const styleSenseAPI = new StyleSenseAPI();
export type { StyleRequest, StyleRecommendation, UserStatus };