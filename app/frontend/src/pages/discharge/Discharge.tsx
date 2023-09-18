import { useRef, useState} from "react";
import { Checkbox, ChoiceGroup, IChoiceGroupOption, Panel, DefaultButton, Spinner, TextField, SpinButton } from "@fluentui/react";
import { Label, Stack } from "@fluentui/react";
import { PrimaryButton } from '@fluentui/react/lib/Button';


import styles from "./Discharge.module.css";

import { dischargeApi, Approaches, AskResponse, DischargeRequest, GetHistoryIndexRequest, HistoryDate, getHistoryIndexApi, GetHistoryDetailRequest, getHistoryDetailApi } from "../../api";
import { Answer, AnswerError } from "../../components/Answer";
import { DischargeList } from "../../components/Example";
import { AnalysisPanel, AnalysisPanelTabs } from "../../components/AnalysisPanel";
import bird from "../../assets/bird.svg";
import { PatientCodeInput } from "../../components/PatientCodeInput/PatientCodeInput";
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

    const lastQuestionRef = useRef<string>("");
    const [completionTokens, setCompletionTokens] = useState<number>(0);
    const [promptTokens, setPromptTokens] = useState<number>(0);
    const [totalTokens, setTotalTokens] = useState<number>(0);

    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<unknown>();
    const [answer, setAnswer] = useState<AskResponse>();

    const [activeCitation, setActiveCitation] = useState<string>();
    const [activeAnalysisPanelTab, setActiveAnalysisPanelTab] = useState<AnalysisPanelTabs | undefined>(undefined);
    const iconStyle: React.CSSProperties = { padding: 10, width: 100, height: 90,  color: "#465f8b" };
    const [historyItems, setHistoryItems] = useState<HistoryDate[]>([]);

    const onLoad = async () => {
        await getHistoryIndex();
    }

    const getHistoryIndex = async () => {
        try {
            const request: GetHistoryIndexRequest = {
                document_name: "退院時サマリ",
            };
            const result = await getHistoryIndexApi(request);
            setHistoryItems(result.history_date_list);
        } catch (e) {
            // TODO エラー表示処理
            alert(e)
            //setError(e);
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

    const onPromptTemplateChange = (_ev?: React.FormEvent<HTMLInputElement | HTMLTextAreaElement>, newValue?: string) => {
        setPromptTemplate(newValue || "");
    };

    const onPromptTemplatePrefixChange = (_ev?: React.FormEvent<HTMLInputElement | HTMLTextAreaElement>, newValue?: string) => {
        setPromptTemplatePrefix(newValue || "");
    };

    const onPromptTemplateSuffixChange = (_ev?: React.FormEvent<HTMLInputElement | HTMLTextAreaElement>, newValue?: string) => {
        setPromptTemplateSuffix(newValue || "");
    };

    const onRetrieveCountChange = (_ev?: React.SyntheticEvent<HTMLElement, Event>, newValue?: string) => {
        setRetrieveCount(parseInt(newValue || "3"));
    };

    const onApproachChange = (_ev?: React.FormEvent<HTMLElement | HTMLInputElement>, option?: IChoiceGroupOption) => {
        setApproach((option?.key as Approaches) || Approaches.RetrieveThenRead);
    };

    const onUseSemanticRankerChange = (_ev?: React.FormEvent<HTMLElement | HTMLInputElement>, checked?: boolean) => {
        setUseSemanticRanker(!!checked);
    };

    const onUseSemanticCaptionsChange = (_ev?: React.FormEvent<HTMLElement | HTMLInputElement>, checked?: boolean) => {
        setUseSemanticCaptions(!!checked);
    };

    const onExcludeCategoryChanged = (_ev?: React.FormEvent, newValue?: string) => {
        setExcludeCategory(newValue || "");
    };

    const onExampleClicked = (example: string) => {
        makeApiRequest(example);
    };

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

    const approaches: IChoiceGroupOption[] = [
        {
            key: Approaches.RetrieveThenRead,
            text: "Retrieve-Then-Read"
        },
        {
            key: Approaches.ReadRetrieveRead,
            text: "Read-Retrieve-Read"
        },
        {
            key: Approaches.ReadDecomposeAsk,
            text: "Read-Decompose-Ask"
        }
    ];

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
        <div className={styles.dischargeContainer}>
            <div className={styles.dischargeTopSection}>
                {/* <SettingsButton className={styles.settingsButton} onClick={() => setIsConfigPanelOpen(!isConfigPanelOpen)} /> */}
                <img src={bird} alt="bird" style={iconStyle}  />
                             <h1 className={styles.chatEmptyStateTitle}>退院サマリ作成システム</h1>
                             <h2 className={styles.chatEmptyStateSubtitle}>どの文書を作成しますか？</h2>
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
                            <DischargeList onExampleClicked={onExampleClicked} />
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

            <Panel
                headerText="Configure answer generation"
                isOpen={isConfigPanelOpen}
                isBlocking={false}
                onDismiss={() => setIsConfigPanelOpen(false)}
                closeButtonAriaLabel="Close"
                onRenderFooterContent={() => <DefaultButton onClick={() => setIsConfigPanelOpen(false)}>Close</DefaultButton>}
                isFooterAtBottom={true}
            >
                <ChoiceGroup
                    className={styles.dischargeSettingsSeparator}
                    label="Approach"
                    options={approaches}
                    defaultSelectedKey={approach}
                    onChange={onApproachChange}
                />

                {(approach === Approaches.RetrieveThenRead || approach === Approaches.ReadDecomposeAsk) && (
                    <TextField
                        className={styles.dischargeSettingsSeparator}
                        defaultValue={promptTemplate}
                        label="Override prompt template"
                        multiline
                        autoAdjustHeight
                        onChange={onPromptTemplateChange}
                    />
                )}

                {approach === Approaches.ReadRetrieveRead && (
                    <>
                        <TextField
                            className={styles.dischargeSettingsSeparator}
                            defaultValue={promptTemplatePrefix}
                            label="Override prompt prefix template"
                            multiline
                            autoAdjustHeight
                            onChange={onPromptTemplatePrefixChange}
                        />
                        <TextField
                            className={styles.dischargeSettingsSeparator}
                            defaultValue={promptTemplateSuffix}
                            label="Override prompt suffix template"
                            multiline
                            autoAdjustHeight
                            onChange={onPromptTemplateSuffixChange}
                        />
                    </>
                )}

                <SpinButton
                    className={styles.dischargeSettingsSeparator}
                    label="Retrieve this many discharges from search:"
                    min={1}
                    max={50}
                    defaultValue={retrieveCount.toString()}
                    onChange={onRetrieveCountChange}
                />
                <TextField className={styles.dischargeSettingsSeparator} label="Exclude category" onChange={onExcludeCategoryChanged} />
                <Checkbox
                    className={styles.dischargeSettingsSeparator}
                    checked={useSemanticRanker}
                    label="Use semantic ranker for retrieval"
                    onChange={onUseSemanticRankerChange}
                />
                <Checkbox
                    className={styles.dischargeSettingsSeparator}
                    checked={useSemanticCaptions}
                    label="Use query-contextual summaries instead of whole discharges"
                    onChange={onUseSemanticCaptionsChange}
                    disabled={!useSemanticRanker}
                />
            </Panel>
        </div>
    </Stack>  
    );
};

export default Discharge;

