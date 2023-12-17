import { useRef, useState} from "react";
import { Dropdown, Checkbox, IDropdownOption, Spinner, TextField, selectProperties} from "@fluentui/react";
import { Label, Stack } from "@fluentui/react";
import { PrimaryButton } from '@fluentui/react/lib/Button';

import styles from "./Discharge.module.css";

import { dischargeApi, Approaches, AskResponse, DischargeRequest, GetHistoryIndexRequest, HistoryDate, getHistoryIndexApi, GetHistoryDetailRequest, getHistoryDetailApi
    , getSoapApi, GetSoapRequest
    , DocumentFormat
    , getDocumentFormatApi, GetDocumentFormatRequest
    , updateDocumentFormatApi, UpdateDocumentFormatRequest 
    , getDocumentFormatIndexApi, GetDocumentFormatIndexRequest, DocumentFormatIndex
    , deleteDocumentFormatApi, DeleteDocumentFormatRequest
} from "../../api";
import { Answer, AnswerError } from "../../components/Answer";
import { DischargeButton } from "../../components/Example/DischargeButton";
import { AnalysisPanel, AnalysisPanelTabs } from "../../components/AnalysisPanel";
import heart from "../../assets/heart.svg";
import { PatientCodeInput } from "../../components/PatientCodeInput/PatientCodeInput";
import { DocumentFormatSetting } from "../../components/DocumentFormatSetting/DocumentFormatSetting";
import { Search24Filled } from "@fluentui/react-icons";
import { 
    USE_RANGE_KIND_ALL_STR, 
    USE_RANGE_KIND_HOSPITALIZATION_STR, 
    USE_RANGE_KIND_DISCHARGE_STR,
    USE_RANGE_KIND_ALL, 
    USE_RANGE_KIND_HOSPITALIZATION, 
    USE_RANGE_KIND_DISCHARGE
    } from "../../components/DocumentFormatSetting/DocumentFormatSettingByCategory";

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
    { key: '', text: '指定なし' },
    { key: 'user1', text: 'user1' },
    { key: 'user2', text: 'user2' },
    { key: 'user3', text: 'user3' },
    { key: 'user4', text: 'user4' },
    { key: 'user5', text: 'user5' },
    { key: 'user6', text: 'user6' },
    { key: 'user7', text: 'user7' },
    { key: 'user8', text: 'user8' },
    { key: 'user9', text: 'user9' },
    { key: 'user10', text: 'user10' },
    { key: 'user11', text: 'user11' },
    { key: 'user12', text: 'user12' },
    { key: 'user13', text: 'user13' },
    { key: 'user14', text: 'user14' },
    { key: 'user15', text: 'user15' },
    { key: 'user16', text: 'user16' },

  ];

