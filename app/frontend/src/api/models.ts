export const enum Approaches {
    RetrieveThenRead = "rtr",
    ReadRetrieveRead = "rrr",
    ReadDecomposeAsk = "rda"
}

export type AskRequestOverrides = {
    semanticRanker?: boolean;
    semanticCaptions?: boolean;
    excludeCategory?: string;
    top?: number;
    temperature?: number;
    promptTemplate?: string;
    promptTemplatePrefix?: string;
    promptTemplateSuffix?: string;
    suggestFollowupQuestions?: boolean;
};

export type AskRequest = {
    question: string;
    approach: Approaches;
    overrides?: AskRequestOverrides;
};

export type DocumentRequest = {
    patientCode: string;
    documentName: string;
    approach: Approaches;
    overrides?: AskRequestOverrides;
};

export type DischargeRequest = {
    departmentCode: string;
    pid: string;
    documentFormatIndexId: number;
    userId: string;
};

export type AskPatientRequest = {
    patientCode: string;
    question: string;
    approach: Approaches;
    overrides?: AskRequestOverrides;
};

export type AskResponse = {
    pid: string | null;
    patient_name: string | null;
    answer: string;
    thoughts: string | null;
    data_points: string[];
    completion_tokens: number;
    prompt_tokens: number;
    total_tokens: number;
    hospitalization_date: string | null;
    discharge_date: string | null;
    error?: string;
};

export type ChatTurn = {
    user: string;
    bot?: string;
};

export type ChatRequest = {
    history: ChatTurn[];
    approach: Approaches;
    overrides?: AskRequestOverrides;
};

export type ChatPatientTurn = {
    patientcode: string;
    bot?: string;
};

export type ChatPatientRequest = {
    history: ChatTurn[];
    history_patient: ChatPatientTurn[];
    approach: Approaches;
    overrides?: AskRequestOverrides;
};

export type GetPatientRequest = {
    pid: string;
    department_code: string;
};

export type GetPatientOldRequest = {
    patient_code: string;
};

export type GetPatientResponse = {
    name: string;
    hospitalization_date: string;
    discharge_date: string;
    error?: string;
};

export type GetHistoryIndexRequest = {
    document_name: string;
};

export type GetHistoryIndexResponse = {
    history_date_list: HistoryDate[];
    error?: string;
};

export type HistoryDate = {
    created_date: string;
    history_list: HistoryIndex[];
};

export type HistoryIndex = {
    id: number;
    pid: string;
    patient_name: string;
    document_name: string;
};

export type GetHistoryDetailRequest = {
    id: number;
};

export type GetSoapRequest = {
    pid: string;
};

export type GetSoapResponse = {
    soap: string;
    error?: string;
};

export type DocumentFormat = {
    id: number;
    kind: number;
    category_name: string;
    order_no: number;
    temperature: number;
    temperature_str: string;
    question: string;
    question_suffix: string;
    response_max_tokens: number;
    is_s: boolean;
    is_o: boolean;
    is_a: boolean;
    is_p: boolean;
    is_b: boolean;
    use_allergy_records: boolean;
    use_discharge_medicine_records: boolean;
    use_range_kind: number;
    use_range_kind_str: string;
    days_before_the_date_of_hospitalization_to_use : number;
    days_after_the_date_of_hospitalization_to_use : number;
    days_before_the_date_of_discharge_to_use : number;
    days_after_the_date_of_discharge_to_use : number;
    days_before_the_date_of_hospitalization_to_use_str : string;
    days_after_the_date_of_hospitalization_to_use_str : string;
    days_before_the_date_of_discharge_to_use_str : string;
    days_after_the_date_of_discharge_to_use_str : string;
};

export type DocumentFormatIndex = {
    index_id: number;
    is_master: boolean;
    index_name: string;
    tags: string;
    updated_by: string;
    updated_date_time: string;
};

export type GetDocumentFormatIndexRequest = {
    document_name: string;
    user_id: string;
    is_only_myself: boolean;
    search_text: string;
};

export type GetDocumentFormatIndexResponse = {
    document_format_index_list: DocumentFormatIndex[];
    error?: string;
};

export type GetDocumentFormatRequest = {
    documnet_format_index_id: number;
};

export type GetDocumentFormatResponse = {
    system_contents: string;
    system_contents_suffix: string;
    document_formats: DocumentFormat[];
    error?: string;
};

export type UpdateDocumentFormatRequest = {
    document_format_index_id: number;
    document_format_index_name: string;
    document_name: string;
    tags: string;
    user_id: string;
    system_contents: string;
    system_contents_suffix: string;
    document_formats: DocumentFormat[];
};

export type UpdateDocumentFormatResponse = {
    document_format_index_id: number;
    error?: string;
};

export type DeleteDocumentFormatRequest = {
    document_format_index_id: number;
    user_id: string;
};

export type DeleteDocumentFormatResponse = {
    error?: string;
};

export type Icd10Master = {
    icd10_code: string;
    caption: string;
};

export type GetIcd10MasterRequest = {
    code_level: number;
    parent_code: string;
};

export type GetIcd10MasterResponse = {
    records: Icd10Master[];
    error?: string;
};

export type DepartmentMaster = {
    department_code: string;
    department_name: string;
};

export type GetDepartmentMasterRequest = {
};

export type GetDepartmentMasterResponse = {
    records: DepartmentMaster[];
    error?: string;
};
