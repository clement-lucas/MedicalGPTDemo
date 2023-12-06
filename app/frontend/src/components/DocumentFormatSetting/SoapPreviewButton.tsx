import { Stack } from "@fluentui/react";
import styles from "./SoapPreviewButton.module.css";
import { Eye24Filled } from "@fluentui/react-icons";

interface Props {
    onClick: (icd10Code: string) => void;

    // 患者番号
    pid: string;
}

export const SoapPreviewButton = ({ onClick, pid }: Props) => {
    return (
        <div className={styles.soapPreviewButton} onClick={() => onClick(pid)}>
            <Stack horizontal>
                <Eye24Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Preview logo" />
                <p className={styles.soapPreviewButtonText}>カルテデータ プレビュー</p>
            </Stack>
        </div>
    );
};
