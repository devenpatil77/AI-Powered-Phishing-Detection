import streamlit as st
import joblib
import fitz
from email import policy
from email.parser import BytesParser
from html import escape

from preprocessing import clean_text


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Email Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background: linear-gradient(180deg, #edf4fc 0%, #f7f9fd 42%, #eef3fa 100%);
        color: #142847;
    }

    .block-container {
        max-width: 1560px;
        padding: 1.5rem 2rem 2.4rem 2rem;
    }

    header {
        visibility: hidden;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* =====================================================
       HEADER
       ===================================================== */

    .top-header {
        background: linear-gradient(
            135deg,
            #071d41,
            #0b3974,
            #0b4d91
        );

        padding: 25px 32px;

        border-radius: 20px;

        margin-bottom: 24px;

        box-shadow:
            0 14px 34px rgba(7, 29, 65, 0.22), 0 0 0 1px rgba(255,255,255,0.08) inset;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .brand-icon {
        width: 58px;
        height: 58px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: rgba(255,255,255,0.10);

        border: 1px solid rgba(255,255,255,0.18);

        border-radius: 15px;

        font-size: 34px;
    }

    .brand-title {
        color: white;

        font-size: 32px;

        font-weight: 800;

        line-height: 1;
    }

    .brand-title span {
        color: #42a5ff;
    }

    .brand-subtitle {
        color: #d4e4f7;

        font-size: 14px;

        margin-top: 7px;
    }

    .header-badge {
        float: right;

        background: rgba(255,255,255,0.10);

        border: 1px solid rgba(255,255,255,0.16);

        color: #e9f3ff;

        padding: 10px 16px;

        border-radius: 12px;

        font-size: 13px;

        font-weight: 600;
    }


    /* =====================================================
       STREAMLIT CONTAINERS
       ===================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {

        border-radius: 18px !important;

        border: 1px solid #dce6f2 !important;

        background: white !important;

        box-shadow:
            0 12px 32px rgba(21, 48, 84, 0.08) !important;
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }


    /* =====================================================
       LEFT CARD
       ===================================================== */

    .upload-heading {
        font-size: 25px;

        font-weight: 800;

        color: #142847;

        margin-bottom: 7px;
    }

    .upload-description {
        color: #63748a;

        font-size: 15px;

        line-height: 1.6;

        margin-bottom: 18px;
    }


    /* =====================================================
       ACTUAL FILE UPLOADER
       ===================================================== */

    [data-testid="stFileUploader"] {
        margin-top: 12px;
    }

    [data-testid="stFileUploaderDropzone"] {

        background: linear-gradient(145deg, #f8fbff, #edf6ff) !important;

        border: 2px dashed #5ba7f5 !important;

        border-radius: 18px !important;

        min-height: 220px !important;

        padding: 30px !important;

        display: flex !important;

        flex-direction: column !important;

        align-items: center !important;

        justify-content: center !important;

        transition: all 0.2s ease !important;
    }

    [data-testid="stFileUploaderDropzone"]:hover {

        background: #edf7ff !important;

        border-color: #2384df !important;

        box-shadow:
            0 5px 18px rgba(35,132,223,0.10);
    }

    [data-testid="stFileUploaderDropzoneInstructions"] {

        color: #174b87 !important;

        display: flex !important;

        flex-direction: column !important;

        align-items: center !important;

        justify-content: center !important;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] svg {

        width: 42px !important;

        height: 42px !important;

        margin-bottom: 8px !important;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] span {

        color: #174b87 !important;

        font-weight: 700 !important;

        font-size: 16px !important;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] small {

        color: #6d86a3 !important;
    }

    [data-testid="stFileUploaderDropzone"] button {

        background: #1677e8 !important;

        color: white !important;

        border: none !important;

        border-radius: 8px !important;

        padding: 8px 18px !important;

        font-weight: 700 !important;

        margin-top: 8px !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {

        background: #1269d0 !important;

        color: white !important;
    }

    [data-testid="stFileUploaderFile"] {

        background: white !important;

        border: 1px solid #dbe5f0 !important;

        border-radius: 9px !important;

        margin-top: 8px !important;
    }


    /* =====================================================
       ANALYZE BUTTON
       ===================================================== */

    .stButton {
        margin-top: 12px;
    }

    .stButton > button {

        width: 100%;

        height: 52px;

        border-radius: 12px;

        border: none;

        background:
            linear-gradient(
                90deg,
                #1677e8,
                #2695f5
            );

        color: white;

        font-size: 17px;

        font-weight: 700;

        box-shadow:
            0 8px 20px rgba(22,119,232,0.28);

        transition: 0.2s;
    }

    .stButton > button:hover {

        background:
            linear-gradient(
                90deg,
                #1269d0,
                #1986df
            );

        color: white;

        transform: translateY(-1px);
    }


    /* =====================================================
       RESULT CARDS
       ===================================================== */

    .result-ready {

        background:
            linear-gradient(
                135deg,
                #f2f7ff,
                #e9f2ff
            );

        border: 1px solid #c9ddf6;

        border-radius: 20px;

        padding: 28px;

        min-height: 360px;

        box-shadow:
            0 6px 24px rgba(22,119,232,0.07);
    }

    .result-danger {

        background:
            linear-gradient(
                135deg,
                #fff5f5,
                #ffe9e9
            );

        border: 1px solid #ffcaca;

        border-radius: 20px;

        padding: 28px;

        min-height: 360px;

        box-shadow:
            0 6px 24px rgba(198,40,40,0.08);
    }

    .result-safe {

        background:
            linear-gradient(
                135deg,
                #f0fcf5,
                #e4f8ed
            );

        border: 1px solid #c1ead1;

        border-radius: 20px;

        padding: 28px;

        min-height: 360px;

        box-shadow:
            0 6px 24px rgba(22,163,74,0.07);
    }

    .result-icon {
        font-size: 52px;

        margin-bottom: 7px;
    }

    .ready-title {

        color: #1769aa;

        font-size: 29px;

        font-weight: 800;
    }

    .danger-title {

        color: #c62828;

        font-size: 29px;

        font-weight: 800;
    }

    .safe-title {

        color: #087443;

        font-size: 29px;

        font-weight: 800;
    }

    .result-description {

        color: #526173;

        font-size: 15px;

        line-height: 1.6;

        margin-top: 8px;
    }


    /* =====================================================
       CONFIDENCE
       ===================================================== */

    .confidence-box {

        background:
            rgba(255,255,255,0.78);

        border-radius: 13px;

        padding: 15px 19px;

        margin-top: 23px;
    }

    .confidence-label {

        color: #63748a;

        font-size: 13px;

        font-weight: 700;
    }

    .confidence-value {

        color: #142847;

        font-size: 34px;

        font-weight: 800;
    }


    /* =====================================================
       INFORMATION CARD
       ===================================================== */

    .info-card {

        background: white;

        border-radius: 20px;

        padding: 23px;

        margin-top: 22px;

        border: 1px solid #e2e9f2;

        box-shadow:
            0 6px 24px rgba(25,50,80,0.07);
    }

    .section-heading {

        font-size: 20px;

        font-weight: 800;

        color: #142847;

        margin-bottom: 17px;
    }


    /* =====================================================
       EMAIL INFORMATION
       ===================================================== */

    .email-row {

        background: #f7f9fc;

        border: 1px solid #edf1f6;

        border-radius: 10px;

        padding: 13px 14px;

        min-height: 64px;
    }

    .email-label {

        color: #64758b;

        font-size: 11px;

        font-weight: 800;

        margin-bottom: 5px;
    }

    .email-value {

        color: #243b5a;

        font-size: 14px;

        line-height: 1.35;

        word-break: break-word;
    }


    /* =====================================================
       EMAIL CONTENT
       ===================================================== */

    .email-content {

        background: #f8fafc;

        border: 1px solid #e3e9f1;

        border-radius: 12px;

        padding: 18px;

        height: 245px;

        overflow-y: auto;

        white-space: pre-wrap;

        color: #26384f;

        font-size: 14px;

        line-height: 1.65;
    }


    /* =====================================================
       SAFETY CARD
       ===================================================== */

    .safety-card {

        background:
            linear-gradient(
                135deg,
                #effbf5,
                #e3f8ee
            );

        border: 1px solid #c4ead4;

        border-radius: 20px;

        padding: 23px;

        margin-top: 22px;

        box-shadow:
            0 6px 24px rgba(22,163,74,0.06);
    }

    .safety-title {

        color: #096b40;

        font-size: 20px;

        font-weight: 800;

        margin-bottom: 15px;
    }

    .safety-item {

        background:
            rgba(255,255,255,0.68);

        border-radius: 9px;

        padding: 11px 13px;

        margin-bottom: 9px;

        color: #285443;

        font-size: 14px;
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {

        background: #071d41;

        color: #b9c9df;

        padding: 20px 28px;

        border-radius: 15px;

        margin-top: 25px;

        text-align: center;

        font-size: 13px;
    }

    .footer strong {
        color: white;
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    /* =====================================================
       HYBRID PREMIUM FINISH
       ===================================================== */

    h1, h2, h3, p { letter-spacing: -0.01em; }

    .top-header {
        position: relative;
        overflow: hidden;
        background: linear-gradient(115deg, #071a38 0%, #0a3266 55%, #1266b3 100%);
    }

    .top-header:after {
        content: "";
        position: absolute;
        width: 280px;
        height: 280px;
        right: -70px;
        top: -170px;
        border-radius: 50%;
        background: rgba(80, 177, 255, 0.16);
        box-shadow: 0 0 75px rgba(64, 165, 255, 0.18);
        pointer-events: none;
    }

    .brand-icon {
        box-shadow: 0 0 25px rgba(64, 165, 255, 0.18);
        backdrop-filter: blur(8px);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 15px 36px rgba(21, 48, 84, 0.11) !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        position: relative;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.8);
    }

    .stButton > button {
        letter-spacing: 0.01em;
        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
    }

    .stButton > button:hover {
        box-shadow: 0 10px 24px rgba(22,119,232,0.30);
        filter: brightness(1.04);
    }

    .result-ready, .result-danger, .result-safe {
        position: relative;
        overflow: hidden;
    }

    .result-ready:after, .result-danger:after, .result-safe:after {
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        right: -75px;
        top: -85px;
        border-radius: 50%;
        background: rgba(255,255,255,0.48);
        pointer-events: none;
    }

    .confidence-box {
        border: 1px solid rgba(220, 230, 242, 0.85);
        box-shadow: 0 5px 16px rgba(20, 40, 71, 0.04);
    }

    .email-row, .email-content, .safety-item {
        transition: border-color 0.18s ease, background 0.18s ease;
    }

    .email-row:hover {
        border-color: #b7d7fb;
        background: #f1f7ff;
    }

    .footer {
        background: linear-gradient(115deg, #061733, #0b2c58 68%, #104b86);
        box-shadow: 0 10px 28px rgba(7, 29, 65, 0.14);
    }

    @media (max-width: 900px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .brand-title {
            font-size: 25px;
        }

        .header-badge {
            display: none;
        }

        .result-ready,
        .result-danger,
        .result-safe {
            min-height: auto;
        }
    }



    /* HYBRID PREMIUM REDESIGN OVERRIDES */
    .stApp {
        background: radial-gradient(circle at 10% 0%, #dcecff 0%, transparent 30%),
                    linear-gradient(180deg, #f5f8ff 0%, #edf3fb 100%) !important;
        color: #102747 !important;
    }
    .block-container { max-width: 1480px !important; padding-top: 1.8rem !important; }
    .top-header {
        background: linear-gradient(120deg, #06152f 0%, #0a3470 55%, #0878d1 100%) !important;
        border: 1px solid rgba(255,255,255,.16) !important;
        border-radius: 24px !important;
        padding: 30px 34px !important;
        box-shadow: 0 18px 45px rgba(8, 43, 91, .22) !important;
        position: relative;
        overflow: hidden;
    }
    .top-header:after {
        content: ""; position: absolute; width: 260px; height: 260px;
        right: -65px; top: -120px; border-radius: 50%;
        border: 1px solid rgba(255,255,255,.18);
        box-shadow: 0 0 0 28px rgba(255,255,255,.035), 0 0 0 58px rgba(255,255,255,.025);
        pointer-events: none;
    }
    .brand-icon { background: rgba(255,255,255,.15) !important; border: 1px solid rgba(255,255,255,.24) !important; box-shadow: inset 0 1px 0 rgba(255,255,255,.18); }
    .brand-title { letter-spacing: -.8px !important; font-size: 36px !important; }
    .brand-subtitle { font-size: 15px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #dce7f5 !important; border-radius: 22px !important;
        box-shadow: 0 12px 32px rgba(18, 54, 96, .075) !important;
        background: rgba(255,255,255,.92) !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        min-height: 240px !important; background: linear-gradient(145deg,#f7fbff,#edf6ff) !important;
        border: 2px dashed #62a8f5 !important; border-radius: 20px !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(135deg,#0878e8,#35a1ff) !important;
        border-radius: 10px !important; box-shadow: 0 6px 16px rgba(8,120,232,.2) !important;
    }
    .stButton > button {
        background: linear-gradient(100deg,#0768d7,#169cf2) !important;
        border-radius: 13px !important; min-height: 56px !important;
        box-shadow: 0 9px 22px rgba(16,120,224,.25) !important;
        letter-spacing: .1px !important; transition: transform .18s ease, box-shadow .18s ease !important;
    }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 13px 28px rgba(16,120,224,.32) !important; }
    .result-ready, .result-danger, .result-safe {
        border-radius: 22px !important; padding: 32px !important; min-height: 375px !important;
        box-shadow: 0 14px 32px rgba(20,50,90,.08) !important;
    }
    .result-ready { background: linear-gradient(145deg,#f0f7ff,#e4f0ff) !important; border-color: #c4dcfb !important; }
    .result-danger { background: linear-gradient(145deg,#fff7f7,#ffe7e9) !important; border-color: #ffc3ca !important; }
    .result-safe { background: linear-gradient(145deg,#f3fff8,#e0f8eb) !important; border-color: #b9e8cd !important; }
    .ready-title, .danger-title, .safe-title { letter-spacing: -.5px !important; }
    .confidence-box { border: 1px solid rgba(150,170,200,.22) !important; box-shadow: 0 4px 15px rgba(20,50,90,.04) !important; }
    .info-card, .safety-card { border-radius: 20px !important; box-shadow: 0 10px 28px rgba(20,50,90,.06) !important; }
    .email-row { border-radius: 13px !important; background: #f6f9fe !important; border-color: #e2eaf5 !important; }
    .email-content { border-radius: 15px !important; background: #f8fbff !important; }
    .safety-card { background: linear-gradient(145deg,#edfff6,#dcf8eb) !important; }
    .footer { border-radius: 18px !important; background: linear-gradient(120deg,#06152f,#0b3974) !important; box-shadow: 0 12px 28px rgba(8,43,91,.16) !important; }
    @media (max-width: 900px) { .top-header { padding: 22px !important; } .brand-title { font-size: 28px !important; } }


    /* ===== EMAIL GUARDIAN STRUCTURAL REDESIGN ===== */
    .hero-panel {
        position: relative;
        overflow: hidden;
        margin: 8px 0 24px 0;
        padding: 30px 34px;
        border-radius: 24px;
        color: #ffffff;
        background: linear-gradient(115deg, #06152f 0%, #0b3974 58%, #0878d1 100%);
        box-shadow: 0 18px 42px rgba(8, 43, 91, .18);
    }
    .hero-panel:after {
        content: "";
        position: absolute;
        width: 250px;
        height: 250px;
        right: -60px;
        top: -130px;
        border-radius: 50%;
        border: 1px solid rgba(255,255,255,.22);
        box-shadow: 0 0 0 28px rgba(255,255,255,.035),
                    0 0 0 58px rgba(255,255,255,.025);
        pointer-events: none;
    }
    .hero-eyebrow {
        display: inline-block;
        padding: 6px 11px;
        border: 1px solid rgba(255,255,255,.24);
        border-radius: 999px;
        background: rgba(255,255,255,.10);
        color: #d8ebff;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 14px;
    }
    .hero-title {
        color: #ffffff;
        font-size: clamp(28px, 3vw, 42px);
        font-weight: 850;
        letter-spacing: -1.2px;
        line-height: 1.12;
        margin: 0 0 12px 0;
        max-width: 780px;
    }
    .hero-title span { color: #62bdff; }
    .hero-copy {
        color: #d6e7fb;
        font-size: 16px;
        line-height: 1.7;
        max-width: 760px;
        margin: 0;
    }
    .hero-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 9px;
        margin-top: 20px;
    }
    .hero-chip {
        color: #eef7ff;
        border: 1px solid rgba(255,255,255,.18);
        background: rgba(255,255,255,.09);
        border-radius: 999px;
        padding: 7px 11px;
        font-size: 12px;
        font-weight: 650;
    }
    .overview-card {
        border: 1px solid #dce7f5;
        background: rgba(255,255,255,.94);
        border-radius: 17px;
        padding: 17px 18px;
        min-height: 108px;
        box-shadow: 0 8px 22px rgba(20,50,90,.055);
        margin-bottom: 20px;
    }
    .overview-icon { font-size: 22px; margin-bottom: 8px; }
    .overview-title { color: #19385e; font-size: 14px; font-weight: 800; margin-bottom: 4px; }
    .overview-copy { color: #687b93; font-size: 12px; line-height: 1.5; }
    @media (max-width: 900px) {
        .hero-panel { padding: 24px 22px; }
        .hero-copy { font-size: 14px; }
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.html("""
<div class="top-header">

    <div class="header-badge">
        🛡️ AI Email Security
    </div>

    <div class="brand">

        <div class="brand-icon">
            🛡️
        </div>

        <div>

            <div class="brand-title">
                Email <span>Guardian</span>
            </div>

            <div class="brand-subtitle">
                AI-Powered Phishing Email Detection
            </div>

        </div>

    </div>

</div>
""")



# =========================================================
# PREMIUM HERO + FEATURE OVERVIEW
# =========================================================

st.html("""
<section class="hero-panel">
    <div class="hero-eyebrow">🛡️ AI SECURITY WORKSPACE</div>
    <div class="hero-title">Detect suspicious emails.<br><span>Stay one step ahead.</span></div>
    <p class="hero-copy">
        Analyze email files with your machine-learning model, inspect extracted
        content, and review clear safety guidance before interacting with a message.
    </p>
    <div class="hero-chips">
        <span class="hero-chip">✦ AI-powered classification</span>
        <span class="hero-chip">📄 PDF text extraction</span>
        <span class="hero-chip">✉️ EML and TXT support</span>
        <span class="hero-chip">🔐 Privacy-conscious workflow</span>
    </div>
</section>
""")

overview_cols = st.columns(3, gap="medium")
overview_cards = [
    ("📂", "Multiple file formats", "Upload .eml, .txt, or text-based .pdf files."),
    ("🧠", "Machine-learning analysis", "Classification uses your existing trained model."),
    ("🛡️", "Actionable safety guidance", "Review the result and practical security tips."),
]
for col, (icon, title, description) in zip(overview_cols, overview_cards):
    with col:
        st.html(f"""
        <div class="overview-card">
            <div class="overview-icon">{icon}</div>
            <div class="overview-title">{title}</div>
            <div class="overview-copy">{description}</div>
        </div>
        """)

# =========================================================
# LOAD MODEL
# =========================================================

@st.cache_resource
def load_model():

    model = joblib.load(
        "archive/models/phishing_model.pkl"
    )

    vectorizer = joblib.load(
        "archive/models/vectorizer.pkl"
    )

    return model, vectorizer


model, vectorizer = load_model()

# =========================================================
# EMAIL AND PDF EXTRACTION
# =========================================================

def extract_email_data(uploaded_file):

    file_name = uploaded_file.name.lower()

    # -----------------------------------------------------
    # PDF FILE
    # -----------------------------------------------------

    if file_name.endswith(".pdf"):

        pdf_document = None

        try:
            pdf_bytes = uploaded_file.getvalue()

            # Limit PDF size to 10 MB
            if len(pdf_bytes) > 10 * 1024 * 1024:
                raise ValueError(
                    "PDF exceeds the 10 MB file size limit."
                )

            pdf_document = fitz.open(
                stream=pdf_bytes,
                filetype="pdf"
            )

            # Limit the number of pages processed
            if pdf_document.page_count > 100:
                raise ValueError(
                    "PDF exceeds the 100-page processing limit."
                )

            body = "\n".join(
                page.get_text()
                for page in pdf_document
            )

            return {
                "subject": uploaded_file.name,
                "sender": "Not available — uploaded PDF",
                "receiver": "Not available",
                "date": "Not available",
                "body": body
            }

        except Exception as e:
            raise ValueError(
                f"Unable to extract PDF text: {e}"
            ) from e

        finally:
            if pdf_document is not None:
                pdf_document.close()

    # -----------------------------------------------------
    # EML FILE
    # -----------------------------------------------------

    if file_name.endswith(".eml"):

        msg = BytesParser(
            policy=policy.default
        ).parsebytes(uploaded_file.getvalue())

        subject = msg.get("subject", "Not available")
        sender = msg.get("from", "Not available")
        receiver = msg.get("to", "Not available")
        date = msg.get("date", "Not available")

        body_parts = []

        if msg.is_multipart():

            for part in msg.walk():

                # Skip attachments; analyze the email body only.
                if part.get_content_disposition() == "attachment":
                    continue

                if part.get_content_type() == "text/plain":

                    try:
                        content = part.get_content()

                        if isinstance(content, str):
                            body_parts.append(content)

                    except Exception:
                        pass

        else:

            try:
                content = msg.get_content()

                if isinstance(content, str):
                    body_parts.append(content)

            except Exception:
                pass

        return {
            "subject": subject,
            "sender": sender,
            "receiver": receiver,
            "date": date,
            "body": "\n".join(body_parts)
        }

    # -----------------------------------------------------
    # TXT FILE
    # -----------------------------------------------------

    text = uploaded_file.getvalue().decode(
        "utf-8",
        errors="ignore"
    )

    subject = "Not available"
    sender = "Not available"
    receiver = "Not available"
    date = "Not available"

    lines = text.splitlines()
    body_start = 0

    for i, line in enumerate(lines):

        lower = line.lower()

        if lower.startswith("subject:"):
            subject = line.split(":", 1)[1].strip()

        elif lower.startswith("from:"):
            sender = line.split(":", 1)[1].strip()

        elif lower.startswith("to:"):
            receiver = line.split(":", 1)[1].strip()

        elif lower.startswith("date:"):
            date = line.split(":", 1)[1].strip()

        elif line.strip() == "":
            body_start = i + 1
            break

    body = "\n".join(lines[body_start:])

    return {
        "subject": subject,
        "sender": sender,
        "receiver": receiver,
        "date": date,
        "body": body
    }


# =========================================================
# TOP DASHBOARD
# =========================================================

left, right = st.columns(
    [1.15, 1],
    gap="large"
)


# =========================================================
# LEFT CARD - UPLOAD
# =========================================================

with left:

    # REAL STREAMLIT CONTAINER
    # Everything inside this stays inside the card.

    with st.container(
        border=True
    ):

        st.markdown(
            '<div class="upload-heading">'
            '🔍 Check if an email is safe'
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            '<div class="upload-description">'
            'Upload an email file and let AI analyze it '
            'for potential phishing threats.'
            '</div>',
            unsafe_allow_html=True
        )


        # REAL UPLOADER
        uploaded_file = st.file_uploader(
            "Upload your email",
            type=["eml", "txt", "pdf"],
            label_visibility="collapsed"
        )


        # ANALYZE BUTTON
        analyze = st.button(
            "🔎  Analyze Email"
        )


# =========================================================
# RIGHT CARD - RESULT
# =========================================================

with right:

    if "prediction" not in st.session_state:

        st.html("""
        <div class="result-ready">

            <div class="result-icon">
                🛡️
            </div>

            <div class="ready-title">
                Ready to Analyze
            </div>

            <div class="result-description">

                Upload an email on the left and click
                <b>Analyze Email</b> to check for potential
                phishing activity.

            </div>

            <div class="confidence-box">

                <div class="confidence-label">
                    AI Analysis
                </div>

                <div class="confidence-value">
                    —
                </div>

            </div>

        </div>
        """)

    else:

        prediction = st.session_state.prediction

        confidence = st.session_state.confidence


        if prediction == "phishing":

            st.html(f"""
            <div class="result-danger">

                <div class="result-icon">
                    🚨
                </div>

                <div class="danger-title">
                    Phishing Detected
                </div>

                <div class="result-description">

                    This email contains patterns associated
                    with phishing. Avoid clicking links or
                    sharing sensitive information.

                </div>

                <div class="confidence-box">

                    <div class="confidence-label">
                        Model Confidence
                    </div>

                    <div class="confidence-value">
                        {confidence:.1f}%
                    </div>

                </div>

            </div>
            """)

        else:

            st.html(f"""
            <div class="result-safe">

                <div class="result-icon">
                    🟢
                </div>

                <div class="safe-title">
                    No Phishing Detected
                </div>

                <div class="result-description">

                    No strong phishing patterns were detected
                    by the AI model in this email.

                </div>

                <div class="confidence-box">

                    <div class="confidence-label">
                        Model Confidence
                    </div>

                    <div class="confidence-value">
                        {confidence:.1f}%
                    </div>

                </div>

            </div>
            """)


# =========================================================
# ANALYZE EMAIL
# =========================================================

if analyze:

    if uploaded_file is None:

        st.warning(
            "Please upload an email file first."
        )

    else:

        try:

            email_data = extract_email_data(
                uploaded_file
            )


            subject = email_data["subject"]

            body = email_data["body"]


            # Combine subject + body

            combined_text = (
                subject + " " + body
            )


            # Clean text

            cleaned_text = clean_text(
                combined_text
            )


            if not cleaned_text.strip():

                st.error(
                    "The uploaded email does not contain enough readable text."
                )

            else:

                # TF-IDF transformation

                text_vector = vectorizer.transform(
                    [cleaned_text]
                )


                # Prediction

                prediction = model.predict(
                    text_vector
                )[0]


                # Probability

                probabilities = model.predict_proba(
                    text_vector
                )[0]


                confidence = (
                    max(probabilities) * 100
                )


                # Normalize label

                prediction_text = str(
                    prediction
                ).lower()


                if "phish" in prediction_text:

                    result = "phishing"

                else:

                    result = "legitimate"


                # Save information

                st.session_state.prediction = result

                st.session_state.confidence = confidence

                st.session_state.email_data = email_data

                st.session_state.file_name = uploaded_file.name


                # Refresh

                st.rerun()


        except Exception as e:

            st.error(
                f"Unable to analyze this email: {e}"
            )


# =========================================================
# EXTRACTED EMAIL INFORMATION
# =========================================================

if "email_data" in st.session_state:

    email_data = st.session_state.email_data


    st.html("""
    <div class="info-card">

        <div class="section-heading">
            ✉️ Extracted Email Information
        </div>

    </div>
    """)


    col1, col2, col3, col4 = st.columns(
        4,
        gap="medium"
    )


    # -----------------------------------------------------
    # FROM
    # -----------------------------------------------------

    with col1:

        st.html(f"""
        <div class="email-row">

            <div class="email-label">
                👤 FROM
            </div>

            <div class="email-value">
                {escape(str(email_data["sender"]))}
            </div>

        </div>
        """)


    # -----------------------------------------------------
    # TO
    # -----------------------------------------------------

    with col2:

        st.html(f"""
        <div class="email-row">

            <div class="email-label">
                👥 TO
            </div>

            <div class="email-value">
                {escape(str(email_data["receiver"]))}
            </div>

        </div>
        """)


    # -----------------------------------------------------
    # SUBJECT
    # -----------------------------------------------------

    with col3:

        st.html(f"""
        <div class="email-row">

            <div class="email-label">
                📋 SUBJECT
            </div>

            <div class="email-value">
                {escape(str(email_data["subject"]))}
            </div>

        </div>
        """)


    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    with col4:

        st.html(f"""
        <div class="email-row">

            <div class="email-label">
                📅 DATE
            </div>

            <div class="email-value">
                {escape(str(email_data["date"]))}
            </div>

        </div>
        """)


# =========================================================
# EMAIL CONTENT + SAFETY
# =========================================================

if "email_data" in st.session_state:

    email_data = st.session_state.email_data


    content_col, safety_col = st.columns(
        [1.6, 1],
        gap="large"
    )


    # =====================================================
    # EMAIL CONTENT
    # =====================================================

    with content_col:

        st.html("""
        <div class="info-card">

            <div class="section-heading">
                📄 Email Content
            </div>

        </div>
        """)


        body_text = email_data["body"]


        if not body_text.strip():

            body_text = (
                "No readable email body was found."
            )


        st.html(f"""
        <div class="email-content">
            {escape(body_text)}
        </div>
        """)


    # =====================================================
    # SAFETY TIPS
    # =====================================================

    with safety_col:

        st.html("""
        <div class="safety-card">

            <div class="safety-title">
                🛡️ Stay Safe Online
            </div>

            <div class="safety-item">
                🔗 Don't click links in suspicious emails.
            </div>

            <div class="safety-item">
                📎 Don't open unexpected attachments.
            </div>

            <div class="safety-item">
                👤 Verify the sender independently.
            </div>

            <div class="safety-item">
                🔐 Never provide passwords or OTPs.
            </div>

            <div class="safety-item">
                ⚠️ Be careful with urgent requests.
            </div>

        </div>
        """)


# =========================================================
# FOOTER
# =========================================================

st.html("""
<div class="footer">

    <strong>🛡️ Email Guardian</strong>

    &nbsp; • &nbsp;

    AI-powered email security for a safer digital world.

    <br><br>

    Stay Alert
    &nbsp; • &nbsp;
    Stay Informed
    &nbsp; • &nbsp;
    Stay Safe

</div>
""")