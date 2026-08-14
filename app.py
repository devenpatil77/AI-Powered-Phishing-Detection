import streamlit as st
import joblib

from preprocessing import clean_text

# Load trained model and vectorizer
model = joblib.load("archive/models/phishing_model.pkl")
vectorizer = joblib.load("archive/models/vectorizer.pkl")

# Page Configuration
st.set_page_config(
    page_title="AI Phishing Detector",
    page_icon="🛡️",
    layout="wide"
)

# Title
st.title("🛡️ AI-Powered Phishing Email Detection")

st.write(
    "This application uses a Machine Learning model to classify emails as **Phishing** or **Legitimate**."
)

st.divider()

# Layout
col1, col2 = st.columns([2, 1])

# Left Column
with col1:

    subject = st.text_input("📧 Email Subject")

    body = st.text_area(
        "📝 Email Content",
        height=250
    )

# Right Column
with col2:

    st.subheader("📊 Project Information")

    st.info("""
**Model:** Logistic Regression

**Technique:** TF-IDF + NLP

**Dataset:** 800 Emails

**Classes:** Phishing / Legitimate
""")

# Detect Button
if st.button("🔍 Detect Email", use_container_width=True):

    # Combine subject and body
    text = subject + " " + body

    # Clean text
    cleaned = clean_text(text)

    # Convert to TF-IDF vector
    vector = vectorizer.transform([cleaned])

    # Prediction
    prediction = model.predict(vector)[0]

    # Confidence Score
    probability = model.predict_proba(vector).max() * 100

    st.divider()

    # Display Result
    if prediction == "phishing":

        st.error("🚨 Prediction: PHISHING")

    else:

        st.success("✅ Prediction: LEGITIMATE")

    # Confidence
    st.write(f"### Confidence: {probability:.2f}%")

    st.progress(min(probability / 100, 1.0))

    # Additional Information
    st.subheader("📋 Analysis")

    if prediction == "phishing":

        st.warning("""
Possible reasons:

- Suspicious language
- Urgent or threatening message
- May contain phishing keywords
- Verify sender before clicking links
""")

    else:

        st.success("""
This email appears to be legitimate.

Still remember:
- Verify unknown senders
- Avoid opening suspicious attachments
- Never share passwords
""")