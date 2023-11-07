import { Stack, Spinner, Label } from "@fluentui/react";

import styles from "./DocumentFormatSetting.module.css";
import { Save24Filled, Add24Filled } from "@fluentui/react-icons";
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

    isEdited: boolean;

    onSaveClicked: () => void;
    onCancelClicked: () => void;
    onReloadFromMasterClicked: () => void;

    onCategoryNameChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onKindChanged: (targetDocumentFormat:DocumentFormat, newValue: number) => void;
    onTargetSoapChanged: (targetDocumentFormat:DocumentFormat, targetSection:string, newValue:boolean) => void;
    onQuestionChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;

    onUpClicked: (documentFormat : DocumentFormat) => void;
    onDownClicked: (documentFormat : DocumentFormat) => void;
    onDeleteClicked: (documentFormatId : number) => void;
    onAddClicked: () => void;
}

export const DocumentFormatSetting = ({
    documentName, departmentCode, icd10Code, icd10Name, userId, documentFormats, isLoading, isEdited,
    onSaveClicked, onCancelClicked, onReloadFromMasterClicked,
    onCategoryNameChanged, onKindChanged, onTargetSoapChanged, onQuestionChanged,
    onUpClicked, onDownClicked, onDeleteClicked, onAddClicked
}: Props) => {
    
    //icd10Name === undefined && setIcd10Name("hoge" + icd10Code);

    return (
        <div>
            <Stack horizontal>
                <Label>　疾病分類: </Label>
                <Label>{icd10Name}</Label>
            </Stack> 
            {isLoading && (
                <div className={styles.loadingDocumentFormatSpinner}>
                    <Spinner label="Loading document settings" />
                </div>
                )}
            {!isLoading && <div>
                <Stack horizontal>
                    <div className={styles.subDocumentFormatSettingButton} onClick={onReloadFromMasterClicked}>
                        <p className={styles.subDocumentFormatSettingButtonText}>マスター再取得</p>
                    </div>
                    <div className={styles.subDocumentFormatSettingButton} onClick={onCancelClicked}>
                        <p className={styles.subDocumentFormatSettingButtonText}>閉じる</p>
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
                    {
                    documentFormats.map((item) => (
                        <DocumentFormatSettingByCategory 
                            isTop={item.order_no === 0}
                            isBottom={item.order_no === documentFormats.length - 1}
                            documentFormat={item}
                            onCategoryNameChanged={onCategoryNameChanged}
                            onKindChanged={onKindChanged}
                            onTargetSoapChanged={onTargetSoapChanged}
                            onQuestionChanged={onQuestionChanged}
                            onUpClicked={onUpClicked}
                            onDownClicked={onDownClicked}
                            onDeleteClicked={onDeleteClicked}
                            />
                    ))
                    }
                <div className={styles.backPanelAddButton}>
                    <div className={styles.documentFormatSettingAddButton}
                        onClick={() => onAddClicked()}>
                        <Add24Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Edit logo" />
                    </div>
                </div>
                </Stack>
                <div className={styles.footer}>
                    <div className={isEdited ? styles.saveDocumentFormatSettingButton : styles.saveDocumentFormatSettingButtonDisabled} onClick={isEdited ? onSaveClicked : undefined}>
                        <Stack horizontal>
                            <Save24Filled primaryFill={isEdited ? "rgba(115, 118, 225, 1)" : "rgba(85, 85, 85, 1)"} aria-hidden="true" aria-label="Edit logo" />
                            <p className={isEdited ? styles.saveDocumentFormatSettingButtonText : styles.saveDocumentFormatSettingButtonTextDisabled}>保存する</p>
                        </Stack>
                    </div>
                </div>
            </div>}
        </div>
    );
};
