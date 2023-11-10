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
    patientCode: string;
    documentName: string;
    departmentCode: string;
    icd10Code: string;
    approach: Approaches;
    userId: string;
    overrides?: AskRequestOverrides;
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
    patient_code: string;
};

export type GetPatientResponse = {
    name: string;
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
    patient_code: string;
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
};

export type GetDocumentFormatRequest = {
    document_name: string;
    department_code: string;
    icd10_code: string;
    user_id: string;
    force_master: boolean;
};

export type GetDocumentFormatResponse = {
    document_formats: DocumentFormat[];
    error?: string;
};

export type UpdateDocumentFormatRequest = {
    document_name: string;
    department_code: string;
    icd10_code: string;
    user_id: string;
    document_formats: DocumentFormat[];
};

export type UpdateDocumentFormatResponse = {
    error?: string;
};
