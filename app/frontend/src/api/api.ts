import { AskRequest, DocumentRequest, DischargeRequest, GetPatientRequest, 
    GetPatientOldRequest, 
    GetPatientResponse, GetHistoryDetailRequest, AskResponse, ChatRequest, ChatPatientRequest,
    GetHistoryIndexRequest, GetHistoryIndexResponse,
    GetSoapRequest, GetSoapResponse, 
    GetDocumentFormatIndexRequest, GetDocumentFormatIndexResponse,
    GetDocumentFormatRequest, GetDocumentFormatResponse,
    UpdateDocumentFormatRequest, UpdateDocumentFormatResponse,
    DeleteDocumentFormatRequest, DeleteDocumentFormatResponse,
    GetIcd10MasterRequest, GetIcd10MasterResponse,
    GetDepartmentMasterRequest, GetDepartmentMasterResponse,
} from "./models";

export async function askApi(options: AskRequest): Promise<AskResponse> {
    const response = await fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: options.question,
            approach: options.approach,
            overrides: {
                semantic_ranker: options.overrides?.semanticRanker,
                semantic_captions: options.overrides?.semanticCaptions,
                top: options.overrides?.top,
                temperature: options.overrides?.temperature,
                prompt_template: options.overrides?.promptTemplate,
                prompt_template_prefix: options.overrides?.promptTemplatePrefix,
                prompt_template_suffix: options.overrides?.promptTemplateSuffix,
                exclude_category: options.overrides?.excludeCategory
            }
        })
    });

    const parsedResponse: AskResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }

    return parsedResponse;
}

export async function documentApi(options: DocumentRequest): Promise<AskResponse> {
    const response = await fetch("/document", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            document_name: options.documentName,
            patient_code: options.patientCode,
            approach: options.approach,
            overrides: {
                semantic_ranker: options.overrides?.semanticRanker,
                semantic_captions: options.overrides?.semanticCaptions,
                top: options.overrides?.top,
                temperature: options.overrides?.temperature,
                prompt_template: options.overrides?.promptTemplate,
                prompt_template_prefix: options.overrides?.promptTemplatePrefix,
                prompt_template_suffix: options.overrides?.promptTemplateSuffix,
                exclude_category: options.overrides?.excludeCategory
            }
        })
    });

    const parsedResponse: AskResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }

    return parsedResponse;
}

export async function dischargeApi(options: DischargeRequest): Promise<AskResponse> {
    const response = await fetch("/discharge", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            department_code: options.departmentCode,
            pid: options.pid,
            document_format_index_id: options.documentFormatIndexId,
            user_id: options.userId
        })
    });

    const parsedResponse: AskResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }

    return parsedResponse;
}

export async function chatApi(options: ChatRequest): Promise<AskResponse> {
    const response = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            history: options.history,
            approach: options.approach,
            overrides: {
                semantic_ranker: options.overrides?.semanticRanker,
                semantic_captions: options.overrides?.semanticCaptions,
                top: options.overrides?.top,
                temperature: options.overrides?.temperature,
                prompt_template: options.overrides?.promptTemplate,
                prompt_template_prefix: options.overrides?.promptTemplatePrefix,
                prompt_template_suffix: options.overrides?.promptTemplateSuffix,
                exclude_category: options.overrides?.excludeCategory,
                suggest_followup_questions: options.overrides?.suggestFollowupQuestions
            }
        })
    });

    const parsedResponse: AskResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }

    return parsedResponse;
}

// export async function askPatientApi(options: AskPatientRequest): Promise<AskResponse> {
//     const response = await fetch("/ask", {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json"
//         },
//         body: JSON.stringify({
//             question: options.question,
//             approach: options.approach,
//             overrides: {
//                 semantic_ranker: options.overrides?.semanticRanker,
//                 semantic_captions: options.overrides?.semanticCaptions,
//                 top: options.overrides?.top,
//                 temperature: options.overrides?.temperature,
//                 prompt_template: options.overrides?.promptTemplate,
//                 prompt_template_prefix: options.overrides?.promptTemplatePrefix,
//                 prompt_template_suffix: options.overrides?.promptTemplateSuffix,
//                 exclude_category: options.overrides?.excludeCategory
//             }
//         })
//     });

//     const parsedResponse: AskResponse = await response.json();
//     if (response.status > 299 || !response.ok) {
//         throw Error(parsedResponse.error || "Unknown error");
//     }

//     return parsedResponse;
// }

export async function chatPatientApi(options: ChatPatientRequest): Promise<AskResponse> {
    const response = await fetch("/chat_patient", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            history: options.history,
            history_patient: options.history_patient,
            approach: options.approach,
            overrides: {
                semantic_ranker: options.overrides?.semanticRanker,
                semantic_captions: options.overrides?.semanticCaptions,
                top: options.overrides?.top,
                temperature: options.overrides?.temperature,
                prompt_template: options.overrides?.promptTemplate,
                prompt_template_prefix: options.overrides?.promptTemplatePrefix,
                prompt_template_suffix: options.overrides?.promptTemplateSuffix,
                exclude_category: options.overrides?.excludeCategory,
                suggest_followup_questions: options.overrides?.suggestFollowupQuestions
            }
        })
    });

    const parsedResponse: AskResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }

    return parsedResponse;
}

