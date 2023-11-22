import { useRef, useState} from "react";
import { Dropdown, IDropdownOption, Spinner, TextField} from "@fluentui/react";
import { Label, Stack } from "@fluentui/react";
import { PrimaryButton } from '@fluentui/react/lib/Button';

import styles from "./Discharge.module.css";

import { dischargeApi, Approaches, AskResponse, DischargeRequest, GetHistoryIndexRequest, HistoryDate, getHistoryIndexApi, GetHistoryDetailRequest, getHistoryDetailApi
    , getSoapApi, GetSoapRequest
    , DocumentFormat
    , getDocumentFormatApi, GetDocumentFormatRequest
    , updateDocumentFormatApi, UpdateDocumentFormatRequest 
    , getIcd10MasterApi, GetIcd10MasterRequest} from "../../api";
import { Answer, AnswerError } from "../../components/Answer";
import { DischargeButton } from "../../components/Example/DischargeButton";
import { AnalysisPanel, AnalysisPanelTabs } from "../../components/AnalysisPanel";
import heart from "../../assets/heart.svg";
import { PatientCodeInput } from "../../components/PatientCodeInput/PatientCodeInput";
import { DocumentFormatSetting } from "../../components/DocumentFormatSetting/DocumentFormatSetting";
import { DocumentFormatEditButton } from "../../components/DocumentFormatSetting/DocumentFormatEditButton";
import { SoapPreviewButton } from "../../components/DocumentFormatSetting/SoapPreviewButton";

export type HistoryIndex = {
    id: number;
    pid: string;
    patientname: string;
    documentname: string;
};

export type DayOfHistoryIndex = {
    createddate: string;
    historylist: HistoryIndex[];
};

// TODO ユーザー認証の仕組みができるまでのつなぎとしての SLOT。
const momorySlotOptions: IDropdownOption[] = [
    { key: 'slot1', text: 'Prompt Slot 1' },
    { key: 'slot2', text: 'Prompt Slot 2' },
    { key: 'slot3', text: 'Prompt Slot 3' },
    { key: 'slot4', text: 'Prompt Slot 4' },
    { key: 'slot5', text: 'Prompt Slot 5' },
    { key: 'slot6', text: 'Prompt Slot 6' },
    { key: 'slot7', text: 'Prompt Slot 7' },
    { key: 'slot8', text: 'Prompt Slot 8' },
    { key: 'slot9', text: 'Prompt Slot 9' },
    { key: 'slot10', text: 'Prompt Slot 10' },
    { key: 'slot11', text: 'Prompt Slot 11' },
    { key: 'slot12', text: 'Prompt Slot 12' },
    { key: 'slot13', text: 'Prompt Slot 13' },
    { key: 'slot14', text: 'Prompt Slot 14' },
    { key: 'slot15', text: 'Prompt Slot 15' },
    { key: 'slot16', text: 'Prompt Slot 16' },
  ];

  const defaultIcd10Options: IDropdownOption[] = [
    { key:  '0000', text: '特に指定しない' },
 ];


