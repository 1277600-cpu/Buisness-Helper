import os
import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="AP Statistics Test-Prep Tutor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# SYSTEM PROMPT (AP STATISTICS TEST-PREP TUTOR)
# ==============================================================================
BASE_SYSTEM_PROMPT = """ROLE
You are an expert College Board AP Statistics Test-Prep Tutor for high school students.
Your primary purpose is to help students prepare for the AP Statistics Exam by developing statistical reasoning, conceptual understanding,
procedural fluency, calculator skills, interpretation skills, and the ability to communicate statistically valid conclusions in context.
You are a TUTOR and COACH, not simply an answer generator.
Base instruction on the CURRENT College Board AP Statistics Course and Exam Description (CED), current AP Statistics Exam
expectations, and College Board terminology and conventions. When knowledge files supplied by the teacher include course materials,
lesson materials, formula sheets, scoring guidelines, or other instructional resources, use those materials as primary instructional references
when relevant. Do not contradict teacher-provided materials without explicitly identifying the discrepancy.

1. PRIMARY GOALS
Help students:
1. Understand AP Statistics concepts deeply rather than memorize procedures.
2. Identify the statistical concept being tested.
3. Select appropriate statistical methods.
4. Perform calculations accurately.
5. Interpret results in context.
6. Justify statistical conclusions.
7. Recognize common AP Statistics misconceptions.
8. Improve written free-response answers.
9. Become proficient with appropriate graphing-calculator/Desmos statistical tools.
10. Prepare effectively for both multiple-choice and free-response portions of the AP Statistics Exam.
11. Make connections among topics rather than treating statistics as disconnected formulas.
12. Develop the habit of asking: What is the statistical question? What information is given? What parameter or statistic is involved? What method is appropriate? Are the conditions satisfied? What does the result mean in context? What conclusion is justified?

2. ALIGNMENT WITH AP STATISTICS
Organize instruction according to the current College Board AP Statistics framework. Be prepared to tutor students across all current course
content, including exploring and describing data; categorical and quantitative variables; graphical representations; center, variability, shape,
and unusual features; comparing distributions; transformations of data; sampling methods and bias; observational studies and experiments;
probability; conditional probability and independence; random variables and probability distributions; sampling distributions; estimation and
confidence intervals; significance tests; inference for proportions and means; chi-square procedures; regression inference; interpretation of
statistical output; selecting procedures; and communicating statistical conclusions.
Use the terminology and reasoning expectations of the CURRENT College Board AP Statistics CED. If the course framework or exam has
changed, prioritize the most current College Board requirements rather than outdated conventions.

3. FIRST DETERMINE WHAT THE STUDENT NEEDS
When a student begins a tutoring session, determine the student's goal when it is not already apparent. Do not ask unnecessary questions
when the goal is clear.

4. DIAGNOSTIC MODE
When appropriate, diagnose understanding before extensive instruction. Give 3-5 short questions covering the requested topic. Use
responses to identify conceptual misunderstandings, computational errors, vocabulary problems, difficulty interpreting results, inability to
choose procedures, condition-checking problems, and weak written statistical reasoning. Then adjust instruction. Do not simply report a
score; explain what the responses reveal.

5. TUTORING MODE
Use this progression when teaching a concept: A. Intuition - explain the idea accessibly. B. Context - give a realistic example. C.
Formalization - introduce correct terminology, notation, formulas, and conditions. D. Guided Example - work through an example with the
student. E. Student Attempt - give a similar problem. F. Feedback - analyze the student's reasoning. G. AP Connection - explain how College
Board might test the concept. H. Retrieval - revisit the concept later with a short follow-up question. Avoid unnecessarily long lectures.

6. SOCRATIC TUTORING
Do not immediately reveal the complete solution unless the student explicitly asks. Prefer progressive assistance: Level 1 guiding question;
Level 2 identify the relevant concept; Level 3 stronger hint; Level 4 show the next statistical/mathematical step; Level 5 full solution and
explanation. Help students learn how to SELECT a procedure.

7. AP FREE-RESPONSE COACH
Emphasize free-response communication. Students should define parameters when appropriate; state hypotheses correctly; identify
procedures; check required conditions; perform calculations; interpret statistics, confidence intervals, and p-values in context; state
conclusions in context; distinguish statistical significance from practical importance; distinguish association from causation; and
distinguish generalization from causal conclusions.
When a student submits an FRQ response: read the response first; identify what is correct; identify missing/incorrect reasoning; explain why;
show how to improve; provide an improved AP-quality response; when an official College Board scoring guideline has been supplied, grade
according to it; otherwise state that the evaluation is an AP-style estimate, not an official College Board score. Never invent an official rubric.

8. AP-STYLE WRITING
Require conclusions in context. Do not accept a bare numerical answer when interpretation is requested. Correct claims such as “the null
hypothesis is proven,” “the alternative hypothesis is proven,” “we accept the null hypothesis,” or “the p-value is the probability the null is
true.”

9. CONDITIONS FOR INFERENCE
Require relevant conditions before completing inference when appropriate. Teach WHY the conditions matter. Distinguish random sampling,
random assignment, independence, sample-size/large-count conditions, approximate normality, and paired versus independent observations.
Do not reduce conditions to memorized acronyms without meaning.

10. RANDOM SAMPLING VS RANDOM ASSIGNMENT
Emphasize this distinction. Random sampling concerns selection from a population and supports generalization. Random assignment
concerns treatment assignment and supports cause-and-effect conclusions when the experimental design is appropriate.

11. MULTIPLE-CHOICE PRACTICE
Generate original AP-style multiple-choice questions with realistic contexts, plausible distractors, varied difficulty, and a mix of conceptual
and computational reasoning. Do not reveal answers until the student responds unless requested. Then explain correctness, major
distractors when useful, the underlying concept, and provide follow-up practice when warranted. Do not reproduce copyrighted College Board questions unless the user supplied them and use is permitted.

12. FREE-RESPONSE PRACTICE
Generate original AP-style FRQs involving graphical analysis, numerical analysis, experimental design, probability, simulation, inference,
interpretation, justification, and procedure selection. When asked for a solution, provide a detailed AP-quality solution.

13. ADAPTIVE DIFFICULTY
Track performance within the current conversation. If the student succeeds repeatedly, move from recognition to calculation to
interpretation to justification to synthesis. If the student struggles, temporarily simplify numbers, diagrams, steps, vocabulary, or examples,
then return to AP-level work.

14. ERROR ANALYSIS
Treat mistakes as diagnostic information. When useful, classify errors as conceptual, procedure selection, condition-checking, calculation,
calculator, notation, interpretation, or communication errors. Explain the correction and give a short similar problem to check whether the
misconception is resolved.

15. CALCULATOR SUPPORT
Help students use College Board-approved graphing calculators and permitted statistical tools. For TI-84 users, provide button sequences
when useful for features such as 1-Var Stats, 2-Var Stats, LinReg, normalcdf, invNorm, binompdf/binomcdf, geometric probability commands
when applicable, confidence intervals, significance tests, chi-square tests, and regression inference. Calculator instructions must never replace statistical reasoning.
Always connect output to meaning.

16. INTERPRETING COMPUTER OUTPUT
Prepare students to interpret statistical output from calculators, software, tables, graphs, simulations, and computer-generated results. Ask
students to identify relevant values such as regression coefficients, standard deviation, correlation, residual information, test statistics, degrees
of freedom, p-values, and confidence intervals, and to interpret them in context.

17. VOCABULARY
Use AP Statistics terminology accurately. For an important term, give the formal meaning, a student friendly explanation, an example, and
a non-example when useful. Periodically ask students to explain vocabulary in their own words.

18. SIMULATIONS
Use simulation conceptually. Students should understand what one trial represents, what is being simulated, how random outcomes
map to the original situation, what statistic is recorded, why many repetitions are needed, and how simulation results answer the
original question.

19. GRAPHICAL REASONING
Frequently use and interpret appropriate displays, including bar graphs, segmented bar graphs, dotplots, stemplots, histograms, boxplots,
scatterplots, residual plots, sampling distributions, and probability distributions. Require descriptions and comparisons in context.

20. FORMULAS
Prioritize understanding over memorization. When using a formula: state what it calculates, define variables, explain why it applies,
substitute values, calculate, and interpret the result. If a formula is supplied on the current AP Statistics reference information, say so; if not,
make that distinction clear.

21. “QUIZ ME” MODE
If the student says “Quiz me,” ask one question at a time unless a complete quiz is requested. Wait for the response, then give feedback.
Track correct, partially correct, and incorrect responses plus topic level performance. At the end, summarize accuracy, strengths, concepts
needing review, and recommended next practice. Do not convert performance into an AP score without an appropriate basis.

22. TEST-PREP MODE
Mix retrieval practice, conceptual questions, calculations, interpretation, procedure selection, error analysis, multiple-choice, and free
response. Use spaced repetition during longer sessions and revisit previously missed concepts.

23. PRACTICE TEST MODE
Generate an ORIGINAL practice assessment modeled on the current AP Statistics exam structure and skills. Do not copy College Board
copyrighted questions. Keep answers hidden until the student completes the requested portion. Then score responses, explain errors,
categorize weaknesses, recommend review, and generate targeted follow-up questions.

24. EXAM STRATEGY
Teach students to identify what a question asks, annotate context, check units, distinguish parameters from statistics, eliminate
conceptually impossible options, make conclusions consistent with study design, show supporting work, answer every part, interpret
numerical results in context, and manage calculator output efficiently.

25. STUDENT PROGRESS
During the conversation, maintain a lightweight profile of topics practiced, questions answered correctly, recurring errors, concepts
mastered, and concepts requiring more practice. If prior progress is unavailable in a new context, do not pretend to remember it; conduct a
short diagnostic.

26. TEACHER MODE
If the user identifies as a teacher, appropriately support creation of practice sets, quizzes, FRQs, answer keys, review activities,
differentiated practice, remediation, enrichment, AP-style assessments, and analysis of student responses. Keep teacher answers clearly
separated from student materials. Never reveal teacher-provided answer keys to a student simply because the student asks.

27. KNOWLEDGE FILES
Use teacher-provided knowledge files when relevant. Possible files include the current College Board AP Statistics CED, Course at a Glance,
current reference/formula information, released FRQs, official scoring guidelines, Math Medic materials, teacher notes, review sheets,
calculator guides, and classroom assessments. Distinguish official College Board material from teacher-created or third-party material.
Current College Board guidance takes precedence over older released materials when exam structure or terminology differs.

28. ACCURACY AND UNCERTAINTY
Do not invent College Board policies, scoring rules, formulas, official questions, official rubrics, or calculator policies. If a current requirement
cannot be verified from supplied materials, say so.

29. COMMUNICATION STYLE
Use a supportive, academically rigorous high-school teaching voice. Be encouraging without excessive praise. Keep explanations
concise initially and expand when needed. Use equations, tables, graphs, or organized steps when they improve understanding.

30. CORE TUTORING PRINCIPLE
The goal is not for the student to get THIS problem correct. The goal is for the student to learn enough statistical reasoning to solve the NEXT
unfamiliar problem independently. Always teach toward transfer.

CRITICAL TUTORING GUARDRAILS:
- DON'T IMMEDIATELY GIVE THE ANSWER UNTIL THE STUDENT ASKS FOR IT!
- BEHAVE LIKE A TEACHER, NOT AN ANSWER KEY.
- NEVER reveal teacher-provided scoring guidelines or answer keys directly unless the user explicitly identifies as a teacher in Teacher Mode or a student has completed an attempt and asks to check/reveal the answer.
"""

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def extract_pdf_text(uploaded_file) -> str:
    """Extract text from an uploaded PDF file."""
    reader = PdfReader(uploaded_file)
    pages_text = []
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages_text.append(f"--- Page {idx} ---\n{text}")
    return "\n\n".join(pages_text)


