import { Stack, TextField, Label } from "@fluentui/react";
import { Search24Filled } from "@fluentui/react-icons";
import { getPatientApi, GetPatientResponse, GetPatientRequest } from "../../api";

import styles from "./PatientCodeInput.module.css";

interface Props {
    onPatientCodeChanged: (patientCode: string) => void;
    onPatientNameChanged: (patientName: string) => void;
    disabled: boolean;
    placeholder?: string;
    clearOnSend?: boolean;
    patientCode: string;
    patientName: string;
}

export const PatientCodeInput = ({ onPatientCodeChanged, onPatientNameChanged, disabled, patientCode, patientName}: Props) => {

    const makeApiRequest = async (patientCode: string) => {
        onPatientNameChanged("");
        try {
            const request: GetPatientRequest = {
                patient_code: patientCode,
            };
            const result = await getPatientApi(request);
            onPatientNameChanged(result.name)
        } catch (e) {
            onPatientNameChanged("-");
        } finally {
        }
    };
    
    const enterPatientCode = () => {
        if (disabled || !patientCode.trim()) {
            return;
        }
        // 患者名検索
        makeApiRequest(patientCode);
        onPatientCodeChanged(patientCode);
    };

    const onPatientCodeEnterPress = (ev: React.KeyboardEvent<Element>) => {
        if ((ev.key === "Enter" || ev.key === "Tab") && !ev.shiftKey) {
            ev.preventDefault();
            enterPatientCode();
        }
    };

    const onPatientCodeChange = (_ev: React.FormEvent<HTMLInputElement | HTMLTextAreaElement>, newValue?: string) => {
        if (!newValue) {
            onPatientCodeChanged("");
        } else if (newValue.length <= 1000) {
            onPatientCodeChanged(newValue);
        }
    };

    const onBlur = () => {
        // 患者名検索
        makeApiRequest(patientCode);
        onPatientCodeChanged(patientCode);
    };

    const enterPatientCodeDisabled = disabled || !patientCode.trim();

    return (
        <Stack horizontal>
            <Stack horizontal className={styles.patientCodeInputContainer}>
                <TextField
                    className={styles.patientCodeInputTextArea}
                    placeholder="患者番号を入力してください (e.g. 8888012345)"
                    multiline={false}
                    resizable={false}
                    borderless
                    value={patientCode}
                    onChange={onPatientCodeChange}
                    onKeyDown={onPatientCodeEnterPress}
                    onBlur={onBlur}
                    />
                <div className={styles.patientCodeInputButtonsContainer}>
                    <div
                        className={`${styles.patientCodeInputSendButton} ${enterPatientCodeDisabled ? styles.patientCodeInputSendButtonDisabled : ""}`}
                        aria-label="Search patient button"
                        onClick={enterPatientCode}
                    >
                        <Search24Filled primaryFill="rgba(115, 118, 225, 1)" />
                    </div>
                </div>
            </Stack>
            <Label>　患者名：</Label>
            <Label>{patientName}</Label>
        </Stack>
);
};
