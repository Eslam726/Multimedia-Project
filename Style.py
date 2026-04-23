SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:        #F0F2F5;
    --dark-blue: #0D1B2A;
    --mid-blue:  #1A2F47;
    --accent:    #FF6B1A;
    --accent-light: #FF8C4A;
    --text:      #0D1B2A;
    --muted:     #6B7A8D;
    --card:      #FFFFFF;
    --border:    #D8DEE6;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}

[data-testid="stSidebar"] {
    background: linear-gradient(160deg, var(--dark-blue) 0%, var(--mid-blue) 100%) !important;
    border-right: 3px solid var(--accent);
}
[data-testid="stSidebar"] * { color: #E8EDF3 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: 'Syne', sans-serif !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stFileUploader label {
    color: #B8C5D3 !important;
    font-size: 0.82rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-weight: 500;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * { color: #FFFFFF !important; }

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    color: var(--dark-blue);
    letter-spacing: -0.03em;
    line-height: 1.15;
}
.hero-title span { color: var(--accent); }
.hero-subtitle {
    font-size: 1rem;
    color: var(--muted);
    margin-top: 0.3rem;
    font-weight: 300;
}

.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 12px rgba(13,27,42,0.06);
}
.card-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.8rem;
}

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.badge-orange { background: #FFF0E8; color: var(--accent); border: 1px solid #FFCBA8; }
.badge-blue   { background: #E8EEF5; color: var(--mid-blue); border: 1px solid #C0CDD8; }
.badge-green  { background: #E8F5EE; color: #1A7A45; border: 1px solid #A8D8BC; }

.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent-light)) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(255,107,26,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(255,107,26,0.45) !important;
}

.stDownloadButton > button {
    background: var(--dark-blue) !important;
    color: #FFFFFF !important;
    border: 2px solid var(--accent) !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.4rem !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    background: var(--accent) !important;
    box-shadow: 0 4px 14px rgba(255,107,26,0.3) !important;
}

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px dashed rgba(255,255,255,0.25) !important;
    border-radius: 10px !important;
    padding: 0.5rem !important;
}

.stSlider > div > div > div { background: var(--accent) !important; }
.stNumberInput input, .stTextInput input {
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
}

.streamlit-expanderHeader {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: var(--dark-blue) !important;
}

hr { border-color: var(--border) !important; margin: 1rem 0 !important; }
[data-testid="stAlert"] { border-radius: 10px !important; }
.stImage > div > div { color: var(--muted) !important; font-size: 0.78rem !important; }

/* Thumbnail grid */
.thumb-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
    gap: 10px;
    margin-top: 0.6rem;
}
.thumb-item {
    border-radius: 8px;
    overflow: hidden;
    border: 2px solid var(--border);
    aspect-ratio: 1;
    position: relative;
}
.thumb-badge {
    position: absolute;
    bottom: 4px;
    right: 4px;
    background: rgba(13,27,42,0.75);
    color: #fff;
    font-size: 0.6rem;
    padding: 1px 5px;
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
}

/* Video player card */
.video-card {
    background: var(--dark-blue);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1.2rem;
}
</style>
"""