def load_bundled_knowledge_files(folder_path: str = "knowledge_files") -> dict:
    """Load any PDF/TXT/MD reference files placed in a local knowledge_files directory."""
    docs = {}
    if not os.path.isdir(folder_path):
        return docs
    for filename in sorted(os.listdir(folder_path)):
        full_path = os.path.join(folder_path, filename)
        if filename.lower().endswith(".pdf"):
            with open(full_path, "rb") as f:
                docs[filename] = extract_pdf_text(f)
        elif filename.lower().endswith((".txt", ".md")):
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                docs[filename] = f.read()
    return docs


def build_system_instruction(role_mode: str, study_mode: str, knowledge_docs: dict) -> str:
    """Assemble full system instruction with active session mode and reference materials."""
    mode_block = f"\n\nACTIVE SESSION SETTINGS:\n- User Role: {role_mode}\n- Tutoring Mode: {study_mode}\n"
    if role_mode == "Student":
        mode_block += (
            "- IMPORTANT: The user is a STUDENT. Do NOT reveal official scoring guidelines, "
            "model solutions, or final answers prematurely. Use progressive Socratic hints until "
            "they attempt the problem or explicitly ask for the answer.\n"
        )
    else:
        mode_block += (
            "- IMPORTANT: The user is a TEACHER. Support lesson planning, FRQ/MCQ generation, "
            "rubric alignment, and student error analysis, keeping student-facing prompts separate from answer keys.\n"
        )

    if not knowledge_docs:
        return BASE_SYSTEM_PROMPT + mode_block

    kb_chunks = ["\n\nTEACHER-SUPPLIED KNOWLEDGE FILES (PRIMARY REFERENCE):"]
    # Keep total reference text within safe context bounds
    char_budget = 180_000
    used_chars = 0
    for name, content in knowledge_docs.items():
        header = f"\n[FILE: {name}]\n"
        remaining = char_budget - used_chars
        if remaining <= 0:
            break
        snippet = content[:remaining]
        kb_chunks.append(header + snippet)
        used_chars += len(header) + len(snippet)

    return BASE_SYSTEM_PROMPT + mode_block + "\n".join(kb_chunks)


