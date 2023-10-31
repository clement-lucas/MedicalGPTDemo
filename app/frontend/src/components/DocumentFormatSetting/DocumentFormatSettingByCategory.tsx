import { useState } from 'react';
import { Stack, TextField, Dropdown, IDropdownOption, Checkbox } from "@fluentui/react";

import styles from "./DocumentFormatSettingByCategory.module.css";

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


// 0: システムコンテンツ
// 1: SOAP と質問文からの生成
// 2: アレルギー・不適応反応
// 3: 退院時使用薬剤
const kindOptions: IDropdownOption[] = [
    { key: 1, text: 'SOAP とプロンプトから生成' },
    { key: 2, text: 'アレルギー・不適応反応' },
    { key: 3, text: '退院時使用薬剤' },
  ];

  
export const DocumentFormatSettingByCategory = ({
    documentName, departmentCode, icd10Code, userId
}: Props) => {
    const [selectedKind, setSelected] = useState<IDropdownOption | undefined>(undefined);
    // Dropdown の初期選択値を設定する
    selectedKind === undefined && setSelected(kindOptions[0]);
    return (
        <div className={styles.backPanel}>
            <div className={styles.container}>
                <p>カテゴリー：<br></br>
                    <TextField
                        className={styles.questionInputTextArea}
                        multiline={false}
                        resizable={false}
                        //onChange={onQuestionChange}
                        //onKeyDown={onEnterPress}
                    />
                </p>
                <p>種類：<br></br>
                    <Dropdown id="hoge"
                        placeholder="Select an option"
                        options={kindOptions}
                        selectedKey={selectedKind ? selectedKind.key : undefined}
                        onChange={(e, option) => setSelected(option)}
                    />            
                </p>
                { selectedKind?.key == 1 && (
                <div>
                    <p>入力情報として使用する項目：<br></br>
                        <Stack horizontal>
                            <Checkbox label="S　　" />
                            <Checkbox label="O　　" />
                            <Checkbox label="A　　" />
                            <Checkbox label="P　　" />
                            <Checkbox label="＃" />
                        </Stack>
                    </p>
                    <p>プロンプト：<br></br>
                        <TextField
                            multiline={true}
                            resizable={true}
                            scrolling="true"
                            //onChange={onQuestionChange}
                            //onKeyDown={onEnterPress}
                        />
                    </p>
                </div>
                )}
            </div>
        </div>
            )}
