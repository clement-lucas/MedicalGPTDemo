import { useRef, useState} from "react";
import { Checkbox, ChoiceGroup, IChoiceGroupOption, Panel, DefaultButton, Spinner, TextField, SpinButton } from "@fluentui/react";
import { Label, Stack } from "@fluentui/react";
import { PrimaryButton } from '@fluentui/react/lib/Button';

import styles from "./Discharge.module.css";

import { dischargeApi, Approaches, AskResponse, DischargeRequest, GetHistoryIndexRequest, HistoryDate, getHistoryIndexApi, GetHistoryDetailRequest, getHistoryDetailApi
    , getSoapApi, GetSoapRequest
    , DocumentFormat
    , getDocumentFormatApi, GetDocumentFormatRequest
    , updateDocumentFormatApi, UpdateDocumentFormatRequest } from "../../api";
import { Answer, AnswerError } from "../../components/Answer";
import { DischargeButton } from "../../components/Example/DischargeButton";
import { AnalysisPanel, AnalysisPanelTabs } from "../../components/AnalysisPanel";
import bird from "../../assets/bird.svg";
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

const Discharge = () => {
    const DEFAULT_DEPARTMENT_CODE: string = "0000";
    const DEFAULT_ICD10_CODE: string = "0000";
    const DEFAULT_ICD10_NAME: string = "指定なし";
    const DEFAULT_USER_ID: string = "00000001";
    const DOCUMENT_NAME: string = "退院時サマリ";
    const DEFAULT_TEMPERATURE = 0.01
    const DEFAULT_RESPONSE_MAX_TOKENS = 1000
    const DEFAULT_QUESTION_SUFFIX = "作成される文章は 900 Token以内とします。"
    const [isConfigPanelOpen, setIsConfigPanelOpen] = useState(false);
    const [approach, setApproach] = useState<Approaches>(Approaches.RetrieveThenRead);
    const [promptTemplate, setPromptTemplate] = useState<string>("");
    const [promptTemplatePrefix, setPromptTemplatePrefix] = useState<string>("");
    const [promptTemplateSuffix, setPromptTemplateSuffix] = useState<string>("");
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
    const iconStyle: React.CSSProperties = { padding: 10, width: 100, height: 90,  color: "#465f8b" };
    const [historyItems, setHistoryItems] = useState<HistoryDate[]>([]);
    const [isDocumnetFormatSettingVisible, setIsDocumnetFormatSettingVisible] = useState<boolean>(false);
    const [documentFormats, setDocumentFormats] = useState<DocumentFormat[]>([]);
    const [isDocumentFormatSettingEdited, setIsDocumentFormatSettingEdited] = useState<boolean>(false);

    const onLoad = async () => {
        setIsDocumnetFormatSettingVisible(false);
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

    const getDocumentFormat = async (force_master:boolean) => {
        setIsLoadingDocumnetFormatSetting(true);
        try {
            const request: GetDocumentFormatRequest = {
                document_name: DOCUMENT_NAME,
                department_code: DEFAULT_DEPARTMENT_CODE,
                icd10_code: DEFAULT_ICD10_CODE,
                force_master: force_master,
            };
            const result = await getDocumentFormatApi(request);
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
                user_id: DEFAULT_USER_ID,
                document_formats: documentFormats,
            };
            await updateDocumentFormatApi(request);
            alert("保存しました。");
        } catch (e) {
            alert(e)
        }
    }

    const makeApiRequest = async (documentName: string) => {
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
                icd10Code: DEFAULT_ICD10_CODE,
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
        getDocumentFormat(true);
        setIsDocumentFormatSettingEdited(true);
    }

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

    const onDocumentFormatEditClicked = () => {
        if (!isDocumnetFormatSettingVisible) {
            // 開く
            getDocumentFormat(false);
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
                <img src={bird} alt="bird" style={iconStyle}  />
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
        { isDocumnetFormatSettingVisible && (
            <div className={styles.dischargeDocumentFormatSettingDiv}>
                <DocumentFormatSetting 
                    documentName={DOCUMENT_NAME}
                    departmentCode={DEFAULT_DEPARTMENT_CODE}
                    icd10Code={DEFAULT_ICD10_CODE}
                    icd10Name={DEFAULT_ICD10_NAME}
                    userId={DEFAULT_USER_ID}
                    documentFormats={documentFormats}
                    isLoading={isLoadingDocumnetFormatSetting}
                    isEdited={isDocumentFormatSettingEdited}
                    onSaveClicked={onSaveDocumentFormatClicked}
                    onCancelClicked={onCancelDocumentFormatClicked}
                    onReloadFromMasterClicked={onReloadFromMasterClicked}
                    onCategoryNameChanged={onCategoryNameChanged}
                    onKindChanged={onKindChanged}
                    onTargetSoapChanged={onTargetSoapChanged}
                    onQuestionChanged={onQuestionChanged}
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

