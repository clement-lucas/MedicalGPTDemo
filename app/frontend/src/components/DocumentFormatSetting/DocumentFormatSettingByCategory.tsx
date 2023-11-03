import { useState } from 'react';
import { Stack, TextField, Dropdown, IDropdownOption, Checkbox, Label } from "@fluentui/react";
import { ArrowUp16Filled, ArrowDown16Filled, Delete16Filled } from "@fluentui/react-icons";

import styles from "./DocumentFormatSettingByCategory.module.css";
import { DocumentFormat } from "../../api";

interface Props {
    documentFormat : DocumentFormat;
    onCategoryNameChanged: (newValue:string, documentFormatId : number) => void;
    onKindChanged: (newValue: number, documentFormatId : number) => void;
    onTargetSoapChanged: (targetSection:string, newValue:boolean, documentFormatId : number) => void;
    onQuestionChanged: (newValue:string, documentFormatId : number) => void;
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
    onUpClicked, onDownClicked, onDeleteClicked
}: Props) => {
    const [selectedKind, setSelected] = useState<IDropdownOption | undefined>(undefined);

    const kind2key = (kind: number) : number => {
        if (kind < 1 || kind > 3) {
            throw new Error("kind is out of range");
        }
        return kind - 1;
    };

    // Dropdown の初期選択値を設定する
    selectedKind === undefined && setSelected(kindOptions[kind2key(documentFormat.kind)]);

    return (
        <div className={styles.backPanel}>
            <div className={styles.container}>
                {/* <div className={styles.documentFormatSettingIconButtonContainer}>
                    <div className={styles.documentFormatSettingIconButton}  
                        onClick={() => onDeleteClicked(documentFormat.id)}>
                        <Delete16Filled primaryFill={"rgba(DD, 0, 0, 1)"} aria-hidden="true" aria-label="Edit logo" />
                    </div>
                    <Stack horizontal>
                        <Label>{documentFormat.order_no}</Label> 
                        <div className={styles.documentFormatSettingIconButton}
                            onClick={() => onUpClicked(documentFormat)}>
                            <ArrowUp16Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Edit logo" />
                        </div>
                        <div className={styles.documentFormatSettingIconButton}
                            onClick={() => onDownClicked(documentFormat)}>
                            <ArrowDown16Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Edit logo" />
                        </div>
                    </Stack>
                </div> */}
                <p>カテゴリー：<br></br>
                    <TextField
                        className={styles.questionInputTextArea}
                        readOnly={false}
                        multiline={false}
                        resizable={false}
                        defaultValue={documentFormat.category_name}
                        onChange={(e, newValue) => onCategoryNameChanged(newValue || "", documentFormat.id)}
                        onBlur={(e) => onCategoryNameChanged(e.target.value || "", documentFormat.id)}
                    />
                </p>
                <p>種類：<br></br>
                    <Dropdown id="hoge"
                        placeholder="Select an option"
                        options={kindOptions}
                        selectedKey={selectedKind ? selectedKind.key : undefined}
                        onChange={(e, newValue) => {
                            setSelected(newValue);
                            onKindChanged(newValue?.key as number || 0, documentFormat.id);
                        }}
                    />            
                </p>
                { selectedKind?.key == 1 && (
                <div>
                    <p>入力情報として使用する項目：<br></br>
                        <Stack horizontal>
                            <Checkbox label="S　　"
                                checked={documentFormat.is_s}
                                onChange={(e, newValue) => onTargetSoapChanged("S", newValue ? true : false, documentFormat.id)}/>
                            <Checkbox label="O　　" 
                                checked={documentFormat.is_o}
                                onChange={(e, newValue) => onTargetSoapChanged("O", newValue ? true : false, documentFormat.id)}/>
                            <Checkbox label="A　　" 
                                checked={documentFormat.is_a}
                                onChange={(e, newValue) => onTargetSoapChanged("A", newValue ? true : false, documentFormat.id)}/>
                            <Checkbox label="P　　" 
                                checked={documentFormat.is_p}
                                onChange={(e, newValue) => onTargetSoapChanged("P", newValue ? true : false, documentFormat.id)}/>
                            <Checkbox label="＃" 
                                checked={documentFormat.is_b}
                                onChange={(e, newValue) => onTargetSoapChanged("B", newValue ? true : false, documentFormat.id)}/>
                        </Stack>
                    </p>
                    <p>プロンプト：<br></br>
                        <TextField
                            readOnly={false}
                            multiline={true}
                            resizable={true}
                            scrolling="true"
                            defaultValue={documentFormat.question}
                            onChange={(e, newValue) => onQuestionChanged(newValue || "", documentFormat.id)}
                            onBlur={(e) => onQuestionChanged(e.target.value || "", documentFormat.id)}
                            //onChange={onQuestionChange}
                            //onKeyDown={onEnterPress}
                        />
                    </p>
                </div>
                )}
            </div>
        </div>
            )}
