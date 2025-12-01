import styles from '../ChatInterface.module.css';

export const WelcomeMessage = () => {
    return (
        <div className={styles.empty}>
            <div className={styles.emptyContent}>
                <div className={styles.emptyIcon}>✨</div>
                <p className={styles.emptyText}>How can I help you today?</p>
            </div>
        </div>
    );
};
