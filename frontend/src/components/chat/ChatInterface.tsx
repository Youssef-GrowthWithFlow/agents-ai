import { useState, useRef, useEffect } from 'react';
import { ChatHeader } from './ChatHeader';
import { UserMessage, AgentMessage, WelcomeMessage } from './messages';
import { ChatInputForm } from './ChatInputForm';
import { useChatMessages } from './hooks';
import styles from './ChatInterface.module.css';

export const ChatInterface = () => {
    const { messages, isLoading, sendMessage } = useChatMessages();
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input;
        setInput('');
        await sendMessage(userMessage);
    };

    return (
        <div className={styles.container}>
            <div className={styles.chatBox}>
                <ChatHeader />

                <main className={styles.main}>
                    <div className={styles.messages}>
                        {messages.length === 0 && <WelcomeMessage />}
                        {messages.map(msg => (
                            msg.isUser ? (
                                <UserMessage key={msg.id} text={msg.text} />
                            ) : (
                                <AgentMessage key={msg.id} text={msg.text} />
                            )
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </main>

                <ChatInputForm
                    input={input}
                    onInputChange={setInput}
                    onSubmit={handleSubmit}
                    isLoading={isLoading}
                />
            </div>
        </div>
    );
};
