const API_URL = 'http://localhost:8001/api/chat';

interface ChatRequest {
  message: string;
}

interface ChatResponse {
  response: string;
}

export const chatService = {
  async sendMessage(message: string): Promise<string> {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message } as ChatRequest)
    });

    if (!response.ok) {
      throw new Error('Failed to get response');
    }

    const data: ChatResponse = await response.json();
    return data.response;
  }
};
