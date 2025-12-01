import { useState } from 'react';
import { chatService } from '../../../services/chat.service';

export interface Message {
    id: string;
    text: string;
    isUser: boolean;
}

export const useChatMessages = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const sendMessage = async (userMessage: string) => {
        setMessages(prev => [...prev, {
            id: Date.now().toString(),
            text: userMessage,
            isUser: true
        }]);

        setIsLoading(true);

        try {
            const response = await chatService.sendMessage(userMessage);
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                text: response,
                isUser: false
            }]);
        } catch (error) {
            console.error('Error:', error);
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                text: "Sorry, I couldn't process your request.",
                isUser: false
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return {
        messages,
        isLoading,
        sendMessage
    };
};
