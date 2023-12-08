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

    tags: string;

    onSaveClicked: (index_id:number, index_name:string) => void;
    onDeleteIndexClicked: (targetDocumentFormatIndex:DocumentFormatIndex) => void;

    onSystemContentsChanged: (newValue:string) => void;
    onCategoryNameChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onKindChanged: (targetDocumentFormat:DocumentFormat, newValue: number) => void;
    onTargetSoapChanged: (targetDocumentFormat:DocumentFormat, targetSection:string, newValue:boolean) => void;
    onQuestionChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onTemperatureChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onStartDayToUseSoapRangeAfterHospitalizationChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onUseSoapRangeDaysAfterHospitalizationChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onStartDayToUseSoapRangeBeforeDischargeChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onUseSoapRangeDaysBeforeDischargeChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onTagsChanged: (targetDocumentFormatIndex:DocumentFormatIndex, newValue:string) => void;
    onSaveAsNameChanged: (newValue:string) => void;

    onUpClicked: (documentFormat : DocumentFormat) => void;
    onDownClicked: (documentFormat : DocumentFormat) => void;
    onDeleteCategoryClicked: (documentFormatId : number) => void;
    onAddClicked: () => void;
}

export const DocumentFormatSetting = ({
    documentName, documentFormatIndex, userId, 
    systemContents, 
    documentFormats, isLoading, isEdited, saveAsName, tags,
    onSaveClicked, onDeleteIndexClicked,
    onSystemContentsChanged,
    onCategoryNameChanged, onKindChanged, onTargetSoapChanged, onQuestionChanged,
    onTemperatureChanged, 
    onStartDayToUseSoapRangeAfterHospitalizationChanged, onUseSoapRangeDaysAfterHospitalizationChanged,
    onStartDayToUseSoapRangeBeforeDischargeChanged, onUseSoapRangeDaysBeforeDischargeChanged,
    onTagsChanged, onSaveAsNameChanged,
    onUpClicked, onDownClicked, onDeleteCategoryClicked: onDeleteClicked, onAddClicked
}: Props) => {
    
    const promptNameLabelStyles = {
        root: {
          color: '#ffffff',
          font: '16px',
          fontWeight: 'bold',
          textAliegn: 'left',
          paddingLeft: '5px',
          width: '100%',
          backgroundColor: 'rgb(95, 95, 95)',
        }
    };

    return (
        <div>
            {isLoading && (
                <div className={styles.loadingDocumentFormatSpinner}>
                    <Spinner label="Loading document settings" />
                </div>
                )}
            {!isLoading && <div>
                <Label styles={promptNameLabelStyles}>{documentFormatIndex.index_name}</Label>
                <table className={styles.documentFormatSettingIndexTable}>
                    {/* <tr>
                        <td className={styles.documentFormatSettingIndexTd}>プロンプト名：</td>
                        <td>{documentFormatIndex.index_name}</td>
                    </tr> */}
                    <tr>
                        <td className={styles.documentFormatSettingIndexTd}>最終更新日時：</td>
                        <td>{documentFormatIndex.updated_date_time}</td>
                    </tr>
                    <tr>
                        <td className={styles.documentFormatSettingIndexTd}>最終更新ユーザー：</td>
                        <td>{documentFormatIndex.updated_by}</td>
                    </tr>
                </table>
                {documentFormatIndex.updated_by === userId &&
                    <div className={styles.subDocumentFormatSettingButton} 
                        onClick={()=>onDeleteIndexClicked(documentFormatIndex)}>
                        <p className={styles.subDocumentFormatSettingButtonText}>削除</p>
                    </div>
                }
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
                            onStartDayToUseSoapRangeAfterHospitalizationChanged={onStartDayToUseSoapRangeAfterHospitalizationChanged}
                            onUseSoapRangeDaysAfterHospitalizationChanged={onUseSoapRangeDaysAfterHospitalizationChanged}
                            onStartDayToUseSoapRangeBeforeDischargeChanged={onStartDayToUseSoapRangeBeforeDischargeChanged}
                            onUseSoapRangeDaysBeforeDischargeChanged={onUseSoapRangeDaysBeforeDischargeChanged}
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
                    <p>検索用タグ：<br></br>
                        <TextField
                            placeholder="例）内科, インフルエンザ, 肺炎"
                            readOnly={false}
                            multiline={true}
                            resizable={true}
                            scrolling="true"
                            defaultValue={tags}
                            value={tags}
                            onChange={(e, newValue) => onTagsChanged(documentFormatIndex, newValue || "")}
                            onBlur={(e) => onTagsChanged(documentFormatIndex, e.target.value || "")}
                        />
                    </p>
                    {documentFormatIndex.updated_by === userId &&
                        <div className={isEdited ? 
                            styles.saveDocumentFormatSettingButton : 
                            styles.saveDocumentFormatSettingButtonDisabled} 
                            onClick={isEdited ? 
                                () =>
                                onSaveClicked(documentFormatIndex.index_id, documentFormatIndex.index_name) :
                            undefined}>
                            <Stack horizontal>
                                <Save24Filled primaryFill={isEdited && userId === documentFormatIndex.updated_by ? "rgba(115, 118, 225, 1)" : "rgba(85, 85, 85, 1)"} aria-hidden="true" aria-label="Edit logo" />
                                <p className={isEdited ? 
                                    styles.saveDocumentFormatSettingButtonText : 
                                    styles.saveDocumentFormatSettingButtonTextDisabled}>上書き保存する</p>
                            </Stack>
                        </div>
                    }
                    <div className={saveAsName != "" ? 
                        styles.saveDocumentFormatSettingButton : 
                        styles.saveDocumentFormatSettingButtonDisabled} 
                        onClick={saveAsName != "" ?
                            () =>
                            onSaveClicked(-1, saveAsName) :
                        undefined}>
                        <Stack horizontal>
                            <Save24Filled primaryFill={saveAsName != "" ? "rgba(115, 118, 225, 1)" : "rgba(85, 85, 85, 1)"} aria-hidden="true" aria-label="Save As logo" />
                            <p className={saveAsName != "" ? 
                                styles.saveDocumentFormatSettingButtonText : 
                                styles.saveDocumentFormatSettingButtonTextDisabled}>名前を付けて保存する</p>
                        </Stack>
                    </div>
                    <TextField
                        placeholder="新しいプロンプト名を入力して下さい"
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
