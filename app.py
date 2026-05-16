import streamlit as st
import time
import base64
from datetime import datetime
from predict_utils import predict_image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import io

st.set_page_config(
    page_title="CardioScan AI",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: #050810; }

[data-testid="stSidebar"] {
    background: #080c18 !important;
    border-right: 1px solid #0f1a2e;
}

@keyframes ecg-scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
@keyframes pulse-slow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(94, 207, 138, 0.3); }
    50% { box-shadow: 0 0 0 14px rgba(94, 207, 138, 0); }
}
@keyframes pulse-fast {
    0%, 100% { box-shadow: 0 0 0 0 rgba(232, 112, 112, 0.4); }
    50% { box-shadow: 0 0 0 18px rgba(232, 112, 112, 0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes scanline {
    0% { top: -2px; }
    100% { top: 102%; }
}

.ecg-svg-container {
    width: 100%; overflow: hidden; height: 56px;
    opacity: 0.3; margin-bottom: 1rem;
}
.ecg-svg-inner {
    display: inline-flex;
    animation: ecg-scroll 5s linear infinite;
    width: 200%;
}

.result-card {
    border-radius: 18px; padding: 1.75rem 2rem;
    margin: 1rem 0; animation: fadeInUp 0.5s ease;
    position: relative; overflow: hidden;
}
.result-normal { background: linear-gradient(135deg, #061a0f, #0a2818); border: 1px solid #1a4a30; animation: pulse-slow 3s infinite; }
.result-disease { background: linear-gradient(135deg, #1a0608, #220a0d); border: 1px solid #4a1a1e; animation: pulse-fast 1.4s infinite; }
.scanline {
    position: absolute; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    animation: scanline 4s linear infinite;
}
.result-status { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 0.4rem; }
.result-title { font-family: 'Syne', sans-serif; font-size: 2.4rem; font-weight: 800; line-height: 1; margin-bottom: 0.6rem; }
.result-desc { font-size: 0.88rem; font-weight: 300; opacity: 0.6; line-height: 1.6; }

.gauge-wrap { text-align: center; margin: 1.2rem 0 0.5rem; }

.tip-card {
    background: #080c18; border: 1px solid #0f1a2e;
    border-radius: 12px; padding: 0.9rem 1.1rem;
    margin: 0.4rem 0; display: flex; gap: 10px; align-items: flex-start;
}
.tip-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
.tip-text { font-size: 0.82rem; color: #7a8aaa; line-height: 1.5; }
.tip-text strong { color: #c0cce0; font-weight: 500; }

.raw-score {
    font-family: 'JetBrains Mono', monospace;
    background: #080c18; border: 1px solid #0f1a2e;
    border-radius: 10px; padding: 0.65rem 1rem;
    display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem;
}
.raw-label { font-size: 0.65rem; color: #1a2a40; letter-spacing: 0.15em; text-transform: uppercase; }
.raw-value { font-size: 0.95rem; color: #c8a882; }

.stat-item { background: #0d1220; border: 1px solid #0f1a2e; border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 0.45rem; }
.stat-label { font-size: 0.6rem; color: #2a3a5a; text-transform: uppercase; letter-spacing: 0.15em; }
.stat-val { font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; color: #4a9eff; margin-top: 2px; }

.hist-item { background: #080c18; border: 1px solid #0f1a2e; border-radius: 10px; padding: 0.65rem 1rem; margin-bottom: 0.35rem; display: flex; justify-content: space-between; align-items: center; }
.hist-name { font-size: 0.75rem; color: #5a6a8a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 130px; }
.hist-badge { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; padding: 2px 8px; border-radius: 20px; }
.hist-normal { background: #061a0f; color: #5ecf8a; border: 1px solid #1a4a30; }
.hist-disease { background: #1a0608; color: #e87070; border: 1px solid #4a1a1e; }

#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
[data-testid="stFileUploader"] > div { background: #080c18 !important; border: 1px dashed #1a2a45 !important; border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []

# ── SIDEBAR ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.75rem 0 0.25rem;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <div style="width:36px;height:36px;background:#0d1a2e;border:1px solid #1a2e4a;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:18px;">🫀</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;color:#e8dcc8;">Cardio<span style="color:#4a9eff;">Scan</span></div>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#1a2a40;letter-spacing:0.2em;text-transform:uppercase;">AI ECG Analysis</div>
    </div>
    <hr style="border:none;border-top:1px solid #0f1a2e;margin:0.75rem 0;">
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.7rem;color:#2a3a5a;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.5rem;'>Model Info</div>", unsafe_allow_html=True)
    for label, val in [("Architecture", "CNN"), ("Input", "224 × 224 px"), ("Runtime", "TensorFlow"), ("Classes", "Normal / Disease"), ("Val Accuracy", "~90%")]:
        st.markdown(f'<div class="stat-item"><div class="stat-label">{label}</div><div class="stat-val">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:1px solid #0f1a2e;margin:0.75rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.7rem;color:#2a3a5a;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.5rem;'>Recent Scans</div>", unsafe_allow_html=True)

    if st.session_state.history:
        for h in reversed(st.session_state.history[-5:]):
            bc = "hist-normal" if h['result'] == "Normal" else "hist-disease"
            st.markdown(f'<div class="hist-item"><span class="hist-name">{h["name"]}</span><span class="hist-badge {bc}">{h["result"]}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.78rem;color:#1a2a40;'>No scans yet</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:1px solid #0f1a2e;margin:0.75rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.6rem;color:#151f30;text-align:center;line-height:1.7;'>For research purposes only · Not a medical device<br>Always consult a physician</div>", unsafe_allow_html=True)

# ── MAIN ─────────────────────────────────────────────

# Animated ECG header
st.markdown("""
<div class="ecg-svg-container">
  <div class="ecg-svg-inner">
    <svg viewBox="0 0 300 56" height="56" width="50%" xmlns="http://www.w3.org/2000/svg">
      <polyline points="0,28 25,28 30,28 35,6 40,50 45,28 60,28 65,22 70,34 75,28 90,28 95,28 100,7 105,50 110,28 130,28 135,28 140,6 145,50 150,28 165,28 170,22 175,34 180,28 195,28 200,28 205,7 210,50 215,28 235,28 240,28 245,6 250,50 255,28 270,28 275,22 280,34 285,28 300,28"
        fill="none" stroke="#4a9eff" stroke-width="1.4"/>
    </svg>
    <svg viewBox="0 0 300 56" height="56" width="50%" xmlns="http://www.w3.org/2000/svg">
      <polyline points="0,28 25,28 30,28 35,6 40,50 45,28 60,28 65,22 70,34 75,28 90,28 95,28 100,7 105,50 110,28 130,28 135,28 140,6 145,50 150,28 165,28 170,22 175,34 180,28 195,28 200,28 205,7 210,50 215,28 235,28 240,28 245,6 250,50 255,28 270,28 275,22 280,34 285,28 300,28"
        fill="none" stroke="#4a9eff" stroke-width="1.4"/>
    </svg>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;color:#e8dcc8;margin:0 0 0.2rem;letter-spacing:-0.5px;">
    ECG <span style="color:#4a9eff;">Heart</span> Detector
</h1>
<p style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#1e2e48;letter-spacing:0.22em;text-transform:uppercase;margin-bottom:1.5rem;">
    Neural Cardiac Analysis System
</p>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Drop ECG image here", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    with open("temp.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.image(uploaded_file, use_container_width=True, caption="Uploaded ECG")

    with col2:
        with st.spinner("Analyzing cardiac pattern..."):
            time.sleep(0.3)
            prob = predict_image("temp.jpg")

        is_normal = prob > 0.5
        confidence = prob if is_normal else (1 - prob)
        conf_pct = round(confidence * 100, 1)
        result_label = "Normal" if is_normal else "Disease"

        st.session_state.history.append({
            'name': uploaded_file.name,
            'result': result_label,
            'prob': prob,
            'time': datetime.now().strftime("%H:%M")
        })

        if is_normal:
            st.markdown(f"""
            <div class="result-card result-normal">
                <div class="scanline"></div>
                <div class="result-status" style="color:#3a7a5a;">◉ Analysis Complete</div>
                <div class="result-title" style="color:#5ecf8a;">Normal Rhythm</div>
                <div class="result-desc" style="color:#4a9e70;">No significant cardiac abnormalities detected. Heart rhythm appears within normal parameters.</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-card result-disease">
                <div class="scanline"></div>
                <div class="result-status" style="color:#8a3a3a;">⚠ Alert Detected</div>
                <div class="result-title" style="color:#e87070;">Anomaly Found</div>
                <div class="result-desc" style="color:#b06060;">Irregular cardiac pattern detected. Please consult a cardiologist for professional diagnosis and evaluation.</div>
            </div>""", unsafe_allow_html=True)

        # Gauge / Probability dial
        needle_angle = -90 + (conf_pct / 100) * 180
        arc_color = "#5ecf8a" if is_normal else "#e87070"
        st.markdown(f"""
        <div class="gauge-wrap">
          <svg viewBox="0 0 200 115" width="230" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#e87070"/>
                <stop offset="50%" style="stop-color:#e8c870"/>
                <stop offset="100%" style="stop-color:#5ecf8a"/>
              </linearGradient>
            </defs>
            <path d="M22,102 A78,78 0 0 1 178,102" fill="none" stroke="#0d1525" stroke-width="18" stroke-linecap="round"/>
            <path d="M22,102 A78,78 0 0 1 178,102" fill="none" stroke="url(#g1)" stroke-width="18" stroke-linecap="round" opacity="0.85"/>
            <g transform="rotate({needle_angle}, 100, 102)">
              <line x1="100" y1="102" x2="100" y2="32" stroke="{arc_color}" stroke-width="2.5" stroke-linecap="round"/>
              <circle cx="100" cy="102" r="7" fill="{arc_color}"/>
              <circle cx="100" cy="102" r="3.5" fill="#050810"/>
            </g>
            <text x="100" y="90" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="20" fill="{arc_color}" font-weight="500">{conf_pct}%</text>
            <text x="100" y="112" text-anchor="middle" font-family="Syne,sans-serif" font-size="7.5" fill="#1e2e48" letter-spacing="2.5">CONFIDENCE</text>
            <text x="28" y="114" font-family="JetBrains Mono,monospace" font-size="7" fill="#2a3a5a">0</text>
            <text x="166" y="114" font-family="JetBrains Mono,monospace" font-size="7" fill="#2a3a5a">100</text>
          </svg>
        </div>
        <div class="raw-score">
          <span class="raw-label">raw score</span>
          <span class="raw-value">{prob:.4f}</span>
        </div>
        """, unsafe_allow_html=True)

    # ── TIPS ──
    st.markdown("<br>", unsafe_allow_html=True)
    section_label = "💚 Health Tips — Keep It Up!" if is_normal else "🔴 Recommended Next Steps"
    st.markdown(f"<div style='font-family:Syne,sans-serif;font-size:1rem;font-weight:600;color:#c8d4e8;margin-bottom:0.75rem;'>{section_label}</div>", unsafe_allow_html=True)

    if is_normal:
        tips = [
            ("🏃", "<strong>Stay Active</strong> — 30 min moderate exercise daily keeps the heart strong and resilient."),
            ("🥗", "<strong>Heart-Healthy Diet</strong> — Reduce sodium, increase omega-3s, fruits and vegetables."),
            ("😴", "<strong>Quality Sleep</strong> — 7–9 hours per night reduces cardiovascular risk significantly."),
            ("🧘", "<strong>Manage Stress</strong> — Chronic stress elevates cortisol and strains the heart over time."),
            ("🚭", "<strong>Avoid Smoking</strong> — Even passive smoke increases cardiac risk by up to 30%."),
            ("💧", "<strong>Stay Hydrated</strong> — Proper hydration helps maintain healthy blood viscosity and pressure."),
        ]
    else:
        tips = [
            ("👨‍⚕️", "<strong>See a Cardiologist</strong> — Schedule an appointment as soon as possible for proper evaluation."),
            ("📋", "<strong>Get a 12-Lead ECG</strong> — A clinical ECG provides far more detail than a single-lead reading."),
            ("💊", "<strong>Review Medications</strong> — Some drugs affect heart rhythm — discuss all medications with your doctor."),
            ("🚫", "<strong>Limit Strenuous Activity</strong> — Until cleared by a physician, avoid intense physical exertion."),
            ("📞", "<strong>Know Emergency Signs</strong> — Chest pain, breathlessness, dizziness — call emergency services immediately."),
            ("📊", "<strong>Track Symptoms</strong> — Keep a log of any palpitations, dizziness, or fatigue to share with your doctor."),
        ]

    tcol1, tcol2 = st.columns(2)
    for i, (icon, text) in enumerate(tips):
        with (tcol1 if i % 2 == 0 else tcol2):
            st.markdown(f'<div class="tip-card"><span class="tip-icon">{icon}</span><span class="tip-text">{text}</span></div>', unsafe_allow_html=True)

    # ── PDF REPORT ──
    st.markdown("<br>", unsafe_allow_html=True)

    def generate_pdf(filename, result, prob, conf_pct, ts):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=0.8*inch, bottomMargin=0.8*inch)
        styles = getSampleStyleSheet()
        story = []
        t_style = ParagraphStyle('t', fontSize=22, fontName='Helvetica-Bold', spaceAfter=4, textColor=colors.HexColor('#0d1525'))
        s_style = ParagraphStyle('s', fontSize=10, fontName='Helvetica', spaceAfter=18, textColor=colors.HexColor('#556688'))
        b_style = ParagraphStyle('b', fontSize=11, fontName='Helvetica', spaceAfter=6, textColor=colors.HexColor('#333344'), leading=16)

        story.append(Paragraph("CardioScan AI — ECG Analysis Report", t_style))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"Generated: {ts}", s_style))
        story.append(Spacer(1, 0.15*inch))

        rc = colors.HexColor('#1a6a40') if result == "Normal" else colors.HexColor('#8a1a1a')
        data = [['File', filename], ['Result', result], ['Confidence', f"{conf_pct}%"], ['Raw Score', f"{prob:.4f}"], ['Timestamp', ts]]
        t = Table(data, colWidths=[1.8*inch, 4.2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f0f2f8')),
            ('TEXTCOLOR', (1,1), (1,1), rc),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('FONTNAME', (1,1), (1,1), 'Helvetica-Bold'),
            ('FONTSIZE', (1,1), (1,1), 13),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.HexColor('#f8f9ff'), colors.white]),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#ccccdd')),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#ddddee')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.25*inch))
        story.append(Paragraph("<b>Disclaimer</b>", b_style))
        story.append(Paragraph("This report is AI-generated for research purposes only and does NOT constitute a medical diagnosis. Always consult a qualified cardiologist or physician.", b_style))
        doc.build(story)
        buf.seek(0)
        return buf

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf = generate_pdf(uploaded_file.name, result_label, prob, conf_pct, ts)
    st.download_button("📄 Download PDF Report", data=pdf, file_name=f"ecg_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf", use_container_width=True)
