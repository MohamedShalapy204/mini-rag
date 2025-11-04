import streamlit as st
import requests
import json
import base64
import time
from io import BytesIO

# --- Third-party library for PDF reading (Requires 'pip install PyPDF2') ---
# We use a try-except block to handle cases where PyPDF2 might not be installed,
# allowing the app to still function for .txt files.
try:
    from PyPDF2 import PdfReader
    PDF_READER_AVAILABLE = True
except ImportError:
    PDF_READER_AVAILABLE = False
    st.warning("To process PDF files, please install PyPDF2: `pip install PyPDF2`")

# --- Configuration ---
# NOTE: The apiKey will be automatically injected by the environment if left as ""
API_KEY = "" # Leave this as-is; the platform will provide it at runtime.
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={API_KEY}"

# --- Helper Functions ---

def extract_text_from_file(uploaded_file):
    """Extracts text content from uploaded .txt or .pdf files."""
    file_extension = uploaded_file.name.split('.')[-1].lower()
    text = ""

    # .TXT file handling
    if file_extension == "txt":
        try:
            # Decode content as UTF-8
            text = uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.error(f"Error reading TXT file: {e}")

    # .PDF file handling (Requires PyPDF2)
    elif file_extension == "pdf":
        if PDF_READER_AVAILABLE:
            try:
                # Use BytesIO to read the uploaded file content in memory
                pdf_reader = PdfReader(BytesIO(uploaded_file.read()))
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            except Exception as e:
                st.error(f"Error processing PDF file: {e}")
        else:
            st.error("Cannot process PDF. PyPDF2 is not installed.")

    return text

def call_gemini_api(document_content, user_query):
    """Calls the Gemini API to get a summary based on the document and query."""
    
    # Check if we have enough content to send
    if not document_content or not user_query:
        return "Please upload documents and enter a question."

    # System instruction guides the model's behavior and role
    system_prompt = (
        "You are a highly efficient document analyst and summarization assistant. "
        "Your primary goal is to answer the user's question with a clear, concise, "
        "and accurate summary based *only* on the provided 'DOCUMENT CONTENT'. "
        "If the information required to answer the question is not present in the content, "
        "you MUST explicitly state, 'I could not find the answer in the provided documents.'"
    )

    # Combine the document content and the user's question into a single prompt
    full_prompt = (
        f"--- DOCUMENT CONTENT ---\n\n{document_content}\n\n"
        f"--- USER QUESTION ---\n\n{user_query}\n\n"
        "--- INSTRUCTIONS ---\n\nBased ONLY on the document content above, provide the summary or answer the question:"
    )

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
    }

    headers = {
        "Content-Type": "application/json"
    }
    
    # Retry logic (Exponential Backoff) for robustness
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            
            result = response.json()
            
            # Extract the text content
            text_result = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response generated.')
            return text_result

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1 and response.status_code in [429, 500, 503]:
                # Implement exponential backoff for retryable errors (429 Too Many Requests, 5xx server errors)
                wait_time = 2 ** attempt
                print(f"Attempt {attempt+1} failed ({response.status_code}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return f"An API error occurred after {attempt + 1} attempts: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
            
    return "Failed to get a response from the API after multiple retries."


# --- Streamlit UI ---

st.set_page_config(
    page_title="Gemini Document Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for a modern, clean look
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5em;
            font-weight: 700;
            color: #4B0082; /* Deep Purple */
            margin-bottom: 0.5em;
        }
        .stButton>button {
            background-color: #7B68EE; /* Medium Slate Blue */
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px 20px;
            transition: all 0.2s;
        }
        .stButton>button:hover {
            background-color: #6A5ACD; /* Slate Blue */
        }
        .stTextInput, .stFileUploader {
            border-radius: 10px;
            padding: 10px;
        }
        .summary-box {
            background-color: #f0f0f5; /* Light Grayish Blue */
            border-left: 5px solid #7B68EE;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            font-size: 1.1em;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📄 AI Document Assistant (RAG Demo)</div>', unsafe_allow_html=True)
st.subheader("Upload your documents and ask a content-specific question.")

# --- Sidebar for File Upload ---
with st.sidebar:
    st.header("1. Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload one or more .txt or .pdf files",
        type=["txt", "pdf"],
        accept_multiple_files=True,
        key="file_uploader"
    )

    st.header("2. Document Content")
    
    # Process files and store the combined content in session state
    document_content = ""
    if uploaded_files:
        with st.spinner("Processing files..."):
            all_text_chunks = []
            for file in uploaded_files:
                text = extract_text_from_file(file)
                if text:
                    all_text_chunks.append(f"--- START OF FILE: {file.name} ---\n{text}\n--- END OF FILE: {file.name} ---\n\n")

            document_content = "\n".join(all_text_chunks)
            st.session_state['document_content'] = document_content
            st.success(f"Successfully processed {len(uploaded_files)} file(s).")
    elif 'document_content' in st.session_state:
         # Clear content if files are removed
        del st.session_state['document_content']


    # Display a preview of the processed content (collapsed)
    if 'document_content' in st.session_state and st.session_state['document_content']:
        st.caption(f"Total characters: {len(st.session_state['document_content']):,}")
        with st.expander("View Processed Text Sample (First 1000 chars)"):
            st.code(st.session_state['document_content'][:1000] + ("..." if len(st.session_state['document_content']) > 1000 else ""), language='text')

# --- Main Area for Query and Result ---
if 'document_content' not in st.session_state or not st.session_state['document_content']:
    st.info("Please upload your document files in the sidebar to begin.")
else:
    st.header("3. Ask a Question")
    user_query = st.text_input(
        "What summary or specific information do you want from the uploaded documents?",
        placeholder="e.g., Summarize the key findings, or, What are the 5 main benefits listed?",
        key="user_query"
    )

    if st.button("Generate Summary / Answer"):
        if not user_query:
            st.error("Please enter a question to get a summary.")
        else:
            with st.spinner("Analyzing document and generating summary with Gemini..."):
                full_content = st.session_state['document_content']
                
                # Truncate content if it's too long for the model's context window.
                # A safe estimate is around 250,000 characters for Gemini Flash, 
                # but we'll cap it lower for robustness and faster response.
                MAX_CHARS = 150000 
                if len(full_content) > MAX_CHARS:
                    st.warning(f"Document content is very large ({len(full_content):,} chars). Truncating to the first {MAX_CHARS:,} characters for processing.")
                    full_content = full_content[:MAX_CHARS]
                
                # Call the LLM
                summary = call_gemini_api(full_content, user_query)
                st.session_state['summary_result'] = summary

    # Display the result
    if 'summary_result' in st.session_state:
        st.header("4. AI Response")
        st.markdown(f'<div class="summary-box">{st.session_state["summary_result"]}</div>', unsafe_allow_html=True)
        
        # Optional: Add a button to clear the result for a new query
        if st.button("Clear Result", key="clear_result_btn"):
            del st.session_state['summary_result']
            st.rerun
tr