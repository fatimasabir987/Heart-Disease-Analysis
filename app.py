import streamlit as st
import time
from predict_utils import predict_image

st.set_page_config(
    page_title="ECG Heart Analyzer",
    page_icon="🫀",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .main {
        background: #0a0a0f;
    }

    .stApp {
        background: linear-gradient(160deg, #0a0a0f 0%, #0d111e 50%, #090d18 100%);
        min-height: 100vh;
    }

    .hero-title {
        font-family: 'DM Serif Display', serif;
        font-size: 3rem;
        color: #e8dcc8;
        letter-spacing: -1px;
        line-height: 1.1;
        margin: 0;
    }

    .hero-title em {
        font-style: italic;
        color: #c8a882;
    }

    .hero-sub {
        font-family: 'DM Sans', sans-serif;
        font-weight: 300;
        font-size: 0.95rem;
        color: #5a6480;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-top: 0.4rem;
    }

    .divider {
        border: none;
        border-top: 1px solid #1e2535;
        margin: 2rem 0;
    }

    .upload-zone {
        background: #0f1421;
        border: 1px solid #1e2a40;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        transition: border-color 0.3s;
    }

    .result-normal {
        background: linear-gradient(135deg, #071a12 0%, #0a2218 100%);
        border: 1px solid #1a4a30;
        border-radius: 16px;
        padding: 2rem;
        margin-top: 1.5rem;
    }

    .result-disease {
        background: linear-gradient(135deg, #1a0a0a 0%, #220d0d 100%);
        border: 1px solid #4a1a1a;
        border-radius: 16px;
        padding: 2rem;
        margin-top: 1.5rem;
    }

    .result-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    .result-value {
        font-family: 'DM Serif Display', serif;
        font-size: 2.2rem;
    }

    .result-message {
        font-size: 0.9rem;
        font-weight: 300;
        margin-top: 0.5rem;
        opacity: 0.7;
    }

    .confidence-bar-bg {
        background: #1a1f2e;
        border-radius: 100px;
        height: 6px;
        margin-top: 1.2rem;
        overflow: hidden;
    }

    .stat-row {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
    }

    .stat-box {
        flex: 1;
        background: #0f1421;
        border: 1px solid #1e2535;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }

    .stat-num {
        font-family: 'DM Mono', monospace;
        font-size: 1.4rem;
        color: #c8a882;
    }

    .stat-label {
        font-size: 0.72rem;
        color: #4a5470;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.2rem;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Style file uploader */
    .stFileUploader > div {
        background: #0f1421 !important;
        border: 1px dashed #2a3550 !important;
        border-radius: 12px !important;
    }

    .stFileUploader label {
        color: #5a6480 !important;
    }

    /* Image display */
    .stImage {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="padding: 2.5rem 0 1rem;">
    <p class="hero-sub">Neural Cardiac Analysis</p>
    <h1 class="hero-title">ECG <em>Heart</em><br>Detector</h1>
</div>
<hr class="divider">
""", unsafe_allow_html=True)

# Stats row (static info)
st.markdown("""
<div class="stat-row">
    <div class="stat-box">
        <div class="stat-num">CNN</div>
        <div class="stat-label">Model Type</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">224px</div>
        <div class="stat-label">Input Size</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">TFLite</div>
        <div class="stat-label">Runtime</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">2</div>
        <div class="stat-label">Classes</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Upload
uploaded_file = st.file_uploader(
    "Drop ECG image here",
    type=["jpg", "jpeg", "png"],
    help="Upload a 2D ECG waveform image for analysis"
)

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.image(uploaded_file, use_container_width=True, caption="Uploaded ECG")

    with col2:
        with st.spinner("Analyzing ECG pattern..."):
            with open("temp.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())
            time.sleep(0.4)  # slight delay for UX feel
            prob = predict_image("temp.jpg")

        confidence = prob if prob > 0.5 else (1 - prob)
        confidence_pct = round(confidence * 100, 1)

        if prob > 0.5:
            st.markdown(f"""
            <div class="result-normal">
                <div class="result-label" style="color: #4a9e70;">Status</div>
                <div class="result-value" style="color: #5ecf8a;">Normal Rhythm</div>
                <div class="result-message" style="color: #4a9e70;">
                    No significant cardiac abnormalities detected. Keep up the healthy habits.
                </div>
                <div class="confidence-bar-bg">
                    <div style="background: linear-gradient(90deg, #2a7a4a, #5ecf8a); 
                                height: 100%; width: {confidence_pct}%; border-radius: 100px;"></div>
                </div>
                <div style="font-family: 'DM Mono', monospace; font-size: 0.72rem; 
                            color: #3a6e52; margin-top: 0.5rem; text-align: right;">
                    {confidence_pct}% confidence
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-disease">
                <div class="result-label" style="color: #c05050;">Alert</div>
                <div class="result-value" style="color: #e87070;">Anomaly Detected</div>
                <div class="result-message" style="color: #b06060;">
                    Irregular cardiac pattern found. Consult a cardiologist for proper diagnosis.
                </div>
                <div class="confidence-bar-bg">
                    <div style="background: linear-gradient(90deg, #8a2020, #e87070); 
                                height: 100%; width: {confidence_pct}%; border-radius: 100px;"></div>
                </div>
                <div style="font-family: 'DM Mono', monospace; font-size: 0.72rem; 
                            color: #8a4040; margin-top: 0.5rem; text-align: right;">
                    {confidence_pct}% confidence
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top: 1rem; padding: 0.8rem 1rem; background: #0f1421; 
                    border: 1px solid #1e2535; border-radius: 10px;">
            <span style="font-family: 'DM Mono', monospace; font-size: 0.75rem; 
                         color: #3a4560;">raw score</span>
            <span style="font-family: 'DM Mono', monospace; font-size: 0.9rem; 
                         color: #c8a882; float: right;">{prob:.4f}</span>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<hr class="divider">
<div style="text-align: center; padding-bottom: 2rem;">
    <p style="font-size: 0.72rem; color: #2a3045; letter-spacing: 0.08em; text-transform: uppercase;">
        For research purposes only · Not a medical device · Always consult a physician
    </p>
</div>
""", unsafe_allow_html=True)