import { Stack, TextField, IconButton, Checkbox } from "@fluentui/react";

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

export const DocumentFormatSettingByCategory = ({
    documentName, departmentCode, icd10Code, userId
}: Props) => {
    return (
        <div>
            <p>カテゴリー：<br></br>
                <TextField
                    className={styles.questionInputTextArea}
                    multiline={false}
                    resizable={false}
                    //onChange={onQuestionChange}
                    //onKeyDown={onEnterPress}
                />
            </p>
            <p>プロンプト：<br></br>
            <TextField
                    className={styles.questionInputTextArea}
                    multiline={true}
                    resizable={true}
                    scrolling="true"
                    //onChange={onQuestionChange}
                    //onKeyDown={onEnterPress}
                />
            </p>
            <p>入力情報として使用する項目：<br></br>
                <Stack horizontal>
                    <Checkbox label="S　　" />
                    <Checkbox label="O　　" />
                    <Checkbox label="A　　" />
                    <Checkbox label="P　　" />
                    <Checkbox label="＃" />
                </Stack>
            </p>
            <hr></hr>
        </div>
            )}
