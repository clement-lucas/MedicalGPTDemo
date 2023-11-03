import { Stack, Spinner, Label } from "@fluentui/react";

import styles from "./DocumentFormatSetting.module.css";
import { Save24Filled } from "@fluentui/react-icons";
import { DocumentFormatSettingByCategory } from "./DocumentFormatSettingByCategory";
import { DocumentFormat } from "../../api";

interface Props {
    // 文書名
    documentName: string;

    // 診療科コード
    departmentCode: string;

    // ICD10コード
    icd10Code: string;

    // 疾病分類名
    icd10Name: string;

    // user id
    userId: string; 
    
    // DocumentFormats
    documentFormats: DocumentFormat[];

    isLoading: boolean;

    onSaveClicked: () => void;
    onCancelClicked: () => void;
    onReloadFromMasterClicked: () => void;

    onCategoryNameChanged: (newValue:string, documentFormatId : number) => void;
    onKindChanged: (newValue:number, documentFormatId : number) => void;
    onTargetSoapChanged: (targetSection:string, newValue:boolean, documentFormatId : number) => void;
    onQuestionChanged: (newValue:string, documentFormatId : number) => void;

    onUpClicked: (documentFormat : DocumentFormat) => void;
    onDownClicked: (documentFormat : DocumentFormat) => void;
    onDeleteClicked: (documentFormatId : number) => void;
}

export const DocumentFormatSetting = ({
    documentName, departmentCode, icd10Code, icd10Name, userId, documentFormats, isLoading,
    onSaveClicked, onCancelClicked, onReloadFromMasterClicked,
    onCategoryNameChanged, onKindChanged, onTargetSoapChanged, onQuestionChanged,
    onUpClicked, onDownClicked, onDeleteClicked
}: Props) => {
    
    //icd10Name === undefined && setIcd10Name("hoge" + icd10Code);

    return (
        <div>
            <Stack horizontal>
                <Label>　疾病分類: </Label>
                <Label>{icd10Name}</Label>
            </Stack> 
            {!isLoading && <div>
                <Stack horizontal>
                    <div className={styles.subDocumentFormatSettingButton} onClick={onReloadFromMasterClicked}>
                        <p className={styles.subDocumentFormatSettingButtonText}>マスター再取得</p>
                    </div>
                    <div className={styles.subDocumentFormatSettingButton} onClick={onCancelClicked}>
                        <p className={styles.subDocumentFormatSettingButtonText}>編集結果を破棄</p>
                    </div>
                </Stack>
                {isLoading && <Spinner label="Loading document settings" />}
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
                    {documentFormats.map((item) => (
                        <DocumentFormatSettingByCategory 
                            documentFormat={item}
                            onCategoryNameChanged={onCategoryNameChanged}
                            onKindChanged={onKindChanged}
                            onTargetSoapChanged={onTargetSoapChanged}
                            onQuestionChanged={onQuestionChanged}
                            onUpClicked={onUpClicked}
                            onDownClicked={onDownClicked}
                            onDeleteClicked={onDeleteClicked}
                            />
                    ))}
                </Stack>
                <div className={styles.footer}>
                    <div className={styles.saveDocumentFormatSettingButton} onClick={onSaveClicked}>
                        <Stack horizontal>
                            <Save24Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Edit logo" />
                            <p className={styles.saveDocumentFormatSettingButtonText}>保存する</p>
                        </Stack>
                    </div>
                </div>
            </div>}
        </div>
    );
};
