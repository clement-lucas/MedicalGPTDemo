import { Stack } from "@fluentui/react";
import styles from "./DocumentFormatEditButton.module.css";
import { Edit24Filled } from "@fluentui/react-icons";

interface Props {
    onClick: () => void;
}

export const DocumentFormatEditButton = ({ onClick }: Props) => {
    return (
        <div className={styles.documentFormatEditButton} onClick={onClick}>
            <Stack horizontal>
                <Edit24Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Edit logo" />
                <p className={styles.documentFormatEditButtonText}>プロンプト編集</p>
            </Stack>
        </div>
    );
};
