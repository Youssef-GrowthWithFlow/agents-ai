import styles from './IconButton.module.css';

interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

export const IconButton = ({ children, className = '', ...props }: IconButtonProps) => (
  <button className={`${styles.button} ${className}`} {...props}>
    {children}
  </button>
);
