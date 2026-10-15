"""Single-page image detection experience."""

import streamlit as st

from detectorLitter.demo import detect, search

st.set_page_config(
    page_title="Litter Detector",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --forest: #153f32;
        --green: #26745a;
        --mint: #e8f3ec;
        --ink: #1d3028;
        --muted: #63756c;
        --paper: #f5f8f4;
    }
    [data-testid="stAppViewContainer"] {
        background: var(--paper);
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1160px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }
    .hero {
        min-height: 270px;
        padding: 2.5rem 2.6rem;
        border-radius: 26px;
        color: #ffffff;
        background:
            radial-gradient(circle at 85% 12%, rgba(190, 235, 199, .24), transparent 27%),
            linear-gradient(125deg, #153f32 0%, #26745a 66%, #3e8a67 100%);
        box-shadow: 0 18px 40px rgba(24, 65, 49, .16);
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .hero-kicker, .section-kicker, .workflow-kicker, .result-kicker {
        font-size: .72rem;
        font-weight: 750;
        letter-spacing: .14em;
        text-transform: uppercase;
    }
    .hero-kicker { color: #cce8d6; }
    .hero h1 {
        margin: .45rem 0 .65rem;
        color: #ffffff;
        font-size: clamp(2.5rem, 5vw, 4rem);
        line-height: 1.02;
        letter-spacing: -.045em;
    }
    .hero-copy {
        max-width: 610px;
        margin: 0;
        color: #e5f1e9;
        font-size: 1.06rem;
        line-height: 1.65;
    }
    .workflow {
        padding: 1.6rem 1.55rem;
        border: 1px solid #e0e9e2;
        border-radius: 22px;
        background: #ffffff;
        box-shadow: 0 12px 30px rgba(30, 60, 44, .06);
    }
    .workflow-kicker { color: var(--green); margin-bottom: 1rem; }
    .workflow-row {
        display: flex;
        gap: .9rem;
        align-items: flex-start;
        padding: .85rem 0;
        border-top: 1px solid #edf1ed;
    }
    .workflow-number {
        display: grid;
        width: 2rem;
        height: 2rem;
        flex: 0 0 2rem;
        place-items: center;
        border-radius: 50%;
        color: var(--green);
        background: var(--mint);
        font-size: .78rem;
        font-weight: 750;
    }
    .workflow-title { color: var(--ink); font-weight: 700; }
    .workflow-copy { margin-top: .18rem; color: var(--muted); font-size: .88rem; line-height: 1.45; }
    .section-heading { margin: 2.2rem 0 1rem; }
    .section-kicker, .result-kicker { color: var(--green); }
    .section-heading h2, .result-heading h2 {
        margin: .3rem 0 .25rem;
        color: var(--ink);
        font-size: 1.65rem;
        letter-spacing: -.025em;
    }
    .section-copy { margin: 0; color: var(--muted); }
    .upload-card {
        padding: 1.2rem 1.25rem;
        border: 1px solid #e0e9e2;
        border-radius: 22px;
        background: #ffffff;
        box-shadow: 0 12px 30px rgba(30, 60, 44, .05);
    }
    div[data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #9bbba6;
        border-radius: 16px;
        background: #f8fbf8;
    }
    div[data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--green);
        background: #f1f8f2;
    }
    div.stButton > button[kind="primary"] {
        min-height: 3rem;
        border: 0;
        border-radius: 12px;
        background: var(--green);
        color: #ffffff;
        font-weight: 700;
        box-shadow: 0 7px 16px rgba(38, 116, 90, .18);
    }
    div.stButton > button[kind="primary"]:hover {
        border: 0;
        background: var(--forest);
        color: #ffffff;
    }
    [data-testid="stMetric"] {
        padding: 1rem 1.1rem;
        border: 1px solid #e0e9e2;
        border-radius: 16px;
        background: #ffffff;
    }
    .empty-note {
        margin-top: .75rem;
        padding: 1rem 1.1rem;
        border-radius: 14px;
        color: #53685d;
        background: #edf5ef;
        line-height: 1.5;
    }
    .footer-note {
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top: 1px solid #e2eae3;
        color: #78877f;
        font-size: .82rem;
        text-align: center;
    }
    @media (max-width: 760px) {
        [data-testid="stMainBlockContainer"] { padding: 1.1rem 1rem 3rem; }
        .hero { min-height: 0; padding: 2rem 1.5rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

hero, guide = st.columns([1.55, 1], gap="large")
with hero:
    st.markdown(
        """
        <section class="hero">
            <div class="hero-kicker">Cleaner places start with a closer look</div>
            <h1>Litter Detector</h1>
            <p class="hero-copy">
                Upload a photo of a street, park, or outdoor space, or search a
                neighborhood on IGN aerial imagery. The detector highlights
                likely litter so you can review the results at a glance.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )
with guide:
    st.markdown(
        """
        <section class="workflow">
            <div class="workflow-kicker">A simple three-step check</div>
            <div class="workflow-row">
                <span class="workflow-number">01</span>
                <div><div class="workflow-title">Choose a photo</div>
                <div class="workflow-copy">Upload one image or select the example.</div></div>
            </div>
            <div class="workflow-row">
                <span class="workflow-number">02</span>
                <div><div class="workflow-title">Set the threshold</div>
                <div class="workflow-copy">Adjust how confident a detection should be.</div></div>
            </div>
            <div class="workflow-row">
                <span class="workflow-number">03</span>
                <div><div class="workflow-title">Review the result</div>
                <div class="workflow-copy">See highlighted objects and confidence scores.</div></div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

map_tab, photo_tab = st.tabs(["Map", "Photo"])

with map_tab:
    search.render()

with photo_tab:
    st.markdown(
        """
        <div class="section-heading">
            <div class="section-kicker">Image analysis</div>
            <h2>Detect litter in a photo</h2>
            <p class="section-copy">Choose a single image to begin. No camera access is needed.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    detect.render()

st.markdown(
    '<div class="footer-note">Litter Detector | Image-based detection for cleaner shared spaces</div>',
    unsafe_allow_html=True,
)
