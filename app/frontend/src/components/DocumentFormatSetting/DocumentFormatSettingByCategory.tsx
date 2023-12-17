import { Stack, TextField, Dropdown, IDropdownOption, Checkbox, Label } from "@fluentui/react";
import { Radio, RadioGroup } from '@fluentui/react-radio';
import { ArrowUp20Filled, ArrowDown20Filled, Delete20Filled } from "@fluentui/react-icons";

import styles from "./DocumentFormatSettingByCategory.module.css";
import { DocumentFormat } from "../../api";

export const USE_RANGE_KIND_ALL_STR = "0"
export const USE_RANGE_KIND_HOSPITALIZATION_STR = "1"
export const USE_RANGE_KIND_DISCHARGE_STR = "2"
export const USE_RANGE_KIND_ALL = 0
export const USE_RANGE_KIND_HOSPITALIZATION = 1
export const USE_RANGE_KIND_DISCHARGE = 2

interface Props {
    documentFormat : DocumentFormat;
    isTop: boolean;
    isBottom: boolean;
    
    onCategoryNameChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onKindChanged: (targetDocumentFormat:DocumentFormat, newValue: number) => void;
    onTargetSoapChanged: (targetDocumentFormat:DocumentFormat, targetSection:string, newValue:boolean) => void;
    onQuestionChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onTemperatureChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onUseRangeKindChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onDaysBeforeTheDateOfHospitalizationToUseChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onDaysAfterTheDateOfHospitalizationToUseChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onDaysBeforeTheDateOfDischargeToUseChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onDaysAfterTheDateOfDischargeToUseChanged: (targetDocumentFormat:DocumentFormat, newValue:string) => void;
    onUpClicked: (documentFormat : DocumentFormat) => void;
    onDownClicked: (documentFormat : DocumentFormat) => void;
    onDeleteClicked: (documentFormatId : number) => void;
}

// 0: システムコンテンツ
// 1: SOAP と質問文からの生成
// 2: アレルギー・不適応反応
// 3: 退院時使用薬剤
const kindOptions: IDropdownOption[] = [
    { key: 1, text: 'SOAP とプロンプトから生成' },
    { key: 2, text: 'アレルギー・不適応反応' },
    { key: 3, text: '退院時使用薬剤' },
  ];
 