const Discharge = () => {
    const DEFAULT_DEPARTMENT_CODE: string = "0000";
    const DEFAULT_ICD10_CODE: string = "0000";
    const DEFAULT_ICD10_NAME: string = "特に指定しない";
    const DEFAULT_USER_ID: string = "00000001";
    const DOCUMENT_NAME: string = "退院時サマリ";
    const DEFAULT_TEMPERATURE = 0.01
    const DEFAULT_RESPONSE_MAX_TOKENS = 1000
    const DEFAULT_QUESTION_SUFFIX = "作成される文章は 900 Token以内とします。"
    const [promptTemplate, setPromptTemplate] = useState<string>("");
    const [retrieveCount, setRetrieveCount] = useState<number>(3);
    const [useSemanticRanker, setUseSemanticRanker] = useState<boolean>(true);
    const [useSemanticCaptions, setUseSemanticCaptions] = useState<boolean>(false);
    const [excludeCategory, setExcludeCategory] = useState<string>("");
    const [patientCode, setPatientCode] = useState<string>("");
    const [patientName, setPatientName] = useState<string>("");
    const [previewSoap, setPreviewSoap] = useState<string>("");

    const lastQuestionRef = useRef<string>("");
    const [completionTokens, setCompletionTokens] = useState<number>(0);
    const [promptTokens, setPromptTokens] = useState<number>(0);
    const [totalTokens, setTotalTokens] = useState<number>(0);

    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [isLoadingHistory, setIsLoadingHistory] = useState<boolean>(false);
    const [isLoadingSoap, setIsLoadingSoap] = useState<boolean>(false);
    const [isLoadingDocumnetFormatSetting, setIsLoadingDocumnetFormatSetting] = useState<boolean>(false);
    const [error, setError] = useState<unknown>();
    const [answer, setAnswer] = useState<AskResponse>();

    const [activeCitation, setActiveCitation] = useState<string>();
    const [activeAnalysisPanelTab, setActiveAnalysisPanelTab] = useState<AnalysisPanelTabs | undefined>(undefined);
    const iconStyle: React.CSSProperties = { padding: 10, marginTop:50, width: 100, height: 100,  color: "#465f8b" };
    const [historyItems, setHistoryItems] = useState<HistoryDate[]>([]);
    const [isDocumnetFormatSettingVisible, setIsDocumnetFormatSettingVisible] = useState<boolean>(false);
    const [systemContents, setSystemContents] = useState<string>("");
    const [systemContentsSuffix, setSystemContentsSuffix] = useState<string>("");
    const [documentFormats, setDocumentFormats] = useState<DocumentFormat[]>([]);
    const [isDocumentFormatSettingEdited, setIsDocumentFormatSettingEdited] = useState<boolean>(false);
    const [slot, setSlot] = useState<string>();
    const [icd10Options0, setIcd10Options0] = useState<IDropdownOption[]>([]);
    const [icd10Options1, setIcd10Options1] = useState<IDropdownOption[]>([]);
    const [icd10Options2, setIcd10Options2] = useState<IDropdownOption[]>([]);
    const [selectedIcd10Code0, setSelectedIcd10Code0] = useState<string>("");
    const [selectedIcd10Code1, setSelectedIcd10Code1] = useState<string>("");
    const [selectedIcd10Code2, setSelectedIcd10Code2] = useState<string>("");
    const [selectedIcd10CodeMax, setSelectedIcd10CodeMax] = useState<string>("");
    const [selectedIcd10CaptionMax, setSelectedIcd10CaptionMax] = useState<string>("");
    const [isLoadingIcd10Master0, setIsLoadingIcd10Master0] = useState<boolean>(false);
    const [isLoadingIcd10Master1, setIsLoadingIcd10Master1] = useState<boolean>(false);
    const [isLoadingIcd10Master2, setIsLoadingIcd10Master2] = useState<boolean>(false);
    const icd10DropDownStyle: React.CSSProperties = { width: 200 };

    const onLoad = async () => {
        setIsDocumnetFormatSettingVisible(false);
        setIcd10Options0(defaultIcd10Options);
        setIcd10Options1(defaultIcd10Options);
        setIcd10Options2(defaultIcd10Options);
        getIcd10Master(0, "");
        setSlot('slot1');
        await getHistoryIndex();
    }

    const getHistoryIndex = async () => {
        setIsLoadingHistory(true);
        try {
            const request: GetHistoryIndexRequest = {
                document_name: DOCUMENT_NAME,
            };
            const result = await getHistoryIndexApi(request);
            setHistoryItems(result.history_date_list);
        } catch (e) {
            alert(e)
        } finally { 
            setIsLoadingHistory(false);
        }
    }

    const getHistoryDetail = async (id:number) => {
        error && setError(undefined);
        setIsLoading(true);
        setActiveCitation(undefined);
        setActiveAnalysisPanelTab(undefined);

        try {
            const request: GetHistoryDetailRequest = {
                id: id,
            };
            const result = await getHistoryDetailApi(request);
            setAnswer(result);
            setCompletionTokens(result.completion_tokens);
            setPromptTokens(result.prompt_tokens);
            setTotalTokens(result.total_tokens);
            setPatientCode(result.pid!);
            setPatientName(result.patient_name!);
        } catch (e) {
            setError(e);
        } finally {
            setIsLoading(false);
        }
    }

    const getSelectedIcd10Code = () => {
        if (selectedIcd10Code2 !== "" && selectedIcd10Code2 !== DEFAULT_ICD10_CODE) {
            // icd10Options2 から selectedIcd10Code2 の text を取得
            for (let icd10 of icd10Options2) {
                if (icd10.key === selectedIcd10Code2) {
                    return [selectedIcd10Code2, icd10.text];
                }
            }
        }
        if (selectedIcd10Code1 !== "" && selectedIcd10Code1 !== DEFAULT_ICD10_CODE) {
            // icd10Options1 から selectedIcd10Code1 の text を取得
            for (let icd10 of icd10Options1) {
                if (icd10.key === selectedIcd10Code1) {
                    return [selectedIcd10Code1, icd10.text];
                }
            }
        }
        if (selectedIcd10Code0 !== "" && selectedIcd10Code0 !== DEFAULT_ICD10_CODE) {
            // icd10Options0 から selectedIcd10Code0 の text を取得
            for (let icd10 of icd10Options0) {
                if (icd10.key === selectedIcd10Code0) {
                    return [selectedIcd10Code0, icd10.text];
                }
            }
        }
        return [DEFAULT_ICD10_CODE, DEFAULT_ICD10_NAME];
    }

    const getDocumentFormat = async (force_master:boolean, slotValue:string) => {
        setIsLoadingDocumnetFormatSetting(true);
        try {
            const request: GetDocumentFormatRequest = {
                document_name: DOCUMENT_NAME,
                department_code: DEFAULT_DEPARTMENT_CODE,
                icd10_code: selectedIcd10CodeMax ? selectedIcd10CodeMax : DEFAULT_ICD10_CODE,
                user_id: slotValue ? slotValue : '',
                force_master: force_master,
            };
            const result = await getDocumentFormatApi(request);
            setSystemContents(result.system_contents);
            setSystemContentsSuffix(result.system_contents_suffix);
            setDocumentFormats(result.document_formats);
        } catch (e) {
            alert(e)
            //setError(e);
        } finally {
            setIsLoadingDocumnetFormatSetting(false);
        }
    }

    const updateDocumentFormat = async () => {
        try {
            const request: UpdateDocumentFormatRequest = {
                document_name: DOCUMENT_NAME,
                department_code: DEFAULT_DEPARTMENT_CODE,
                icd10_code: DEFAULT_ICD10_CODE,
                user_id: slot ? slot : '',
                system_contents: systemContents,
                system_contents_suffix: systemContentsSuffix,
                document_formats: documentFormats,
            };
            await updateDocumentFormatApi(request);
            alert("保存しました。");
        } catch (e) {
            alert(e)
        }
    }

    const setIsLoadingIcd10Master = async (codeLevel:number, isLoading:boolean) => {
        if (codeLevel === 0) {
            setIsLoadingIcd10Master0(isLoading);
        } else if (codeLevel === 1) {
            setIsLoadingIcd10Master1(isLoading);
        } else if (codeLevel === 2) {
            setIsLoadingIcd10Master2(isLoading);
        }
    }

    const setIcd10Options = async (codeLevel:number, options:IDropdownOption[]) => {
        if (codeLevel === 0) {
            setIcd10Options0(options);
        } else if (codeLevel === 1) {
            setIcd10Options1(options);
        } else if (codeLevel === 2) {
            setIcd10Options2(options);
        }
    }

    const setSelectedIcd10 = async (codeLevel:number, key:string) => {
        if (codeLevel === 0) {
            setSelectedIcd10Code0(key);
        } else if (codeLevel === 1) {
            setSelectedIcd10Code1(key);
        } else if (codeLevel === 2) {
            setSelectedIcd10Code2(key);
        }
    }

    const getIcd10Master = async (codeLevel:number, parentIcd10Code:string) => {
        setIsLoadingIcd10Master(codeLevel, true);

        try {
            const request: GetIcd10MasterRequest = {
                code_level: codeLevel,
                parent_code: parentIcd10Code,
            };
            const result = await getIcd10MasterApi(request);

            const options: IDropdownOption[] = [{ key: DEFAULT_ICD10_CODE, text: DEFAULT_ICD10_NAME}]
            for (let icd10 of result.records) {
                options.push({ key: icd10.icd10_code, text: icd10.icd10_code + " " + icd10.caption });
            }
            setIcd10Options(codeLevel, options);
            setSelectedIcd10(codeLevel, DEFAULT_ICD10_CODE);
            setSelectedIcd10CodeMax(DEFAULT_ICD10_CODE)
            setSelectedIcd10CaptionMax(DEFAULT_ICD10_NAME)
        } catch (e) {
            alert(e)
            //setError(e);
        } finally {
            setIsLoadingIcd10Master(codeLevel, false);
        }
    }

    const makeApiRequest = async (documentName: string) => {
        if (patientCode === "") {
            alert("患者番号を入力してください。");
            return;
        }

        lastQuestionRef.current = documentName;

        error && setError(undefined);
        setIsLoading(true);
        setActiveCitation(undefined);
        setActiveAnalysisPanelTab(undefined);

        try {
            const request: DischargeRequest = {
                documentName: documentName,
                patientCode: patientCode,
                departmentCode: DEFAULT_DEPARTMENT_CODE,
                icd10Code: selectedIcd10CodeMax ? selectedIcd10CodeMax : DEFAULT_ICD10_CODE,
                userId: slot ? slot : '',
                approach: Approaches.ReadRetrieveRead,
                overrides: {
                    promptTemplate: promptTemplate.length === 0 ? undefined : promptTemplate,
                    excludeCategory: excludeCategory.length === 0 ? undefined : excludeCategory,
                    top: retrieveCount,
                    semanticRanker: useSemanticRanker,
                    semanticCaptions: useSemanticCaptions
                }
            };
            const result = await dischargeApi(request);
            setAnswer(result);
            setCompletionTokens(result.completion_tokens);
            setPromptTokens(result.prompt_tokens);
            setTotalTokens(result.total_tokens);

            // 履歴の取り直し
            await getHistoryIndex();

        } catch (e) {
            setError(e);
        } finally {
            setIsLoading(false);
        }
    };

    const onCreateClicked = (documentName:string) => {
        // 実行を確認する
        if (isDocumentFormatSettingEdited) {
            const result = window.confirm("プロンプト編集内容が保存されていません。\n保存しない場合、以前のプロンプトのまま実行されます。\nよろしいですか？");
            if (!result) {
                return;
            }
        }
        makeApiRequest(documentName);
    };
    const onSaveDocumentFormatClicked = () => {
        // 入力チェック
        let errorMessages:string = "";
        for (let documentFormat of documentFormats) {
            if (slot === undefined || slot === "") {
                errorMessages += "保存先のスロットが選択されていません。\n";
            }
            // newValue が float に変換できるかチェック
            const temperature = Number(documentFormat.temperature_str);
            if (isNaN(temperature) || temperature < 0 || temperature > 1) {
                errorMessages += "Temperature には 0~1 までの整数または小数を入力してください。表示順: " + (documentFormat.order_no + 1) + "\n";
            }
            else {
                documentFormat.temperature = temperature;
            }
            if (documentFormat.category_name === "") {
                errorMessages += "カテゴリ名が入力されていません。表示順: " + (documentFormat.order_no + 1) + "\n";
            }
            if (documentFormat.kind === 1 && documentFormat.question === "") {
                errorMessages += "プロンプトが入力されていません。表示順: " + (documentFormat.order_no + 1) + "\n";
            }
        }
        if (errorMessages !== "") {
            alert(errorMessages);
            return;
        }
        updateDocumentFormat();
        setIsDocumentFormatSettingEdited(false);
    }

    const cancelDocumentSetting = () => {
        // 実行を確認する
        if (isDocumentFormatSettingEdited) {
            const result = window.confirm("保存していない編集内容は破棄されます。\nよろしいですか？");
            if (!result) {
                return;
            }
        }
        setDocumentFormats([]);
        setIsDocumnetFormatSettingVisible(false);
        setIsDocumentFormatSettingEdited(false);
    }

    const onCancelDocumentFormatClicked = () => {
        cancelDocumentSetting();
    }

    const onReloadFromMasterClicked = () => {
        // 実行を確認する
        const result = window.confirm("マスターから再取得します。\n保存していない編集内容は破棄されます。\nマスターから取得した内容は、保存ボタンを押されるまで保存されません。\nよろしいですか？");
        if (!result) {
            return;
        }
        getDocumentFormat(true, slot ? slot : '');
        setIsDocumentFormatSettingEdited(true);
    }

    const onSystemContentsChanged = (newValue:string) => {
        // 値が変わっているかチェック
        // 改行コード 統一
        const targetQ = systemContents.replace(/\r?\n/g, "\n");
        const newQ = newValue.replace(/\r?\n/g, "\n");
        if (targetQ !== newQ) {
            setIsDocumentFormatSettingEdited(true);
            setSystemContents(newValue);
        }
    }

    const onTemperatureChanged = (targetDocumentFormat:DocumentFormat, newValue:string) => {
        // 値が変わっているかチェック
        if (targetDocumentFormat.temperature.toString() !== newValue) {
            setIsDocumentFormatSettingEdited(true);
        }

        const newDocumentFormats = documentFormats.map((documentFormat) => {
            if (documentFormat.id === targetDocumentFormat.id) {
                documentFormat.temperature_str = newValue;
            }
            return documentFormat;
        });
        setDocumentFormats(newDocumentFormats);
    };

    const onCategoryNameChanged = (targetDocumentFormat:DocumentFormat, newValue:string) => {
        // 値が変わっているかチェック
        if (targetDocumentFormat.category_name !== newValue) {
            setIsDocumentFormatSettingEdited(true);
        }

        const newDocumentFormats = documentFormats.map((documentFormat) => {
            if (documentFormat.id === targetDocumentFormat.id) {
                documentFormat.category_name = newValue;
            }
            return documentFormat;
        });
        setDocumentFormats(newDocumentFormats);
    };

    const onKindChanged = (targetDocumentFormat:DocumentFormat, newValue:number) => {
        const newDocumentFormats = documentFormats.map((documentFormat) => {
            if (documentFormat.id === targetDocumentFormat.id) {
                documentFormat.kind = newValue as number;
            }
            return documentFormat;
        });
        setDocumentFormats(newDocumentFormats);
        setIsDocumentFormatSettingEdited(true);
    };

    const onTargetSoapChanged = (targetDocumentFormat:DocumentFormat, targetSection:string, newValue:boolean) => {
        const newDocumentFormats = documentFormats.map((documentFormat) => {
            if (documentFormat.id === targetDocumentFormat.id) {
                if (targetSection === "S") {
                    documentFormat.is_s = newValue;
                } else if (targetSection === "O") {
                    documentFormat.is_o = newValue;
                } else if (targetSection === "A") {
                    documentFormat.is_a = newValue;
                } else if (targetSection === "P") {
                    documentFormat.is_p = newValue;
                } else if (targetSection === "B") {
                    documentFormat.is_b = newValue;
                }
            }
            return documentFormat;
        });
        setDocumentFormats(newDocumentFormats);
        setIsDocumentFormatSettingEdited(true);
    };

    const onQuestionChanged = (targetDocumentFormat:DocumentFormat, newValue:string) => {
        // 値が変わっているかチェック
        // 改行コード 統一
        const targetQ = targetDocumentFormat.question.replace(/\r?\n/g, "\n");
        const newQ = newValue.replace(/\r?\n/g, "\n");
        if (targetQ !== newQ) {
            setIsDocumentFormatSettingEdited(true);
        }

        const newDocumentFormats = documentFormats.map((documentFormat) => {
            if (documentFormat.id === targetDocumentFormat.id) {
                documentFormat.question = newValue;
            }
            return documentFormat;
        });
        setDocumentFormats(newDocumentFormats);
    };

    const onDocumentFormatUpClicked = (documentFormat : DocumentFormat) => {
        if (documentFormats[0].id === documentFormat.id) {
            return;
        }
        const newDocumentFormats: DocumentFormat[] = [];
        const oldOrderNoOfTarget: number = documentFormat.order_no;
        for (let i = 0; i < oldOrderNoOfTarget - 1; i++) {
            newDocumentFormats.push(documentFormats[i]);
        }
        documentFormat.order_no = oldOrderNoOfTarget - 1;
        newDocumentFormats.push(documentFormat);
        for (let i = oldOrderNoOfTarget - 1; i < documentFormats.length; i++) {
            if (documentFormats[i].id !== documentFormat.id) {
                if (documentFormats[i].order_no === oldOrderNoOfTarget - 1) {
                    documentFormats[i].order_no ++;
                }
                newDocumentFormats.push(documentFormats[i]);
            }
        }
        //setDocumentFormats([]);
        //alert(JSON.stringify(newDocumentFormats));
        setDocumentFormats(newDocumentFormats);
        setIsDocumentFormatSettingEdited(true);
    }

    const onDocumentFormatDownClicked = (documentFormat : DocumentFormat) => {
        // const newDocumentFormats = documentFormats.map((documentFormat) => {
        //     documentFormat.order_no = documentFormat.order_no + 1;
        //     documentFormat.category_name = "あああ";
        //     return documentFormat;
        // });
        // setDocumentFormats([]);
        // setDocumentFormats(newDocumentFormats);


        if (documentFormats[documentFormats.length - 1].id === documentFormat.id) {
            return;
        }
        const newDocumentFormats: DocumentFormat[] = [];
        const oldOrderNoOfTarget: number = documentFormat.order_no;
        for (let i = 0; i < oldOrderNoOfTarget; i++) {
            newDocumentFormats.push(documentFormats[i]);
        }
        const nextRow = documentFormats[oldOrderNoOfTarget+1];
        nextRow.order_no --;
        newDocumentFormats.push(nextRow);
        documentFormat.order_no = oldOrderNoOfTarget + 1;
        newDocumentFormats.push(documentFormat);
        for (let i = oldOrderNoOfTarget + 2; i < documentFormats.length; i++) {
            if (documentFormats[i].id !== documentFormat.id 
                && documentFormats[i].id !== nextRow.id) {
                newDocumentFormats.push(documentFormats[i]);
            }
        }
        //setDocumentFormats([]);
        //alert(JSON.stringify(newDocumentFormats));
        setDocumentFormats(newDocumentFormats);
        setIsDocumentFormatSettingEdited(true);
    }

    const onAddDocumentFormatClicked = () => {
        const newDocumentFormat: DocumentFormat = {
            id: -1,
            kind: 1,
            category_name: "",
            order_no: documentFormats.length,
            question: "",
            is_s: false,
            is_o: false,
            is_a: false,
            is_p: false,
            is_b: false,
            temperature: DEFAULT_TEMPERATURE,
            temperature_str: DEFAULT_TEMPERATURE.toString(),
            response_max_tokens: DEFAULT_RESPONSE_MAX_TOKENS,
            question_suffix: DEFAULT_QUESTION_SUFFIX,
            use_allergy_records: false,
            use_discharge_medicine_records: false,
        };

        const newDocumentFormats: DocumentFormat[] = [];
        for (let documentFormat of documentFormats) {
            newDocumentFormats.push(documentFormat);
        }

        newDocumentFormats.push(newDocumentFormat);
        setDocumentFormats(newDocumentFormats);
        setIsDocumentFormatSettingEdited(true);
    }

    const onDocumentSettingDeleteClicked = (documentFormatId : number) => {
        // 実行確認
        const result = window.confirm("カテゴリーを削除してよろしいですか？");
        if (!result) {
            return;
        }
        const newDocumentFormats: DocumentFormat[] = [];
        let order:number = 0;
        for (let documentFormat of documentFormats) {
            if (documentFormat.id !== documentFormatId) {
                documentFormat.order_no = order;
                newDocumentFormats.push(documentFormat);
                order ++;
            }
        }
        setDocumentFormats(newDocumentFormats);
        setIsDocumentFormatSettingEdited(true);
    }

    const getSoap = async () => {
        setIsLoadingSoap(true);
        try {
            const request: GetSoapRequest = {
                patient_code: patientCode,
            };
            const result = await getSoapApi(request);
            setPreviewSoap("患者番号: " + patientCode + "\n" + result.soap);
        } catch (e) {
            setError(e);
        } finally {
            setIsLoadingSoap(false);
        }
    }

    const onSoapPreviewClicked = (patient_code: string) => {
        if (patient_code === "") {
            setPreviewSoap("患者番号を入力してください。");
            return;
        }
        setPreviewSoap("");
        getSoap();
    };

    const onChangeSlot = (newSlot: string) => {
        if (isDocumnetFormatSettingVisible) {
            if (isDocumentFormatSettingEdited) {
                const result = window.confirm("スロットを切り替えます。\nプロンプト編集内容が保存されていません。\n編集内容を破棄してよろしいですか？");
                if (!result) {
                    setSlot(slot ? slot : '');
                    return;
                }
            }
            getDocumentFormat(false, newSlot);
            setIsDocumentFormatSettingEdited(false);
        }
    }

    const onChangeIcd10Code = (codeLevel:number, newCode: string) => {
        if (isDocumnetFormatSettingVisible) {
            if (isDocumentFormatSettingEdited) {
                const result = window.confirm("使用するプロンプトを切り替えます。\nプロンプト編集内容が保存されていません。\n編集内容を破棄してよろしいですか？");
                if (!result) {
                    if (codeLevel === 0) setSelectedIcd10Code0(selectedIcd10Code0 ? selectedIcd10Code0 : '');
                    if (codeLevel === 1) setSelectedIcd10Code1(selectedIcd10Code1 ? selectedIcd10Code1 : '');
                    if (codeLevel === 2) setSelectedIcd10Code2(selectedIcd10Code2 ? selectedIcd10Code2 : '');
                    return;
                }
                setIsDocumentFormatSettingEdited(false);
            }
        }
        for (let i = codeLevel + 1; i < 3; i++) {
            setIcd10Options(i, defaultIcd10Options);
            setSelectedIcd10(i, DEFAULT_ICD10_CODE);
        }
        if (codeLevel < 2) {
            // 子の階層のマスターを取得
            getIcd10Master(codeLevel + 1, newCode);
        }
        let selectedIcd10 = getSelectedIcd10Code();
        setSelectedIcd10CodeMax(selectedIcd10[0]);
        setSelectedIcd10CaptionMax(selectedIcd10[1]);
    }

    const onDocumentFormatEditClicked = () => {
        if (!isDocumnetFormatSettingVisible) {
            // 開く
            getDocumentFormat(false, slot ? slot : '');
            setIsDocumnetFormatSettingVisible(true);
        } else {
            // 閉じる
            cancelDocumentSetting();
        }
    }

    const onShowCitation = (citation: string) => {
        if (activeCitation === citation && activeAnalysisPanelTab === AnalysisPanelTabs.CitationTab) {
            setActiveAnalysisPanelTab(undefined);
        } else {
            setActiveCitation(citation);
            setActiveAnalysisPanelTab(AnalysisPanelTabs.CitationTab);
        }
    };

    const onToggleTab = (tab: AnalysisPanelTabs) => {
        if (activeAnalysisPanelTab === tab) {
            setActiveAnalysisPanelTab(undefined);
        } else {
            setActiveAnalysisPanelTab(tab);
        }
    };

    function onHistoryButtonClicked(id:number): void {
        getHistoryDetail(id);
    }

    const hitoryTitleLabelStyles = {
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

    const hitoryDateLabelStyles = {
        root: {
          color: '#ffffff',
          font: '14px',
          fontWeight: 'bold',
          textAliegn: 'left',
          paddingLeft: '5px',
          width: '100%',
          backgroundColor: '#858585',
        }
    };

    const hitoryButtonStyles = {
        root: {
            backgroundColor: '#CFCFCF',
            borderColor: 'transparent',
            color: 'rgb(95, 95, 95)',
            fontWeight: 'bold',
            width: '100%',
            padding: '0px',
            margin: '0px',
            borderRadius: '0px',
            textAliegn: 'left',
            paddingLeft: '0px',
            alignItems: 'left',
          }
    };

    const rootStackStyles = {
        root: {
            height: '100%',
            backgroundColor: 'transparent',
        }
    }

    return (
    <Stack styles={rootStackStyles} horizontal onLoad={onLoad}>  
        <div className={styles.dischargeHistoryDiv}>
            <Label styles={hitoryTitleLabelStyles}>作成履歴</Label>
            {isLoadingHistory && (
                <div className={styles.loadingHistorySpinner}>
                    <Spinner label="Loading history" />
                </div>
            )}
            {!isLoadingHistory && (
                <div>
                    {historyItems.map((item) => (
                        <div>
                            <Label styles={hitoryDateLabelStyles}>{item.created_date}</Label>
                        {item.history_list.map((history) => (
                            <div>
                                <PrimaryButton styles={hitoryButtonStyles} 
                                    text={history.pid + " " + history.patient_name}
                                    onClick={() => onHistoryButtonClicked(history.id)}>
                                </PrimaryButton>                 
                            </div>
                            ))}
                            </div>
                        ))}
                </div>
            )}
        </div>            
        <div className={styles.dischargeContainer}>
            <div className={styles.dischargeTopSection}>
                {/* <SettingsButton className={styles.settingsButton} onClick={() => setIsConfigPanelOpen(!isConfigPanelOpen)} /> */}
                <img src={heart} alt="heart" style={iconStyle}  />
                             <h1 className={styles.chatEmptyStateTitle}>退院サマリ作成システム</h1>
                             {/* <h2 className={styles.chatEmptyStateSubtitle}>{patientCode}</h2> */}
                             <div className={styles.dischargeInput}>
                                 <PatientCodeInput
                                     onPatientCodeChanged={x => (setPatientCode(x))}
                                     onPatientNameChanged={x => (setPatientName(x))}
                                     clearOnSend
                                     patientCode={patientCode}
                                     patientName={patientName}
                                     placeholder="Type a new question (e.g. how to prevent chronic disease?)"
                                     disabled={isLoading}
                             />
                            </div>
                            {/* <h3 className={styles.chatEmptyStateSubtitle}>カルテデータ プレビュー</h3> */}
                            {/* <h3 className={styles.chatEmptyStateSubtitle}>使用するプロンプトを指定する</h3> */}
                            <SoapPreviewButton 
                                patientCode={patientCode}
                                onClick={onSoapPreviewClicked} />
                            {isLoadingSoap && <Spinner label="Loading soap" />}
                            { previewSoap != "" && (
                                <TextField
                                    className={styles.soapPreviewField}
                                    readOnly={true}
                                    multiline={true}
                                    resizable={true}
                                    scrolling="true"
                                    value={previewSoap}
                                    //onChange={onQuestionChange}
                                    //onKeyDown={onEnterPress}
                                />)}
                            <br></br>
                            <Label>プロンプトとして使用する疾病コードを選ぶ</Label>
                            <Stack horizontal>
                                <Label>大項目: </Label>
                                {isLoadingIcd10Master0 && <Spinner label="Loading icd10 master" />}
                                {!isLoadingIcd10Master0 && (
                                    <Dropdown
                                        style={icd10DropDownStyle}
                                        placeholder="Select icd10 code"
                                        options={icd10Options0}
                                        selectedKey={selectedIcd10Code0}
                                        onChange={(e, newValue) => {
                                            setSelectedIcd10Code0(newValue?.key as string || '');
                                            onChangeIcd10Code(0, newValue?.key as string || '');
                                        }}
                                    />            
                                )}
                                <Label>　中項目: </Label>
                                {isLoadingIcd10Master1 && <Spinner label="Loading icd10 master" />}
                                {!isLoadingIcd10Master1 && (
                                    <Dropdown 
                                        style={icd10DropDownStyle}
                                        placeholder="Select icd10 code"
                                        options={icd10Options1}
                                        selectedKey={selectedIcd10Code1}
                                        onChange={(e, newValue) => {
                                            setSelectedIcd10Code1(newValue?.key as string || '');
                                            onChangeIcd10Code(1, newValue?.key as string || '');
                                        }}
                                    />            
                                )}
                                <Label>　小項目: </Label>
                                {isLoadingIcd10Master2 && <Spinner label="Loading icd10 master" />}
                                {!isLoadingIcd10Master2 && (
                                    <Dropdown 
                                        style={icd10DropDownStyle}
                                        placeholder="Select icd10 code"
                                        options={icd10Options2}
                                        selectedKey={selectedIcd10Code2}
                                        onChange={(e, newValue) => {
                                            setSelectedIcd10Code2(newValue?.key as string || '');
                                            onChangeIcd10Code(2, newValue?.key as string || '');
                                        }}
                                    />            
                                )}
                            </Stack>
                            <br></br>
                            <DocumentFormatEditButton 
                                onClick={ onDocumentFormatEditClicked } />
                            <DischargeButton
                                text="退院時サマリを作成する"
                                value="退院時サマリ"
                                onClick={onCreateClicked} />
            </div>
            <div className={styles.dischargeBottomSection}>
                {isLoading && <Spinner label="Generating answer" />}
                {!isLoading && answer && !error && (
                    <div className={styles.dischargeAnswerContainer}>
                        <Answer
                            answer={answer}
                            onCitationClicked={x => onShowCitation(x)}
                            onThoughtProcessClicked={() => onToggleTab(AnalysisPanelTabs.ThoughtProcessTab)}
                            onSupportingContentClicked={() => onToggleTab(AnalysisPanelTabs.SupportingContentTab)}
                            isSupportingContentVisible = {false}
                            isThoughtProcessVisible = {false}
                        />
                        <Stack horizontal>
                            <Label>completion_tokens: </Label>
                            <Label>{completionTokens}</Label>
                        </Stack>
                        <Stack horizontal>
                            <Label>  prompt_tokens: </Label>
                            <Label>{promptTokens}</Label>
                        </Stack>
                        <Stack horizontal>
                            <Label>  total_tokens: </Label>
                            <Label>{totalTokens}</Label>
                        </Stack>
                    </div>
                )}
                {error ? (
                    <div className={styles.dischargeAnswerContainer}>
                        <AnswerError error={error.toString()} onRetry={() => makeApiRequest(lastQuestionRef.current)} />
                    </div>
                ) : null}
                {activeAnalysisPanelTab && answer && (
                    <AnalysisPanel
                        className={styles.dischargeAnalysisPanel}
                        activeCitation={activeCitation}
                        onActiveTabChanged={x => onToggleTab(x)}
                        citationHeight="600px"
                        answer={answer}
                        activeTab={activeAnalysisPanelTab}
                    />
                )}
            </div>

        </div>
        <Dropdown 
                placeholder="Select prompt slot"
                options={momorySlotOptions}
                selectedKey={slot}
                onChange={(e, newValue) => {
                    setSlot(newValue?.key as string || '');
                    onChangeSlot(newValue?.key as string || '');
                }}
            />            
        { isDocumnetFormatSettingVisible && (
            <div className={styles.dischargeDocumentFormatSettingDiv}>
                <DocumentFormatSetting 
                    documentName={DOCUMENT_NAME}
                    departmentCode={DEFAULT_DEPARTMENT_CODE}
                    icd10Code={selectedIcd10CodeMax}
                    icd10Name={selectedIcd10CaptionMax}
                    userId={slot ? slot : ''}
                    systemContents={systemContents}
                    documentFormats={documentFormats}
                    isLoading={isLoadingDocumnetFormatSetting}
                    isEdited={isDocumentFormatSettingEdited}
                    onSaveClicked={onSaveDocumentFormatClicked}
                    onCancelClicked={onCancelDocumentFormatClicked}
                    onReloadFromMasterClicked={onReloadFromMasterClicked}
                    onSystemContentsChanged={onSystemContentsChanged}
                    onCategoryNameChanged={onCategoryNameChanged}
                    onKindChanged={onKindChanged}
                    onTargetSoapChanged={onTargetSoapChanged}
                    onQuestionChanged={onQuestionChanged}
                    onTemperatureChanged={onTemperatureChanged}
                    onUpClicked={onDocumentFormatUpClicked}
                    onDownClicked={onDocumentFormatDownClicked}
                    onDeleteClicked={onDocumentSettingDeleteClicked}
                    onAddClicked={onAddDocumentFormatClicked}
                ></DocumentFormatSetting>
            </div>
        )}
    </Stack>  
    );
};

export default Discharge;

