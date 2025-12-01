import { Input } from '../common/Input';
import { IconButton } from '../common/IconButton';
import styles from './ChatInterface.module.css';

interface ChatInputFormProps {
    input: string;
    onInputChange: (value: string) => void;
    onSubmit: (e: React.FormEvent) => void;
    isLoading: boolean;
}

export const ChatInputForm = ({ input, onInputChange, onSubmit, isLoading }: ChatInputFormProps) => {
    return (
        <form onSubmit={onSubmit} className={styles.form}>
            <div className={styles.inputContainer}>
                <Input
                    value={input}
                    onChange={(e) => onInputChange(e.target.value)}
                    placeholder="Enter a prompt here"
                    disabled={isLoading}
                />
                <IconButton type="submit" disabled={!input.trim() || isLoading}>
                    <svg className={styles.icon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                    </svg>
                </IconButton>
            </div>
        </form>
    );
};
