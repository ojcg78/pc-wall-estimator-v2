import os
import streamlit as st
import pandas as pd
import random as rand

import streamlit as st

# --- Utilidad: divide solo si el denominador es > 0 ---
def safe_div(n, d):
    try:
        return n / d if (d is not None and d > 0) else 0.0
    except Exception:
        return 0.0


# --- Protección por contraseña simple ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "Precast123":  # << Cambia aquí la clave que quieras
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 🔒 Borra la contraseña ingresada del estado
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔒 Enter Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔒 Enter Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Incorrect password, try again.")
        return False
    else:
        return True

# 🚪 Detener la app si no se ingresa correctamente la contraseña
if not check_password():
    st.stop()

st.markdown("""
    <style>
    /* Fuente base y fondo */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f8f9fa;
    }

    /* Títulos y subtítulos */
    .title {
        font-size: 28px;
        font-weight: 600;
        color: #003366;
        padding-top: 10px;
        padding-bottom: 5px;
    }

    .subtitle {
        font-size: 20px;
        font-weight: 500;
        color: #205375;
        padding-bottom: 10px;
    }

    /* Bloques destacados */
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* Texto resaltado */
    .highlight {
        color: #c0392b;
        font-weight: bold;
    }

    /* Separadores */
    hr {
        border: none;
        border-top: 1px solid #ccc;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)


# 🧠 Inicializar el número de secciones de refuerzo detallado
if 'num_detail_sections' not in st.session_state:
    st.session_state.num_detail_sections = 1

# 🎨 Estilo CSS personalizado para mejorar visualmente la interfaz
st.markdown("""
    <style>
        /* Ajustar el ancho de la página */
        .main {
            max-width: 95%;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        /* Encabezados bonitos */
        h1, h2, h3, h4 {
            color: #2C3E50;
        }

        /* Subrayado para secciones */
        .block-container > div > h3 {
            border-bottom: 1px solid #DDD;
            padding-bottom: 0.2rem;
            margin-bottom: 1rem;
        }

        /* Texto de resultados en negrita y espaciado */
        .result-line {
            font-weight: 600;
            margin-bottom: 0.4rem;
        }

        /* Colores para iconos */
        .element-icon::before {
            content: "🔹";
            margin-right: 0.3rem;
            color: #3498db;
        }

        /* Cost Summary listado */
        .cost-summary {
            font-size: 0.95rem;
            line-height: 1.5;
        }

        /* Separación entre secciones */
        .section-block {
            margin-top: 2rem;
        }

        /* Botón de descarga centrado */
        .stDownloadButton {
            margin-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)


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
}



concrete_options = ["Concrete 50 MPa", "Concrete 65 MPa", "Concrete 50 MPa (Special Mix)"]

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

if os.path.exists(COSTS_FILE):
    costs_df = pd.read_csv(COSTS_FILE)
else:
    costs_df = pd.DataFrame(default_costs_data)


from PIL import Image
import base64
from io import BytesIO

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
    <div style='display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;'>
        <img src='data:image/png;base64,{logo_base64}' width='50' style='margin-right: 15px;'/>
        <h1 style='color:#003366; margin: 0;'>Precast Wall Cost Estimator</h1>
    </div>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* Anchura de la página */
.main {
    max-width: 1200px;
    padding: 2rem;
}

/* Encabezado general */
h2 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

/* Subtítulos */
h3 {
    color: #2980b9;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
}

/* Texto resaltado */
strong {
    color: #34495e;
}

/* Ajuste de los ítems listados */
ul {
    padding-left: 1.5rem;
}

li {
    margin-bottom: 0.5rem;
}

/* Resultados individuales */
div[data-testid="stMarkdownContainer"] ul {
    margin-top: 0;
    margin-bottom: 1rem;
}

/* Subsecciones como Breakdown */
.breakdown-title {
    font-weight: bold;
    font-size: 1rem;
    color: #555;
    margin-top: 1rem;
}

/* Cost summary con indentación */
.cost-summary-item {
    padding-left: 10px;
    margin-bottom: 4px;
}

/* Aumentar tamaño del botón de descarga */
button[title="Download"] {
    font-size: 16px;
    padding: 0.75em 1.5em;
}
</style>
""", unsafe_allow_html=True)

# 🔧 Función para calcular barras horizontales y verticales
def calculate_rebar_weight(area, spacing_h, spacing_v, bar_type_h, bar_type_v, placement_h, placement_v):
    spacing_h /= 1000 if spacing_h else 1  # Convertir a metros, evita división por 0
    spacing_v /= 1000 if spacing_v else 1

    total_length_per_m2_h = 0
    total_length_per_m2_v = 0
    total_weight_m2 = 0

    if bar_type_h:
        diameter_h = bar_diameter_lookup[bar_type_h]
        lap_factor_h = 1 + (40 * diameter_h / 6000) if apply_lap_splice else 1
        factor_placement_h = 2 if placement_h == "EF" else 1
        bars_per_meter_h = 1 / spacing_v if spacing_v > 0 else 0  # Espaciamiento vertical
        total_length_per_m2_h = bars_per_meter_h * lap_factor_h * factor_placement_h
        total_weight_m2 += total_length_per_m2_h * steel_weight_lookup[bar_type_h]

    if bar_type_v:
        diameter_v = bar_diameter_lookup[bar_type_v]
        lap_factor_v = 1 + (40 * diameter_v / 6000) if apply_lap_splice else 1
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
def calculate_trimer_bar_weight(area, num_panels, wall_thickness, trimer_type, placement, apply_lap, opening_area, num_openings):
    if not trimer_type or num_panels == 0:
        return 0, 0

    avg_width = area / num_panels if num_panels > 0 else 0
    perimeter_per_panel = 2 * (avg_width + (wall_thickness / 1000))
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



def calculate_section_weight(section, area, wall_thickness, apply_lap, num_panels, opening_area, num_openings):
    bars_weight_m2, bars_weight_total = calculate_rebar_weight(
        area,
        section["horizontal_spacing"],
        section["vertical_spacing"],
        section["horizontal_bar"],
        section["vertical_bar"],
        section["horizontal_placement"],
        section["vertical_placement"]
    )

    if section["mesh_reinforcement"] == "Yes":
        mesh_weight_total = calculate_mesh_weight(area, section["mesh_type"], section["mesh_placement"], apply_lap)
    else:
        mesh_weight_total = 0

    trimer_bar_m2, trimer_weight_total = calculate_trimer_bar_weight(
        area, num_panels, wall_thickness,
        section["trimer_bar"], section["trimer_placement"], apply_lap,
        opening_area, num_openings
    )

    return {
        "bars_total": bars_weight_total,
        "mesh_total": mesh_weight_total,
        "trimer_total": trimer_weight_total
    }



# 📌 Código del proyecto ingresado por el usuario
project_code = st.text_input("Enter Project Code", placeholder="e.g. A4980 - Beard")

# 📌 Código del proyecto ingresado por el usuario
element_type = st.text_input("Enter Element Type", placeholder="e.g. PT1")

# Editable Costs Table
if st.checkbox("Show Editable Cost Table"):
    with st.expander("🧾 Editable Costs Table", expanded=True):
        edited_df = st.data_editor(costs_df, num_rows="dynamic")

        # 🔄 Reset dentro del bloque editable
        st.markdown("---")
        st.markdown("### ⚠️ Reset Costs to Default")
        confirm_reset = st.checkbox("I confirm I want to reset all costs to default values")

        if st.button("🔄 Reset Costs", disabled=not confirm_reset):
            costs_df = pd.DataFrame(default_costs_data)
            costs_df.to_csv(COSTS_FILE, index=False)
            st.success("✅ Costs reset to default successfully! Please reload the page.")

        # 🔹 Guardar edición automáticamente
        if edited_df is not None:
            edited_df.to_csv(COSTS_FILE, index=False)
            cost_dict = dict(zip(edited_df["Element"], edited_df["Cost"]))

else:
    cost_dict = dict(zip(costs_df["Element"], costs_df["Cost"]))

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
# Agrupación de Inputs
# 📐 Panel Dimensions
with st.expander("📐 Panel Dimensions"):
    number_of_panels = st.number_input(
        "Number of Panels",
        min_value=0,
        value=0,
        step=1,
        key="num_panels_input",
    )

    wall_area = float_input(
        "Total Wall Area (m²)",
        key="wall_area_input_text",
        default=0.0,
        decimals=4,
        min_value=0.0,
    )


    wall_thickness = st.number_input(
        "Wall Thickness (mm)",
        min_value=0,
        value=0,
        step=10,
        key="wall_thickness_input",
    )

    concrete_type = st.selectbox(
        "Concrete Type",
        concrete_options,
        index=0,
        key="concrete_type_select",
    )


with st.expander("🪟 Openings"):
    has_openings = st.radio("Do the panels have openings?", ["No", "Yes"], index=0)
    if has_openings == "Yes":
        opening_area = float_input("Total Openings Area (m²)", key="opening_area_input_text", default=0.0, decimals=4, min_value=0.0)
        number_of_openings = st.number_input("Number of Openings", min_value=0, value=0)
    else:
        opening_area = 0
        number_of_openings = 0

# 🔹 Reinforcement
with st.expander("🪢 Reinforcement"):
    reo_rate = st.number_input("Reo Rate (kg/m³) (optional)", min_value=0.0, value=0.0)
    use_reo_rate_only = st.radio("Use only Reo Rate or add to bars/mesh?", ["Add to bars and mesh", "Use only Reo Rate"], index=0, key="use_reo_option")
    apply_lap_splice = st.checkbox("Apply Lap Splice (40d for bars, 20% for mesh)", value=True)
    extra_steel_kg = st.number_input("Additional Steel Reinforcement (kg)", min_value=0.0, step=1.0, key="extra_steel_input_main")

    # 🔸 Sub-secciones de refuerzo dentro del mismo expander
    st.markdown("### 🟠 Bars and Mesh Sections")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("➕ Add Bars and Mesh Section"):
            st.session_state.num_detail_sections += 1
    with col2:
        if st.button("➖ Remove Last Section") and st.session_state.num_detail_sections > 1:
            st.session_state.num_detail_sections -= 1

    detailed_sections_data = []
    for i in range(st.session_state.num_detail_sections):
        with st.container(border=True):
            st.markdown(f"### 💠 Bars and Mesh Section {i + 1}")
            section_data = detailed_reinforcement_section(i, steel_weight_lookup, mesh_weight_lookup)
            detailed_sections_data.append(section_data)

    

    # 📦 Steel Weight por Sección
    st.markdown("### 📦 Steel Weight per Section")
    total_section_weight = 0
    for i, section in enumerate(detailed_sections_data):
        result = calculate_section_weight(
            section, wall_area, wall_thickness,
            apply_lap_splice, number_of_panels,
            opening_area, number_of_openings
        )
        section_weight = result["bars_total"] + result["mesh_total"] + result["trimer_total"]
        total_section_weight += section_weight
        st.write(f"🔹 Section {i+1}: {section_weight:.2f} kg")

    # ➕ Reo Rate total
    reo_rate_kg_total = (reo_rate * (wall_thickness / 1000)) * wall_area if reo_rate > 0 else 0
    if reo_rate_kg_total > 0:
        st.write(f"➕ Reo Rate: {reo_rate_kg_total:.2f} kg")

    # ➕ Refuerzo adicional
    if extra_steel_kg > 0:
        st.write(f"➕ Additional Steel: {extra_steel_kg:.2f} kg")

    # 🔸 Total general
    total_steel_weight = total_section_weight + reo_rate_kg_total + extra_steel_kg
    st.success(f"🔸 Total Steel Reinforcement: {total_steel_weight:.2f} kg")

    # 🔚 Mostrar total de secciones solamente
    st.success(f"🔸 Total Combined Steel Weight (sections only): {total_section_weight:.2f} kg")



# 🔹 Dowels (SEPARADO)
with st.expander("🔹 Dowels"):
    dowels = st.radio("Dowels", ["No", "Yes"])
    total_dowel_weight = 0  # 🔹 Inicialización

    if dowels == "Yes":
        dowel_calculation_method = st.radio("Dowel Weight Calculation", ["Calculate Automatically", "Enter Manually"])

        if dowel_calculation_method == "Enter Manually":
            total_dowel_weight = st.number_input("Total Dowels Weight (kg)", min_value=0.0, value=0.0)

        else:  # 🔹 Cálculo Automático
            dowel_bar_type = st.selectbox("Dowel Bar Type", [""] + list(steel_weight_lookup.keys()))
            dowel_spacing = st.number_input("Dowel Spacing (mm)", min_value=0, step=10, value=0)

            # 🔹 Opción para ingresar la longitud manualmente o calcularla
            use_manual_length = st.checkbox("Enter Dowel Length Manually?")
            
            if use_manual_length:
                dowel_length = st.number_input("Dowel Length (m)", min_value=0.0, value=0.0)
            if dowel_bar_type:
                dowel_length = (40 * bar_diameter_lookup[dowel_bar_type] * 2) / 1000 + 0.02
            else:
                dowel_length = 0.0
                st.warning("Please select a valid Dowel Bar Type to calculate length.")



            # 🔹 Ancho promedio del panel (respetando límite de 4.2 m)
            if number_of_panels > 0:
                avg_panel_width = min(4.2, wall_area / number_of_panels)
            else:
                avg_panel_width = 0
                st.warning("Please enter number of panels greater than zero to calculate dowel bars.")


            # 🔹 Número de dowels por panel
            if dowel_spacing > 0:
                dowels_per_panel = avg_panel_width / (dowel_spacing / 1000)
                dowels_per_panel = int(dowels_per_panel) + (1 if dowels_per_panel % 1 > 0 else 0)
                total_dowels = dowels_per_panel * number_of_panels
                total_dowel_weight = total_dowels * dowel_length * steel_weight_lookup[dowel_bar_type]
            else:
                total_dowel_weight = 0
                st.warning("Please enter a valid Dowel Spacing greater than zero to calculate dowels.")



# 🔹 Additional Elements (SEPARADO)
with st.expander("🔩 Additional Elements"):
    ripbox = st.number_input("Ripbox (m)", value=0.0)
    ferrules = st.number_input("Ferrules (units)", value=0)
    Threadbar = st.number_input("Threadbar (units)", value=0)
    couplers = st.number_input("Couplers (units)", value=0)
    lifters_per_panel = st.number_input("Lifters per Panel", value=0)
    special_accessories_per_m2 = st.number_input("Special Accessories per m²", min_value=0.0, value=0.0, step=0.1)

    st.markdown("### ➕ Add Custom Additional Elements")
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


            if item_label.strip():
                if item_unit == "$/panel" and number_of_panels > 0:
                    additional_custom_elements[item_label.strip()] = safe_div((item_value * number_of_panels), wall_area)

                elif item_unit == "$/m²":
                    additional_custom_elements[item_label.strip()] = item_value
                elif item_unit == "$/unit":
                    additional_custom_elements[item_label.strip()] = (item_value * item_qty) / wall_area if wall_area > 0 else 0



with st.expander("➕ EO Items (Optional)", expanded=False):
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


        
        if eo_label.strip():
            if eo_unit == "$/panel" and number_of_panels > 0:
                eo_costs[eo_label.strip()] = safe_div((eo_value * number_of_panels), wall_area)

            elif eo_unit == "$/m²":
                eo_costs[eo_label.strip()] = eo_value




# 🔹 Cálculo Correcto del Steel Reinforcement (todos los componentes explícitos)

# 🔁 Cálculo acumulado desde secciones dinámicas
bars_weight_total = 0
mesh_weight_total = 0
trimer_bar_total = 0

for section in detailed_sections_data:
    result = calculate_section_weight(
        section, wall_area, wall_thickness,
        apply_lap_splice, number_of_panels,
        opening_area, number_of_openings
    )
    bars_weight_total += result["bars_total"]
    mesh_weight_total += result["mesh_total"]
    trimer_bar_total += result["trimer_total"]

# 🔹 Calcular peso por m²
bars_weight_m2 = bars_weight_total / wall_area if wall_area > 0 else 0
mesh_weight_m2 = mesh_weight_total / wall_area if wall_area > 0 else 0
trimer_bar_m2 = trimer_bar_total / wall_area if wall_area > 0 else 0

additional_reinforcement_kg_total = extra_steel_kg


# 🔹 Cálculo del peso total por m²
total_steel_weight_m2 = total_steel_weight / wall_area if wall_area > 0 else 0


# 📌 Cálculo del volumen de concreto
concrete_volume = wall_area * (wall_thickness / 1000)  # 🔹 Convertimos a metros cúbicos

    # 🔹 Waste % por elemento
with st.expander("♻️ Waste Factors (Optional)"):
    st.markdown("Enter a percentage of waste for each applicable item (leave at 0 if not needed):")

    # Diccionario base con nombres legibles y claves técnicas
    waste_items = {
        "Concrete": concrete_volume,
        "Steel Bars (H+V)": bars_weight_total,
        "Trimmer Bar": trimer_bar_total,
        "Mesh": mesh_weight_total,
        "Ripbox": ripbox
    }

    # Diccionarios para almacenar resultados
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

    # Asignar a las variables usadas en cálculos
    waste_concrete = waste_percentages.get("Concrete", 0.0)
    waste_steel = waste_percentages.get("Steel Bars (H+V)", 0.0)
    waste_trimmer = waste_percentages.get("Trimmer Bar", 0.0)
    waste_mesh = waste_percentages.get("Mesh", 0.0)
    waste_ripbox = waste_percentages.get("Ripbox", 0.0)

    # 🔹 Cálculo explícito del peso total combinado (con waste)
total_steel_weight = (
    reo_rate_kg_total * (1 + waste_steel / 100) +
    bars_weight_total * (1 + waste_steel / 100) +
    mesh_weight_total * (1 + waste_mesh / 100) +
    trimer_bar_total * (1 + waste_trimmer / 100) +
    additional_reinforcement_kg_total
)

  
# Cálculo de pesos individuales para costos separados
bars_weight_kg = bars_weight_m2 * wall_area
reo_rate_kg = (reo_rate * (wall_thickness / 1000)) * wall_area if reo_rate > 0 else 0


# 🟧 Obtener los datos de la primera sección de refuerzo
if detailed_sections_data:
    first_section = detailed_sections_data[0]
    mesh_type = first_section.get("mesh_type")
    mesh_reinforcement = first_section.get("mesh_reinforcement")

    # Calcular total_mesh_weight correctamente para evitar errores de None
    if mesh_reinforcement == "Yes" and mesh_type:
        total_mesh_weight = sum([
            calculate_mesh_weight(
                wall_area, sec["mesh_type"], sec["mesh_placement"], apply_lap_splice
    )
    for sec in detailed_sections_data
    if sec["mesh_reinforcement"] == "Yes" and sec["mesh_type"]
])

    else:
        total_mesh_weight = 0
else:
    total_mesh_weight = 0

# ✅ Inicializar por defecto para evitar errores
mesh_cost_per_m2 = 0
if mesh_reinforcement == "Yes" and mesh_type in cost_dict:
    if total_mesh_weight is not None:
        mesh_cost_per_m2 = safe_div((total_mesh_weight * cost_dict[mesh_type]), wall_area)

cost_per_m2 = {
    "Concrete": (
    (concrete_volume * (1 + waste_concrete / 100)) * cost_dict.get(concrete_type, 0) / wall_area
    if wall_area > 0 else 0
),


    "Concrete Testing": (concrete_volume * cost_dict.get("Concrete Testing", 0) / wall_area) if wall_area > 0 else 0,

    # 🔹 Refuerzo desglosado
    "Steel Bars (H+V)": (bars_weight_m2 * (1 + waste_steel / 100) * cost_dict.get("Steel Bars", 0)),
    "Trimer Bar": (trimer_bar_m2 * (1 + waste_trimmer / 100) * cost_dict.get("Steel Bars", 0)),
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

# ➕ Crear df_costs vacío con las columnas necesarias, añadiendo los items
df_costs = pd.DataFrame({
    "Item": list(cost_per_m2.keys()),
    "Unit": [custom_additional_info[k]["unit"] if k in custom_additional_info else units.get(k, "") for k in cost_per_m2.keys()],
    "Unit Cost ($)": [
        custom_additional_info[k]["cost"] if k in custom_additional_info else
        eo_costs.get(k, 0) if k in eo_costs else
        (cost_dict.get(section.get("mesh_type"), 0)
        if k == "Mesh" and any(sec.get("mesh_type") for sec in detailed_sections_data if sec["mesh_reinforcement"] == "Yes")
        else cost_dict.get("Steel Bars", 0) if k in [
            "Steel Bars (H+V)", "Trimer Bar", "Reo Rate", "Additional Reinforcement", "Dowel Bars"
        ]
        else cost_dict.get(concrete_type, 0) if k == "Concrete"
        else cost_dict.get("Concrete Testing", 0) if k == "Concrete Testing"
        else cost_dict.get("Ripbox", 0) if k == "Ripbox"
        else cost_dict.get("Ferrule with chair", 0) if k == "Ferrules"
        else cost_dict.get("Threadbar", 0) if k == "Threadbar"
        else cost_dict.get("Couplers", 0) if k == "Couplers"
        else cost_dict.get("Lifting", 0) if k == "Lifting"
        else cost_dict.get("Special Accessories", 0) if k == "Special Accessories"
        else cost_dict.get("Wages", 0) if k == "Wages"
        else cost_dict.get("Shopdrawings", 0) if k == "Shopdrawings"
        else cost_dict.get("Formwork", 0) if k == "Formwork"
        else cost_dict.get("Patching", 0) if k == "Patching"
        else 0)
        for k in cost_per_m2.keys()
    ],

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
    audit_sheet.write("A3", "PROJECT INPUTS", bold_format)

    audit_data = [
        ("Project Code", project_code if project_code else "N/A"),
        ("Total Wall Area (m²)", wall_area),
        ("Number of Panels", number_of_panels),
        ("Wall Thickness (mm)", wall_thickness),
        ("Openings Area (m²)", opening_area),
        ("Number of Openings", number_of_openings),
        ("Concrete Type", concrete_type),
        ("Waste Steel (%)", waste_steel),
        ("Waste Concrete (%)", waste_concrete),
        ("Apply Lap Splice?", "Yes" if apply_lap_splice else "No"),
    ]
    for idx, (label, val) in enumerate(audit_data, start=5):
        audit_sheet.write(f"A{idx}", label)
        audit_sheet.write(f"B{idx}", val)

    # 🔹 Sección de Reforzamiento Total
    start_row = idx + 2
    audit_sheet.write(f"A{start_row}", "REINFORCEMENT SUMMARY", bold_format)
    start_row += 1
    audit_sheet.write(f"A{start_row}", "Total Steel Weight (kg)")
    audit_sheet.write(f"B{start_row}", total_steel_weight)
    start_row += 1
    audit_sheet.write(f"A{start_row}", "Total Steel per m² (kg/m²)")
    audit_sheet.write(f"B{start_row}", total_steel_weight_m2)

    # 🔹 Detalle por sección de refuerzo
    start_row += 2
    audit_sheet.write(f"A{start_row}", "DETAILED SECTIONS", bold_format)
    start_row += 1
    audit_sheet.write(f"A{start_row}", "Section")
    audit_sheet.write(f"B{start_row}", "Bars (kg)")
    audit_sheet.write(f"C{start_row}", "Mesh (kg)")
    audit_sheet.write(f"D{start_row}", "Trimer Bar (kg)")

    for i, section in enumerate(detailed_sections_data):
        result = calculate_section_weight(
        section, wall_area, wall_thickness,
        apply_lap_splice, number_of_panels,
        opening_area, number_of_openings
    )
    start_row += 1
    audit_sheet.write(f"A{start_row}", f"Section {i+1}")
    audit_sheet.write(f"B{start_row}", result["bars_total"])
    audit_sheet.write(f"C{start_row}", result["mesh_total"])
    audit_sheet.write(f"D{start_row}", result["trimer_total"])

    # 🔹 Refuerzo Adicional y Reo Rate
    start_row += 2
    audit_sheet.write(f"A{start_row}", "Additional Steel (kg)")
    audit_sheet.write(f"B{start_row}", extra_steel_kg)
    start_row += 1
    audit_sheet.write(f"A{start_row}", "Reo Rate (kg)")
    audit_sheet.write(f"B{start_row}", reo_rate_kg_total)

    # 🔹 COST SUMMARY PER COMPONENT (usando cantidades reales)
    start_row += 1  # 🔹 Añade una fila vacía para separación visual
    audit_sheet.write(start_row, 0, "COST SUMMARY PER COMPONENT", header_format)
    start_row += 2
    headers = ["Component", "Quantity", "Unit", "Unit Price", "Total Cost"]
    for col_num, header in enumerate(headers):
        audit_sheet.write(start_row, col_num, header, header_format)
    start_row += 1

    summary_total = 0.0

    # Construir el mapa entre los nombres en la hoja de auditoría y las claves reales en cost_dict
    cost_mapping = {
        "Steel Bars (H+V)": "Steel Bars",
        "Trimer Bar": "Steel Bars",
        "Reo Rate": "Steel Bars",
        "Additional Reinforcement": "Steel Bars",
        "Mesh": mesh_type if mesh_type else "Mesh",
        "Concrete": concrete_type,
        "Concrete Testing": "Concrete Testing",
        "Dowel Bars": "Steel Bars",
        "Ripbox": "Ripbox",
        "Ferrules": "Ferrule with chair",
        "Threadbar": "Threadbar",
        "Couplers": "Couplers",
        "Lifting": "Lifting",
        "Special Accessories": "Special Accessories",
        "Wages": "Wages",
        "Shopdrawings": "Shopdrawings",
        "Formwork": "Formwork",
        "Patching": "Patching"
    }

    # Agregar EO personalizados al mapping
    for eo_label in eo_costs:
        cost_mapping[eo_label] = eo_label

    for item in df_costs["Item"]:
        if item == "Total Cost":
            continue

        unit = units.get(item, "")
        mapped_item = cost_mapping.get(item, item)

        # Obtener precio unitario
        if item in eo_costs:
            unit_price = eo_costs[item]
        elif mapped_item in cost_dict:
            unit_price = cost_dict.get(mapped_item, 0)
        else:
            unit_price = 0

        # Definir ítems fijos por m² (no multiplicar)
        fixed_m2_items = ["Wages", "Shopdrawings", "Formwork", "Patching", "EO - Special FW"]

        if item in eo_costs:
            qty_total = wall_area  # EO siempre por m²
        elif item in fixed_m2_items:
            qty_total = wall_area
        elif unit == "m":
            qty_total = ripbox * (1 + waste_ripbox / 100)
        else:
            qty_total = quantities.get(item, 0) * wall_area  # Escalar por área

        total_cost_item = qty_total * unit_price
        summary_total += total_cost_item

        audit_sheet.write(start_row, 0, item, border_format)
        audit_sheet.write(start_row, 1, qty_total, border_format)
        audit_sheet.write(start_row, 2, unit, border_format)
        audit_sheet.write(start_row, 3, unit_price, money_format)  # <-- ESTE FORMATO AGREGA $
        audit_sheet.write(start_row, 4, total_cost_item, money_format)
        start_row += 1




    # 🔸 Fila Total Cost con formato uniforme (sin salto ni ruptura visual)
    audit_sheet.write(start_row, 0, "Total Cost", total_row_format)
    audit_sheet.write(start_row, 1, "", total_row_format)
    audit_sheet.write(start_row, 2, "", total_row_format)
    audit_sheet.write(start_row, 3, "", total_row_format)
    audit_sheet.write(start_row, 4, summary_total, total_format)





# ✅ Botón de descarga
st.download_button(
    label="📥 Download Excel Report",
    data=output.getvalue(),
    file_name=f"{project_code}_{element_type}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


if wall_area > 0 and wall_thickness > 0 and number_of_panels > 0:
    # Mostrar resultados
    show_results = st.toggle("📊 Show Results", value=False)

    if show_results:
        st.markdown("## 📊 Results")

        # 🔸 📌 Concrete Info
        st.markdown(f"""
        <div class="card">
            <div class="subtitle">🧱 Concrete Information</div>
            <ul>
                <li><b>Concrete Volume:</b> {(concrete_volume * (1 + waste_concrete / 100)):.2f} m³</li>
                <li><b>Concrete Testing:</b> {concrete_volume:.2f} m³</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # 🔸 📌 Steel Summary con Breakdown como expander
        st.markdown(f"""
        <div class="card">
            <div class="subtitle">🔩 Steel Reinforcement Summary</div>
            <ul>
                <li><b>Total Steel Weight:</b> {total_steel_weight:.2f} kg</li>
                <li><b>Total Steel per m²:</b> {total_steel_weight_m2:.2f} kg/m²</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🔍 View Reinforcement Breakdown", expanded=False):
            st.markdown(f"""
            <div class="card">
                <div class="subtitle">🧱 Breakdown of Steel Reinforcement</div>
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
                <div class="subtitle">📦 Additional Elements Summary</div>
                <ul>
            """, unsafe_allow_html=True)

            for item in ["Ripbox", "Ferrules", "Threadbar", "Couplers", "Lifting", "Special Accessories"]:
                if cost_per_m2.get(item, 0) > 0:
                    st.markdown(f"<li><b>{item}:</b> ${cost_per_m2[item]:.2f} per m²</li>", unsafe_allow_html=True)

            st.markdown("</ul></div>", unsafe_allow_html=True)

        if eo_costs:
            st.markdown(f"""
            <div class="card">
                <div class="subtitle">➕ EO Items (Optional)</div>
                <ul>
            """, unsafe_allow_html=True)

            for label, cost in eo_costs.items():
                st.markdown(f"<li><b>{label}:</b> ${cost:.2f} per m²</li>", unsafe_allow_html=True)

            st.markdown("</ul></div>", unsafe_allow_html=True)


    if st.toggle("💲 Show Cost Summary", value=False):
        st.markdown("### 💲 Cost Summary (per m²)")
        for item, cost in cost_per_m2.items():
            st.write(f"   - **{item}:** ${cost:.2f}")

    st.markdown(f"""
        <div style="
            padding: 1rem;
            background-color: #eaf6ff;
            border-left: 6px solid #3498db;
            margin-top: 2rem;
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;">
            💰 Total Cost per m²: ${total_cost_per_m2:.2f}
        </div>
    """, unsafe_allow_html=True)

else:
        st.warning("Please enter wall area, thickness, and number of panels greater than zero to start calculations.")
