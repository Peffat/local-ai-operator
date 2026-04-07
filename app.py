import streamlit as st
import os

from agent.planner import detect_intent
from agent.router import route
from tools.excel_tool import analyze_excel_with_ai

st.set_page_config(page_title="Local AI Operator", layout="wide")

MODEL = "gemma4:e2b"

# =========================
# SESSION STATE
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "file_path" not in st.session_state:
    st.session_state.file_path = None

if "last_mode" not in st.session_state:
    st.session_state.last_mode = None

if "last_task" not in st.session_state:
    st.session_state.last_task = None

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# =========================
# HEADER
# =========================
st.title("🤖 Local AI Operator")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("⚙️ Controls")

mode = st.sidebar.selectbox(
    "Mode",
    ["General Assistant", "Health Assistant", "Agri Advisor", "Smart Tools"]
)

if mode == "Smart Tools":
    task_options = [
        "Auto (AI decides)",
        "Excel Analysis (PDF report)",
        "Document/Image Analysis"
    ]
else:
    task_options = ["Auto (AI decides)"]

function = st.sidebar.selectbox("Task", task_options)

# =========================
# RESET LOGIC
# =========================
if st.session_state.last_mode != mode or st.session_state.last_task != function:
    st.session_state.chat_history = []
    st.session_state.file_path = None
    st.session_state.uploader_key += 1
    st.session_state.last_mode = mode
    st.session_state.last_task = function

# =========================
# CHART TYPE
# =========================
chart_type = "auto"

if mode == "Smart Tools" and function == "Excel Analysis (PDF report)":
    chart_type = st.sidebar.selectbox(
        "Chart Type",
        ["auto", "histogram", "boxplot", "heatmap"]
    )

# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader(
    "Upload file",
    type=["xlsx", "csv", "pdf", "docx", "png", "jpg", "jpeg"],
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_file:
    file_path = os.path.join("data", uploaded_file.name)

    os.makedirs("data", exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.session_state.file_path = file_path

    if uploaded_file.type.startswith("image"):
        st.image(uploaded_file, width="stretch")

# =========================
# CHAT DISPLAY
# =========================
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# INPUT
# =========================
user_input = st.chat_input("Ask something...")

if user_input:

    response = ""
    result = {}

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    file_path = st.session_state.file_path

    try:
        # =========================
        # EXCEL
        # =========================
        if mode == "Smart Tools" and function == "Excel Analysis (PDF report)" and file_path:

            result = analyze_excel_with_ai(
                file_path,
                model=MODEL,
                mode=mode,
                chart_type=chart_type,
                user_input=user_input
            )

            response = result.get("insights", "No insights generated.")

        else:
            if file_path and file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                intent = "document_analysis"
            else:
                plan = detect_intent(user_input)
                intent = plan["intent"]

            result = route(
                intent,
                user_input,
                file_path,
                MODEL,
                mode,
                history=st.session_state.chat_history
            )

            response = result.get("insights", "Something went wrong.")

    except Exception as e:
        response = f"⚠️ Error: {str(e)}"

    # =========================
    # SAVE CHAT
    # =========================
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.markdown(response)

        # 📄 REPORT PREVIEW + DOWNLOAD
        if result.get("report"):
            preview_text = response.split("\n")[:3]
            if preview_text:
                st.markdown("**Report preview:**")
                for line in preview_text:
                    if line.strip():
                        st.markdown(line)

            with open(result["report"], "rb") as f:
                st.download_button(
                    "📥 Download Report",
                    f,
                    os.path.basename(result["report"])
                )

        # 📊 CLEAN DATA DOWNLOAD
        if result.get("cleaned_file"):
            with open(result["cleaned_file"], "rb") as f:
                st.download_button(
                    "📥 Download Cleaned Data",
                    f,
                    os.path.basename(result["cleaned_file"])
                )