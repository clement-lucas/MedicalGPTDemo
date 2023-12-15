import os
import mimetypes
import time
import logging
import openai
from flask import Flask, request, jsonify
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from approaches.retrievethenread import RetrieveThenReadApproach
from approaches.readretrieveread import ReadRetrieveReadApproach
from approaches.readdecomposeask import ReadDecomposeAsk
from approaches.chatreadretrieveread import ChatReadRetrieveReadApproach
from approaches.chatpatientreadretrieveread import ChatPatientReadRetrieveReadApproach
from approaches.readretrievedocumentread import ReadRetrieveDocumentReadApproach
from approaches.readretrievedischargeread import ReadRetrieveDischargeReadApproach
from approaches.getpatient import GetPatientApproach
from approaches.getpatientold import GetPatientOldApproach
from approaches.gethistoryinex import GetHistoryIndexApproach
from approaches.gethistorydetail import GetHistoryDetailApproach
from approaches.getsoap import GetSoapApproach
from approaches.getdocumentfotmatindex import GetDocumentFormatIndexApproach
from approaches.deletedocumentfotmat import DeleteDocumentFormatApproach
from approaches.getdocumentfotmat import GetDocumentFormatApproach
from approaches.updatedocumentfotmat import UpdateDocumentFormatApproach
from approaches.geticd10master import GetIcd10MasterApproach
from approaches.getdepartmentmaster import GetDepartmentMasterApproach
from azure.storage.blob import BlobServiceClient
from lib.sqlconnector import SQLConnector

# Replace these with your own values, either in environment variables or directly here
AZURE_STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT") or "mystorageaccount"
AZURE_STORAGE_CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER") or "content"
AZURE_SEARCH_SERVICE = os.environ.get("AZURE_SEARCH_SERVICE") or "gptkb"
AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX") or "gptkbindex"
AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE") or "myopenai"
AZURE_OPENAI_GPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_GPT_DEPLOYMENT") or "chat"
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHATGPT_DEPLOYMENT") or "chat"

KB_FIELDS_CONTENT = os.environ.get("KB_FIELDS_CONTENT") or "content"
KB_FIELDS_CATEGORY = os.environ.get("KB_FIELDS_CATEGORY") or "category"
KB_FIELDS_SOURCEPAGE = os.environ.get("KB_FIELDS_SOURCEPAGE") or "sourcepage"

AZURE_OPENAI_AUTHENTICATION=os.environ.get("AZURE_OPENAI_AUTHENTICATION") or "ActiveDirectory"
is_openal_ad_auth = False if AZURE_OPENAI_AUTHENTICATION == "ApiKey" else True
AZURE_OPENAI_KEY=os.environ.get("AZURE_OPENAI_KEY") or ""
if (not is_openal_ad_auth and not AZURE_OPENAI_KEY):
    raise Exception("AZURE_OPENAI_KEY is required")

# Use the current user identity to authenticate with Azure OpenAI, Cognitive Search and Blob Storage (no secrets needed, 
# just use 'az login' locally, and managed identity when deployed on Azure). If you need to use keys, use separate AzureKeyCredential instances with the 
# keys for each service
# If you encounter a blocking error during a DefaultAzureCredntial resolution, you can exclude the problematic credential by using a parameter (ex. exclude_shared_token_cache_credential=True)
azure_credential = DefaultAzureCredential()

# Used by the OpenAI SDK
openai.api_base = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com"
openai.api_version = "2023-05-15"

if is_openal_ad_auth:
    print("Using Azure AD authentication for OpenAI")
    openai.api_type = "azure_ad"
    openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
    openai.api_key = openai_token.token
else:
    print("Using API key authentication for OpenAI")
    openai.api_type = "azure"
    openai.api_key = AZURE_OPENAI_KEY

sql_connector = SQLConnector()

# Set up clients for Cognitive Search and Storage
search_client = SearchClient(
    endpoint=f"https://{AZURE_SEARCH_SERVICE}.search.windows.net",
    index_name=AZURE_SEARCH_INDEX,
    credential=azure_credential)