export const DocumentFormatSettingByCategory = ({ documentFormat,
    onCategoryNameChanged, onKindChanged, onTargetSoapChanged, onQuestionChanged,
    onTemperatureChanged,
    onUseRangeKindChanged,
    onDaysBeforeTheDateOfHospitalizationToUseChanged, 
    onDaysAfterTheDateOfHospitalizationToUseChanged,
    onDaysBeforeTheDateOfDischargeToUseChanged,
    onDaysAfterTheDateOfDischargeToUseChanged,
    onUpClicked, onDownClicked, onDeleteClicked, isTop, isBottom
}: Props) => {
    return (
        <div className={styles.backPanel}>
            <div className={styles.container}>
                <div className={styles.documentFormatSettingIconButtonContainer}>
                    <div className={styles.documentFormatSettingIconButton}  
                        onClick={() => onDeleteClicked(documentFormat.id)}>
                        <Delete20Filled primaryFill={"rgba(100, 100, 100, 1)"} aria-hidden="true" aria-label="Delete logo" />
                    </div>
                    <Stack horizontal>
                        {!isTop && (
                            <div className={styles.documentFormatSettingIconButton}
                                onClick={() => onUpClicked(documentFormat)}>
                                <ArrowUp20Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Up logo" />
                            </div>
                        )}
                        {!isBottom && (
                            <div className={styles.documentFormatSettingIconButton}
                                onClick={() => onDownClicked(documentFormat)}>
                                <ArrowDown20Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Down logo" />
                            </div>
                        )}
                        <Label>{"表示順: " + (documentFormat.order_no + 1) as string}</Label> 
                    </Stack>
                </div>
                <p>カテゴリー：<br></br>
                    <TextField
                        className={styles.questionInputTextArea}
                        readOnly={false}
                        multiline={false}
                        resizable={false}
                        defaultValue={documentFormat.category_name}
                        value={documentFormat.category_name}
                        onChange={(e, newValue) => onCategoryNameChanged(documentFormat, newValue || "")}
                        onBlur={(e) => onCategoryNameChanged(documentFormat, e.target.value || "")}
                    />
                </p>
                <p>種類：<br></br>
                    <Dropdown
                        placeholder="Select an option"
                        options={kindOptions}
                        selectedKey={documentFormat.kind}
                        onChange={(e, newValue) => {
                            documentFormat.kind = newValue?.key as number || 0;
                            onKindChanged(documentFormat, newValue?.key as number || 0);
                        }}
                    />            
                </p>
                { documentFormat.kind == 1 && (
                <div>
                    <p>入力情報として使用する項目：<br></br>
                        <Stack horizontal>
                            <Checkbox label="S　　"
                                checked={documentFormat.is_s}
                                onChange={(e, newValue) => onTargetSoapChanged(documentFormat, "S", newValue ? true : false)}/>
                            <Checkbox label="O　　" 
                                checked={documentFormat.is_o}
                                onChange={(e, newValue) => onTargetSoapChanged(documentFormat, "O", newValue ? true : false)}/>
                            <Checkbox label="A　　" 
                                checked={documentFormat.is_a}
                                onChange={(e, newValue) => onTargetSoapChanged(documentFormat, "A", newValue ? true : false)}/>
                            <Checkbox label="P　　" 
                                checked={documentFormat.is_p}
                                onChange={(e, newValue) => onTargetSoapChanged(documentFormat, "P", newValue ? true : false)}/>
                            <Checkbox label="＃" 
                                checked={documentFormat.is_b}
                                onChange={(e, newValue) => onTargetSoapChanged(documentFormat, "B", newValue ? true : false)}/>
                        </Stack>
                    </p>
                    <p>Temperature：<br></br>
                        <TextField
                            readOnly={false}
                            multiline={false}
                            resizable={false}
                            defaultValue={documentFormat.temperature_str}
                            value={documentFormat.temperature_str}
                            onChange={(e, newValue) => onTemperatureChanged(documentFormat, newValue || "")}
                            onBlur={(e) => onTemperatureChanged(documentFormat, e.target.value || "")}
                        />
                    </p>
                    <p>使用するカルテデータの期間：<br></br>
                        <RadioGroup value={documentFormat.use_range_kind_str} onChange={(_, data) => onUseRangeKindChanged(documentFormat, data.value)}>
                            <Stack horizontal>
                                <Radio className={styles.radioButton} value={USE_RANGE_KIND_ALL_STR}/>
                                入院日～退院日までのデータを使用
                            </Stack>
                            <Stack horizontal>
                                <Radio className={styles.radioButtonForW} value={USE_RANGE_KIND_HOSPITALIZATION_STR}/>
                                <div className={styles.textForRange}>
                                    入院日
                                </div>
                                <TextField 
                                    className={styles.dayTextField}
                                    readOnly={false}
                                    multiline={false}
                                    resizable={false}
                                    defaultValue={documentFormat.days_before_the_date_of_hospitalization_to_use_str}
                                    value={documentFormat.days_before_the_date_of_hospitalization_to_use_str}
                                    onChange={(e, newValue) => onDaysBeforeTheDateOfHospitalizationToUseChanged(documentFormat, newValue || "")}
                                    onBlur={(e) => onDaysBeforeTheDateOfHospitalizationToUseChanged(documentFormat, e.target.value || "")}
                                />
                                <div className={styles.textForRange}>
                                    日前～入院日
                                </div>
                                <TextField
                                    className={styles.dayTextField}
                                    readOnly={false}
                                    multiline={false}
                                    resizable={false}
                                    defaultValue={documentFormat.days_after_the_date_of_hospitalization_to_use_str}
                                    value={documentFormat.days_after_the_date_of_hospitalization_to_use_str}
                                    onChange={(e, newValue) => onDaysAfterTheDateOfHospitalizationToUseChanged(documentFormat, newValue || "")}
                                    onBlur={(e) => onDaysAfterTheDateOfHospitalizationToUseChanged(documentFormat, e.target.value || "")}
                                />
                                <div className={styles.textForRange}>
                                    日後
                                </div>
                            </Stack>
                            <div className={styles.textForRangeSufix}>
                                までのデータを使用
                            </div>
                            <Stack horizontal>
                                <Radio className={styles.radioButtonForW} value="2"/>
                                <div className={styles.textForRange}>
                                    退院日
                                </div>
                                <TextField 
                                    className={styles.dayTextField}
                                    readOnly={false}
                                    multiline={false}
                                    resizable={false}
                                    defaultValue={documentFormat.days_before_the_date_of_discharge_to_use_str}
                                    value={documentFormat.days_before_the_date_of_discharge_to_use_str}
                                    onChange={(e, newValue) => onDaysBeforeTheDateOfDischargeToUseChanged(documentFormat, newValue || "")}
                                    onBlur={(e) => onDaysBeforeTheDateOfDischargeToUseChanged(documentFormat, e.target.value || "")}
                                />
                                <div className={styles.textForRange}>
                                    日前～退院日
                                </div>
                                <TextField
                                    className={styles.dayTextField}
                                    readOnly={false}
                                    multiline={false}
                                    resizable={false}
                                    defaultValue={documentFormat.days_after_the_date_of_discharge_to_use_str}
                                    value={documentFormat.days_after_the_date_of_discharge_to_use_str}
                                    onChange={(e, newValue) => onDaysAfterTheDateOfDischargeToUseChanged(documentFormat, newValue || "")}
                                    onBlur={(e) => onDaysAfterTheDateOfDischargeToUseChanged(documentFormat, e.target.value || "")}
                                />
                                <div className={styles.textForRange}>
                                    日後
                                </div>
                            </Stack>
                            <div className={styles.textForRangeSufix}>
                                までのデータを使用
                            </div>
                        </RadioGroup>
                    </p>
                    <p>プロンプト：<br></br>
                        <TextField 
                            readOnly={false}
                            multiline={true}
                            resizable={true}
                            scrolling="true"
                            defaultValue={documentFormat.question}
                            value={documentFormat.question}
                            onChange={(e, newValue) => onQuestionChanged(documentFormat, newValue || "")}
                            onBlur={(e) => onQuestionChanged(documentFormat, e.target.value || "")}
                            //onChange={onQuestionChange}
                            //onKeyDown={onEnterPress}
                        />
                    </p>
                </div>
                )}
            </div>
        </div>
            )}
