import styles from './Input.module.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = ({ className = '', ...props }: InputProps) => (
  <input className={`${styles.input} ${className}`} {...props} />
);
