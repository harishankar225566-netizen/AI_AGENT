import streamlit as st
from huggingface_hub import InferenceClient
from pypdf import PdfReader
from dotenv import load_dotenv

import os
# Load .env from project root (same folder as requirements.txt)
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    st.error("HF_TOKEN missing. Create a .env file in project root and set HF_TOKEN.")
    st.stop()

os.environ["HF_TOKEN"] = HF_TOKEN
client = InferenceClient(token=HF_TOKEN)
# ----------------------------
# Function to Extract Text
# ----------------------------
def extract_text(file):
    text = ""

    if file.type == "application/pdf":
        pdf_reader = PdfReader(file)

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

    elif file.type == "text/plain":
        text = file.read().decode("utf-8")

    return text


def get_ai_response(prompt, max_tokens=800):
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(
            "The AI request failed. This is usually caused by an expired or invalid Hugging Face token. "
            f"Details: {e}"
        )
        return None

# Streamlit Config
# ---------------------------
st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🚀",
    layout="wide"
)

# ---------------------------
# CSS
# ---------------------------
st.markdown("""
<style>

.hero {
    padding:20px;
    border-radius:15px;
    background: linear-gradient(90deg,#6A11CB,#2575FC);
    color:white;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("🚀 AI Career Assistant")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Career Roadmap",
        "Placement Predictor",
        "Interview Generator",
        "Resume Analyzer"
    ]
)

# ---------------------------
# Dashboard
# ---------------------------
if page == "Dashboard":

    st.markdown("""
    <div class='hero'>
    <h1>🚀 AI Career Assistant</h1>
    <h3>Your Personal AI Career Mentor</h3>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Skills Analyzed", "120")

    with col2:
        st.metric("Jobs Matched", "45")

    with col3:
        st.metric("Interview Questions", "350")

    st.write("---")

    st.subheader("💬 Career Chat")

    question = st.text_input("Ask Anything")

    if st.button("Send"):

        with st.spinner("Thinking..."):
            answer = get_ai_response(question, max_tokens=800)
            if answer:
                st.write(answer)

# ---------------------------
# Career Roadmap
# ---------------------------
elif page == "Career Roadmap":

    st.title("🎯 Career Roadmap")

    goal = st.text_input("Enter Career Goal")

    if st.button("Generate Roadmap"):

        with st.spinner("Generating Roadmap..."):
            prompt = f"""
            Create a complete roadmap for becoming a {goal}.

            Include:
            - Skills
            - Technologies
            - Learning Path
            - Projects
            - Certifications
            - Interview Preparation
            """

            roadmap = get_ai_response(prompt, max_tokens=1200)
            if roadmap:
                st.write(roadmap)

# ---------------------------
# Placement Predictor
# ---------------------------
elif page == "Placement Predictor":

    st.title("📊 Placement Predictor")

    cgpa = st.slider(
        "CGPA",
        0.0,
        10.0,
        7.0
    )

    skills = st.text_input(
        "Skills (Python, SQL, ML...)"
    )

    if st.button("Predict"):

        if cgpa >= 8:
            st.success("High Placement Chance")
        elif cgpa >= 6:
            st.warning("Moderate Placement Chance")
        else:
            st.error("Need Improvement")

        prompt = f"""
        Student CGPA: {cgpa}
        Skills: {skills}

        Give placement advice.
        """

        advice = get_ai_response(prompt, max_tokens=500)
        if advice:
            st.write(advice)

# ---------------------------
# Interview Generator
# ---------------------------
elif page == "Interview Generator":

    st.title("🎤 Interview Questions")

    tech = st.text_input("Technology")

    if st.button("Generate"):

        with st.spinner(
            "Generating Questions..."
        ):
            prompt = f"""
            Generate 10 interview questions
            with answers for {tech}.
            """

            result = get_ai_response(prompt, max_tokens=1500)
            if result:
                st.write(result)



# ----------------------------
# Resume Analyzer Page
# ----------------------------
elif page == "Resume Analyzer":

    st.title("📄 ATS Resume Analyzer")

    file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "txt"]
    )

    job_description = st.text_area(
        "Paste Job Description",
        height=200
    )

    if file:

        st.success("Resume Uploaded Successfully")

        # Extract Resume Text
        resume_text = extract_text(file)

        if st.button("Analyze Resume"):

            with st.spinner("Analyzing Resume..."):

                prompt = f"""
                You are an expert ATS Resume Scanner.

                Compare the Resume with the Job Description and provide:

                ## ATS Match Score
                Give score out of 100.

                ## Matching Skills
                List all matching skills.

                ## Missing Skills
                List skills present in JD but missing in resume.

                ## Missing Keywords
                Important ATS keywords missing from resume.

                ## Resume Strengths
                Strong points of resume.

                ## Resume Weaknesses
                Areas that need improvement.

                ## Resume Improvement Suggestions
                Give actionable recommendations.

                ## Interview Readiness
                Evaluate readiness for this role.

                Resume:
                {resume_text}

                Job Description:
                {job_description}
                """

                analysis = get_ai_response(prompt, max_tokens=1500)

                if analysis:
                    st.subheader("📊 Analysis Report")
                    st.write(analysis)

                st.subheader("📄 Resume Preview")

                st.text_area(
                    "Extracted Resume Text",
                    resume_text,
                    height=300
                )