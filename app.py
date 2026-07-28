import os
import streamlit as st
import pandas as pd
import random as rand
from columns_tab import render_columns_tab

# Bump this string on every meaningful deploy — shown in the page footer so
# it's obvious (without guessing) whether Streamlit Cloud is actually running
# the latest code after a push, instead of a stale cached build.
APP_BUILD_VERSION = "2026-07-24.1"

st.set_page_config(page_title="Precast Elements Estimator", page_icon=":material/apartment:", initial_sidebar_state="collapsed")

import streamlit as st

# --- Utilidad: divide solo si el denominador es > 0 ---
def safe_div(n, d):
    try:
        return n / d if (d is not None and d > 0) else 0.0
    except Exception:
        return 0.0


# --- Protección por contraseña simple ---
# ✅ CORREGIDO (riesgo crítico de seguridad): la contraseña ya NO está escrita
# en el código. Antes decía literalmente "Precast123" aquí mismo, visible para
# cualquiera que entrara al repositorio de GitHub (que es público). Ahora se
# lee desde st.secrets, que en Streamlit Community Cloud se configura por
# fuera del código (Settings > Secrets de tu app), y nunca queda expuesta en
# GitHub. Ver instrucciones para configurar el secreto la primera vez.
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("APP_PASSWORD", ""):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 🔒 Borra la contraseña ingresada del estado
        else:
            st.session_state["password_correct"] = False

    if "APP_PASSWORD" not in st.secrets:
        st.error(
            "App password isn't configured. "
            "Go to your app's settings in Streamlit Cloud (Settings → Secrets) "
            "and add: APP_PASSWORD = \"your_password_here\"",
            icon=":material/warning:"
        )
        st.stop()

    if "password_correct" not in st.session_state:
        st.text_input(":material/lock: Enter Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(":material/lock: Enter Password", type="password", on_change=password_entered, key="password")
        st.error("Incorrect password, try again.", icon=":material/error:")
        return False
    else:
        return True

# 🚪 Detener la app si no se ingresa correctamente la contraseña
if not check_password():
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,300..500,0,0&display=swap');

.pw-icon {
    font-family: 'Material Symbols Outlined';
    font-weight: normal;
    font-style: normal;
    font-size: inherit;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    display: inline-block;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    vertical-align: -15%;
}

:root {
    --pw-shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.06);
    --pw-shadow-md: 0 4px 8px rgba(15, 23, 42, 0.06), 0 10px 22px rgba(15, 23, 42, 0.08);
    --pw-navy: #1A1A18;
    --pw-teal: #B8912F;
    --pw-teal-dark: #8A6A1E;
    --pw-teal-light: #F6EFDC;
    --pw-bg: #F4F3F1;
    --pw-card: #FFFFFF;
    --pw-border: #E4E1D9;
    --pw-text-secondary: #6B6660;
    --pw-success-bg: #ECFDF5;
    --pw-success-text: #047857;
    --pw-ink: #131311;
}

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

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

/* --- Campos de entrada --- */
/* El borde/radio va en el contenedor que envuelve TODO el control
   (texto + botones -/+ del number_input), no en el <input> suelto —
   así queda una sola pieza en vez de una caja rota en dos partes. */
.stTextInput div[data-baseweb="input"], .stNumberInput div[data-baseweb="input"] {
    border-radius: 10px !important;
    border: 1px solid var(--pw-border) !important;
    background: var(--pw-card) !important;
    box-shadow: var(--pw-shadow-sm);
    overflow: hidden;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.stTextInput div[data-baseweb="input"]:focus-within, .stNumberInput div[data-baseweb="input"]:focus-within {
    border-color: var(--pw-teal) !important;
    box-shadow: 0 0 0 3px var(--pw-teal-light) !important;
}
.stTextInput input, .stNumberInput input {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
.stNumberInput button {
    background: transparent !important;
    border: none !important;
    border-left: 1px solid var(--pw-border) !important;
    border-radius: 0 !important;
}
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
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

/* --- Iconos con volumen real (badge circular con degradado y sombra "soft 3D") --- */
.pw-icon-badge {
    display: inline-flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    border-radius: 9px;
    background: linear-gradient(150deg, #E4CB86, var(--pw-teal-dark));
    box-shadow:
        inset 0 1px 1px rgba(255,255,255,0.45),
        inset 0 -3px 5px rgba(0,0,0,0.22),
        0 2px 6px rgba(138,106,30,0.35);
}
.pw-icon-badge .pw-icon {
    color: var(--pw-ink) !important;
}
.pw-card-title .pw-icon-badge, .subtitle .pw-icon-badge {
    width: 24px; height: 24px; border-radius: 8px; margin-right: 2px;
}
.pw-card-title .pw-icon-badge .pw-icon, .subtitle .pw-icon-badge .pw-icon {
    font-size: 14px !important;
}

/* --- Encabezado de la app --- */
.pw-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--pw-card);
    border: 1px solid var(--pw-border);
    border-radius: 18px;
    padding: 1.1rem 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--pw-shadow-md);
}
.pw-header-left { display: flex; align-items: center; gap: 16px; }
.pw-header-title { font-size: 34px; font-weight: 800; color: var(--pw-navy); margin: 0; letter-spacing: -0.02em; }
.pw-header-subtitle { font-size: 15px; color: var(--pw-text-secondary); margin: 4px 0 0 0; }
.pw-badge {
    background: var(--pw-success-bg); color: var(--pw-success-text);
    font-size: 12px; font-weight: 600; padding: 5px 14px; border-radius: 999px;
    white-space: nowrap;
    display: inline-flex; align-items: center; gap: 6px;
}
.pw-badge .pw-icon { font-size: 14px; }

/* --- Tarjetas de contenido --- */
.pw-card {
    background: var(--pw-card);
    border: 1px solid var(--pw-border);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--pw-shadow-sm);
    transition: box-shadow 0.15s ease;
}
.pw-card-title {
    font-size: 12.5px; font-weight: 700; color: var(--pw-text-secondary);
    text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 0.85rem 0;
    display: flex; align-items: center; gap: 10px;
}

/* --- Tarjetas de métricas (resultados) --- */
.pw-metric-row { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 1rem; }
.pw-metric {
    flex: 1; min-width: 170px;
    background: var(--pw-card); border: 1px solid var(--pw-border);
    border-radius: 14px; padding: 1.1rem 1.3rem;
    box-shadow: var(--pw-shadow-sm);
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}
.pw-metric:hover { box-shadow: var(--pw-shadow-md); transform: translateY(-1px); }
.pw-metric-accent {
    background: linear-gradient(135deg, #2A2A26, var(--pw-ink));
    border-color: var(--pw-ink);
    box-shadow: var(--pw-shadow-md);
}
.pw-metric-icon {
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(150deg, #E4CB86, var(--pw-teal-dark));
    color: var(--pw-ink);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; margin-bottom: 12px;
    box-shadow:
        inset 0 1px 1px rgba(255,255,255,0.45),
        inset 0 -3px 6px rgba(0,0,0,0.22),
        0 2px 6px rgba(138,106,30,0.35);
}
.pw-metric-accent .pw-metric-icon {
    background: rgba(255,255,255,0.12);
    color: var(--pw-teal);
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.15);
}
.pw-metric-label { font-size: 12px; color: var(--pw-text-secondary); margin: 0 0 4px 0; }
.pw-metric-accent .pw-metric-label { color: rgba(255,255,255,0.65); }
.pw-metric-value { font-size: 25px; font-weight: 800; color: var(--pw-navy); margin: 0; letter-spacing: -0.02em; }
.pw-metric-accent .pw-metric-value { color: var(--pw-teal); }

/* --- Expanders más elegantes --- */
div[data-testid="stExpander"] {
    border: 1px solid var(--pw-border) !important;
    border-left: 4px solid var(--pw-teal) !important;
    border-radius: 14px !important;
    background: var(--pw-card);
    margin-bottom: 0.85rem;
    box-shadow: var(--pw-shadow-sm);
    transition: box-shadow 0.15s ease, border-left-color 0.15s ease;
}
div[data-testid="stExpander"]:hover {
    box-shadow: var(--pw-shadow-md);
}
div[data-testid="stExpander"] summary {
    font-weight: 600; color: var(--pw-navy);
}
/* Nota: Streamlit todavía no permite recolorear el ícono pasado en
   icon=":material/...:" de un expander (limitación conocida, issue #11426
   sin resolver). El acento de color queda en el borde izquierdo en vez
   del ícono en sí. */

/* --- Botones --- */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: box-shadow 0.15s ease, transform 0.1s ease !important;
}
.stButton > button:hover {
    box-shadow: var(--pw-shadow-sm) !important;
    transform: translateY(-1px);
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #E4CB86, var(--pw-teal)) !important;
    color: var(--pw-ink) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    margin-top: 1rem;
    box-shadow: 0 2px 6px rgba(138,106,30,0.35) !important;
    transition: box-shadow 0.15s ease, transform 0.1s ease !important;
}
.stDownloadButton > button:hover {
    box-shadow: 0 4px 12px rgba(138,106,30,0.45) !important;
    transform: translateY(-1px);
}

/* --- Control para abrir/cerrar la barra lateral: más visible que el
   default (best-effort — el testid puede variar según versión) --- */
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="stSidebarCollapseButton"] button {
    background: var(--pw-teal) !important;
    border-radius: 8px !important;
    box-shadow: var(--pw-shadow-md) !important;
}
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg {
    color: var(--pw-ink) !important;
    fill: var(--pw-ink) !important;
}

/* --- Selector grande de módulo (Walls / Columns) en la pantalla de menú --- */
.st-key-module_selector .stButton > button {
    height: 90px !important;
    font-size: 19px !important;
    font-weight: 700 !important;
    border-radius: 14px !important;
}
.st-key-module_selector .stButton > button[kind="secondary"] {
    border: 1.5px solid var(--pw-border) !important;
    color: var(--pw-navy) !important;
}
.st-key-module_selector .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #E4CB86, var(--pw-teal)) !important;
    color: var(--pw-ink) !important;
    border: none !important;
    box-shadow: var(--pw-shadow-md) !important;
}

/* --- Pestañas de navegación --- */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 15px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--pw-teal-dark) !important;
}
div[data-baseweb="tab-highlight"] {
    background-color: var(--pw-teal-dark) !important;
}

/* --- Detalles heredados que siguen siendo útiles --- */
hr {
    border: none;
    border-top: 1px solid var(--pw-border);
    margin-top: 20px;
    margin-bottom: 20px;
}
.breakdown-title {
    font-weight: 600;
    font-size: 1rem;
    color: var(--pw-text-secondary);
    margin-top: 1rem;
}