export async function getPatientApi(options: GetPatientRequest): Promise<GetPatientResponse> {
    const response = await fetch("/get_patient", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            pid: options.pid,
        })
    });

    const parsedResponse: GetPatientResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }

    return parsedResponse;
}

export async function getPatientOldApi(options: GetPatientOldRequest): Promise<GetPatientResponse> {
    const response = await fetch("/get_patient_old", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            patient_code: options.patient_code,
        })
    });

    const parsedResponse: GetPatientResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }

    return parsedResponse;
}

export async function getHistoryIndexApi(options: GetHistoryIndexRequest): Promise<GetHistoryIndexResponse> {
    const response = await fetch("/get_history_index", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            document_name: options.document_name,
        })
    });

    const parsedResponse: GetHistoryIndexResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }

    return parsedResponse;
}

export async function getHistoryDetailApi(options: GetHistoryDetailRequest): Promise<AskResponse> {
    const response = await fetch("/get_history_detail", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id: options.id,
        })
    });

    const parsedResponse: AskResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }

    return parsedResponse;
}

export async function getSoapApi( options: GetSoapRequest): Promise<GetSoapResponse> {
    // return new Promise((resolve, reject) => {
    //     const xhr = new XMLHttpRequest();
    //     xhr.open("POST", "/soap");
    //     xhr.setRequestHeader("Content-Type", "application/json");
    //     xhr.responseType = "json";
    //     xhr.onload = () => {
    //         if (xhr.status > 299 || !xhr.response) {
    //             reject(Error(xhr.response?.error || "Unknown error"));
    //         } else {
    //             resolve(xhr.response);
    //         }
    //     };
    //     xhr.onerror = () => {
    //         reject(Error("Unknown error"));
    //     };
    //     xhr.send(JSON.stringify({
    //         patient_code: options.patient_code,
    //     }));
    // });

    const response = await fetch("/soap", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            pid: options.pid,
        })
    });

    const parsedResponse: GetSoapResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }

    return parsedResponse;
}

export async function getDocumentFormatIndexApi( options: GetDocumentFormatIndexRequest): Promise<GetDocumentFormatIndexResponse> {
    const response = await fetch("/get_document_format_index", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            document_name: options.document_name,
            user_id: options.user_id,
            is_only_myself: options.is_only_myself,
            search_text: options.search_text
        })
    });

    const parsedResponse: GetDocumentFormatIndexResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }
    return parsedResponse;
}

export async function getDocumentFormatApi( options: GetDocumentFormatRequest): Promise<GetDocumentFormatResponse> {
    const response = await fetch("/get_document_format", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            document_format_index_id: options.documnet_format_index_id
        })
    });

    const parsedResponse: GetDocumentFormatResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }
    return parsedResponse;
}

export async function updateDocumentFormatApi( options: UpdateDocumentFormatRequest): Promise<UpdateDocumentFormatResponse> {
    const response = await fetch("/update_document_format", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            document_format_index_id: options.document_format_index_id,
            document_format_index_name: options.document_format_index_name,
            document_name: options.document_name,
            tags: options.tags,
            user_id: options.user_id,
            system_contents: options.system_contents,
            system_contents_suffix: options.system_contents_suffix,
            document_formats: options.document_formats,
        })
    });

    const parsedResponse: UpdateDocumentFormatResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }
    return parsedResponse;
}

export async function deleteDocumentFormatApi( options: DeleteDocumentFormatRequest): Promise<DeleteDocumentFormatResponse> {
    const response = await fetch("/delete_document_format", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            document_format_index_id: options.document_format_index_id,
            user_id: options.user_id,
        })
    });

    const parsedResponse: DeleteDocumentFormatResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }
    return parsedResponse;
}

export async function getIcd10MasterApi( options: GetIcd10MasterRequest): Promise<GetIcd10MasterResponse> {
    const response = await fetch("/get_icd10_master", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            code_level: options.code_level,
            parent_code: options.parent_code,
        })
    });

    const parsedResponse: GetIcd10MasterResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }
    return parsedResponse;
}

export async function getDepartmentMasterApi( options: GetDepartmentMasterRequest): Promise<GetDepartmentMasterResponse> {
    const response = await fetch("/get_department_master", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
        })
    });

    const parsedResponse: GetDepartmentMasterResponse = await response.json();
    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }
    return parsedResponse;
}

export function getCitationFilePath(citation: string): string {
    return `/content/${citation}`;
}

