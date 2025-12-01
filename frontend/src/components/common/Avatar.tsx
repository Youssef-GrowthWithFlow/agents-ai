import styles from './Avatar.module.css';

interface AvatarProps {
  icon: string;
}

export const Avatar = ({ icon }: AvatarProps) => (
  <div className={styles.avatar}>{icon}</div>
);
