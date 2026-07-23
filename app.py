.main, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: var(--pw-bg) !important;
}

.main {
    max-width: 100%;
    padding: 2rem 3rem;
}

h1, h2, h3, h4 {
    color: var(--pw-navy);
}

/* --- Campos de entrada (antes quedaron con el estilo por defecto de Streamlit) --- */
.stTextInput input, .stNumberInput input {
    border-radius: 9px !important;
    border: 1px solid var(--pw-border) !important;
    background: var(--pw-card) !important;
    box-shadow: var(--pw-shadow-sm);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--pw-teal) !important;
    box-shadow: 0 0 0 3px var(--pw-teal-light) !important;
}
div[data-baseweb="select"] > div {
    border-radius: 9px !important;
    border-color: var(--pw-border) !important;
    background: var(--pw-card) !important;
    box-shadow: var(--pw-shadow-sm);
}
div[data-baseweb="select"]:hover > div {
    border-color: var(--pw-teal) !important;
}
.stTextInput label p, .stNumberInput label p, .stSelectbox label p,
.stRadio label p, .stCheckbox label p, .stTextInput label, .stNumberInput label,
.stSelectbox label, .stRadio label, .stCheckbox label {
    font-weight: 500 !important;
    color: var(--pw-navy) !important;
    font-size: 14.5px !important;
}
.stRadio > div, .stCheckbox {
    padding: 2px 0;
}
