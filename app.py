import streamlit as st
import PyPDF2
from docx import Document
import re
import os

from google import genai


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Study with Subha",
    page_icon="🎓",
    layout="wide"
)


# =====================================================
# DARK THEME
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #212121;
    color: white;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #bbbbbb;
    font-size: 18px;
    margin-bottom: 30px;
}

.info-box {
    background-color: #303030;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# GEMINI SETTINGS
# =====================================================
model = genai.GenerativeModel("models/gemini-3.8-flash")



def get_api_key():

    try:
        return st.secrets["GEMINI_API_KEY"]

    except Exception:

        return os.getenv("GEMINI_API_KEY")


def get_gemini_client():

    api_key = get_api_key()

    if not api_key:
        return None

    try:
        return genai.Client(api_key=api_key)

    except Exception:
        return None


# =====================================================
# SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []

if "chunks" not in st.session_state:
    st.session_state.chunks = []


# =====================================================
# TEXT CLEANING
# =====================================================

def clean_text(text):

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =====================================================
# PDF EXTRACTION
# =====================================================

def extract_pdf(uploaded_file):

    text = ""

    try:

        reader = PyPDF2.PdfReader(uploaded_file)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

    except Exception as e:

        return f"PDF reading error: {e}"

    return clean_text(text)


# =====================================================
# DOCX EXTRACTION
# =====================================================

def extract_docx(uploaded_file):

    text = ""

    try:

        document = Document(uploaded_file)

        for paragraph in document.paragraphs:

            if paragraph.text.strip():

                text += paragraph.text + "\n"

    except Exception as e:

        return f"DOCX reading error: {e}"

    return clean_text(text)


# =====================================================
# TXT EXTRACTION
# =====================================================

def extract_txt(uploaded_file):

    try:

        return clean_text(
            uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )
        )

    except Exception as e:

        return f"TXT reading error: {e}"


# =====================================================
# FILE EXTRACTION
# =====================================================

def extract_file(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):

        return extract_pdf(uploaded_file)

    elif file_name.endswith(".docx"):

        return extract_docx(uploaded_file)

    elif file_name.endswith(".txt"):

        return extract_txt(uploaded_file)

    return ""


# =====================================================
# CREATE TEXT CHUNKS
# =====================================================

def create_chunks(
    text,
    chunk_size=1200,
    overlap=200
):

    if not text:

        return []

    chunks = []

    start = 0

    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:

            chunks.append(chunk)

        start = end - overlap

    return chunks


# =====================================================
# RETRIEVE RELEVANT CHUNKS
# =====================================================

def retrieve_relevant_chunks(
    question,
    chunks,
    top_k=5
):

    if not chunks:

        return []

    question_words = set(
        re.findall(
            r"\b[a-zA-Z0-9]+\b",
            question.lower()
        )
    )

    scored_chunks = []

    for chunk in chunks:

        chunk_words = set(
            re.findall(
                r"\b[a-zA-Z0-9]+\b",
                chunk.lower()
            )
        )

        score = len(
            question_words.intersection(
                chunk_words
            )
        )

        scored_chunks.append(
            (score, chunk)
        )

    scored_chunks.sort(
        key=lambda x: x[0],
        reverse=True
    )

    selected = [
        chunk
        for score, chunk in scored_chunks[:top_k]
        if score > 0
    ]

    if not selected:

        selected = chunks[:top_k]

    return selected


# =====================================================
# ASK GEMINI
# =====================================================

def ask_gemini(question, context):

    client = get_gemini_client()

    if client is None:

        return """
⚠️ Gemini API is not connected.

Please add GEMINI_API_KEY in
Streamlit Cloud → Settings → Secrets.
"""

    system_prompt = """
You are Study with Subha, an AI study assistant.

Your job is to help students understand their study materials.

Rules:

1. Give simple and clear answers.
2. If the user asks in Bengali, answer in Bengali.
3. If the user asks in English, answer in simple English.
4. For exams, provide easy exam-ready answers.
5. Use the provided study material when relevant.
6. Do not invent information that is not supported by the material.
7. If the answer is not available in the material, clearly say that.
8. Use headings and bullet points when useful.
9. Keep explanations suitable for a college student.
"""

    user_prompt = f"""
{system_prompt}

STUDY MATERIAL:

{context}

STUDENT QUESTION:

{question}

Answer the student's question clearly.
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_prompt
        )

        if response.text:

            return response.text

        return "Sorry, I could not generate an answer."

    except Exception as e:

        return f"""
⚠️ AI error occurred.

Please check your Gemini API key and
Streamlit Cloud settings.

Error:
{e}
"""


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("🎓 Study with Subha")

    st.write(
        "Your personal AI study assistant."
    )

    st.divider()

    if st.button(
        "🆕 New Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.subheader("📚 Upload Study Material")

    uploaded_files = st.file_uploader(
        "Upload PDF, TXT or DOCX",
        type=[
            "pdf",
            "txt",
            "docx"
        ],
        accept_multiple_files=True
    )

    if uploaded_files:

        st.session_state.documents = []

        st.session_state.chunks = []

        for uploaded_file in uploaded_files:

            text = extract_file(
                uploaded_file
            )

            if text:

                chunks = create_chunks(text)

                st.session_state.documents.append(
                    uploaded_file.name
                )

                st.session_state.chunks.extend(
                    chunks
                )

        st.success(
            f"{len(st.session_state.documents)} "
            f"file(s) loaded."
        )

    st.divider()

    st.subheader("🤖 AI Status")

    api_key = get_api_key()

    if api_key:

        st.success(
            "Gemini API connected"
        )

    else:

        st.error(
            "Gemini API key missing"
        )

    st.caption(
        f"Model: {MODEL_NAME}"
    )


# =====================================================
# MAIN PAGE
# =====================================================

st.markdown(
    '<div class="main-title">'
    '🎓 Study with Subha'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your AI Study Assistant'
    '</div>',
    unsafe_allow_html=True
)


# =====================================================
# INFORMATION BOX
# =====================================================

if not st.session_state.messages:

    st.markdown("""
    <div class="info-box">

    👋 <b>Welcome!</b>

    <br><br>

    📚 Upload your study material from the sidebar.

    <br>

    🤖 Ask questions about your notes.

    <br>

    ✍️ Get simple exam-ready answers.

    <br>

    🌐 You can ask questions in English or Bengali.

    </div>
    """, unsafe_allow_html=True)


# =====================================================
# CHAT HISTORY
# =====================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =====================================================
# CHAT INPUT
# =====================================================

question = st.chat_input(
    "Ask your study question..."
)


if question:

    # -------------------------------------------------
    # USER QUESTION
    # -------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)


    # -------------------------------------------------
    # RETRIEVE STUDY MATERIAL
    # -------------------------------------------------

    relevant_chunks = retrieve_relevant_chunks(
        question,
        st.session_state.chunks,
        top_k=5
    )


    # -------------------------------------------------
    # CREATE CONTEXT
    # -------------------------------------------------

    if relevant_chunks:

        context = "\n\n".join(
            relevant_chunks
        )

    else:

        context = (
            "No study material has been uploaded."
        )


    # -------------------------------------------------
    # GENERATE AI ANSWER
    # -------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            answer = ask_gemini(
                question,
                context
            )

            st.markdown(answer)


    # -------------------------------------------------
    # SAVE ANSWER
    # -------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
