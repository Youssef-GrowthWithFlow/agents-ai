import styles from '../ChatInterface.module.css';

interface AgentMessageProps {
    text: string;
}

export const AgentMessage = ({ text }: AgentMessageProps) => {
    return (
        <div className={styles.message} data-testid="agent-message">
            <div className={styles.content}>
                <p className={styles.text}>{text}</p>
            </div>
        </div>
    );
};