const Discharge = () => {
    const DOCUMENT_NAME: string = "退院時サマリ";
    const DEFAULT_TEMPERATURE = 0.01
    const DEFAULT_RESPONSE_MAX_TOKENS = 1000
    const DEFAULT_QUESTION_SUFFIX = "作成される文章は 900 Token以内とします。"
    const DEFAULT_USE_RANGE_KIND = 0
    const DEFAULT_DAYS_BEFORE_THE_DATE_OF_HOSPITALIZATION_TO_USE = 0
    const DEFAULT_DAYS_AFTER_THE_DATE_OF_HOSPITALIZATION_TO_USE = 3
    const DEFAULT_DAYS_BEFORE_THE_DATE_OF_DISCHARGE_TO_USE = 3
    const DEFAULT_DAYS_AFTER_THE_DATE_OF_DISCHARGE_TO_USE = 0
    
    const DEFAULT_DEPARTMENT_CODE = "001"

    const [pid, setPid] = useState<string>("");
    const [patientName, setPatientName] = useState<string>("");
    const [hospitalizationDate, setHospitalizationDate] = useState<string>(""); // 入院日
    const [dischargeDate, setDischargeDate] = useState<string>(""); // 退院日
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
    const [systemContents, setSystemContents] = useState<string>("");
    const [systemContentsSuffix, setSystemContentsSuffix] = useState<string>("");
    const [documentFormats, setDocumentFormats] = useState<DocumentFormat[]>([]);
    const [isDocumentFormatSettingEdited, setIsDocumentFormatSettingEdited] = useState<boolean>(false);
    const [selectedSlot, setSelectedSlot] = useState<string>("");
    const [documentFormatIndexList, setDocumentFormatIndexList] = useState<DocumentFormatIndex[]>([]);
    const [isLoadingDocumentFormatIndexList, setIsLoadingDocumentFormatIndexList] = useState<boolean>(false);
    const [selectedDocumentFormatIndex, setSelectedDocumentFormatIndex] = useState<DocumentFormatIndex>();
    const [isOnlyMyself, setIsOnlyMyself] = useState<boolean>(false);
    const [searchText, setSearchText] = useState<string>("");
    const [saveAsName, setSaveAsName] = useState<string>("");
    const [tags, setTags] = useState<string>("");
    const [departmantCode, setDepartmantCode] = useState<string>("");

    const onLoad = async () => {
        setIsDocumentFormatSettingEdited(false);
        getDocumentFormatIndexList();
        setSelectedSlot('');
        setDepartmantCode(DEFAULT_DEPARTMENT_CODE);
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
            setPid(result.pid!);
            setPatientName(result.patient_name!);
            setHospitalizationDate(result.hospitalization_date!);
            setDischargeDate(result.discharge_date!);
        } catch (e) {
            setError(e);
        } finally {
            setIsLoading(false);
        }
    }

    const getDocumentFormatIndexList = async (newSelectedIndexId:number = -1, 
        newSearchText:string = "") => {
        
        setIsLoadingDocumentFormatIndexList(true);
        if(newSelectedIndexId == -1) {
            newSearchText = searchText;
        }
        try {
            const request: GetDocumentFormatIndexRequest = {
                document_name: DOCUMENT_NAME,
                is_only_myself: isOnlyMyself,
                search_text: newSearchText,
                user_id: selectedSlot ? selectedSlot : '',
            };
            const result = await getDocumentFormatIndexApi(request);
            setDocumentFormatIndexList(result.document_format_index_list);
            let masterIndex:DocumentFormatIndex | undefined = undefined;
            let foundSelectedDocumentFormatIndex:boolean = false;
            for (let documentFormatIndex of result.document_format_index_list) {
                if (documentFormatIndex.is_master) {
                    masterIndex = documentFormatIndex;
                }
                if (newSelectedIndexId == documentFormatIndex.index_id) {
                    setSelectedDocumentFormatIndex(documentFormatIndex);
                    setSaveAsName("");
                    setTags(documentFormatIndex.tags);
                    foundSelectedDocumentFormatIndex = true;
                    getDocumentFormat(documentFormatIndex!);
                    break;
                }
            }
            if (!foundSelectedDocumentFormatIndex) {
                setSelectedDocumentFormatIndex(masterIndex);
                setSaveAsName("");
                setTags("");
                getDocumentFormat(masterIndex!);
            }
        } catch (e) {
            alert(e)
            //setError(e);
        } finally {
            setIsLoadingDocumentFormatIndexList(false);
        }
    }

    const getDocumentFormat = async (documentFormatIndex:DocumentFormatIndex) => {
        setIsLoadingDocumnetFormatSetting(true);
        try {
            const request: GetDocumentFormatRequest = {
                documnet_format_index_id: documentFormatIndex.index_id,
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

    const updateDocumentFormat = async (index_id:number, index_name:string) => {
        try {
            const request: UpdateDocumentFormatRequest = {
                document_format_index_id: index_id,
                document_format_index_name: saveAsName != undefined && saveAsName != "" ? saveAsName: index_name,
                document_name: DOCUMENT_NAME,
                tags: tags,
                user_id: selectedSlot ? selectedSlot : '',
                system_contents: systemContents,
                system_contents_suffix: systemContentsSuffix,
                document_formats: documentFormats,
            };
            const result = await updateDocumentFormatApi(request);

            alert("保存しました。");
            setSearchText("");
            getDocumentFormatIndexList(result.document_format_index_id, "");
        } catch (e) {
            alert(e)
        }
    }

    const deleteDocumentFormat = async (document_format_index_id:number) => {
        try {
            const request: DeleteDocumentFormatRequest = {
                document_format_index_id: document_format_index_id,
                user_id: selectedSlot ? selectedSlot : '',
            };
            await deleteDocumentFormatApi(request);
            getDocumentFormatIndexList();
        } catch (e) {
            alert(e)
        }
    }

    const makeApiRequest = async (documentName: string) => {
        if (pid === "") {
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
                departmentCode: departmantCode,
                pid: pid,
                documentFormatIndexId: selectedDocumentFormatIndex ? selectedDocumentFormatIndex.index_id : 0,
                userId: selectedSlot ? selectedSlot : ''
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

    // 整数かどうかチェックする関数
    const isInteger = (str: string): boolean => {  
        const pattern = /^-?\d+$/;   
        return pattern.test(str);  
    }

    const onSaveDocumentFormatClicked = async (index_id:number, index_name:string) => {
        // 入力チェック
        let errorMessages:string = "";
        for (let documentFormat of documentFormats) {
            // newValue が float に変換できるかチェック
            const temperature = Number(documentFormat.temperature_str);
            if (isNaN(temperature) || temperature < 0 || temperature > 1) {
                errorMessages += "Temperature には 0~1 までの整数または小数を入力してください。表示順: " + (documentFormat.order_no + 1) + "\n";
            }
            else {
                documentFormat.temperature = temperature;
            }
            if (!isInteger(documentFormat.days_before_the_date_of_hospitalization_to_use_str)) {
                errorMessages += "入院日何日前からカルテデータを使用するかには整数を入力してください。表示順: " + (documentFormat.order_no + 1) + "\n";
            }
            else {
                documentFormat.days_before_the_date_of_hospitalization_to_use = Number(documentFormat.days_before_the_date_of_hospitalization_to_use_str);
            }
            if (!isInteger(documentFormat.days_after_the_date_of_hospitalization_to_use_str)) {
                errorMessages += "入院日何日後までカルテデータを使用するかには整数を入力してください。表示順: " + (documentFormat.order_no + 1) + "\n";
            }
            else {
                documentFormat.days_after_the_date_of_hospitalization_to_use = Number(documentFormat.days_after_the_date_of_hospitalization_to_use_str);
            }
            if (!isInteger(documentFormat.days_before_the_date_of_discharge_to_use_str)) {
                errorMessages += "退院日何日前からカルテデータを使用するかには整数を入力してください。表示順: " + (documentFormat.order_no + 1) + "\n";
            }
            else {
                documentFormat.days_before_the_date_of_discharge_to_use = Number(documentFormat.days_before_the_date_of_discharge_to_use_str);
            }
            if (!isInteger(documentFormat.days_after_the_date_of_discharge_to_use_str)) {
                errorMessages += "退院日何日後までカルテデータを使用するかには整数を入力してください。表示順: " + (documentFormat.order_no + 1) + "\n";
            }
            else {
                documentFormat.days_after_the_date_of_discharge_to_use = Number(documentFormat.days_after_the_date_of_discharge_to_use_str);
            }
            if (documentFormat.use_range_kind_str === USE_RANGE_KIND_ALL_STR) {
                documentFormat.use_range_kind = USE_RANGE_KIND_ALL;
            } else if(documentFormat.use_range_kind_str === USE_RANGE_KIND_HOSPITALIZATION_STR) {
                documentFormat.use_range_kind = USE_RANGE_KIND_HOSPITALIZATION;
                if (documentFormat.days_before_the_date_of_hospitalization_to_use + documentFormat.days_after_the_date_of_hospitalization_to_use < 0) {
                    errorMessages += "使用するカルテデータの合計期間が0日以上になるように入力してください。 表示順: " + (documentFormat.order_no + 1) + "\n";
                }
            } else {
                documentFormat.use_range_kind = USE_RANGE_KIND_DISCHARGE;
                if (documentFormat.days_before_the_date_of_discharge_to_use + documentFormat.days_after_the_date_of_discharge_to_use < 0) {
                    errorMessages += "使用するカルテデータの合計期間が0日以上になるように入力してください。 表示順: " + (documentFormat.order_no + 1) + "\n";
                }
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
        updateDocumentFormat(index_id, index_name);

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
        setIsDocumentFormatSettingEdited(false);
    }

    const onCancelDocumentFormatClicked = () => {
        cancelDocumentSetting();
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

    const onUseRangeKindChanged = (targetDocumentFormat:DocumentFormat, newValue:string) => {
        const newDocumentFormats = documentFormats.map((documentFormat) => {
            if (documentFormat.id === targetDocumentFormat.id) {
                documentFormat.use_range_kind_str = newValue;
            }
            return documentFormat;
        });
        setDocumentFormats(newDocumentFormats);
        setIsDocumentFormatSettingEdited(true);
    };

    const onDaysBeforeTheDateOfHospitalizationToUseChanged = (targetDocumentFormat:DocumentFormat, newValue:string) => {
        // 値が変わっているかチェック
        if (targetDocumentFormat.days_before_the_date_of_hospitalization_to_use_str !== newValue) {
            setIsDocumentFormatSettingEdited(true);
        }

        const newDocumentFormats = documentFormats.map((documentFormat) => {
            if (documentFormat.id === targetDocumentFormat.id) {
                documentFormat.days_before_the_date_of_hospitalization_to_use_str = newValue;
            }
            return documentFormat;
        });
        setDocumentFormats(newDocumentFormats);
    };

    const onDaysAfterTheDateOfHospitalizationToUseChanged = (targetDocumentFormat:DocumentFormat, newValue:string) => {
        // 値が変わっているかチェック
        if (targetDocumentFormat.days_after_the_date_of_hospitalization_to_use_str !== newValue) {
            setIsDocumentFormatSettingEdited(true);
        }

        const newDocumentFormats = documentFormats.map((documentFormat) => {
            if (documentFormat.id === targetDocumentFormat.id) {
                documentFormat.days_after_the_date_of_hospitalization_to_use_str = newValue;
            }
            return documentFormat;
        });
        setDocumentFormats(newDocumentFormats);
    };

    const onDaysBeforeTheDateOfDischargeToUseChanged = (targetDocumentFormat:DocumentFormat, newValue:string) => {
        // 値が変わっているかチェック
        if (targetDocumentFormat.days_before_the_date_of_discharge_to_use_str !== newValue) {
            setIsDocumentFormatSettingEdited(true);
        }

        const newDocumentFormats = documentFormats.map((documentFormat) => {
            if (documentFormat.id === targetDocumentFormat.id) {
                documentFormat.days_before_the_date_of_discharge_to_use_str = newValue;
            }
            return documentFormat;
        });
        setDocumentFormats(newDocumentFormats);
    };

    const onDaysAfterTheDateOfDischargeToUseChanged = (targetDocumentFormat:DocumentFormat, newValue:string) => {
        // 値が変わっているかチェック
        if (targetDocumentFormat.days_after_the_date_of_discharge_to_use_str !== newValue) {
            setIsDocumentFormatSettingEdited(true);
        }

        const newDocumentFormats = documentFormats.map((documentFormat) => {
            if (documentFormat.id === targetDocumentFormat.id) {
                documentFormat.days_after_the_date_of_discharge_to_use_str = newValue;
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

    const onTagsChanged = (targetDocumentFormatIndex:DocumentFormatIndex, newValue:string) => {
        if (tags !== newValue) {
            setIsDocumentFormatSettingEdited(true);
        }
        setTags(newValue);
    };

    const onSaveAsNameChanged = (newValue:string) => {
        if (saveAsName !== newValue) {
            setIsDocumentFormatSettingEdited(true);
        }
        setSaveAsName(newValue);
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
            use_range_kind: DEFAULT_USE_RANGE_KIND,
            use_range_kind_str: DEFAULT_USE_RANGE_KIND.toString(),
            days_before_the_date_of_hospitalization_to_use: DEFAULT_DAYS_BEFORE_THE_DATE_OF_HOSPITALIZATION_TO_USE,
            days_after_the_date_of_hospitalization_to_use: DEFAULT_DAYS_AFTER_THE_DATE_OF_HOSPITALIZATION_TO_USE,
            days_before_the_date_of_discharge_to_use: DEFAULT_DAYS_BEFORE_THE_DATE_OF_DISCHARGE_TO_USE,
            days_after_the_date_of_discharge_to_use: DEFAULT_DAYS_AFTER_THE_DATE_OF_DISCHARGE_TO_USE,
            days_before_the_date_of_hospitalization_to_use_str: DEFAULT_DAYS_BEFORE_THE_DATE_OF_HOSPITALIZATION_TO_USE.toString(),
            days_after_the_date_of_hospitalization_to_use_str: DEFAULT_DAYS_AFTER_THE_DATE_OF_HOSPITALIZATION_TO_USE.toString(),
            days_before_the_date_of_discharge_to_use_str: DEFAULT_DAYS_BEFORE_THE_DATE_OF_DISCHARGE_TO_USE.toString(),
            days_after_the_date_of_discharge_to_use_str: DEFAULT_DAYS_AFTER_THE_DATE_OF_DISCHARGE_TO_USE.toString(),
        };

        const newDocumentFormats: DocumentFormat[] = [];
        for (let documentFormat of documentFormats) {
            newDocumentFormats.push(documentFormat);
        }

        newDocumentFormats.push(newDocumentFormat);
        setDocumentFormats(newDocumentFormats);
        setIsDocumentFormatSettingEdited(true);
    }

    const onDocumentSettingIndexDeleteClicked = (targetDocumentFormatIndex:DocumentFormatIndex) => {
        // 実行確認
        const result = window.confirm("プロンプトを削除してよろしいですか？");
        if (!result) {
            return;
        }
        deleteDocumentFormat(targetDocumentFormatIndex.index_id);
    }

    const onDocumentSettingCategoryDeleteClicked = (documentFormatId : number) => {
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
                pid: pid,
            };
            const result = await getSoapApi(request);
            setPreviewSoap("患者番号: " + pid + "\n" + result.soap);
        } catch (e) {
            setError(e);
        } finally {
            setIsLoadingSoap(false);
        }
    }

    const onSoapPreviewClicked = (pid: string) => {
        if (pid === "") {
            setPreviewSoap("患者番号を入力してください。");
            return;
        }
        setPreviewSoap("");
        getSoap();
    };

    const onChangeSlot = (newSlot: string) => {
        setSelectedSlot(newSlot ? newSlot : '');
    }

    const onDocumentFormatIndexClicked = (newItem:DocumentFormatIndex) => {
        if (selectedDocumentFormatIndex && selectedDocumentFormatIndex.index_id === newItem.index_id) {
            return;
        }

        if (isDocumentFormatSettingEdited) {
            const result = window.confirm("使用するプロンプトを切り替えます。\nプロンプト編集内容が保存されていません。\n編集内容を破棄してよろしいですか？");
            if (!result) {
                return;
            }
        }
        getDocumentFormat(newItem);
        setIsDocumentFormatSettingEdited(false);
        setSelectedDocumentFormatIndex(newItem);
        setSaveAsName("");
        setTags(newItem.tags);
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
                             {/* <h2 className={styles.chatEmptyStateSubtitle}>{pid}</h2> */}
                             <div className={styles.dischargeInput}>
                                 <PatientCodeInput
                                     onPatientCodeChanged={x => (setPid(x))}
                                     onPatientNameChanged={(patientName, hospitalizationDate, dischargeDate) => (setPatientName(patientName), setHospitalizationDate(hospitalizationDate), setDischargeDate(dischargeDate))}
                                     clearOnSend
                                     pid={pid}
                                     patientName={patientName}
                                     departmentCode={departmantCode}
                                     hospitalizationDate={hospitalizationDate}
                                     dischargeDate={dischargeDate}
                                     placeholder="Type a new question (e.g. how to prevent chronic disease?)"
                                     disabled={isLoading}
                             />
                            </div>
                            {/* <h3 className={styles.chatEmptyStateSubtitle}>カルテデータ プレビュー</h3> */}
                            {/* <h3 className={styles.chatEmptyStateSubtitle}>使用するプロンプトを指定する</h3> */}
                            {/* 中間データ作成により、この機能の整合性がとれなくなってきたため、一旦コメントアウト
                             <SoapPreviewButton 
                                pid={pid}
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
                            <br></br> */}
                            <Label>使用するプロンプトを選ぶ</Label>
                            <table className={styles.documentFormatSettingIndexSearchTable}>
                                <tr>
                                    <td>
                                        <Checkbox label="自分が作成したプロンプトとマスターファイルのみ表示　"
                                            checked={isOnlyMyself}
                                            onChange={(e, checked) => setIsOnlyMyself(checked!)}/>
                                    </td>
                                    <td>
                                        <TextField
                                            placeholder="タグ検索ワードを指定"
                                            readOnly={false}
                                            multiline={false}
                                            resizable={false}
                                            defaultValue={searchText}
                                            value={searchText}
                                            onChange={(e, newValue) => setSearchText(newValue || "")}
                                            onBlur={(e) => setSearchText(e.target.value || "")}
                                        />
                                    </td>
                                    <td>　</td>
                                    <td>
                                        <div className={
                                            styles.searchDocumentFormatButton} 
                                            onClick={() => getDocumentFormatIndexList()}>
                                            <Search24Filled primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Search logo" />
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            {isLoadingDocumentFormatIndexList && <Spinner label="Loading prompt list" />}
                            <Stack.Item>
                                <Stack horizontal wrap tokens={{ childrenGap: 5 }}>
                                    {documentFormatIndexList.map((item) => {
                                        return (
                                            <a key={item.index_id} className={selectedDocumentFormatIndex?.index_id == item.index_id ? styles.selectedPromptName : styles.promptName} title={item.index_name} onClick={() => onDocumentFormatIndexClicked(item)}>
                                                {`${item.index_name}`}
                                            </a>
                                        );
                                    })}
                                </Stack>
                            </Stack.Item>

                            <br></br>
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
        <div>
            <Dropdown 
                    placeholder="Select user"
                    options={momorySlotOptions}
                    selectedKey={selectedSlot}
                    onChange={(e, newValue) => {
                        onChangeSlot(newValue?.key as string || '');
                    }}
            />  <br></br>
            <p>診療科コード：<br></br>
                <TextField
                    readOnly={false}
                    multiline={false}
                    resizable={false}
                    scrolling="false"
                    defaultValue={departmantCode}
                    value={departmantCode}
                    onChange={(e, newValue) => setDepartmantCode(newValue || "")}
                    onBlur={(e) => setDepartmantCode(e.target.value || "")}
                />
            </p>
        </div>
        {selectedDocumentFormatIndex && documentFormats && (
            <div className={styles.dischargeDocumentFormatSettingDiv}>
                <DocumentFormatSetting 
                    documentName={DOCUMENT_NAME}
                    documentFormatIndex={selectedDocumentFormatIndex!}
                    saveAsName={saveAsName}
                    tags={tags}
                    userId={selectedSlot ? selectedSlot : ''}
                    systemContents={systemContents}
                    documentFormats={documentFormats}
                    isLoading={isLoadingDocumnetFormatSetting}
                    isEdited={isDocumentFormatSettingEdited}
                    onSaveClicked={onSaveDocumentFormatClicked}
                    onDeleteIndexClicked={onDocumentSettingIndexDeleteClicked}
                    onSystemContentsChanged={onSystemContentsChanged}
                    onCategoryNameChanged={onCategoryNameChanged}
                    onTagsChanged={onTagsChanged}
                    onSaveAsNameChanged={onSaveAsNameChanged}
                    onKindChanged={onKindChanged}
                    onTargetSoapChanged={onTargetSoapChanged}
                    onQuestionChanged={onQuestionChanged}
                    onTemperatureChanged={onTemperatureChanged}
                    onUseRangeKindChanged={onUseRangeKindChanged}
                    onDaysBeforeTheDateOfHospitalizationToUseChanged={onDaysBeforeTheDateOfHospitalizationToUseChanged}
                    onDaysAfterTheDateOfHospitalizationToUseChanged={onDaysAfterTheDateOfHospitalizationToUseChanged}
                    onDaysBeforeTheDateOfDischargeToUseChanged={onDaysBeforeTheDateOfDischargeToUseChanged}
                    onDaysAfterTheDateOfDischargeToUseChanged={onDaysAfterTheDateOfDischargeToUseChanged}
                    onUpClicked={onDocumentFormatUpClicked}
                    onDownClicked={onDocumentFormatDownClicked}
                    onDeleteCategoryClicked={onDocumentSettingCategoryDeleteClicked}
                    onAddClicked={onAddDocumentFormatClicked}
                ></DocumentFormatSetting>
            </div>
            )}
        </Stack>  
    );
};

export default Discharge;

