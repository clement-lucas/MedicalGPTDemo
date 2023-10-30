import { Stack, IconButton } from "@fluentui/react";

import styles from "./DocumentFormatSetting.module.css";

import { DocumentFormatSettingByCategory } from "./DocumentFormatSettingByCategory";

interface Props {
    // 文書名
    documentName: string;

    // 診療科コード
    departmentCode: string;

    // ICD10コード
    icd10Code: string;

    // user id
    userId: string;    
}

export const DocumentFormatSetting = ({
    documentName, departmentCode, icd10Code, userId
}: Props) => {
    return (
        <div>
            <Stack>
                <table>
                    <tr>
                        <td className={styles.documentFormatSettingIndexTd}>文書名</td>
                        <td>{documentName}</td>
                    </tr>
                    <tr>
                        <td className={styles.documentFormatSettingIndexTd}>診療科コード</td>
                        <td>{departmentCode}</td>
                    </tr>
                    <tr>
                        <td className={styles.documentFormatSettingIndexTd}>疾病分類</td>
                        <td>{icd10Code}</td>
                    </tr>
                </table>
                <DocumentFormatSettingByCategory 
                    documentName={documentName}
                    departmentCode={departmentCode}
                    icd10Code={icd10Code}
                    userId={userId} />
            </Stack>
        </div>
    );
};
