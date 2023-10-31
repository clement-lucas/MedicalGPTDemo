import { Stack } from "@fluentui/react";
import styles from "./EditButton.module.css";
import { Edit24Filled } from "@fluentui/react-icons";

interface Props {
    onClick: (icd10Code: string) => void;

    // 文書名
    documentName: string;

    // 診療科コード
    departmentCode: string;

    // ICD10コード
    icd10Code: string;

    // user id
    userId: string;    
}

export const EditButton = ({ onClick, documentName, departmentCode, icd10Code, userId }: Props) => {
    return (
        <div className={styles.editButton} onClick={() => onClick(icd10Code)}>
            <Stack horizontal>
                <Edit24Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Edit logo" />
                <p className={styles.editButtonText}>プロンプト編集</p>
            </Stack>
        </div>
    );
};
