import styles from '../ChatInterface.module.css';

interface UserMessageProps {
    text: string;
}

export const UserMessage = ({ text }: UserMessageProps) => {
    return (
        <div className={styles.userMessage} data-testid="user-message">
            <div className={styles.userMessageContent}>
                <p className={styles.userMessageText}>{text}</p>
            </div>
        </div>
    );
};