/* --- Tarjetas de resultados detallados --- */
.card {
    background-color: var(--pw-card);
    border: 1px solid var(--pw-border);
    padding: 1.25rem 1.5rem;
    border-radius: 16px;
    margin-bottom: 1rem;
    box-shadow: var(--pw-shadow-sm);
}
.subtitle {
    font-size: 14.5px;
    font-weight: 700;
    color: var(--pw-navy);
    padding-bottom: 10px;
    margin-bottom: 10px;
    border-bottom: 1px solid var(--pw-border);
    display: flex; align-items: center; gap: 10px;
}
</style>
""", unsafe_allow_html=True)


# 🧠 Inicializar el número de secciones de refuerzo detallado
if 'num_detail_sections' not in st.session_state:
    st.session_state.num_detail_sections = 1

# 🎨 Estilo CSS personalizado para mejorar visualmente la interfaz
# (fusionado en el bloque de estilos consolidado de arriba)


# 🔹 NUEVAS CONSTANTES DE PESO PARA BARRAS 🔹
steel_weight_lookup = {
    "N10": 0.66, "N12": 0.928, "N16": 1.649, "N20": 2.577,
    "N24": 3.711, "N28": 5.051, "N32": 6.597, "N36": 8.35, "N40": 10.309,
    "D10": 0.56, "D12": 0.995, "D16": 1.58, "D20": 2.47  # 🔹 NUEVAS BARRAS DE TIPO "D"
}


# Diámetro en mm de cada barra para calcular traslape (40d / 6m)
bar_diameter_lookup = {
    "N10": 10, "N12": 12, "N16": 16, "N20": 20, "N24": 24,
    "N28": 28, "N32": 32, "N36": 36, "N40": 40,
    "D10": 10, "D12": 12, "D16": 16, "D20": 20  # 🔹 NUEVAS BARRAS DE TIPO "D"
}

mesh_weight_lookup = {
    "RL1018": 7.57, "RL1118": 9.17, "RL1218": 10.9, "RL718": 4.72, "RL818": 5.49,
    "RL918": 6.53, "SL102": 5.57, "SL62": 2.29, "SL72": 2.83, "SL81": 7.27,
    "SL82": 3.63, "SL92": 4.55
}
def detailed_reinforcement_section(index, steel_weight_lookup, mesh_weight_lookup):
        
    bar_type_h = st.selectbox(
        f"Horizontal Bar Type {index + 1}",
        [""] + list(steel_weight_lookup.keys()),
        key=f"hb_type_{index}"
    )
    spacing_h = st.number_input(
        f"Horizontal Bar Spacing (mm) {index + 1}",
        min_value=0, step=10, value=0,
        key=f"hb_spacing_{index}"
    )
    placement_h = st.radio(
        f"Horizontal Bar Placement {index + 1}",
        ["CTR", "EF"],
        key=f"hb_place_{index}"
    )

    bar_type_v = st.selectbox(
        f"Vertical Bar Type {index + 1}",
        [""] + list(steel_weight_lookup.keys()),
        key=f"vb_type_{index}"
    )
    spacing_v = st.number_input(
        f"Vertical Bar Spacing (mm) {index + 1}",
        min_value=0, step=10, value=0,
        key=f"vb_spacing_{index}"
    )
    placement_v = st.radio(
        f"Vertical Bar Placement {index + 1}",
        ["CTR", "EF"],
        key=f"vb_place_{index}"
    )

    mesh_enabled = st.radio(
        f"Mesh Reinforcement {index + 1}",
        ["No", "Yes"],
        key=f"mesh_enable_{index}"
    )

    mesh_type = ""
    mesh_placement = "CTR"
    if mesh_enabled == "Yes":
        mesh_type = st.selectbox(
            f"Mesh Type {index + 1}",
            list(mesh_weight_lookup.keys()),
            key=f"mesh_type_{index}"
        )
        mesh_placement = st.radio(
            f"Mesh Placement {index + 1}",
            ["CTR", "EF"],
            key=f"mesh_place_{index}"
        )

    trimer_type = st.selectbox(
        f"Trimer Bar Type {index + 1}",
        [""] + list(steel_weight_lookup.keys()),
        key=f"trimer_type_{index}"
    )
    trimer_placement = st.radio(
        f"Trimer Bar Placement {index + 1}",
        ["CTR", "EF"],
        key=f"trimer_place_{index}"
    )

    # NUEVO: U-Bar (barra en U de borde, Bottom o Top)
    u_bar_type = st.selectbox(
        f"U-Bar Type {index + 1}",
        [""] + list(steel_weight_lookup.keys()),
        key=f"ubar_type_{index}"
    )
    u_bar_spacing = st.number_input(
        f"U-Bar Spacing (mm) {index + 1}",
        min_value=0, step=10, value=0,
        key=f"ubar_spacing_{index}"
    )
    u_bar_location = st.radio(
        f"U-Bar Location {index + 1}",
        ["Bottom", "Top"],
        key=f"ubar_location_{index}"
    )
    u_bar_manual_length = st.checkbox(
        f"Enter U-Bar Leg Length Manually? {index + 1}",
        key=f"ubar_manual_len_{index}"
    )
    if u_bar_manual_length:
        u_bar_leg_length_mm = st.number_input(
            f"U-Bar Single Leg Length (mm) {index + 1} — one leg only, not the full U shape",
            min_value=0, step=10, value=0,
            key=f"ubar_leg_len_mm_{index}"
        )
        u_bar_leg_length = u_bar_leg_length_mm / 1000
    elif u_bar_type:
        u_bar_leg_length = (40 * bar_diameter_lookup[u_bar_type]) / 1000
    else:
        u_bar_leg_length = 0.0
        if u_bar_spacing > 0:
            st.warning(f"Please select a valid U-Bar Type to calculate leg length. {index + 1}")

    return {
    "horizontal_bar": bar_type_h,
    "horizontal_spacing": spacing_h,
    "horizontal_placement": placement_h,
    "vertical_bar": bar_type_v,
    "vertical_spacing": spacing_v,
    "vertical_placement": placement_v,
    "mesh_reinforcement": mesh_enabled,
    "mesh_type": mesh_type,
    "mesh_placement": mesh_placement,
    "trimer_bar": trimer_type,
    "trimer_placement": trimer_placement,
    "u_bar_type": u_bar_type,
    "u_bar_spacing": u_bar_spacing,
    "u_bar_location": u_bar_location,
    "u_bar_leg_length": u_bar_leg_length,
}



# 📁 Archivo CSV donde se guardarán los costos
COSTS_FILE = "costos_guardado.csv"

# 📌 Cargar costos si el archivo ya existe, si no, usa costos predeterminados
default_costs_data = {
    "Element": [
        "Concrete 50 MPa", "Concrete 65 MPa", "Concrete 50 MPa (Special Mix)",
        "RL1018", "RL1118", "RL1218", "RL718", "RL818", "RL918",
        "SL102", "SL62", "SL72", "SL81", "SL82", "SL92",
        "Steel Bars", "Concrete Testing", "Ripbox", "Lifting", "Wages",
        "Shopdrawings", "Formwork", "Patching", "Ferrule with chair",
        "Threadbar", "Couplers", "Special Accessories"
    ],
    "Unit": [
        "m³", "m³", "m³",
        "kg", "kg", "kg", "kg", "kg", "kg",
        "kg", "kg", "kg", "kg", "kg", "kg",
        "kg", "m³", "m", "ea", "m²",
        "m²", "m²", "m²", "ea", "ea", "ea", "ea"
    ],
    "Cost": [
        265, 295, 1000,
        3.20, 3.20, 3.20, 3.20, 3.20, 3.20,
        2.75, 3.04, 2.69, 2.72, 2.59, 3.16,
        3.2, 40, 90, 25, 45,
        20, 35, 15, 5, 13, 11, 5
    ]
}

@st.cache_data(show_spinner=False)
def load_costs(path, defaults, mtime):
    import os
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(defaults)

_costs_mtime = os.path.getmtime(COSTS_FILE) if os.path.exists(COSTS_FILE) else 0
costs_df = load_costs(COSTS_FILE, default_costs_data, _costs_mtime)

# Built from Cost Settings rather than a fixed list, so adding a new
# concrete grade there (e.g. "Concrete 80 MPa") makes it selectable
# straight away — no code change needed.
concrete_options = sorted(
    e for e in costs_df["Element"].astype(str) if e.startswith("Concrete ") and "MPa" in e
)



from PIL import Image
import base64
from io import BytesIO
from datetime import datetime

# --- Helper robusto para números float sin "rebotes" del widget ---
def float_input(label: str, key: str, default: float = 0.0, decimals: int = 4, min_value: float = 0.0):
    # guarda y muestra el valor como texto, tolera comas y espacios
    if key not in st.session_state:
        st.session_state[key] = f"{default:.{decimals}f}"
    txt = st.text_input(label, value=st.session_state[key])
    val_str = (txt or "").strip().replace(",", ".")
    try:
        val = float(val_str)
    except ValueError:
        val = default
    # aplica mínimo si corresponde
    if val < min_value:
        val = min_value
    # mantiene formato estable en pantalla
    st.session_state[key] = f"{val:.{decimals}f}"
    return val



# Cargar el logo e incrustarlo como base64
@st.cache_data(show_spinner=False)
def image_to_base64(filename_base):
    import os
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        path = filename_base + ext
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None


logo_base64 = image_to_base64("concrete")

st.markdown(f"""
<div class="pw-header">
    <div class="pw-header-left">
        <img src='data:image/png;base64,{logo_base64}' width='58' style='border-radius:10px;'/>
        <div>
            <p class="pw-header-title">Precast Elements Estimator</p>
            <p class="pw-header-subtitle">Cost estimation for precast concrete elements fabrication</p>
        </div>
    </div>
    <span class="pw-badge"><span class="pw-icon">check_circle</span> Active</span>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ #
# PROJECT SETUP — landing menu: capture the project name/code and which
# module (Walls or Columns) to estimate. Nothing else on the page renders
# until this is confirmed. Wrapping the Walls tab content in
# render_walls_tab() (further below) means only the chosen module's code
# actually runs each time — no change to any Walls calculation logic,
# just moved inside a function so it can be called conditionally.
# ------------------------------------------------------------------ #
if "project_configured" not in st.session_state:
    st.session_state.project_configured = False

if "menu_estimate_type_choice" not in st.session_state:
    st.session_state.menu_estimate_type_choice = "Walls"

# --- Modo desarrollador oculto -----------------------------------------
# El módulo de Columns todavía no se muestra a los usuarios normales (se
# está guardando como sorpresa para más adelante). Para poder seguir
# trabajándolo, entrando a la app con ?dev=1 al final de la URL se
# desbloquea la opción de Columns en el menú. Sin ese parámetro, solo
# aparece Walls — nadie más ve que Columns existe.
_dev_mode = st.query_params.get("dev") == "1"

# ------------------------------------------------------------------ #
# PROJECT SUMMARY — a running list of groups (Walls and/or Columns)
# already priced in this session, with a grand total. Each module calls
# add_to_project_summary(...) after showing its own result, via an
# "Add to Project Summary" button — nothing is added automatically, so
# a group only counts once, when the user confirms it's ready.
#
# Each entry also carries the FULL detail used for that group's cost
# (every input, plus its line-by-line cost breakdown) so the consolidated
# report below can list everything the estimate was built from — not
# just the summary figures. None of this is meant to persist beyond the
# session: once the report is downloaded, "Clear Project Summary" (or
# simply closing the tab) is all that's needed — nothing is saved
# server-side.
# ------------------------------------------------------------------ #
if "project_summary" not in st.session_state:
    st.session_state.project_summary = []


