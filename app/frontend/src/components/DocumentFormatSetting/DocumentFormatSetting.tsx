import { Stack, IconButton, Label } from "@fluentui/react";
import { useState } from 'react';

import styles from "./DocumentFormatSetting.module.css";
import { Save24Filled } from "@fluentui/react-icons";
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
    const [icd10Name, setIcd10Name] = useState<string>("");
    
    const onSaveClicked = () => {
    };

    const onCancelClicked = () => {
    };

    const onReloadFromMasterClicked = () => {
    };

    //setIcd10Name("すべて");
    //icd10Name === undefined && setIcd10Name("hoge" + icd10Code);

    return (
        <div>
            <Stack horizontal>
                <Label>　疾病分類: すべて</Label>
                <Label>{icd10Name}</Label>
            </Stack>
            <Stack horizontal>
                <div className={styles.subDocumentFormatSettingButton} onClick={onReloadFromMasterClicked}>
                    <p className={styles.subDocumentFormatSettingButtonText}>マスター再取得</p>
                </div>
                <div className={styles.subDocumentFormatSettingButton} onClick={onCancelClicked}>
                    <p className={styles.subDocumentFormatSettingButtonText}>編集結果を破棄</p>
                </div>
            </Stack>
            {/* <Label>文書名: </Label>
            <Label>{documentName}</Label><br></br>
            <Label>診療科コード: </Label>
            <Label>{departmentCode}</Label><br></br>
            <Label>疾病分類: </Label>
            <Label>{icd10Name}</Label><br></br> */}
            <Stack>
                {/* <table>
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
                        <td>{icd10Name}</td>
                    </tr>
                </table> */}
                <DocumentFormatSettingByCategory 
                    documentName={documentName}
                    departmentCode={departmentCode}
                    icd10Code={icd10Code}
                    userId={userId} />
                <DocumentFormatSettingByCategory 
                    documentName={documentName}
                    departmentCode={departmentCode}
                    icd10Code={icd10Code}
                    userId={userId} />
                <DocumentFormatSettingByCategory 
                    documentName={documentName}
                    departmentCode={departmentCode}
                    icd10Code={icd10Code}
                    userId={userId} />
                <DocumentFormatSettingByCategory 
                    documentName={documentName}
                    departmentCode={departmentCode}
                    icd10Code={icd10Code}
                    userId={userId} />
                <DocumentFormatSettingByCategory 
                    documentName={documentName}
                    departmentCode={departmentCode}
                    icd10Code={icd10Code}
                    userId={userId} />
                <DocumentFormatSettingByCategory 
                    documentName={documentName}
                    departmentCode={departmentCode}
                    icd10Code={icd10Code}
                    userId={userId} />
                <DocumentFormatSettingByCategory 
                    documentName={documentName}
                    departmentCode={departmentCode}
                    icd10Code={icd10Code}
                    userId={userId} />
            </Stack>
            <div className={styles.footer}>
                <div className={styles.saveDocumentFormatSettingButton} onClick={onSaveClicked}>
                    <Stack horizontal>
                        <Save24Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Edit logo" />
                        <p className={styles.saveDocumentFormatSettingButtonText}>保存する</p>
                    </Stack>
                </div>
            </div>
        </div>
    );
};
