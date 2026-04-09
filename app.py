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
    ["General Assistant", "Data Analysis", "Health Assistant", "Agri Advisor"]
)

if mode == "Data Analysis":
    task_options = [
        "Auto (AI decides)",
        "Data Analysis (PDF report)",
        "Document/Image Analysis"
    ]
else:
    task_options = ["Auto (AI decides)"]

function = st.sidebar.selectbox("Task", task_options)

# =========================
# DISCLAIMERS
# =========================
if mode == "Health Assistant":
    st.warning(
        "**Medical Disclaimer**: AI analysis is NOT a substitute for professional medical advice. "
        "Always verify any health-related insights with a licensed healthcare provider before taking action. "
        "For emergencies, contact medical professionals immediately.",
        icon="⚠️"
    )
elif mode == "Agri Advisor":
    st.warning(
        "**Agricultural Disclaimer**: These recommendations are AI-generated insights only. "
        "Consult with agricultural experts or local specialists before implementing any practices. "
        "Results vary by region, climate, and soil conditions.",
        icon="🌾"
    )
else:
    st.info(
        "**General Advisory**: AI responses should always be verified independently. "
        "Do not rely solely on this system for critical decisions.",
        icon="ℹ️"
    )

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

status_area = st.empty()
progress_bar = st.progress(0)

if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_response" not in st.session_state:
    st.session_state.last_response = ""
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

response = ""
result = {}

if user_input:

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    file_path = st.session_state.file_path

    def progress_callback(message, percent=None):
        if percent is not None:
            progress_bar.progress(min(max(int(percent), 0), 100))
        status_area.info(message)

    try:
        # =========================
        # EXCEL
        # =========================
        if mode == "Data Analysis" and function == "Data Analysis (PDF report)" and file_path:

            with st.spinner("Running data analysis..."):
                result = analyze_excel_with_ai(
                    file_path,
                    model=MODEL,
                    mode=mode,
                    chart_type=chart_type,
                    user_input=user_input,
                    progress_callback=progress_callback
                )

            if result.get("status") == "error":
                response = f"⚠️ Error: {result.get('message', 'Analysis failed without details')}"
                status_area.error(response)
                progress_bar.progress(0)
            else:
                response = result.get("insights") or "No insights generated."
                status_area.success("Data analysis complete. Your report is ready for download.")
                progress_bar.progress(100)

            report_mode = True

        else:
            report_mode = False
            if file_path and file_path.lower().endswith((".png", ".jpg", ".jpeg", ".pdf", ".docx", ".xlsx", ".xls", ".csv")):
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

    st.session_state.last_result = result
    st.session_state.last_response = response
    st.session_state.last_user_input = user_input

    # =========================
    # SAVE CHAT
    # =========================
    if not (mode == "Data Analysis" and function == "Data Analysis (PDF report)" and file_path):
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

    if not (mode == "Data Analysis" and function == "Data Analysis (PDF report)" and file_path):
        with st.chat_message("assistant"):
            st.markdown(response.replace("\n", "  \n"))

# Persist downloads and report preview after reruns
display_result = result if result else st.session_state.last_result
display_response = response if response else st.session_state.last_response

if (mode == "Data Analysis" and function == "Data Analysis (PDF report)") and display_result and (display_result.get("report") or display_result.get("cleaned_file")):
    st.markdown("**Downloads:**")
    col1, col2 = st.columns(2)

    if display_result.get("report"):
        with open(display_result["report"], "rb") as f:
            report_data = f.read()
        col1.download_button(
            "📥 Download Report",
            report_data,
            os.path.basename(display_result["report"]),
            key="download_report"
        )

    if display_result.get("cleaned_file"):
        with open(display_result["cleaned_file"], "rb") as f:
            cleaned_data = f.read()
        col2.download_button(
            "📥 Download Cleaned Data",
            cleaned_data,
            os.path.basename(display_result["cleaned_file"]),
            key="download_cleaned"
        )

    if display_result.get("report"):
        preview_text = "\n".join(display_response.split("\n")[:8]).strip()
        if preview_text:
            st.markdown("**Report preview:**")
            st.text(preview_text)