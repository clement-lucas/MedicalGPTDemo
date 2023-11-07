import styles from "./DischargeButton.module.css";

interface Props {
    text: string;
    value: string;
    onClick: (value: string) => void;
}

export const DischargeButton = ({ text, value, onClick }: Props) => {
    return (
        <div className={styles.dischargeButton} onClick={() => onClick(value)}>
            <p className={styles.dischargeButtonText}>{text}</p>
        </div>
    );
};