def add_to_project_summary(kind, group_id, unit_label, price_per_unit, total_group_cost, inputs=None, cost_breakdown=None):
    st.session_state.project_summary.append({
        "Type": kind,
        "Group ID": group_id or "N/A",
        f"Price per {unit_label}": round(price_per_unit, 2),
        "Total Group Cost": round(total_group_cost, 2) if total_group_cost else None,
        "_inputs": inputs or [],
        "_cost_breakdown": cost_breakdown.to_dict("records") if cost_breakdown is not None else [],
    })


def render_project_summary_panel(editable=False):
    if st.session_state.project_summary:
        with st.expander(f"📊 Project Summary ({len(st.session_state.project_summary)} group(s) added)", expanded=False):
            if editable:
                st.caption("Edit a Group ID or remove a group below. Everything else (prices, costs) reflects the actual calculation and can't be hand-edited here.")
                hdr = st.columns([2, 3, 2, 2, 1])
                for c, label in zip(hdr, ["Type", "Group ID", "Price", "Total Group Cost", ""]):
                    c.markdown(f"**{label}**")
                for i, entry in enumerate(st.session_state.project_summary):
                    price_key = [k for k in entry if k.startswith("Price per")][0]
                    row = st.columns([2, 3, 2, 2, 1])
                    row[0].write(entry["Type"])
                    new_group_id = row[1].text_input(
                        "Group ID", value=entry["Group ID"], key=f"summary_edit_groupid_{i}", label_visibility="collapsed"
                    )
                    if new_group_id != entry["Group ID"]:
                        st.session_state.project_summary[i]["Group ID"] = new_group_id
                    row[2].write(f"${entry[price_key]:,.2f}")
                    row[3].write(f"${entry['Total Group Cost']:,.2f}" if entry.get("Total Group Cost") is not None else "n/a")
                    if row[4].button("🗑️", key=f"summary_delete_{i}", help="Remove this group"):
                        st.session_state.project_summary.pop(i)
                        st.rerun()
            else:
                display_cols = []
                for entry in st.session_state.project_summary:
                    for k in entry.keys():
                        if not k.startswith("_") and k not in display_cols:
                            display_cols.append(k)
                summary_df = pd.DataFrame(st.session_state.project_summary).reindex(columns=display_cols)
                st.dataframe(summary_df, hide_index=True, use_container_width=True)

            grand_total = sum(row.get("Total Group Cost") or 0 for row in st.session_state.project_summary)
            if grand_total > 0:
                st.markdown(f"**Grand total (groups with a known quantity): ${grand_total:,.2f}**")

            if not editable:
                st.caption("Editing Group IDs, removing groups, and downloading the full report are available from the project menu.")
                return

            summary_dl_col1, summary_dl_col2 = st.columns(2)
            with summary_dl_col1:
                summary_output = BytesIO()
                with pd.ExcelWriter(summary_output, engine="xlsxwriter") as summary_writer:
                    summary_workbook = summary_writer.book
                    bold_fmt = summary_workbook.add_format({"bold": True})
                    title_fmt = summary_workbook.add_format({"bold": True, "font_size": 13})
                    section_fmt = summary_workbook.add_format({"bold": True, "bg_color": "#E4E1D9"})
                    subsection_fmt = summary_workbook.add_format({"bold": True, "italic": True, "bg_color": "#F4F3F1"})
                    money_fmt = summary_workbook.add_format({"num_format": "$#,##0.00"})
                    total_fmt = summary_workbook.add_format({"bold": True, "top": 1, "num_format": "$#,##0.00"})

                    report_sheet = summary_workbook.add_worksheet("Report")
                    audit_sheet = summary_workbook.add_worksheet("Audit")
                    report_sheet.set_column("A:A", 34)
                    report_sheet.set_column("B:F", 16)
                    audit_sheet.set_column("A:A", 40)
                    audit_sheet.set_column("B:B", 24)

                    proj_line = f"Project: {st.session_state.get('project_name') or 'N/A'} ({st.session_state.get('project_code_menu') or 'N/A'})"
                    report_sheet.write(0, 0, proj_line, title_fmt)
                    report_sheet.write(1, 0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} — {len(st.session_state.project_summary)} group(s)")
                    audit_sheet.write(0, 0, proj_line, title_fmt)
                    audit_sheet.write(1, 0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} — {len(st.session_state.project_summary)} group(s)")

                    # --- Project-level totals block, so the grand total's origin is traceable at a glance ---
                    report_sheet.write(3, 0, "PROJECT TOTALS", section_fmt)
                    report_sheet.write(3, 1, "", section_fmt)
                    r_totals = 4
                    for e in st.session_state.project_summary:
                        price_key = [k for k in e if k.startswith("Price per")][0]
                        report_sheet.write(r_totals, 0, f"{e['Type']} — {e['Group ID']} ({price_key})")
                        report_sheet.write(r_totals, 1, e[price_key], money_fmt)
                        report_sheet.write(r_totals, 2, e["Total Group Cost"] if e["Total Group Cost"] is not None else "n/a",
                                            money_fmt if e["Total Group Cost"] is not None else None)
                        r_totals += 1
                    grand_total_val = sum(row["Total Group Cost"] or 0 for row in st.session_state.project_summary)
                    report_sheet.write(r_totals, 0, "GRAND TOTAL", bold_fmt)
                    report_sheet.write(r_totals, 2, grand_total_val, total_fmt)

                    r_report = r_totals + 3
                    r_audit = 3
                    for entry in st.session_state.project_summary:
                        header = f"{entry['Type']} — {entry['Group ID']}"
                        price_key = [k for k in entry if k.startswith("Price per")][0]

                        # --- Report sheet: header + cost breakdown table for this group ---
                        report_sheet.write(r_report, 0, header, section_fmt)
                        report_sheet.write(r_report, 1, "", section_fmt)
                        r_report += 1
                        report_sheet.write(r_report, 0, price_key)
                        report_sheet.write(r_report, 1, entry[price_key], money_fmt)
                        r_report += 1
                        if entry.get("Total Group Cost") is not None:
                            report_sheet.write(r_report, 0, "Total Group Cost")
                            report_sheet.write(r_report, 1, entry["Total Group Cost"], money_fmt)
                            r_report += 1
                        r_report += 1
                        if entry.get("_cost_breakdown"):
                            cb_df = pd.DataFrame(entry["_cost_breakdown"])
                            for c_idx, col_name in enumerate(cb_df.columns):
                                report_sheet.write(r_report, c_idx, col_name, bold_fmt)
                            r_report += 1
                            for _, row in cb_df.iterrows():
                                is_total_row = str(row.iloc[0]).strip().lower() == "total cost"
                                for c_idx, val in enumerate(row):
                                    report_sheet.write(r_report, c_idx, val, total_fmt if is_total_row else None)
                                r_report += 1
                        else:
                            report_sheet.write(r_report, 0, "(No detailed cost breakdown available — this group was added before this report format existed. Remove it from the Project Summary and add it again to get full detail.)")
                            r_report += 1
                        r_report += 2  # blank rows between groups

                        # --- Audit sheet: header + every input for this group (with sub-sections) ---
                        audit_sheet.write(r_audit, 0, header, section_fmt)
                        audit_sheet.write(r_audit, 1, "", section_fmt)
                        r_audit += 1
                        if not entry.get("_inputs"):
                            audit_sheet.write(r_audit, 0, "(No detailed inputs available — this group was added before this report format existed. Remove it from the Project Summary and add it again to get full detail.)")
                            r_audit += 1
                        for label, value in entry.get("_inputs", []):
                            if label.startswith(">>> "):
                                audit_sheet.write(r_audit, 0, label.replace(">>> ", ""), subsection_fmt)
                                audit_sheet.write(r_audit, 1, "", subsection_fmt)
                            else:
                                audit_sheet.write(r_audit, 0, label)
                                audit_sheet.write(r_audit, 1, str(value))
                            r_audit += 1
                        r_audit += 2  # blank rows between groups

                st.download_button(
                    label="Download Project Summary Report",
                    icon=":material/download:",
                    data=summary_output.getvalue(),
                    file_name=f"{st.session_state.get('project_code_menu') or 'project'}_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="project_summary_download_button",
                )
            with summary_dl_col2:
                if st.button("Clear Project Summary", key="clear_project_summary_btn", icon=":material/delete:"):
                    st.session_state.project_summary = []
                    st.rerun()

if not st.session_state.project_configured:
    st.markdown("##### :material/apartment: Project Setup")
    menu_project_name = st.text_input(
        "Project Name", key="menu_project_name", placeholder="e.g. Beard Street Apartments",
        value=st.session_state.get("project_name", ""),
    )
    menu_project_code = st.text_input(
        "Project Code", key="menu_project_code", placeholder="e.g. A4980",
        value=st.session_state.get("project_code_menu", ""),
    )

    render_project_summary_panel(editable=True)

    if _dev_mode:
        st.markdown("##### What would you like to estimate?")
        with st.container(key="module_selector"):
            col_w, col_c = st.columns(2)
            with col_w:
                if st.button(
                    "Walls",
                    icon=":material/apartment:",
                    key="menu_pick_walls",
                    use_container_width=True,
                    type="primary" if st.session_state.menu_estimate_type_choice == "Walls" else "secondary",
                ):
                    st.session_state.menu_estimate_type_choice = "Walls"
                    st.rerun()
            with col_c:
                if st.button(
                    "Columns",
                    icon=":material/account_balance:",
                    key="menu_pick_columns",
                    use_container_width=True,
                    type="primary" if st.session_state.menu_estimate_type_choice == "Columns" else "secondary",
                ):
                    st.session_state.menu_estimate_type_choice = "Columns"
                    st.rerun()
        menu_estimate_type = st.session_state.menu_estimate_type_choice
    else:
        menu_estimate_type = "Walls"

    if st.button("Continue", icon=":material/arrow_forward:", type="primary"):
        st.session_state.project_configured = True
        st.session_state.project_name = menu_project_name
        st.session_state.project_code_menu = menu_project_code
        st.session_state.estimate_type = menu_estimate_type
        st.rerun()
    st.stop()

menu_col1, menu_col2 = st.columns([5, 1])
with menu_col1:
    st.caption(
        f"Project: **{st.session_state.get('project_name') or 'N/A'}** "
        f"({st.session_state.get('project_code_menu') or 'N/A'}) — "
        f"Estimating: **{st.session_state.estimate_type}**"
    )
with menu_col2:
    if st.button("Back to Menu", key="menu_change_btn", icon=":material/arrow_back:", use_container_width=True):
        # Reset every group-specific field (Walls' and Columns') so the next
        # group always starts at zero/blank — only project-level state
        # (name, code, summary, login) survives the trip back to the menu.
        _keep_keys = {
            "project_configured", "project_name", "project_code_menu", "estimate_type",
            "menu_estimate_type_choice", "project_summary", "password_correct",
            "menu_project_name", "menu_project_code",
        }
        for _k in list(st.session_state.keys()):
            if _k not in _keep_keys:
                del st.session_state[_k]
        st.session_state.project_configured = False
        st.rerun()

