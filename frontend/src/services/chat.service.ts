const API_URL = 'http://localhost:8001/api/chat';

interface ChatRequest {
  message: string;
  conversation_id?: string;
  model_type?: string;
  use_rag: boolean;
}

interface ChatResponse {
  conversation_id: string;
  response: string;
  metadata: {
    model_type: string;
    rag_enabled: boolean;
    sources?: Array<{
      source_title: string;
      document_id: string;
      chunk_index: number;
    }>;
  };
}

let currentConversationId: string | null = null;

export const chatService = {
  async sendMessage(message: string): Promise<string> {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_id: currentConversationId,
        model_type: 'fast',
        use_rag: true
      } as ChatRequest)
    });

    if (!response.ok) {
      throw new Error('Failed to get response');
    }

    const data: ChatResponse = await response.json();

    // Store conversation ID for next messages
    if (!currentConversationId) {
      currentConversationId = data.conversation_id;
    }

    return data.response;
  },

  resetConversation() {
    currentConversationId = null;
  }
};
