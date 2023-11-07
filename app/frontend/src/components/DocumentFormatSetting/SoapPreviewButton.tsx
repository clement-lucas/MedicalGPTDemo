import { Stack } from "@fluentui/react";
import styles from "./SoapPreviewButton.module.css";
import { Eye24Filled } from "@fluentui/react-icons";

interface Props {
    onClick: (icd10Code: string) => void;

    // 患者番号
    patientCode: string;
}

export const SoapPreviewButton = ({ onClick, patientCode }: Props) => {
    return (
        <div className={styles.soapPreviewButton} onClick={() => onClick(patientCode)}>
            <Stack horizontal>
                <Eye24Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Preview logo" />
                <p className={styles.soapPreviewButtonText}>カルテデータ プレビュー</p>
            </Stack>
        </div>
    );
};