render_project_summary_panel()

# 🔧 Función para calcular barras horizontales y verticales
def calculate_rebar_weight(area, spacing_h, spacing_v, bar_type_h, bar_type_v, placement_h, placement_v, apply_lap):
    spacing_h /= 1000 if spacing_h else 1  # Convertir a metros, evita división por 0
    spacing_v /= 1000 if spacing_v else 1

    total_length_per_m2_h = 0
    total_length_per_m2_v = 0
    total_weight_m2 = 0

    if bar_type_h:
        diameter_h = bar_diameter_lookup[bar_type_h]
        lap_factor_h = 1 + (40 * diameter_h / 6000) if apply_lap else 1
        factor_placement_h = 2 if placement_h == "EF" else 1
        bars_per_meter_h = 1 / spacing_v if spacing_v > 0 else 0  # Espaciamiento vertical
        total_length_per_m2_h = bars_per_meter_h * lap_factor_h * factor_placement_h
        total_weight_m2 += total_length_per_m2_h * steel_weight_lookup[bar_type_h]

    if bar_type_v:
        diameter_v = bar_diameter_lookup[bar_type_v]
        lap_factor_v = 1 + (40 * diameter_v / 6000) if apply_lap else 1
        factor_placement_v = 2 if placement_v == "EF" else 1
        bars_per_meter_v = 1 / spacing_h if spacing_h > 0 else 0  # Espaciamiento horizontal
        total_length_per_m2_v = bars_per_meter_v * lap_factor_v * factor_placement_v
        total_weight_m2 += total_length_per_m2_v * steel_weight_lookup[bar_type_v]

    total_weight = total_weight_m2 * area
    return total_weight_m2, total_weight



# 🔧 Función para calcular el peso de malla
def calculate_mesh_weight(area, mesh_type, mesh_placement, apply_lap):
    base_weight = mesh_weight_lookup.get(mesh_type, 0) * area
    lap_factor = 1.2 if apply_lap else 1
    placement_factor = 2 if mesh_placement == "EF" else 1
    return base_weight * lap_factor * placement_factor


# 🔧 Función mejorada para calcular Trimer Bars con protección contra errores
def calculate_trimer_bar_weight(area, num_panels, wall_thickness, trimer_type, placement, apply_lap, opening_area, num_openings, avg_panel_height=0):
    if not trimer_type or num_panels == 0 or avg_panel_height <= 0:
        return 0, 0

    # CORREGIDO: el perímetro real de un panel es ancho + alto (no ancho + espesor).
    # avg_width ahora se deriva correctamente: área÷paneles da m² por panel, que
    # dividido por la altura promedio da el ancho real (antes se usaba el área
    # directamente como si fuera un largo, inflando el resultado varias veces).
    avg_width = (area / num_panels) / avg_panel_height if num_panels > 0 else 0
    perimeter_per_panel = 2 * (avg_width + avg_panel_height)
    total_length = perimeter_per_panel * num_panels

    if placement == "EF":
        total_length *= 2

    # Acceso seguro a diámetro y peso por metro
    diameter = bar_diameter_lookup.get(trimer_type, 0)
    weight_per_m = steel_weight_lookup.get(trimer_type, 0)

    lap_factor = 1 + (40 * diameter / 6000) if apply_lap else 1
    lap_factor_openings = 1 + (40 * diameter / 6000) if apply_lap else 1

    total_length_with_lap = total_length * lap_factor

    total_opening_rebar_length = 0
    if num_openings > 0:
        avg_opening_side = (opening_area / num_openings) ** 0.5
        avg_opening_perimeter = 4 * avg_opening_side
        total_opening_rebar_length = avg_opening_perimeter * num_openings

        if placement == "EF":
            total_opening_rebar_length *= 2

        total_opening_rebar_length *= lap_factor_openings
        total_length_with_lap += total_opening_rebar_length

    total_weight = total_length_with_lap * weight_per_m
    return total_weight / area if area > 0 else 0, total_weight



def calculate_u_bar_weight(area, num_panels, wall_thickness, u_bar_type, u_bar_spacing, u_bar_leg_length, avg_panel_height=0):
    if not u_bar_type or num_panels == 0 or u_bar_spacing <= 0 or u_bar_leg_length <= 0 or avg_panel_height <= 0:
        return 0, 0
    # CORREGIDO: mismo ajuste que Trimer Bar — área÷paneles÷altura, no área÷paneles directo.
    # Sin tope de 4.2m: los paneles reales pueden ser más largos, un tope fijo subestimaría.
    avg_width = ((area / num_panels) / avg_panel_height) if num_panels > 0 else 0
    bars_per_panel = avg_width / (u_bar_spacing / 1000)
    bars_per_panel = int(bars_per_panel) + (1 if bars_per_panel % 1 > 0 else 0)
    total_bars = bars_per_panel * num_panels
    short_leg = wall_thickness / 1000
    length_per_bar = (2 * u_bar_leg_length) + short_leg
    weight_per_m = steel_weight_lookup.get(u_bar_type, 0)
    total_weight = total_bars * length_per_bar * weight_per_m
    return (total_weight / area if area > 0 else 0), total_weight


def calculate_section_weight(section, area, wall_thickness, apply_lap, num_panels, opening_area, num_openings, avg_panel_height=0):
    bars_weight_m2, bars_weight_total = calculate_rebar_weight(
        area,
        section["horizontal_spacing"],
        section["vertical_spacing"],
        section["horizontal_bar"],
        section["vertical_bar"],
        section["horizontal_placement"],
        section["vertical_placement"],
        apply_lap
    )

    if section["mesh_reinforcement"] == "Yes":
        mesh_weight_total = calculate_mesh_weight(area, section["mesh_type"], section["mesh_placement"], apply_lap)
    else:
        mesh_weight_total = 0

    trimer_bar_m2, trimer_weight_total = calculate_trimer_bar_weight(
        area, num_panels, wall_thickness,
        section["trimer_bar"], section["trimer_placement"], apply_lap,
        opening_area, num_openings, avg_panel_height
    )

    u_bar_m2, u_bar_weight_total = calculate_u_bar_weight(
        area, num_panels, wall_thickness,
        section["u_bar_type"], section["u_bar_spacing"], section["u_bar_leg_length"], avg_panel_height
    )

    return {
        "bars_total": bars_weight_total,
        "mesh_total": mesh_weight_total,
        "trimer_total": trimer_weight_total,
        "u_bar_total": u_bar_weight_total
    }




with st.sidebar:
    st.markdown("##### :material/settings: Cost Settings")
    st.caption("Unit prices used across all projects — not specific to this element.")

    # Editable Costs Table
    if st.checkbox("Show Editable Cost Table"):
        with st.expander("Editable Costs Table", icon=":material/receipt_long:", expanded=True):
            edited_df = st.data_editor(costs_df, num_rows="dynamic")

            # Reset dentro del bloque editable
            st.markdown("---")
            st.markdown("### :material/settings_backup_restore: Reset Costs to Default")
            confirm_reset = st.checkbox("I confirm I want to reset all costs to default values")

            if st.button("Reset Costs", icon=":material/refresh:", disabled=not confirm_reset, key="reset_costs_btn"):
                costs_df = pd.DataFrame(default_costs_data)
                costs_df.to_csv(COSTS_FILE, index=False)
                st.cache_data.clear()                       # invalida la caché de load_costs
                st.session_state["did_reset_costs"] = True  # marca que hubo reset en este render
                st.success("Costs reset to default. Reloading…", icon=":material/check_circle:")
                st.rerun()                                   # recarga inmediata para leer defaults


            # 🔹 Guardar edición automáticamente
            if edited_df is not None and not st.session_state.get("did_reset_costs"):
                edited_df.to_csv(COSTS_FILE, index=False)
                st.cache_data.clear()   # 🔄 limpiar caché para que load_costs recargue
                cost_dict = dict(zip(edited_df["Element"], edited_df["Cost"]))

            # ✅ Asegurar cost_dict aunque no se edite nada
            cost_df_current = edited_df if edited_df is not None else costs_df
            cost_dict = dict(zip(cost_df_current["Element"], cost_df_current["Cost"]))


    else:
        cost_dict = dict(zip(costs_df["Element"], costs_df["Cost"]))

if st.session_state.estimate_type == "Columns":
    render_columns_tab(cost_dict, steel_weight_lookup, bar_diameter_lookup,
                        concrete_options, float_input, safe_div, add_to_project_summary)