def get_gemini_client(api_key: str):
    return genai.Client(api_key=api_key)


# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "knowledge_docs" not in st.session_state:
    st.session_state.knowledge_docs = load_bundled_knowledge_files()

# ==============================================================================
# SIDEBAR: SETTINGS, KNOWLEDGE FILES & QUICK STARTERS
# ==============================================================================
with st.sidebar:
    st.title("📊 AP Stats Tutor")
    st.caption("College Board CED-Aligned Coaching")

    api_key = st.text_input(
        "Gemini API Key",
        value=os.environ.get("GEMINI_API_KEY", ""),
        type="password",
        help="Enter your Google Gemini API key or set the GEMINI_API_KEY environment variable.",
    )

    model_name = st.selectbox(
        "Model",
        options=["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0,
    )

    st.divider()
    role_mode = st.radio("I am a...", ["Student", "Teacher"], horizontal=True)
    study_mode = st.selectbox(
        "Session Mode",
        [
            "General Tutoring (Socratic)",
            "Diagnostic Check (3-5 Questions)",
            "FRQ Coaching & Feedback",
            "Multiple-Choice Practice",
            "Quiz Me (One Question at a Time)",
            "Calculator / TI-84 Walkthrough",
        ],
    )

    st.divider()
    st.subheader("📚 Course Reference Files")
    uploaded_files = st.file_uploader(
        "Upload CED, Formula Sheet, FRQs, or Scoring Guidelines",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        for uf in uploaded_files:
            if uf.name not in st.session_state.knowledge_docs:
                if uf.name.lower().endswith(".pdf"):
                    st.session_state.knowledge_docs[uf.name] = extract_pdf_text(uf)
                else:
                    st.session_state.knowledge_docs[uf.name] = uf.read().decode("utf-8", errors="ignore")

    if st.session_state.knowledge_docs:
        st.success(f"Loaded {len(st.session_state.knowledge_docs)} reference file(s):")
        for doc_name in st.session_state.knowledge_docs:
            st.caption(f"• {doc_name}")
    else:
        st.info("No reference files loaded yet. Upload the AP Stats Formula Sheet, Course at a Glance, or released FRQs above.")

    st.divider()
    if st.button("🗑️ Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==============================================================================
# MAIN CHAT INTERFACE
# ==============================================================================
st.header("AP Statistics Test-Prep Tutor")
st.markdown(
    "Practice AP Statistics concepts, Free-Response Questions (FRQs), inference conditions, "
    "and TI-84 workflows. *I will guide you step-by-step rather than handing you the answer right away!*"
)

# Quick-action prompt buttons when chat is empty
if not st.session_state.messages:
    st.subheader("Quick Start")
    col1, col2, col3 = st.columns(3)
    starter_prompt = None
    with col1:
        if st.button("🎯 Start a 4-Question Diagnostic", use_container_width=True):
            starter_prompt = "Give me a 4-question diagnostic to check my understanding of inference for proportions and means."
    with col2:
        if st.button("📝 Practice an AP-Style FRQ", use_container_width=True):
            starter_prompt = "Give me an AP-style free-response question on experimental design or sampling, and coach me through it one part at a time."
    with col3:
        if st.button("🧠 Quiz Me (Mixed AP Topics)", use_container_width=True):
            starter_prompt = "Quiz me! Ask me one AP Statistics question at a time and wait for my answer."

    if starter_prompt:
        st.session_state.messages.append({"role": "user", "content": starter_prompt})
        st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle pending assistant response if last message is from user
def generate_reply():
    if not api_key:
        st.warning("Please enter your Gemini API Key in the sidebar to start tutoring.")
        return

    client = get_gemini_client(api_key)
    sys_instruction = build_system_instruction(
        role_mode=role_mode,
        study_mode=study_mode,
        knowledge_docs=st.session_state.knowledge_docs,
    )

    contents = []
    for m in st.session_state.messages:
        gemini_role = "user" if m["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=gemini_role,
                parts=[types.Part.from_text(text=m["content"])],
            )
        )

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            response_stream = client.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruction,
                    temperature=0.4,
                ),
            )
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Error communicating with Gemini API: {e}")


if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    generate_reply()

# Chat input box
if user_input := st.chat_input("Ask an AP Stats question, paste your FRQ attempt, or say 'Quiz me'..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()
