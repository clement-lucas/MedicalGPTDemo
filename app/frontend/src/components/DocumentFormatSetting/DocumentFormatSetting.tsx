import { Stack, Spinner, Label, TextField } from "@fluentui/react";

import styles from "./DocumentFormatSetting.module.css";
import { Save24Filled, Add24Filled } from "@fluentui/react-icons";
import { DocumentFormatSettingByCategory } from "./DocumentFormatSettingByCategory";
import { DocumentFormatIndex, DocumentFormat } from "../../api";

interface Props {
    // 文書名
    documentName: string;

    // 選択された文書フォーマットのインデックス
    documentFormatIndex: DocumentFormatIndex;

    // user id
    userId: string; 

    systemContents: string;
    
    // DocumentFormats
    documentFormats: DocumentFormat[];

    isLoading: boolean;

    isEdited: boolean;

    saveAsName: string;

    onSaveClicked: (index_id:number, index_name:string) => void;
    onCancelClicked: () => void;

    onSystemContentsChanged: (newValue:string) => void;
    onCategoryNameChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onKindChanged: (targetDocumentFormat:DocumentFormat, newValue: number) => void;
    onTargetSoapChanged: (targetDocumentFormat:DocumentFormat, targetSection:string, newValue:boolean) => void;
    onQuestionChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onTemperatureChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onTagsChanged: (targetDocumentFormatIndex:DocumentFormatIndex, newValue:string) => void;
    onSaveAsNameChanged: (newValue:string) => void;

    onUpClicked: (documentFormat : DocumentFormat) => void;
    onDownClicked: (documentFormat : DocumentFormat) => void;
    onDeleteClicked: (documentFormatId : number) => void;
    onAddClicked: () => void;
}

export const DocumentFormatSetting = ({
    documentName, documentFormatIndex, userId, 
    systemContents, 
    documentFormats, isLoading, isEdited, saveAsName,
    onSaveClicked, onCancelClicked,
    onSystemContentsChanged,
    onCategoryNameChanged, onKindChanged, onTargetSoapChanged, onQuestionChanged,
    onTemperatureChanged, onTagsChanged, onSaveAsNameChanged,
    onUpClicked, onDownClicked, onDeleteClicked, onAddClicked
}: Props) => {
    
    return (
        <div>
            {isLoading && (
                <div className={styles.loadingDocumentFormatSpinner}>
                    <Spinner label="Loading document settings" />
                </div>
                )}
            {!isLoading && <div>
                <Label>プロンプト名</Label>
                <Label>{documentFormatIndex.index_name}</Label><br></br>
                <Stack horizontal>
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
                    <p className={styles.systemContens} >System Contents Prompt : <br></br>
                        <TextField
                            readOnly={false}
                            multiline={true}
                            resizable={true}
                            scrolling="true"
                            defaultValue={systemContents}
                            value={systemContents}
                            onChange={(e, newValue) => onSystemContentsChanged(newValue || "")}
                            onBlur={(e) => onSystemContentsChanged(e.target.value || "")}
                            //onChange={onQuestionChange}
                            //onKeyDown={onEnterPress}
                        />
                    </p>
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
                            onTemperatureChanged={onTemperatureChanged}
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
                    <p>最終更新日時: </p>
                    <p>{documentFormatIndex.updated_date_time}</p><br></br>
                    <p>最終更新ユーザー: </p>
                    <p>{documentFormatIndex.updated_by}</p><br></br>
                    <p>検索用タグ：<br></br>
                        <TextField
                            placeholder="e.g. 内科, インフルエンザ, 肺炎"
                            readOnly={false}
                            multiline={true}
                            resizable={true}
                            scrolling="true"
                            defaultValue={documentFormatIndex.tags}
                            value={documentFormatIndex.tags}
                            onChange={(e, newValue) => onTagsChanged(documentFormatIndex, newValue || "")}
                            onBlur={(e) => onTagsChanged(documentFormatIndex, e.target.value || "")}
                        />
                    </p>
                    
                    <div className={isEdited && userId === documentFormatIndex.updated_by ? 
                        styles.saveDocumentFormatSettingButton : 
                        styles.saveDocumentFormatSettingButtonDisabled} 
                        onClick={isEdited && userId === documentFormatIndex.updated_by ? 
                            () =>
                            onSaveClicked(documentFormatIndex.index_id, documentFormatIndex.index_name) :
                        undefined}>
                        <Stack horizontal>
                            <Save24Filled primaryFill={isEdited ? "rgba(115, 118, 225, 1)" : "rgba(85, 85, 85, 1)"} aria-hidden="true" aria-label="Edit logo" />
                            <p className={isEdited && userId === documentFormatIndex.updated_by ? 
                                styles.saveDocumentFormatSettingButtonText : 
                                styles.saveDocumentFormatSettingButtonTextDisabled}>上書き保存する</p>
                        </Stack>
                    </div>
                    <div className={isEdited ? 
                        styles.saveDocumentFormatSettingButton : 
                        styles.saveDocumentFormatSettingButtonDisabled} 
                        onClick={isEdited ? 
                            () =>
                            onSaveClicked(-1, saveAsName) :
                        undefined}>
                        <Stack horizontal>
                            <Save24Filled primaryFill={isEdited ? "rgba(115, 118, 225, 1)" : "rgba(85, 85, 85, 1)"} aria-hidden="true" aria-label="Edit logo" />
                            <p className={isEdited ? 
                                styles.saveDocumentFormatSettingButtonText : 
                                styles.saveDocumentFormatSettingButtonTextDisabled}>名前を付けて保存する</p>
                        </Stack>
                    </div>
                    <TextField
                        placeholder="新しいプロンプト名"
                        readOnly={false}
                        multiline={false}
                        resizable={false}
                        defaultValue={saveAsName}
                        value={saveAsName}
                        onChange={(e, newValue) => onSaveAsNameChanged(newValue || "")}
                        onBlur={(e) => onSaveAsNameChanged(e.target.value || "")}
                    />
                </div>
            </div>}
        </div>
    );
};