def render_walls_tab():
    # 📌 Código del proyecto — tomado de la pantalla de menú, ya no se vuelve a pedir
    project_code = st.session_state.get("project_code_menu", "")
    st.caption(f"Project Code: **{project_code or 'N/A'}**")

    # 📌 Código del proyecto ingresado por el usuario
    element_type = st.text_input("Enter Element Type", placeholder="e.g. PT1")

    # 🔹 Ajustar el ancho de la hoja con CSS personalizado
    st.markdown(
        """
        <style>
        .main {
            max-width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    sub_geom, sub_reo, sub_costs = st.tabs(["Geometry", "Reinforcement", "Costs & Extras"])

    with sub_geom:
        # Panel Dimensions
        with st.expander("Panel Dimensions", icon=":material/straighten:", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                number_of_panels = st.number_input(
                    "Number of Panels",
                    min_value=0,
                    value=0,
                    step=1,
                    key="num_panels_input",
                )
            with col2:
                wall_area = float_input(
                    "Total Wall Area (m²)",
                    key="wall_area_input_text",
                    default=0.0,
                    decimals=4,
                    min_value=0.0,
                )
            with col3:
                wall_thickness = st.number_input(
                    "Wall Thickness (mm)",
                    min_value=0,
                    value=0,
                    step=10,
                    key="wall_thickness_input",
                )

            col4, col5 = st.columns(2)
            with col4:
                avg_panel_height = float_input(
                    "Average Panel Height (m)",
                    key="avg_panel_height_input_text",
                    default=0.0,
                    decimals=2,
                    min_value=0.0,
                )
                if avg_panel_height == 0:
                    st.caption(":material/warning: Required — average height across panels.")
            with col5:
                concrete_type = st.selectbox(
                    "Concrete Type",
                    concrete_options,
                    index=0,
                    key="concrete_type_select",
                )

        with st.expander("Openings", icon=":material/window:"):
            has_openings = st.radio("Do the panels have openings?", ["No", "Yes"], index=0)
            if has_openings == "Yes":
                col1, col2 = st.columns(2)
                with col1:
                    opening_area = float_input("Total Openings Area (m²)", key="opening_area_input_text", default=0.0, decimals=4, min_value=0.0)
                with col2:
                    number_of_openings = st.number_input("Number of Openings", min_value=0, value=0)
            else:
                opening_area = 0
                number_of_openings = 0

    with sub_reo:
        # Reinforcement
        with st.expander("Reinforcement", icon=":material/construction:", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                reo_rate = st.number_input("Reo Rate (kg/m³) (optional)", min_value=0.0, value=0.0, key="reo_rate_input")
            with col2:
                extra_steel_kg = st.number_input("Additional Steel Reinforcement (kg)", min_value=0.0, step=1.0, key="extra_steel_input_main")
            use_reo_rate_only = st.radio("Use only Reo Rate or add to bars/mesh?", ["Add to bars and mesh", "Use only Reo Rate"], index=0, key="use_reo_option")
            apply_lap_splice = st.checkbox("Apply Lap Splice (40d for bars, 20% for mesh)", value=True)

        with st.expander("Reinforcement — Detailed Sections (Bars & Mesh)", icon=":material/view_agenda:"):
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Add Bars and Mesh Section", icon=":material/add:"):
                    st.session_state.num_detail_sections += 1
            with col2:
                if st.button("Remove Last Section", icon=":material/remove:") and st.session_state.num_detail_sections > 1:
                    st.session_state.num_detail_sections -= 1

            detailed_sections_data = []
            for i in range(st.session_state.num_detail_sections):
                with st.container(border=True):
                    st.markdown(f"### :material/hub: Bars and Mesh Section {i + 1}")
                    section_data = detailed_reinforcement_section(i, steel_weight_lookup, mesh_weight_lookup)
                    detailed_sections_data.append(section_data)

            # Steel Weight por Sección
            st.markdown("### :material/inventory_2: Steel Weight per Section")
            total_section_weight = 0
            for i, section in enumerate(detailed_sections_data):
                result = calculate_section_weight(
                    section, wall_area, wall_thickness,
                    apply_lap_splice, number_of_panels,
                    opening_area, number_of_openings, avg_panel_height
                )
                section_weight = result["bars_total"] + result["mesh_total"] + result["trimer_total"] + result["u_bar_total"]
                total_section_weight += section_weight
                st.write(f":material/label: Section {i+1}: {section_weight:.2f} kg")

            # Reo Rate total
            reo_rate_kg_total = (reo_rate * (wall_thickness / 1000)) * wall_area if reo_rate > 0 else 0
            if reo_rate_kg_total > 0:
                st.write(f":material/add: Reo Rate: {reo_rate_kg_total:.2f} kg")

            # Refuerzo adicional
            if extra_steel_kg > 0:
                st.write(f":material/add: Additional Steel: {extra_steel_kg:.2f} kg")

            # 🔸 Total general (PREVIA, sin waste — el waste % se define más abajo,
            # en "Waste Factors", así que todavía no se puede aplicar aquí).
            # ✅ CORREGIDO (Bug 3): antes esta variable se llamaba "total_steel_weight",
            # el mismo nombre que se reasignaba más abajo con el waste ya aplicado.
            # El número que se mostraba aquí en pantalla NO incluía waste, pero el
            # usuario no tenía forma de saberlo porque el rótulo no lo aclaraba y el
            # nombre de la variable era idéntico al del total "real". Se renombra para
            # que sea imposible confundirlos, y se aclara en el texto.
            total_steel_weight_preview = total_section_weight + reo_rate_kg_total + extra_steel_kg
            st.markdown(f"""
            <div class="pw-metric-row">
                <div class="pw-metric">
                    <div class="pw-metric-icon"><span class="pw-icon">hardware</span></div>
                    <p class="pw-metric-label">Total steel (before waste %)</p>
                    <p class="pw-metric-value">{total_steel_weight_preview:.2f} kg</p>
                </div>
                <div class="pw-metric">
                    <div class="pw-metric-icon"><span class="pw-icon">grid_view</span></div>
                    <p class="pw-metric-label">Steel from sections only</p>
                    <p class="pw-metric-value">{total_section_weight:.2f} kg</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Dowels (SEPARADO)
        with st.expander("Dowels", icon=":material/link:"):
            dowels = st.radio("Dowels", ["No", "Yes"])
            total_dowel_weight = 0  # 🔹 Inicialización

            if dowels == "Yes":
                dowel_calculation_method = st.radio("Dowel Weight Calculation", ["Calculate Automatically", "Enter Manually"])

                if dowel_calculation_method == "Enter Manually":
                    total_dowel_weight = st.number_input("Total Dowels Weight (kg)", min_value=0.0, value=0.0)

                else:  # 🔹 Cálculo Automático
                    col1, col2 = st.columns(2)
                    with col1:
                        dowel_bar_type = st.selectbox("Dowel Bar Type", [""] + list(steel_weight_lookup.keys()))
                    with col2:
                        dowel_spacing = st.number_input("Dowel Spacing (mm)", min_value=0, step=10, value=0)

                    # 🔹 Opción para ingresar la longitud manualmente o calcularla
                    use_manual_length = st.checkbox("Enter Dowel Length Manually?")

                    if use_manual_length:
                        dowel_length = float_input("Dowel Length (m)", key="dowel_len_manual_text", default=0.0, decimals=4, min_value=0.0)
                    elif dowel_bar_type:
                        dowel_length = (40 * bar_diameter_lookup[dowel_bar_type] * 2) / 1000 + 0.02
                    else:
                        dowel_length = 0.0
                        st.warning("Please select a valid Dowel Bar Type to calculate length.", icon=":material/warning:")

                    # 🔹 Largo promedio del panel (área÷paneles÷altura). Sin tope artificial:
                    # los paneles reales de este proyecto pueden llegar a 10-12 m de largo,
                    # así que un tope fijo subestimaría la cantidad de barras.
                    if number_of_panels > 0 and avg_panel_height > 0:
                        avg_panel_width = (wall_area / number_of_panels) / avg_panel_height
                    else:
                        avg_panel_width = 0
                        st.warning("Please enter number of panels and average panel height greater than zero to calculate dowel bars.", icon=":material/warning:")

                    # 🔹 Número de dowels por panel
                    if dowel_spacing > 0 and dowel_bar_type:
                        dowels_per_panel = avg_panel_width / (dowel_spacing / 1000)
                        dowels_per_panel = int(dowels_per_panel) + (1 if dowels_per_panel % 1 > 0 else 0)
                        total_dowels = dowels_per_panel * number_of_panels
                        total_dowel_weight = total_dowels * dowel_length * steel_weight_lookup[dowel_bar_type]
                    else:
                        total_dowel_weight = 0
                        if dowel_spacing > 0 and not dowel_bar_type:
                            st.warning("Please select a Dowel Bar Type to calculate dowels.", icon=":material/warning:")
                        elif dowel_spacing <= 0:
                            st.warning("Please enter a valid Dowel Spacing greater than zero to calculate dowels.", icon=":material/warning:")

    with sub_costs:
        # Additional Elements (SEPARADO)
        with st.expander("Additional Elements", icon=":material/build:", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                ripbox = st.number_input("Ripbox (m)", value=0.0)
            with col2:
                ferrules = st.number_input("Ferrules (units)", value=0)
            with col3:
                Threadbar = st.number_input("Threadbar (units)", value=0)
            col4, col5, col6 = st.columns(3)
            with col4:
                couplers = st.number_input("Couplers (units)", value=0)
            with col5:
                lifters_per_panel = st.number_input("Lifters per Panel", value=0, key="lifters_per_panel_input")
            with col6:
                special_accessories_per_m2 = st.number_input("Special Accessories per m²", min_value=0.0, value=0.0, step=0.1, key="special_accessories_input")

            st.markdown("### :material/add_circle: Add Custom Additional Elements")
            num_custom_elements = st.number_input("How many additional elements do you want to add?", min_value=0, max_value=10, value=0)

            additional_custom_elements = {}
            custom_additional_info = {}


            for i in range(num_custom_elements):
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    item_label = col1.text_input(f"Description {i+1}", key=f"add_item_label_{i}")
                    item_unit = col2.selectbox("Unit", ["$/panel", "$/m²", "$/unit"], key=f"add_item_unit_{i}")
                    item_value = col3.number_input("Cost", min_value=0.0, step=0.1, key=f"add_item_value_{i}")
                    custom_additional_info[item_label.strip()] = {"unit": item_unit, "cost": item_value}


                item_qty = 1  # Valor por defecto
                if item_unit == "$/unit":
                    item_qty = st.number_input(f"Qty for '{item_label or f'Item {i+1}'}'", min_value=0, step=1, value=1, key=f"add_item_qty_{i}")

                if item_label.strip():
                    if item_unit == "$/panel" and number_of_panels > 0:
                        additional_custom_elements[item_label.strip()] = safe_div((item_value * number_of_panels), wall_area)

                    elif item_unit == "$/m²":
                        additional_custom_elements[item_label.strip()] = item_value
                    elif item_unit == "$/unit":
                        additional_custom_elements[item_label.strip()] = (item_value * item_qty) / wall_area if wall_area > 0 else 0

        # 🔁 Cálculo acumulado desde secciones dinámicas (se necesita ya acá para
        # que el filtro de Waste Factors sepa qué elementos están realmente en uso)
        bars_weight_total = 0
        mesh_weight_total = 0
        trimer_bar_total = 0
        u_bar_total = 0
        for section in detailed_sections_data:
            result = calculate_section_weight(
                section, wall_area, wall_thickness,
                apply_lap_splice, number_of_panels,
                opening_area, number_of_openings, avg_panel_height
            )
            bars_weight_total += result["bars_total"]
            mesh_weight_total += result["mesh_total"]
            trimer_bar_total += result["trimer_total"]
            u_bar_total += result["u_bar_total"]

        concrete_volume = wall_area * (wall_thickness / 1000)  # 🔹 Convertimos a metros cúbicos

        # Waste % por elemento — solo se muestra el % de waste para elementos
        # que realmente están en uso (filtro por cantidad > 0).
        with st.expander("Waste Factors (Optional)", icon=":material/recycling:"):
            st.markdown("Enter a percentage of waste for each applicable item (leave at 0 if not needed):")

            waste_items = {
                "Concrete": concrete_volume,
                "Steel Bars (H+V)": bars_weight_total,
                "Trimer Bar": trimer_bar_total,
                "U-Bar": u_bar_total,
                "Mesh": mesh_weight_total,
                "Ripbox": ripbox
            }

            waste_percentages = {}
            for label, qty in waste_items.items():
                if qty > 0:  # solo mostrar si tiene cantidad
                    waste_percentages[label] = st.number_input(
                        f"Waste % for {label}",
                        min_value=0.0,
                        value=0.0,
                        step=0.1,
                        key=f"waste_{label.replace(' ', '_')}"
                    )

            waste_concrete = waste_percentages.get("Concrete", 0.0)
            waste_steel = waste_percentages.get("Steel Bars (H+V)", 0.0)
            waste_trimmer = waste_percentages.get("Trimer Bar", 0.0)
            waste_u_bar = waste_percentages.get("U-Bar", 0.0)
            waste_mesh = waste_percentages.get("Mesh", 0.0)
            waste_ripbox = waste_percentages.get("Ripbox", 0.0)

        with st.expander("EO Items (Optional)", icon=":material/add_circle:", expanded=False):
            num_eo = st.number_input("How many EO Items (Optional) do you want to add?", min_value=0, max_value=10, step=1, value=0)

            eo_costs = {}

            for i in range(num_eo):
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    eo_label = col1.text_input(f"EO Desc {i+1}", key=f"eo_label_{i}", value=f"EO - Extra {i+1}")
                    eo_unit = col2.selectbox("Unit", ["$/panel", "$/m²"], key=f"eo_unit_{i}")
                    eo_value = col3.number_input("Value", min_value=0.0, step=1.0, key=f"eo_value_{i}")

                    if eo_label.strip():
                        if eo_unit == "$/panel" and number_of_panels > 0:
                            eo_costs[eo_label.strip()] = safe_div((eo_value * number_of_panels), wall_area)

                        elif eo_unit == "$/m²":
                            eo_costs[eo_label.strip()] = eo_value

        # --- Review Checklist (barra lateral) -----------------------------
        # Vive en la sidebar y se recalcula en cada rerun, así que se va
        # actualizando en vivo a medida que el usuario carga datos en
        # cualquiera de las 3 sub-pestañas — no es un checkpoint al final,
        # es una guía que acompaña mientras se trabaja.
        openings_summary = (
            f"{number_of_openings} opening(s), {opening_area:.2f} m² total"
            if has_openings == "Yes" and number_of_openings > 0
            else "None"
        )
        dowels_summary = (
            f"Included — {total_dowel_weight:.2f} kg"
            if dowels == "Yes"
            else "Not included"
        )
        reo_summary = (
            f"Reo Rate only — {reo_rate:.1f} kg/m³"
            if use_reo_rate_only == "Use only Reo Rate"
            else f"{len(detailed_sections_data)} bar/mesh section(s) configured"
        )

        additional_items = []
        if ripbox > 0:
            additional_items.append(f"Ripbox {ripbox:.2f} m")
        if ferrules > 0:
            additional_items.append(f"Ferrules {ferrules}")
        if Threadbar > 0:
            additional_items.append(f"Threadbar {Threadbar}")
        if couplers > 0:
            additional_items.append(f"Couplers {couplers}")
        if lifters_per_panel > 0:
            additional_items.append(f"{lifters_per_panel} lifter(s)/panel")
        if special_accessories_per_m2 > 0:
            additional_items.append(f"Special accessories {special_accessories_per_m2:.2f}/m²")
        if num_custom_elements > 0:
            additional_items.append(f"{num_custom_elements} custom element(s)")
        additional_summary = ", ".join(additional_items) if additional_items else "None"

        waste_applied = [
            label for label, val in [
                ("Concrete", waste_concrete), ("Steel", waste_steel),
                ("Trimer Bar", waste_trimmer), ("Mesh", waste_mesh), ("Ripbox", waste_ripbox)
            ] if val and val > 0
        ]
        waste_summary = ", ".join(waste_applied) if waste_applied else "None applied"

        eo_summary = f"{num_eo} item(s)" if num_eo > 0 else "None"

        _geom_done = number_of_panels > 0 and wall_area > 0 and wall_thickness > 0
        _reo_done = (
            (use_reo_rate_only == "Use only Reo Rate" and reo_rate > 0)
            or (
                use_reo_rate_only == "Add to bars and mesh"
                and any(sec.get("horizontal_bar") or sec.get("vertical_bar") for sec in detailed_sections_data)
            )
        )
        _costs_done = lifters_per_panel > 0 or special_accessories_per_m2 > 0

        st.sidebar.markdown("---")
        st.sidebar.markdown("##### :material/fact_check: Review Checklist")
        st.sidebar.caption(f"{'✅ ' if _geom_done else ''}Geometry")
        st.sidebar.markdown(f"Panels: **{number_of_panels}** · Area: **{wall_area:.2f} m²** · Thickness: **{wall_thickness} mm**")
        st.sidebar.markdown(f"Concrete Type: **{concrete_type}**")
        st.sidebar.markdown(f"Openings: **{openings_summary}**")
        st.sidebar.caption(f"{'✅ ' if _reo_done else ''}Reinforcement")
        st.sidebar.markdown(f"Bars/Mesh: **{reo_summary}**")
        if extra_steel_kg > 0:
            st.sidebar.markdown(f"Additional Steel: **{extra_steel_kg:.1f} kg**")
        st.sidebar.markdown(f"Lap Splice: **{'Applied' if apply_lap_splice else 'Not applied'}**")
        st.sidebar.markdown(f"Dowels: **{dowels_summary}**")
        st.sidebar.caption(f"{'✅ ' if _costs_done else ''}Costs & Extras")
        st.sidebar.markdown(f"Additional Elements: **{additional_summary}**")
        st.sidebar.markdown(f"Waste % applied to: **{waste_summary}**")
        st.sidebar.markdown(f"EO Items: **{eo_summary}**")



    # (bars_weight_total, mesh_weight_total, trimer_bar_total y concrete_volume
    # ya se calcularon más arriba, justo después de Additional Elements, para
    # que Waste Factors pudiera filtrar qué elementos están en uso)

    # 🔹 Calcular peso por m²
    bars_weight_m2 = bars_weight_total / wall_area if wall_area > 0 else 0
    mesh_weight_m2 = mesh_weight_total / wall_area if wall_area > 0 else 0
    trimer_bar_m2 = trimer_bar_total / wall_area if wall_area > 0 else 0
    u_bar_m2 = u_bar_total / wall_area if wall_area > 0 else 0

    additional_reinforcement_kg_total = extra_steel_kg

    # Nota: los % de waste (waste_concrete, waste_steel, waste_trimmer, waste_mesh,
    # waste_ripbox) ya se capturaron más arriba, en el expander "Waste Factors"
    # (ubicado después de Additional Elements, antes de EO Items).
    total_steel_weight = (
        reo_rate_kg_total * (1 + waste_steel / 100) +
        bars_weight_total * (1 + waste_steel / 100) +
        mesh_weight_total * (1 + waste_mesh / 100) +
        trimer_bar_total * (1 + waste_trimmer / 100) +
        u_bar_total * (1 + waste_u_bar / 100) +
        additional_reinforcement_kg_total
    )

    # ✅ CORREGIDO (Bug 3, parte 2): este cálculo estaba ANTES en el archivo
    # (antes del bloque de Waste Factors) y usaba el total de acero SIN waste,
    # porque en ese punto todavía no existía el total con waste. El resultado
    # ("Total Steel per m²" que se muestra al final) no coincidía con el peso
    # total real usado para costear. Ahora se calcula aquí, después de que
    # total_steel_weight ya tiene su valor final (con waste incluido).
    total_steel_weight_m2 = total_steel_weight / wall_area if wall_area > 0 else 0

    # 🟧 Datos de referencia de la primera sección (se mantienen por compatibilidad
    # con el resto del archivo, que aún los usa para mostrar/etiquetar resultados;
    # YA NO se usan para calcular el costo de la malla — ver corrección abajo).
    if detailed_sections_data:
        first_section = detailed_sections_data[0]
        mesh_type = first_section.get("mesh_type")
        mesh_reinforcement = first_section.get("mesh_reinforcement")
    else:
        mesh_type = ""
        mesh_reinforcement = "No"

    # ✅ CORREGIDO (Bug 2): el peso Y el costo de la malla ahora se calculan
    # sumando TODAS las secciones que tengan malla activada, cada una con su
    # propio tipo de malla y por lo tanto su propio costo unitario — antes solo
    # se usaba el tipo de malla de la primera sección para el costo, aunque el
    # peso sí sumaba todas las secciones (dinero no cobrado si la sección 1 no
    # tenía malla pero otra sección sí).
    total_mesh_weight = 0.0
    total_mesh_cost = 0.0
    for sec in detailed_sections_data:
        if sec.get("mesh_reinforcement") == "Yes" and sec.get("mesh_type"):
            sec_mesh_weight = calculate_mesh_weight(
                wall_area, sec["mesh_type"], sec["mesh_placement"], apply_lap_splice
            )
            total_mesh_weight += sec_mesh_weight
            total_mesh_cost += sec_mesh_weight * cost_dict.get(sec["mesh_type"], 0)

    mesh_cost_per_m2 = safe_div(total_mesh_cost, wall_area)

    cost_per_m2 = {
        "Concrete": (
        (concrete_volume * (1 + waste_concrete / 100)) * cost_dict.get(concrete_type, 0) / wall_area
        if wall_area > 0 else 0
    ),


        "Concrete Testing": (concrete_volume * cost_dict.get("Concrete Testing", 0) / wall_area) if wall_area > 0 else 0,

        # 🔹 Refuerzo desglosado
        "Steel Bars (H+V)": (bars_weight_m2 * (1 + waste_steel / 100) * cost_dict.get("Steel Bars", 0)),
        "Trimer Bar": (trimer_bar_m2 * (1 + waste_trimmer / 100) * cost_dict.get("Steel Bars", 0)),
        "U-Bar": (u_bar_m2 * (1 + waste_u_bar / 100) * cost_dict.get("Steel Bars", 0)),
        "Mesh": mesh_cost_per_m2 * (1 + waste_mesh / 100),
        "Reo Rate": (reo_rate * (wall_thickness / 1000)) * cost_dict.get("Steel Bars", 0),
        "Additional Reinforcement": (extra_steel_kg * cost_dict.get("Steel Bars", 0)) / wall_area if wall_area > 0 else 0,

        # 🔹 Otros elementos
        "Dowel Bars": (total_dowel_weight * cost_dict.get("Steel Bars", 0) / wall_area) if wall_area > 0 else 0,
        "Ripbox": (ripbox * (1 + waste_ripbox / 100) * cost_dict.get("Ripbox", 0) / wall_area) if wall_area > 0 else 0,
        "Ferrules": (ferrules * cost_dict.get("Ferrule with chair", 0) / wall_area) if wall_area > 0 else 0,
        "Threadbar": (Threadbar * cost_dict.get("Threadbar", 0) / wall_area) if wall_area > 0 else 0,
        "Couplers": (couplers * cost_dict.get("Couplers", 0) / wall_area) if wall_area > 0 else 0,
        "Lifting": ((lifters_per_panel * number_of_panels) * cost_dict.get("Lifting", 0) / wall_area) if wall_area > 0 else 0,
        "Special Accessories": special_accessories_per_m2 * cost_dict.get("Special Accessories", 0),

        # 🔹 Costos fijos por m²
        "Wages": cost_dict.get("Wages", 0),
        "Shopdrawings": cost_dict.get("Shopdrawings", 0),
        "Formwork": cost_dict.get("Formwork", 0),
        "Patching": cost_dict.get("Patching", 0)
    }

    # Inicialización de df_costs
    import pandas as pd
    from io import BytesIO

    # ✅ Definir unidades, cantidades y costos unitarios antes de mostrar resultados
    units = {
        "Concrete": "m³",
        "Concrete Testing": "m³",
        "Steel Bars (H+V)": "kg",
        "Trimer Bar": "kg",
        "U-Bar": "kg",
        "Mesh": "kg",
        "Reo Rate": "kg",
        "Additional Reinforcement": "kg",
        "Dowel Bars": "kg",
        "Ripbox": "m",
        "Ferrules": "ea",
        "Threadbar": "ea",
        "Couplers": "ea",
        "Lifting": "ea",
        "Special Accessories": "ea",
        "Wages": "m²",
        "Shopdrawings": "m²",
        "Formwork": "m²",
        "Patching": "m²"
    }

    # ➕ Agregar unidades para EO items personalizados
    for label in eo_costs.keys():
        if label.strip():
            units[label] = "m²"  # Unidades de los items EO como m²

    # ➕ Incluir todos los EO definidos por el usuario (añadir dinámicamente)
    for label, cost in eo_costs.items():
        if label and cost > 0:
            cost_per_m2[label] = cost

    # ➕ Incluir Additional Custom Elements definidos por el usuario
    for label, cost in additional_custom_elements.items():
        if label and cost > 0:
            cost_per_m2[label] = cost
            units[label] = "m²"

    # 📌 Calcular el total de los costos por m²
    total_cost_per_m2 = sum(cost_per_m2.values())  # Asegúrate de tener el total calculado

    # 📌 Cálculo del costo total del proyecto
    total_cost = total_cost_per_m2 * wall_area

    # ➕ Asegurar que las variables estén definidas antes del toggle de resultados
    reo_rate_m2 = reo_rate * (wall_thickness / 1000)
    reo_rate_total = reo_rate_m2 * wall_area
    extra_steel_kg_m2 = extra_steel_kg / wall_area if wall_area > 0 else 0

    # Cálculo de las cantidades (para todos los ítems, incluidos los EO)
    quantities = {
        "Concrete": (concrete_volume / wall_area if wall_area > 0 else 0) * (1 + waste_concrete / 100),
        "Concrete Testing": concrete_volume / wall_area if wall_area > 0 else 0,
        "Steel Bars (H+V)": bars_weight_m2 * (1 + waste_steel / 100),
        "Trimer Bar": trimer_bar_m2 * (1 + waste_trimmer / 100),
        "U-Bar": u_bar_m2 * (1 + waste_u_bar / 100),
        "Mesh": mesh_weight_m2 * (1 + waste_mesh / 100),
        "Reo Rate": reo_rate_m2,
        "Additional Reinforcement": extra_steel_kg_m2,
        "Dowel Bars": total_dowel_weight / wall_area if wall_area > 0 else 0,
        "Ripbox": (ripbox / wall_area if wall_area > 0 else 0) * (1 + waste_ripbox / 100),
        "Ferrules": ferrules / wall_area if wall_area > 0 else 0,
        "Threadbar": Threadbar / wall_area if wall_area > 0 else 0,
        "Couplers": couplers / wall_area if wall_area > 0 else 0,
        "Lifting": (lifters_per_panel * number_of_panels) / wall_area if wall_area > 0 else 0,
        "Special Accessories": special_accessories_per_m2,
        "Wages": 1,
        "Shopdrawings": 1,
        "Formwork": 1,
        "Patching": 1
    }

    # Agregar EO dinámicos a cantidades
    for label in eo_costs.keys():
        if label.strip():
            quantities[label] = 1  # todos los EO aplican por m²

    # Agregar adicionales dinámicos a cantidades
    for label in additional_custom_elements.keys():
        if label.strip():
            quantities[label] = 1  # todos los adicionales aplican por m²

    # Costo unitario por elemento (basado en cost_dict)
    unit_costs = {item: cost_dict.get(item, 0) for item in quantities}

    # ✅ CORREGIDO (Bug 4): ÚNICA fuente de verdad para "qué costo unitario de
    # cost_dict le corresponde a cada ítem del reporte". Antes existían DOS
    # versiones distintas de esta misma lógica en el archivo (una aquí, como una
    # cadena larga de if/elif, y otra más abajo, como diccionario, para la hoja
    # de auditoría del Excel) — podían divergir si se actualizaba una sin la otra.
    # Ahora ambas partes del archivo usan este mismo diccionario `cost_mapping`.
    #
    # Para "Mesh" en particular: ya no se usa el tipo de malla de la primera
    # sección (podía ser distinto al de otras secciones — ver Bug 2). Se calcula
    # un costo unitario promedio ponderado real: costo total de malla / peso
    # total de malla, consistente con el dinero que realmente se está cobrando.
    mesh_unit_price = safe_div(total_mesh_cost, total_mesh_weight) if total_mesh_weight > 0 else 0

    cost_mapping = {
        "Steel Bars (H+V)": "Steel Bars",
        "Trimer Bar": "Steel Bars",
        "U-Bar": "Steel Bars",
        "Reo Rate": "Steel Bars",
        "Additional Reinforcement": "Steel Bars",
        "Dowel Bars": "Steel Bars",
        "Mesh": None,  # se resuelve aparte con mesh_unit_price (ver abajo)
        "Concrete": concrete_type,
        "Concrete Testing": "Concrete Testing",
        "Ripbox": "Ripbox",
        "Ferrules": "Ferrule with chair",
        "Threadbar": "Threadbar",
        "Couplers": "Couplers",
        "Lifting": "Lifting",
        "Special Accessories": "Special Accessories",
        "Wages": "Wages",
        "Shopdrawings": "Shopdrawings",
        "Formwork": "Formwork",
        "Patching": "Patching",
    }
    # Agregar EO e ítems adicionales personalizados al mapping (se resuelven
    # directamente desde eo_costs / custom_additional_info, no desde cost_dict)
    for eo_label in eo_costs:
        cost_mapping[eo_label] = eo_label


    def resolve_unit_cost(item_name):
        """Única función que decide el costo unitario ($) de un ítem del reporte.
        Usada tanto para la tabla en pantalla como para la hoja de auditoría del Excel."""
        if item_name in custom_additional_info:
            return custom_additional_info[item_name]["cost"]
        if item_name in eo_costs:
            return eo_costs[item_name]
        if item_name == "Mesh":
            return mesh_unit_price
        mapped_item = cost_mapping.get(item_name, item_name)
        return cost_dict.get(mapped_item, 0)


    # ➕ Crear df_costs vacío con las columnas necesarias, añadiendo los items
    df_costs = pd.DataFrame({
        "Item": list(cost_per_m2.keys()),
        "Unit": [custom_additional_info[k]["unit"] if k in custom_additional_info else units.get(k, "") for k in cost_per_m2.keys()],
        "Unit Cost ($)": [resolve_unit_cost(k) for k in cost_per_m2.keys()],
        "Total Qty for m²": [quantities.get(k, 0) for k in cost_per_m2.keys()],
        "Cost per m² ($)": list(cost_per_m2.values()),
        "Cost sharing (%)": [
        round((cost / total_cost_per_m2) * 100, 2) if total_cost_per_m2 > 0 else 0
        for cost in cost_per_m2.values()
    ]

    })
    # ➕ Agregar fila final: Total Cost
    df_costs.loc[len(df_costs.index)] = [
        "Total Cost", "", "", "", round(total_cost_per_m2, 2), 100.0
    ]


    # Inicializamos reinforcement_desc con un valor por defecto
    reinforcement_desc = "No reinforcement data"

    # Lógica para definir reinforcement_desc dependiendo de los datos disponibles
    if reo_rate > 0:
        reinforcement_desc = f"Reo Rate: {reo_rate} kg/m³"
    elif extra_steel_kg > 0:
        reinforcement_desc = f"Additional Steel Reinforcement: {extra_steel_kg} kg"

    _wall_section_rows = []
    for _i, _sec in enumerate(detailed_sections_data):
        _parts = []
        if _sec["horizontal_bar"] and _sec["horizontal_spacing"] > 0:
            _parts.append(f"H: {_sec['horizontal_bar']} @ {_sec['horizontal_spacing']}mm ({_sec['horizontal_placement']})")
        if _sec["vertical_bar"] and _sec["vertical_spacing"] > 0:
            _parts.append(f"V: {_sec['vertical_bar']} @ {_sec['vertical_spacing']}mm ({_sec['vertical_placement']})")
        if _sec["mesh_reinforcement"] == "Yes" and _sec["mesh_type"]:
            _parts.append(f"Mesh: {_sec['mesh_type']} ({_sec['mesh_placement']})")
        if _sec["trimer_bar"]:
            _parts.append(f"Trimer: {_sec['trimer_bar']} ({_sec['trimer_placement']})")
        if _sec.get("u_bar_type") and _sec.get("u_bar_spacing", 0) > 0:
            _parts.append(f"U-Bar: {_sec['u_bar_type']} @ {_sec['u_bar_spacing']}mm ({_sec['u_bar_location']})")
        _wall_section_rows.append((f"Section {_i + 1}", ", ".join(_parts) if _parts else "Not configured"))

    if dowels == "Yes":
        if dowel_calculation_method == "Enter Manually":
            _dowel_row = ("Dowels", f"Manual entry — {total_dowel_weight:.2f} kg total")
        elif dowel_bar_type:
            _dowel_row = ("Dowels", f"{dowel_bar_type} @ {dowel_spacing}mm — {total_dowel_weight:.2f} kg total")
        else:
            _dowel_row = ("Dowels", "Configured but incomplete")
    else:
        _dowel_row = ("Dowels", "Not included")

    walls_audit_rows = [
        (">>> GEOMETRY", ""),
        ("Element Type", element_type or "N/A"),
        ("Wall Area (m²)", wall_area), ("Wall Thickness (mm)", wall_thickness),
        ("Number of Panels", number_of_panels), ("Concrete Type", concrete_type),
        ("Average Panel Height (m)", avg_panel_height),

        (">>> REINFORCEMENT", ""),
        ("Apply Lap Splice", "Yes" if apply_lap_splice else "No"),
        ("Reo Rate (kg/m³)", reo_rate if reo_rate > 0 else "Not used"),
        ("Additional Steel Reinforcement (kg)", extra_steel_kg if extra_steel_kg > 0 else "Not used"),
    ] + _wall_section_rows + [
        _dowel_row,
        ("Total Steel Weight (kg)", round(total_steel_weight, 2)),
        ("Total Steel per m² (kg/m²)", round(total_steel_weight_m2, 2)),

        (">>> WASTE FACTORS APPLIED", ""),
        ("Waste % applied to", waste_summary),

        (">>> UNIT RATES USED (from Cost Settings)", ""),
        (f"Concrete — {concrete_type or 'n/a'} ($/m³)", cost_dict.get(concrete_type, 0)),
        ("Concrete Testing ($/m³)", cost_dict.get("Concrete Testing", 0)),
        ("Wages ($/m²)", cost_dict.get("Wages", 0)),
        ("Shopdrawings ($/m²)", cost_dict.get("Shopdrawings", 0)),
        ("Formwork ($/m²)", cost_dict.get("Formwork", 0)),
        ("Patching ($/m²)", cost_dict.get("Patching", 0)),

        (">>> RESULTS", ""),
        ("Total Cost per m² ($) — PRIMARY", round(total_cost_per_m2, 2)),
        ("Total Cost ($) — reference", round(total_cost_per_m2 * wall_area, 2)),
    ]

    # 📦 Exportar el reporte a Excel con hoja de auditoría
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book

        # --------- Hoja PRINCIPAL: Report ----------
        df_costs.to_excel(writer, sheet_name="Report", startrow=6, index=False)
        worksheet = writer.sheets["Report"]

        # Encabezados
        worksheet.write("A1", f"Project Code: {project_code}" if project_code else "Project Code: N/A")
        worksheet.write("A2", f"Element Type: {element_type}" if element_type else "Element Type: N/A")

        # Descripción del refuerzo
        reinforcement_parts = []
        for section in detailed_sections_data:
            if section["vertical_bar"] and section["vertical_spacing"] > 0:
                reinforcement_parts.append(f"{section['vertical_bar']}-{section['vertical_spacing']} {section['vertical_placement']} Ver")
            if section["horizontal_bar"] and section["horizontal_spacing"] > 0:
                reinforcement_parts.append(f"{section['horizontal_bar']}-{section['horizontal_spacing']} {section['horizontal_placement']} Hor")
            if section["mesh_reinforcement"] == "Yes" and section["mesh_type"]:
                reinforcement_parts.append(f"{section['mesh_type']} Mesh")
            if section["trimer_bar"]:
                reinforcement_parts.append(f"{section['trimer_bar']} Trimer Bar")
            if section["u_bar_type"] and section["u_bar_spacing"] > 0:
                reinforcement_parts.append(f"{section['u_bar_type']}-{section['u_bar_spacing']} U-Bar {section['u_bar_location']}")
        if reo_rate > 0:
            reinforcement_parts.append(f"{reo_rate:.0f} kg/m³ Reo Rate")
        if extra_steel_kg > 0:
            reinforcement_parts.append(f"{extra_steel_kg:.0f} kg Extra Reinforcement")

        worksheet.write("A3", "Reinforcement: " + ", ".join(reinforcement_parts))
        worksheet.write("A4", f"Number of Panels: {number_of_panels}")
        worksheet.write("A5", f"Total Wall Area: {wall_area:.2f} m²")
        worksheet.write("A6", f"Wall Thickness: {wall_thickness} mm")

        # Formato
        bold_format = workbook.add_format({'bold': True})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1})
        money_format = workbook.add_format({'num_format': '$#,##0.00', 'border': 1})
        percent_format = workbook.add_format({'num_format': '0.00"%"', 'border': 1})
        border_format = workbook.add_format({'border': 1})
        total_row_format = workbook.add_format({'bold': True, 'bg_color': '#FFF2CC', 'border': 1})
        total_format = workbook.add_format({
        "bold": True,
        "bg_color": "#FFF2CC",
        "border": 1,
        "num_format": "$#,##0.00"
        })



        for col_num, value in enumerate(df_costs.columns.values):
            worksheet.write(6, col_num, value, header_format)

        for i, row in df_costs.iterrows():
            row_num = 7 + i
            is_total = row["Item"] == "Total Cost"
            for col_num, val in enumerate(row):
                if is_total:
                    fmt = total_row_format if col_num != 4 else workbook.add_format({'bold': True, 'num_format': '$#,##0.00', 'bg_color': '#FFF2CC', 'border': 1})
                    if col_num == 5:
                        fmt = workbook.add_format({'bold': True, 'num_format': '0.00"%"', 'bg_color': '#FFF2CC', 'border': 1})
                else:
                    fmt = money_format if col_num in [2, 4] else (percent_format if col_num == 5 else border_format)
                worksheet.write(row_num, col_num, val, fmt)

        worksheet.freeze_panes(7, 0)
        worksheet.set_column("A:A", 24)
        worksheet.set_column("B:B", 10)
        worksheet.set_column("C:D", 18)
        worksheet.set_column("E:F", 18)

        # --------- Hoja de Auditoría ----------
        audit_sheet = workbook.add_worksheet("Audit_Calculations")
        audit_sheet.write("A1", f"Element Type: {element_type}" if element_type else "Element Type: N/A", bold_format)

        _subsection_fmt = workbook.add_format({"bold": True, "bg_color": "#E4E1D9"})
        _r_audit = 2
        for _label, _value in walls_audit_rows:
            if _label.startswith(">>> "):
                audit_sheet.write(_r_audit, 0, _label.replace(">>> ", ""), _subsection_fmt)
                audit_sheet.write(_r_audit, 1, "", _subsection_fmt)
            else:
                audit_sheet.write(_r_audit, 0, _label)
                audit_sheet.write(_r_audit, 1, str(_value))
            _r_audit += 1

        audit_sheet.set_column("A:A", 40)
        audit_sheet.set_column("B:B", 24)





    if wall_area > 0 and wall_thickness > 0 and number_of_panels > 0 and avg_panel_height > 0:
        show_results = st.toggle(":material/bar_chart: Show Details (results & cost breakdown)", value=False)
        show_cost_breakdown = show_results

        if show_results:
            st.markdown("## 📊 Results")

            # 🔸 📌 Concrete Info
            st.markdown(f"""
            <div class="card">
                <div class="subtitle"><span class="pw-icon-badge"><span class="pw-icon">foundation</span></span>Concrete Information</div>
                <ul>
                    <li><b>Concrete Volume:</b> {(concrete_volume * (1 + waste_concrete / 100)):.2f} m³</li>
                    <li><b>Concrete Testing:</b> {concrete_volume:.2f} m³</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            # 🔸 📌 Steel Summary con Breakdown como expander
            steel_per_m3 = total_steel_weight / concrete_volume if concrete_volume > 0 else 0
            st.markdown(f"""
            <div class="card">
                <div class="subtitle"><span class="pw-icon-badge"><span class="pw-icon">hardware</span></span>Steel Reinforcement Summary</div>
                <ul>
                    <li><b>Total Steel Weight:</b> {total_steel_weight:.2f} kg</li>
                    <li><b>Total Steel per m²:</b> {total_steel_weight_m2:.2f} kg/m²</li>
                    <li><b>Reinforcement Ratio:</b> {steel_per_m3:.1f} kg/m³ of concrete</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("View Reinforcement Breakdown", icon=":material/table_rows:", expanded=False):
                st.markdown(f"""
                <div class="card">
                    <div class="subtitle"><span class="pw-icon-badge"><span class="pw-icon">table_rows</span></span>Breakdown of Steel Reinforcement</div>
                    <table style="width:100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #f0f0f0;">
                                <th style="text-align:left; padding: 6px;">Component</th>
                                <th style="text-align:right; padding: 6px;">kg/m²</th>
                                <th style="text-align:right; padding: 6px;">Total (kg)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="text-align:left; padding: 6px;">Reo Rate</td>
                                <td style="text-align:right; padding: 6px;">{reo_rate_m2:.2f}</td>
                                <td style="text-align:right; padding: 6px;">{reo_rate_total:.2f}</td>
                            </tr>
                            <tr>
                                <td style="text-align:left; padding: 6px;">Bars (H+V)</td>
                                <td style="text-align:right; padding: 6px;">{(bars_weight_m2 * (1 + waste_steel / 100)):.2f}</td>
                                <td style="text-align:right; padding: 6px;">{(bars_weight_total * (1 + waste_steel / 100)):.2f}</td>
                            </tr>
                            <tr>
                                <td style="text-align:left; padding: 6px;">Mesh</td>
                                <td style="text-align:right; padding: 6px;">{(mesh_weight_m2 * (1 + waste_mesh / 100)):.2f}</td>
                                <td style="text-align:right; padding: 6px;">{(total_mesh_weight * (1 + waste_mesh / 100)):.2f}</td>
                            </tr>
                            <tr>
                                <td style="text-align:left; padding: 6px;">Trimer Bar</td>
                                <td style="text-align:right; padding: 6px;">{trimer_bar_m2:.2f}</td>
                                <td style="text-align:right; padding: 6px;">{(trimer_bar_total * (1 + waste_trimmer / 100)):.2f}</td>
                            </tr>
                            <tr>
                                <td style="text-align:left; padding: 6px;">Additional Reinforcement</td>
                                <td style="text-align:right; padding: 6px;">{extra_steel_kg_m2:.2f}</td>
                                <td style="text-align:right; padding: 6px;">{extra_steel_kg:.2f}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)



            if any(k in cost_per_m2 for k in ["Ripbox", "Ferrules", "Threadbar", "Couplers", "Lifting", "Special Accessories"]):
                st.markdown(f"""
                <div class="card">
                    <div class="subtitle"><span class="pw-icon-badge"><span class="pw-icon">inventory_2</span></span>Additional Elements Summary</div>
                    <ul>
                """, unsafe_allow_html=True)

                for item in ["Ripbox", "Ferrules", "Threadbar", "Couplers", "Lifting", "Special Accessories"]:
                    if cost_per_m2.get(item, 0) > 0:
                        st.markdown(f"<li><b>{item}:</b> ${cost_per_m2[item]:.2f} per m²</li>", unsafe_allow_html=True)

                st.markdown("</ul></div>", unsafe_allow_html=True)

            if eo_costs:
                st.markdown(f"""
                <div class="card">
                    <div class="subtitle"><span class="pw-icon-badge"><span class="pw-icon">add_circle</span></span>EO Items (Optional)</div>
                    <ul>
                """, unsafe_allow_html=True)

                for label, cost in eo_costs.items():
                    st.markdown(f"<li><b>{label}:</b> ${cost:.2f} per m²</li>", unsafe_allow_html=True)

                st.markdown("</ul></div>", unsafe_allow_html=True)


        if show_cost_breakdown:
            st.markdown("### :material/payments: Cost Breakdown (per m²)")
            st.dataframe(
                df_costs,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Unit Cost ($)": st.column_config.NumberColumn(format="$%.2f"),
                    "Total Qty for m²": st.column_config.NumberColumn(format="%.2f"),
                    "Cost per m² ($)": st.column_config.NumberColumn(format="$%.2f"),
                    "Cost sharing (%)": st.column_config.NumberColumn(format="%.1f%%"),
                }
            )

        st.markdown(f"""
            <div class="pw-metric pw-metric-accent" style="text-align:center; padding: 1.5rem;">
                <div class="pw-metric-icon" style="margin: 0 auto 10px;"><span class="pw-icon">payments</span></div>
                <p class="pw-metric-label" style="font-size:14px;">Total cost per m²</p>
                <p class="pw-metric-value" style="font-size:32px;">${total_cost_per_m2:.2f}</p>
            </div>
        """, unsafe_allow_html=True)


        if st.button("➕ Add to Project Summary", key="walls_add_to_summary_btn"):
            add_to_project_summary("Walls", element_type, "m²", total_cost_per_m2, total_cost_per_m2 * wall_area,
                                    inputs=walls_audit_rows, cost_breakdown=df_costs)
            st.toast("Added to Project Summary", icon=":material/check_circle:")

        # Descarga del reporte — último paso, una vez que ya se revisaron los
        # resultados en pantalla (antes aparecía antes de verlos).
        st.download_button(
            label="Download Excel Report",
            icon=":material/download:",
            data=output.getvalue(),
            file_name=f"{project_code}_{element_type}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
            st.warning("Please enter wall area, thickness, number of panels, and average panel height greater than zero to start calculations.", icon=":material/warning:")


if st.session_state.estimate_type == "Walls":
    render_walls_tab()

st.markdown(
    f"""<div style="text-align:center; color:var(--pw-text-muted, #999); font-size:12px; margin-top:2rem;">
    Build: {APP_BUILD_VERSION}
    </div>""",
    unsafe_allow_html=True,
)