blob_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net", 
    credential=azure_credential)
blob_container = blob_client.get_container_client(AZURE_STORAGE_CONTAINER)

# Various approaches to integrate GPT and external knowledge, most applications will use a single one of these patterns
# or some derivative, here we include several for exploration purposes
ask_approaches = {
    "rtr": RetrieveThenReadApproach(search_client, AZURE_OPENAI_GPT_DEPLOYMENT, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT),
    "rrr": ReadRetrieveReadApproach(search_client, AZURE_OPENAI_GPT_DEPLOYMENT, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT),
    "rda": ReadDecomposeAsk(search_client, AZURE_OPENAI_GPT_DEPLOYMENT, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

document_approaches = {
    "rrr": ReadRetrieveDocumentReadApproach(search_client, sql_connector, AZURE_OPENAI_CHATGPT_DEPLOYMENT, AZURE_OPENAI_GPT_DEPLOYMENT, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

discharge_approaches = {
    "rrr": ReadRetrieveDischargeReadApproach(search_client, sql_connector, AZURE_OPENAI_CHATGPT_DEPLOYMENT, AZURE_OPENAI_GPT_DEPLOYMENT, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

chat_approaches = {
    "rrr": ChatReadRetrieveReadApproach(search_client, AZURE_OPENAI_CHATGPT_DEPLOYMENT, AZURE_OPENAI_GPT_DEPLOYMENT, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

chat_patient_approaches = {
    "rrr": ChatPatientReadRetrieveReadApproach(search_client, sql_connector, AZURE_OPENAI_CHATGPT_DEPLOYMENT, AZURE_OPENAI_GPT_DEPLOYMENT, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

get_patient_approaches = {
    "rrr": GetPatientApproach(sql_connector, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

get_patient_old_approaches = {
    "rrr": GetPatientOldApproach(sql_connector, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

get_history_index_approaches = {
    "rrr": GetHistoryIndexApproach(sql_connector, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

get_history_detail_approaches = {
    "rrr": GetHistoryDetailApproach(sql_connector, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

soap_approaches = {
    "get": GetSoapApproach(sql_connector, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

document_format_index_approaches = {
    "get": GetDocumentFormatIndexApproach(sql_connector, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT),
}

document_format_approaches = {
    "get": GetDocumentFormatApproach(sql_connector, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT),
    "upd": UpdateDocumentFormatApproach(sql_connector, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT),
    "del": DeleteDocumentFormatApproach(sql_connector, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

get_icd10_master_approaches = {
    "get": GetIcd10MasterApproach(sql_connector, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}

get_department_master_approaches = {
    "get": GetDepartmentMasterApproach(sql_connector, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}


app = Flask(__name__)

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def static_file(path):
    return app.send_static_file(path)

# Serve content files from blob storage from within the app to keep the example self-contained. 
# *** NOTE *** this assumes that the content files are public, or at least that all users of the app
# can access all the files. This is also slow and memory hungry.
@app.route("/content/<path>")
def content_file(path):
    blob = blob_container.get_blob_client(path).download_blob()
    mime_type = blob.properties["content_settings"]["content_type"]
    if mime_type == "application/octet-stream":
        mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    return blob.readall(), 200, {"Content-Type": mime_type, "Content-Disposition": f"inline; filename={path}"}
    
@app.route("/ask", methods=["POST"])
def ask():
    ensure_openai_token()
    approach = request.json["approach"]
    try:
        impl = ask_approaches.get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["question"], request.json.get("overrides") or {})
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /ask")
        return jsonify({"error": str(e)}), 500
    
@app.route("/document", methods=["POST"])
def document():
    ensure_openai_token()
    approach = request.json["approach"]
    try:
        impl = document_approaches.get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["document_name"], request.json["patient_code"], request.json.get("overrides") or {})
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /document")
        return jsonify({"error": str(e)}), 500
    
@app.route("/discharge", methods=["POST"])
def discharge():
    ensure_openai_token()
    approach = "rrr"
    try:
        impl = discharge_approaches.get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(
                     request.json["department_code"], 
                     request.json["pid"], 
                     request.json["document_format_index_id"], 
                     request.json["user_id"])
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /discharge")
        return jsonify({"error": str(e)}), 500
    
@app.route("/chat", methods=["POST"])
def chat():
    ensure_openai_token()
    approach = request.json["approach"]
    try:
        impl = chat_approaches.get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["history"], request.json.get("overrides") or {})
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /chat")
        return jsonify({"error": str(e)}), 500

@app.route("/chat_patient", methods=["POST"])
def chat_patient():
    ensure_openai_token()
    approach = request.json["approach"]
    try:
        impl = chat_patient_approaches.get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["history"], request.json["history_patient"], request.json.get("overrides") or {})
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /chat_patient")
        return jsonify({"error": str(e)}), 500

@app.route("/get_patient", methods=["POST"])
def get_patient():
    try:
        impl = get_patient_approaches.get("rrr")
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["pid"], request.json["department_code"])
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /get_patient")
        return jsonify({"error": str(e)}), 500

@app.route("/get_patient_old", methods=["POST"])
def get_patient_old():
    try:
        impl = get_patient_old_approaches.get("rrr")
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["patient_code"])
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /get_patient_old")
        return jsonify({"error": str(e)}), 500

@app.route("/get_history_index", methods=["POST"])
def get_history_index():
    try:
        impl = get_history_index_approaches.get("rrr")
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["document_name"])
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /get_history_index")
        return jsonify({"error": str(e)}), 500

@app.route("/get_history_detail", methods=["POST"])
def get_history_detail():
    try:
        impl = get_history_detail_approaches.get("rrr")
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["id"])
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /get_history_detail")
        return jsonify({"error": str(e)}), 500

@app.route("/soap", methods=["POST"])
def soap():
    try:
        impl = soap_approaches.get("get")
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["pid"])
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /soap")
        return jsonify({"error": str(e)}), 500

@app.route("/get_document_format_index", methods=["POST"])
def get_document_format_index():
    try:
        impl = document_format_index_approaches.get("get")
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["document_name"],
                     request.json["user_id"],
                     request.json["is_only_myself"],
                     request.json["search_text"])
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /get_document_format_index")
        return jsonify({"error": str(e)}), 500

@app.route("/get_document_format", methods=["POST"])
def get_document_format():
    try:
        impl = document_format_approaches.get("get")
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["document_format_index_id"])
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /get_document_format")
        return jsonify({"error": str(e)}), 500
    
@app.route("/update_document_format", methods=["POST"])
def update_document_format():
    try:
        impl = document_format_approaches.get("upd")
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["document_format_index_id"],
                     request.json["document_format_index_name"],
                     request.json["document_name"], 
                     request.json["tags"],
                     request.json["user_id"], 
                     request.json["system_contents"],
                     request.json["system_contents_suffix"],
                     request.json["document_formats"])
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /update_document_format")
        return jsonify({"error": str(e)}), 500

@app.route("/delete_document_format", methods=["POST"])
def delete_document_format():
    try:
        impl = document_format_approaches.get("del")
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["document_format_index_id"],
                     request.json["user_id"])
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /delete_document_format")
        return jsonify({"error": str(e)}), 500

def ensure_openai_token():
    if not is_openal_ad_auth:
        return
    global openai_token
    if openai_token.expires_on < int(time.time()) - 60:
        openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
        openai.api_key = openai_token.token
    
@app.route("/get_icd10_master", methods=["POST"])
def get_icd10_master():
    try:
        impl = get_icd10_master_approaches.get("get")
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["code_level"], request.json["parent_code"])
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /get_icd10_master")
        return jsonify({"error": str(e)}), 500
    
@app.route("/get_department_master", methods=["POST"])
def get_department_master():
    try:
        impl = get_department_master_approaches.get("get")
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run()
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /get_department_master")
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run()

