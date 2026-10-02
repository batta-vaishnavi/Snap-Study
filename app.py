import streamlit as st
from google import genai
from google.genai import types
import requests

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    EXPLAIN_PROMPT,
    NOTES_PROMPT,
    QUIZ_PROMPT,
    EXAM_PROMPT,
    SUMMARY_REQUEST_PROMPT,
)


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚",
    layout="centered",
)


# ==================================================
# SIMPLE UI STYLING
# ==================================================

st.markdown(
    """
    <style>
        .block-container {
            max-width: 900px;
            padding-top: 2rem;
            padding-bottom: 6rem;
        }

        h1 {
            margin-bottom: 0.2rem;
        }

        .subtitle {
            color: #6b7280;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# GEMINI CONFIG
# ==================================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

MODEL_NAME = "gemini-3.5-flash-lite"


# ==================================================
# TELEGRAM CONFIG
# ==================================================

TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]


# ==================================================
# GEMINI CLIENT
# ==================================================

@st.cache_resource
def get_gemini_client():
    return genai.Client(
        api_key=GEMINI_API_KEY
    )


gemini_client = get_gemini_client()


# ==================================================
# SESSION STATE
# ==================================================

if "onboarded" not in st.session_state:
    st.session_state.onboarded = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_image_bytes" not in st.session_state:
    st.session_state.last_image_bytes = None

if "last_image_type" not in st.session_state:
    st.session_state.last_image_type = None

if "last_image_name" not in st.session_state:
    st.session_state.last_image_name = None


# ==================================================
# GEMINI FUNCTION
# ==================================================

def ask_gemini(parts):

    try:

        response = st.session_state.chat.send_message(
            parts
        )

        return response.text

    except Exception as error:

        return (
            "⚠️ I couldn't generate a response right now.\n\n"
            f"Error: {error}"
        )


# ==================================================
# TELEGRAM FUNCTION
# ==================================================

def send_to_telegram(message):

    try:

        url = (
            f"https://api.telegram.org/"
            f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        )

        response = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
            },
            timeout=10,
        )

        if response.ok:

            return (
                True,
                "Study summary sent to Telegram! ✅"
            )

        return False, response.text

    except Exception as error:

        return False, str(error)


# ==================================================
# MESSAGE DISPLAY
# ==================================================

def render_message(message):

    with st.chat_message(message["role"]):

        if message.get("image_bytes"):

            st.image(
                message["image_bytes"],
                caption=message.get(
                    "image_name",
                    "Uploaded study material"
                ),
                width="stretch",
            )

        if message.get("content"):

            st.markdown(
                message["content"]
            )


# ==================================================
# ADD MESSAGE
# ==================================================

def add_message(
    role,
    content,
    image_bytes=None,
    image_name=None,
):

    message = {
        "role": role,
        "content": content,
        "image_bytes": image_bytes,
        "image_name": image_name,
    }

    st.session_state.messages.append(
        message
    )

    render_message(message)


# ==================================================
# ONBOARDING
# ==================================================

if not st.session_state.onboarded:

    st.title("📚 Snap & Study")

    st.markdown(
        '<div class="subtitle">'
        "Your AI-powered study buddy"
        "</div>",
        unsafe_allow_html=True,
    )

    st.info(
        "Upload your notes, textbook pages, questions "
        "or diagrams and let AI help you understand "
        "and revise them."
    )

    st.write("### Let's get started 👋")

    with st.form("onboarding_form"):

        name = st.text_input(
            "Your name",
            placeholder="Enter your name",
        )

        submitted = st.form_submit_button(
            "Start Studying 🚀",
            use_container_width=True,
        )

    if submitted:

        if not name.strip():

            st.warning(
                "Please enter your name."
            )

        else:

            st.session_state.name = (
                name.strip()
            )

            st.session_state.chat = (
                gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    ),
                )
            )

            st.session_state.messages = []

            st.session_state.onboarded = True

            st.rerun()

    st.stop()


# ==================================================
# MAIN HEADER
# ==================================================

st.title("📚 Snap & Study")

st.markdown(
    f'<div class="subtitle">'
    f"Hey {st.session_state.name} 👋 "
    "What are we learning today?"
    "</div>",
    unsafe_allow_html=True,
)


# ==================================================
# QUICK STUDY TOOLS
# ==================================================

st.write("### ⚡ Quick Study Tools")

col1, col2, col3, col4 = st.columns(4)


with col1:

    explain_clicked = st.button(
        "💡 Explain",
        use_container_width=True,
    )


with col2:

    notes_clicked = st.button(
        "📝 Notes",
        use_container_width=True,
    )


with col3:

    quiz_clicked = st.button(
        "❓ Quiz",
        use_container_width=True,
    )


with col4:

    exam_clicked = st.button(
        "🎯 Exam Answer",
        use_container_width=True,
    )


# ==================================================
# WELCOME MESSAGE / CHAT HISTORY
# ==================================================

if not st.session_state.messages:

    welcome_message = (
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        )
    )

    add_message(
        "assistant",
        welcome_message,
    )

else:

    for message in st.session_state.messages:

        render_message(message)


# ==================================================
# QUICK ACTION HANDLER
# ==================================================

quick_prompt = None


if explain_clicked:

    quick_prompt = EXPLAIN_PROMPT


elif notes_clicked:

    quick_prompt = NOTES_PROMPT


elif quiz_clicked:

    quick_prompt = QUIZ_PROMPT


elif exam_clicked:

    quick_prompt = EXAM_PROMPT


if quick_prompt:

    add_message(
        "user",
        quick_prompt,
    )

    parts = [
        quick_prompt
    ]

    # Reuse latest uploaded image
    if st.session_state.last_image_bytes:

        image_part = types.Part.from_bytes(
            data=st.session_state.last_image_bytes,
            mime_type=st.session_state.last_image_type,
        )

        parts.append(
            image_part
        )

    with st.spinner(
        "Studying with you..."
    ):

        answer = ask_gemini(
            parts
        )

    add_message(
        "assistant",
        answer,
    )


# ==================================================
# STUDY SUMMARY
# ==================================================

st.divider()

st.write("### 📲 Study Summary")

st.caption(
    "Generate a summary of your study session "
    "and send it directly to your Telegram."
)


if st.button(
    "Generate & Send Summary to Telegram",
    use_container_width=True,
):

    with st.spinner(
        "Preparing your study summary..."
    ):

        summary = ask_gemini(
            [
                SUMMARY_REQUEST_PROMPT
            ]
        )

    if summary:

        success, message = (
            send_to_telegram(summary)
        )

        if success:

            st.success(
                message
            )

        else:

            st.error(
                "Could not send the summary "
                "to Telegram."
            )


# ==================================================
# CHAT INPUT + IMAGE UPLOAD
# ==================================================

user_input = st.chat_input(
    "Ask a study question or upload an image...",
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png",
    ],
)


# ==================================================
# PROCESS USER INPUT
# ==================================================

if user_input:

    text = user_input.text.strip()

    uploaded_files = user_input.files

    photo = None


    if uploaded_files:

        photo = uploaded_files[0]


    # ----------------------------------------------
    # IMAGE INFORMATION
    # ----------------------------------------------

    image_bytes = None
    image_type = None
    image_name = None


    if photo:

        image_bytes = photo.getvalue()

        image_name = photo.name

        image_type = photo.type


        # Fix MIME type if browser doesn't provide it
        if (
            not image_type
            or not image_type.startswith(
                "image/"
            )
        ):

            extension = (
                photo.name
                .lower()
                .split(".")[-1]
            )


            if extension in [
                "jpg",
                "jpeg",
            ]:

                image_type = "image/jpeg"


            elif extension == "png":

                image_type = "image/png"


            else:

                image_type = "image/jpeg"


        # Save latest image
        st.session_state.last_image_bytes = (
            image_bytes
        )

        st.session_state.last_image_type = (
            image_type
        )

        st.session_state.last_image_name = (
            image_name
        )


    # ----------------------------------------------
    # USER MESSAGE
    # ----------------------------------------------

    if text:

        user_message = text


    elif photo:

        user_message = (
            f"📷 Uploaded: **{image_name}**"
        )


    else:

        user_message = ""


    if user_message or photo:

        add_message(
            "user",
            user_message,
            image_bytes=image_bytes,
            image_name=image_name,
        )


    # ----------------------------------------------
    # SEND TO GEMINI
    # ----------------------------------------------

    parts = []


    if text:

        parts.append(
            text
        )


    elif photo:

        parts.append(
            "Analyze this study material. "
            "Identify the topic, explain the "
            "important concepts in simple language, "
            "highlight key points, and mention "
            "important exam points."
        )


    if photo:

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=image_type,
        )

        parts.append(
            image_part
        )


    # ----------------------------------------------
    # GEMINI RESPONSE
    # ----------------------------------------------

    if parts:

        with st.spinner(
            "Thinking..."
        ):

            answer = ask_gemini(
                parts
            )

        add_message(
            "assistant",
            answer,
        )