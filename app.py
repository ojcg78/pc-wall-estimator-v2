import os
import streamlit as st
import pandas as pd

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

concrete_options = ["Concrete 50 MPa", "Concrete 60 MPa", "Concrete 50 MPa (Special Mix)"]

# 📁 Archivo CSV donde se guardarán los costos
COSTS_FILE = "costos_guardados.csv"

# 📌 Cargar costos si el archivo ya existe, si no, usa costos predeterminados
default_costs_data = {
    "Element": [
        "Concrete 50 MPa", "Concrete 60 MPa", "Concrete 50 MPa (Special Mix)",
        "RL1018", "RL1118", "RL1218", "RL718", "RL818", "RL918",
        "SL102", "SL62", "SL72", "SL81", "SL82", "SL92",
        "Steel Bars", "Concrete Testing", "Ripbox", "Lifting", "Wages",
        "Shopdrawings", "Formwork", "Patching", "Ferrule with chair",
        "Starter insert", "Couplers", "Special Accessories"
    ],
    "Unit": [
        "m³", "m³", "m³",
        "kg", "kg", "kg", "kg", "kg", "kg",
        "kg", "kg", "kg", "kg", "kg", "kg",
        "kg", "m³", "m", "ea", "m²",
        "m²", "m²", "m²", "ea", "m²", "ea", "ea"
    ],
    "Cost": [
        300, 330, 1000,
        3.20, 3.20, 3.20, 3.20, 3.20, 3.20,
        2.75, 3.04, 2.69, 2.72, 2.59, 3.16,
        3.2, 40, 90, 25, 45,
        20, 35, 15, 5, 10, 8, 12
    ]
}

if os.path.exists(COSTS_FILE):
    costs_df = pd.read_csv(COSTS_FILE)
else:
    costs_df = pd.DataFrame(default_costs_data)

# 🔄 Botón para resetear costos a valores originales
with st.expander("⚠️ Reset Costs to Default"):
    confirm_reset = st.checkbox("I confirm I want to reset all costs to default values")

    if st.button("🔄 Reset Costs", disabled=not confirm_reset):
        costs_df = pd.DataFrame(default_costs_data)
        costs_df.to_csv(COSTS_FILE, index=False)
        st.success("Costs reset to default successfully! Please reload the page to see the changes.")

st.title("Precast Walls Cost Estimator")

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
    if not bar_type_h and not bar_type_v:
        return 0, 0

    spacing_h /= 1000
    spacing_v /= 1000

    total_length_per_m2_h = 0
    total_length_per_m2_v = 0
    total_weight_m2 = 0

    if bar_type_h:
        diameter_h = bar_diameter_lookup[bar_type_h]
        lap_factor_h = 1 + (40 * diameter_h / 6000) if apply_lap_splice else 1
        factor_placement_h = 2 if placement_h == "EF" else 1
        bars_per_meter_h = 1 / spacing_v if spacing_v > 0 else 0
        total_length_per_m2_h = bars_per_meter_h * lap_factor_h * factor_placement_h
        total_weight_m2 += total_length_per_m2_h * steel_weight_lookup[bar_type_h]

    if bar_type_v:
        diameter_v = bar_diameter_lookup[bar_type_v]
        lap_factor_v = 1 + (40 * diameter_v / 6000) if apply_lap_splice else 1
        factor_placement_v = 2 if placement_v == "EF" else 1
        bars_per_meter_v = 1 / spacing_h if spacing_h > 0 else 0
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


# 🔧 Función para calcular Trimer Bars incluyendo refuerzo de aperturas
def calculate_trimer_bar_weight(area, num_panels, wall_thickness, trimer_type, placement, apply_lap, opening_area, num_openings):
    if not trimer_type:
        return 0, 0

    avg_width = area / num_panels
    perimeter_per_panel = 2 * (avg_width + (wall_thickness / 1000))
    total_length = perimeter_per_panel * num_panels

    if placement == "EF":
        total_length *= 2

    total_opening_rebar_length = 0
    if num_openings > 0:
        avg_opening_side = (opening_area / num_openings) ** 0.5
        avg_opening_perimeter = 4 * avg_opening_side
        total_opening_rebar_length = avg_opening_perimeter * num_openings

        if placement == "EF":
            total_opening_rebar_length *= 2

        lap_factor_openings = 1 + (40 * bar_diameter_lookup[trimer_type] / 6000) if apply_lap else 1
        total_opening_rebar_length *= lap_factor_openings

    total_length += total_opening_rebar_length
    lap_factor = 1 + (40 * bar_diameter_lookup[trimer_type] / 6000) if apply_lap else 1
    total_length_with_lap = total_length * lap_factor

    total_weight = total_length_with_lap * steel_weight_lookup[trimer_type]
    return total_weight / area, total_weight


# 📌 Código del proyecto ingresado por el usuario
project_code = st.text_input("Enter Project Code (optional)", placeholder="e.g. WALL-2025-001")

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
# 📌 Panel Dimensions
with st.expander("📌 Panel Dimensions"):
    number_of_panels = st.number_input("Number of Panels", min_value=1, value=1)
    wall_area = st.number_input("Total Wall Area (m²)", min_value=1.0, value=100.0)
    wall_thickness = st.number_input("Wall Thickness (mm)", min_value=100, step=10, value=200)
    concrete_type = st.selectbox("Concrete Type", concrete_options)

# 📌 Aperturas
with st.expander("📌 Openings"):
    has_openings = st.radio("Do the panels have openings?", ["No", "Yes"], index=0)
    if has_openings == "Yes":
        opening_area = st.number_input("Total Openings Area (m²)", min_value=0.1, value=5.0)
        number_of_openings = st.number_input("Number of Openings", min_value=1, value=2)
    else:
        opening_area = 0
        number_of_openings = 0

# 🔹 Reinforcement
with st.expander("🔹 Reinforcement"):
    reo_rate = st.number_input("Reo Rate (kg/m³) (optional)", min_value=0.0, value=0.0)
    use_reo_rate_only = st.radio("Use only Reo Rate or add to bars/mesh?", ["Add to bars and mesh", "Use only Reo Rate"], index=0)
    apply_lap_splice = st.checkbox("Apply Lap Splice (40d for bars, 20% for mesh)", value=True)

    # 🔹 Barras Horizontales
    horizontal_bar = st.selectbox("Horizontal Bar Type", [""] + list(steel_weight_lookup.keys()))
    horizontal_spacing = st.number_input("Horizontal Bar Spacing (mm)", min_value=0, step=10, value=0)
    horizontal_placement = st.radio("Horizontal Bar Placement", ["CTR", "EF"])

    # 🔹 Barras Verticales
    vertical_bar = st.selectbox("Vertical Bar Type", [""] + list(steel_weight_lookup.keys()))
    vertical_spacing = st.number_input("Vertical Bar Spacing (mm)", min_value=0, step=10, value=0)
    vertical_placement = st.radio("Vertical Bar Placement", ["CTR", "EF"])

    # 🔹 Malla de refuerzo
    mesh_reinforcement = st.radio("Mesh Reinforcement", ["No", "Yes"])
    if mesh_reinforcement == "Yes":
        mesh_type = st.selectbox("Mesh Type", list(mesh_weight_lookup.keys()))
        mesh_placement = st.radio("Mesh Placement", ["CTR", "EF"])

    # 🔹 Trimer Bar
    trimer_bar = st.selectbox("Trimer Bar Type", [""] + list(steel_weight_lookup.keys()))
    trimer_placement = st.radio("Trimer Bar Placement", ["CTR", "EF"])

    # 🔹 Refuerzos adicionales en kg
    extra_steel_kg = st.number_input("Additional Steel Reinforcement (kg)", min_value=0.0, value=0.0, step=0.1)


# 🔹 Dowels (SEPARADO)
with st.expander("🔹 Dowels"):
    dowels = st.radio("Dowels", ["No", "Yes"])
    total_dowel_weight = 0  # 🔹 Inicialización

    if dowels == "Yes":
        dowel_calculation_method = st.radio("Dowel Weight Calculation", ["Calculate Automatically", "Enter Manually"])

        if dowel_calculation_method == "Enter Manually":
            total_dowel_weight = st.number_input("Total Dowels Weight (kg)", min_value=0.0, value=0.0)

        else:  # 🔹 Cálculo Automático
            dowel_bar_type = st.selectbox("Dowel Bar Type", list(steel_weight_lookup.keys()))
            dowel_spacing = st.number_input("Dowel Spacing (mm)", min_value=50, step=10, value=200)

            # 🔹 Opción para ingresar la longitud manualmente o calcularla
            use_manual_length = st.checkbox("Enter Dowel Length Manually?")
            
            if use_manual_length:
                dowel_length = st.number_input("Dowel Length (m)", min_value=0.0, value=1.2)
            else:
                dowel_length = (40 * bar_diameter_lookup[dowel_bar_type] * 2) / 1000 + 0.02  # 🔹 Cálculo Automático

            # 🔹 Ancho promedio del panel (respetando límite de 4.2 m)
            avg_panel_width = min(4.2, wall_area / number_of_panels)

            # 🔹 Número de dowels por panel
            dowels_per_panel = avg_panel_width / (dowel_spacing / 1000)

            # 🔹 Redondeamos hacia arriba
            dowels_per_panel = int(dowels_per_panel) + (1 if dowels_per_panel % 1 > 0 else 0)

            # 🔹 Dowels totales en la panelería
            total_dowels = dowels_per_panel * number_of_panels

            # 🔹 Cálculo del peso total
            total_dowel_weight = total_dowels * dowel_length * steel_weight_lookup[dowel_bar_type]


# 🔹 Additional Elements (SEPARADO)
with st.expander("🔹 Additional Elements"):
    ripbox = st.number_input("Ripbox (m)", value=0.0)
    ferrules = st.number_input("Ferrules (units)", value=0)
    starter_inserts = st.number_input("Starter Inserts (units)", value=0)
    couplers = st.number_input("Couplers (units)", value=0)
    lifters_per_panel = st.number_input("Lifters per Panel", value=0)
    special_accessories_per_panel = st.number_input("Special Accessories per Panel", value=0)

# 🔹 EO - Custom Extra Cost
with st.expander("🔹 EO - Extra Item (optional)"):
    eo_enabled = st.radio("Do you want to add an Extra Optional (EO) cost?", ["No", "Yes"], index=0)

    eo_cost_per_m2 = 0  # valor por defecto
    eo_label = ""       # nombre personalizado del EO

    if eo_enabled == "Yes":
        eo_label = st.text_input("Enter a description for this EO (e.g., Extra Formwork, Crane Access, etc.)", value="EO - Extra Item")
        eo_unit = st.selectbox("EO Cost is based on:", ["$/panel", "$/m²"])
        eo_value = st.number_input("Enter EO Value", min_value=0.0, value=0.0)

        if eo_unit == "$/panel" and number_of_panels > 0:
            eo_cost_per_m2 = (eo_value * number_of_panels) / wall_area
        elif eo_unit == "$/m²":
            eo_cost_per_m2 = eo_value

# 🔹 Waste % por elemento
with st.expander("🔹 Waste Percentage (Optional)"):
    st.markdown("Enter a percentage of waste for each applicable item (leave at 0 if not needed):")

    waste_concrete = st.number_input("Waste % for Concrete", min_value=0.0, value=0.0, step=0.1)
    waste_steel = st.number_input("Waste % for Steel Bars (H+V)", min_value=0.0, value=0.0, step=0.1)
    waste_trimmer = st.number_input("Waste % for Trimmer Bar", min_value=0.0, value=0.0, step=0.1)
    waste_mesh = st.number_input("Waste % for Mesh", min_value=0.0, value=0.0, step=0.1)
    waste_ripbox = st.number_input("Waste % for Ripbox", min_value=0.0, value=0.0, step=0.1)


# Editable Costs Table
if st.checkbox("Show Editable Cost Table"):
    edited_df = st.data_editor(costs_df, num_rows="dynamic")

    # 🔹 Guardar costos automáticamente al editar
    if edited_df is not None:
        edited_df.to_csv(COSTS_FILE, index=False)
        cost_dict = dict(zip(edited_df["Element"], edited_df["Cost"]))
else:
    cost_dict = dict(zip(costs_df["Element"], costs_df["Cost"]))


# Cálculo de refuerzo con traslape opcional
# 🔧 Cálculo de refuerzo con traslape opcional (permitiendo barras vacías)
def calculate_rebar_weight(area, spacing_h, spacing_v, bar_type_h, bar_type_v, placement_h, placement_v):
    # Si no se selecciona ninguna barra, retornamos 0
    if not bar_type_h and not bar_type_v:
        return 0, 0

    spacing_h /= 1000
    spacing_v /= 1000

    total_length_per_m2_h = 0
    total_length_per_m2_v = 0
    total_weight_m2 = 0

    if bar_type_h:
        diameter_h = bar_diameter_lookup[bar_type_h]
        lap_factor_h = 1 + (40 * diameter_h / 6000) if apply_lap_splice else 1
        factor_placement_h = 2 if placement_h == "EF" else 1
        bars_per_meter_h = 1 / spacing_v if spacing_v > 0 else 0
        total_length_per_m2_h = bars_per_meter_h * lap_factor_h * factor_placement_h
        total_weight_m2 += total_length_per_m2_h * steel_weight_lookup[bar_type_h]

    if bar_type_v:
        diameter_v = bar_diameter_lookup[bar_type_v]
        lap_factor_v = 1 + (40 * diameter_v / 6000) if apply_lap_splice else 1
        factor_placement_v = 2 if placement_v == "EF" else 1
        bars_per_meter_v = 1 / spacing_h if spacing_h > 0 else 0
        total_length_per_m2_v = bars_per_meter_v * lap_factor_v * factor_placement_v
        total_weight_m2 += total_length_per_m2_v * steel_weight_lookup[bar_type_v]

    total_weight = total_weight_m2 * area
    return total_weight_m2, total_weight


# 🔹 Cálculo Correcto del Steel Reinforcement (todos los componentes explícitos)

# Inicialización de variables claras
reo_rate_kg_total = (reo_rate * (wall_thickness / 1000)) * wall_area if reo_rate > 0 else 0

bars_weight_m2, bars_weight_total = calculate_rebar_weight(
    wall_area, horizontal_spacing, vertical_spacing,
    horizontal_bar, vertical_bar, horizontal_placement, vertical_placement
)
total_bars_weight = bars_weight_total  # 🔹 ESTA LÍNEA es necesaria

mesh_weight_total = calculate_mesh_weight(wall_area, mesh_type, mesh_placement, apply_lap_splice) if mesh_reinforcement == "Yes" else 0

trimer_bar_m2, trimer_bar_total = calculate_trimer_bar_weight(
    wall_area, number_of_panels, wall_thickness,
    trimer_bar, trimer_placement, apply_lap_splice,
    opening_area, number_of_openings
)

additional_reinforcement_kg_total = extra_steel_kg

# 🔹 Cálculo explícito del peso total combinado
total_steel_weight = (
    reo_rate_kg_total +
    bars_weight_total +
    mesh_weight_total +
    trimer_bar_total +
    additional_reinforcement_kg_total
)

# 🔹 Cálculo del peso total por m²
total_steel_weight_m2 = total_steel_weight / wall_area if wall_area > 0 else 0



# Cálculo de peso total de la malla con traslape
def calculate_mesh_weight(area, mesh_type, mesh_placement, apply_lap):
    base_weight = mesh_weight_lookup.get(mesh_type, 0) * area
    lap_factor = 1.2 if apply_lap else 1  # 20% adicional si aplica traslape
    placement_factor = 2 if mesh_placement == "EF" else 1  # EF usa doble capa de malla
    return base_weight * lap_factor * placement_factor

total_mesh_weight = 0
if mesh_reinforcement == "Yes":
    total_mesh_weight = calculate_mesh_weight(wall_area, mesh_type, mesh_placement, apply_lap_splice)
mesh_weight_m2 = total_mesh_weight / wall_area if wall_area > 0 else 0


# Cálculo de Trimer Bar por separado (incluyendo aperturas)
def calculate_trimer_bar_weight(area, num_panels, wall_thickness, trimer_type, placement, apply_lap, opening_area, num_openings):
    if not trimer_type:
        return 0, 0  # Si el tipo de barra está vacío, retorna 0

    avg_width = area / num_panels
    perimeter_per_panel = 2 * (avg_width + (wall_thickness / 1000))
    total_length = perimeter_per_panel * num_panels

    if placement == "EF":
        total_length *= 2  # EF usa barras en ambas caras

    # 🔹 CÁLCULO DEL REFUERZO DE APERTURAS 🔹
    total_opening_rebar_length = 0
    if num_openings > 0:
        avg_opening_side = (opening_area / num_openings) ** 0.5
        avg_opening_perimeter = 4 * avg_opening_side
        total_opening_rebar_length = avg_opening_perimeter * num_openings

        if placement == "EF":
            total_opening_rebar_length *= 2

        lap_factor_openings = 1 + (40 * bar_diameter_lookup[trimer_type] / 6000) if apply_lap else 1
        total_opening_rebar_length *= lap_factor_openings

    total_length += total_opening_rebar_length
    lap_factor = 1 + (40 * bar_diameter_lookup[trimer_type] / 6000) if apply_lap else 1
    total_length_with_lap = total_length * lap_factor

    total_weight = total_length_with_lap * steel_weight_lookup[trimer_type]
    return total_weight / area, total_weight

    avg_width = area / num_panels
    perimeter_per_panel = 2 * (avg_width + (wall_thickness / 1000))
    total_length = perimeter_per_panel * num_panels

    # Aplicar factor de placement
    if placement == "EF":
        total_length *= 2  # EF usa barras en ambas caras

    # 🔹 CÁLCULO DEL REFUERZO DE APERTURAS 🔹
    total_opening_rebar_length = 0  # Inicialización
    
    if num_openings > 0:
        avg_opening_side = (opening_area / num_openings) ** 0.5  # Lado promedio de la apertura
        avg_opening_perimeter = 4 * avg_opening_side  # Perímetro de cada apertura
        total_opening_rebar_length = avg_opening_perimeter * num_openings  # Total de todas las aperturas

        # 🔹 Aplicar el factor de colocación 🔹
        if placement == "EF":
            total_opening_rebar_length *= 2  # EF usa refuerzo en ambas caras

        # 🔹 Aplicar traslape a la apertura 🔹
        lap_factor_openings = 1 + (40 * bar_diameter_lookup[trimer_type] / 6000) if apply_lap else 1
        total_opening_rebar_length *= lap_factor_openings  

    # 🔹 SUMAR EL REFUERZO DE APERTURAS AL TOTAL 🔹
    total_length += total_opening_rebar_length

    # 🔹 Aplicar traslape final 🔹
    lap_factor = 1 + (40 * bar_diameter_lookup[trimer_type] / 6000) if apply_lap else 1
    total_length_with_lap = total_length * lap_factor
    
    # 🔹 Cálculo del peso total 🔹
    total_weight = total_length_with_lap * steel_weight_lookup[trimer_type]
    
    # 🔹 NO descontamos aperturas en el cálculo de kg/m² 🔹
    return total_weight / area, total_weight





trimer_bar_m2, total_trimer_bar = calculate_trimer_bar_weight(
    wall_area, number_of_panels, wall_thickness, trimer_bar, trimer_placement, apply_lap_splice, opening_area, number_of_openings
)

# 📌 Inicializar `cost_dict` con valores predeterminados si faltan elementos
default_costs = {
    "Concrete 50 MPa": 300, "Concrete 60 MPa": 330, "Concrete 50 MPa (Special Mix)": 1000,
    "Steel Bars": 3.2, "Concrete Testing": 40, "Ripbox": 90,
    "Lifting": 25, "Wages": 45, "Shopdrawings": 20, "Formwork": 35,
    "Patching": 15, "Ferrule with chair": 5, "Starter insert": 10, "Couplers": 8,
    "Special Accessories": 12,

    # 🔹 Precios por tipo de malla en $/kg
    "RL1018": 3.20, "RL1118": 3.20, "RL1218": 3.20,
    "RL718": 3.20, "RL818": 3.20, "RL918": 3.20,
    "SL102": 2.75, "SL62": 3.04, "SL72": 2.69,
    "SL81": 2.72, "SL82": 2.59, "SL92": 3.16
}



# 📌 Asegurar que `wall_area` no sea cero para evitar errores en la división
if wall_area == 0:
    wall_area = 1  # Evita división por cero (valor mínimo)

# 📌 Cálculo del volumen de concreto
concrete_volume = wall_area * (wall_thickness / 1000)  # 🔹 Convertimos a metros cúbicos

# Cálculo de pesos individuales para costos separados
bars_weight_kg = bars_weight_m2 * wall_area
reo_rate_kg = (reo_rate * (wall_thickness / 1000)) * wall_area if reo_rate > 0 else 0


    # 🔹 Calcular el costo de la malla seleccionada antes del diccionario
mesh_cost_per_m2 = 0
if mesh_reinforcement == "Yes" and mesh_type in cost_dict:
    mesh_cost_per_m2 = (total_mesh_weight * cost_dict[mesh_type]) / wall_area


# 📌 Cálculo de costos por m² para cada elemento
cost_per_m2 = {
    "Concrete": ((concrete_volume * (1 + waste_concrete / 100)) * cost_dict.get(concrete_type, 0) / wall_area),
    "Concrete Testing": (concrete_volume * cost_dict.get("Concrete Testing", 0) / wall_area),
    
    # 🔹 Refuerzo desglosado
    "Steel Bars (H+V)": (bars_weight_kg * (1 + waste_steel / 100) * cost_dict.get("Steel Bars", 0) / wall_area),
    "Trimer Bar": (total_trimer_bar * (1 + waste_trimmer / 100) * cost_dict.get("Steel Bars", 0) / wall_area),
    "Mesh": mesh_cost_per_m2 * (1 + waste_mesh / 100),
    "Reo Rate": (reo_rate_kg * cost_dict.get("Steel Bars", 0) / wall_area),
    "Additional Reinforcement": (extra_steel_kg * cost_dict.get("Steel Bars", 0) / wall_area),

    # 🔹 Otros elementos
    "Dowel Bars": (total_dowel_weight * cost_dict.get("Steel Bars", 0) / wall_area),
    "Ripbox": (ripbox * (1 + waste_ripbox / 100) * cost_dict.get("Ripbox", 0) / wall_area),
    "Ferrules": (ferrules * cost_dict.get("Ferrule with chair", 0) / wall_area),
    "Starter Inserts": (starter_inserts * cost_dict.get("Starter insert", 0) / wall_area),
    "Couplers": (couplers * cost_dict.get("Couplers", 0) / wall_area),
    "Lifting": ((lifters_per_panel * number_of_panels) * cost_dict.get("Lifting", 0) / wall_area),
    "Special Accessories": ((special_accessories_per_panel * number_of_panels) * cost_dict.get("Special Accessories", 0) / wall_area),

    # 🔹 Costos fijos por m²
    "Wages": cost_dict.get("Wages", 0),
    "Shopdrawings": cost_dict.get("Shopdrawings", 0),
    "Formwork": cost_dict.get("Formwork", 0),
    "Patching": cost_dict.get("Patching", 0)
}

# 🔹 Agregar EO personalizado si aplica
if eo_enabled == "Yes" and eo_cost_per_m2 > 0 and eo_label.strip() != "":
    cost_per_m2[eo_label.strip()] = eo_cost_per_m2


# 📌 Cálculo del costo total por metro cuadrado
total_cost_per_m2 = sum(cost_per_m2.values())

# 📌 Cálculo del costo total del proyecto
total_cost = total_cost_per_m2 * wall_area


# 📊 Nueva visualización usando pestañas
tab1, tab2 = st.tabs(["📊 Results", "💲 Cost Summary"])

# 📊 TAB 1 - Resultados

# 🔹 Cálculo individual de cada componente para Steel Reinforcement
reo_rate_m2 = reo_rate * (wall_thickness / 1000)
reo_rate_total = reo_rate_m2 * wall_area

bars_weight_m2 = total_bars_weight / wall_area if wall_area > 0 else 0
bars_weight_total = total_bars_weight

mesh_weight_m2 = total_mesh_weight / wall_area if wall_area > 0 else 0

trimer_bar_m2 = total_trimer_bar / wall_area if wall_area > 0 else 0

extra_steel_kg_m2 = extra_steel_kg / wall_area if wall_area > 0 else 0

# 🔹 Total combinado
total_steel_kg_m2 = reo_rate_m2 + bars_weight_m2 + mesh_weight_m2 + trimer_bar_m2 + extra_steel_kg_m2

with tab1:
    st.subheader("📊 Results")

    # 🔹 Cálculo del volumen de concreto
    concrete_volume = wall_area * (wall_thickness / 1000)
    st.write(f"🔹 **Concrete Volume:** {concrete_volume:.2f} m³")
    st.write(f"🔹 **Concrete Testing:** {concrete_volume:.2f} m³")

    # 🔹 Steel Reinforcement total y desglose
    st.write(f"🔹 **Steel Reinforcement:** {total_steel_kg_m2:.2f} kg/m², **Total:** {total_steel_weight:.2f} kg")
    with st.expander("🧱 Breakdown of Steel Reinforcement", expanded=True):
        st.write(f"   - **Reo Rate:** {reo_rate_m2:.2f} kg/m², Total: {reo_rate_total:.2f} kg")
        st.write(f"   - **Bars (H+V):** {bars_weight_m2:.2f} kg/m², Total: {bars_weight_total:.2f} kg")
        st.write(f"   - **Mesh:** {mesh_weight_m2:.2f} kg/m², Total: {total_mesh_weight:.2f} kg")
        st.write(f"   - **Trimer Bar:** {trimer_bar_m2:.2f} kg/m², Total: {total_trimer_bar:.2f} kg")
        st.write(f"   - **Additional Reinforcement:** {extra_steel_kg_m2:.2f} kg/m², Total: {extra_steel_kg:.2f} kg")

with st.expander("🔧 Waste-adjusted Quantities", expanded=False):
    st.markdown("These values reflect the quantities after applying the selected waste percentages:")

    st.write(f"• Concrete with Waste: {(concrete_volume / wall_area) * (1 + waste_concrete / 100):.2f} m³/m²")
    st.write(f"• Steel Bars (H+V) with Waste: {bars_weight_m2 * (1 + waste_steel / 100):.2f} kg/m²")
    st.write(f"• Trimmer Bar with Waste: {trimer_bar_m2 * (1 + waste_trimmer / 100):.2f} kg/m²")
    st.write(f"• Mesh with Waste: {mesh_weight_m2 * (1 + waste_mesh / 100):.2f} kg/m²")
    st.write(f"• Ripbox with Waste: {(ripbox / wall_area) * (1 + waste_ripbox / 100):.2f} m/m²")


    # 🔹 Dowels
    st.write(f"🔹 **Dowel Weight:** {total_dowel_weight:.2f} kg")

    # 🔹 Elementos adicionales
    st.markdown("🔹 **Additional Elements:**")
    st.write(f"   - **Ripbox:** {ripbox:.2f} m")
    st.write(f"   - **Ferrules:** {ferrules} units")
    st.write(f"   - **Starter Inserts:** {starter_inserts} units")
    st.write(f"   - **Couplers:** {couplers} units")
    st.write(f"   - **Lifters:** {lifters_per_panel * number_of_panels} units")
    st.write(f"   - **Special Accessories:** {special_accessories_per_panel * number_of_panels} units")


# 💲 TAB 2 - Cost Summary
with tab2:
    st.subheader("💲 Cost Summary (per m²)")

    for item, cost in cost_per_m2.items():
        st.write(f"   - **{item}:** ${cost:.2f}")

    st.write(f"\n🔹 **Total Project Cost per m²:** ${total_cost_per_m2:.2f}")


# 📌 Generar la especificación del refuerzo en formato profesional
reinforcement_spec = f"{horizontal_bar} @ {horizontal_spacing}mm {horizontal_placement} / {vertical_bar} @ {vertical_spacing}mm {vertical_placement}"

# 📌 Crear el encabezado del reporte
report_header = f"Precast panel type Wall, Reinforcement {reinforcement_spec}"

# 📌 Crear un DataFrame con los costos por m²
df_summary = pd.DataFrame(list(cost_per_m2.items()), columns=["Element", "Cost per m²"])

from io import BytesIO

# 📌 Crear descripción profesional del refuerzo
reinforcement_desc = f"{horizontal_bar}@{horizontal_spacing} {horizontal_placement} + {vertical_bar}@{vertical_spacing} {vertical_placement}"
if mesh_reinforcement == "Yes":
    reinforcement_desc += f" + {mesh_type} {mesh_placement}"
report_header = f"Project Code: {project_code} | Precast panel type Wall | Reinforcement: {reinforcement_desc}"


# 📌 Unidades por elemento
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
    "Starter Inserts": "ea",
    "Couplers": "ea",
    "Lifting": "ea",
    "Special Accessories": "ea",
    "Wages": "m²",
    "Shopdrawings": "m²",
    "Formwork": "m²",
    "Patching": "m²"
}

# 📌 Costo unitario por elemento (ya está en tu cost_dict)
unit_costs = {item: cost_dict.get(item, 0) for item in units}

# 📌 Cantidades totales por m²
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
    "Starter Inserts": starter_inserts / wall_area if wall_area > 0 else 0,
    "Couplers": couplers / wall_area if wall_area > 0 else 0,
    "Lifting": (lifters_per_panel * number_of_panels) / wall_area if wall_area > 0 else 0,
    "Special Accessories": (special_accessories_per_panel * number_of_panels) / wall_area if wall_area > 0 else 0,
    "Wages": 1,
    "Shopdrawings": 1,
    "Formwork": 1,
    "Patching": 1
}

# 📌 Crear DataFrame consolidado (CORREGIDO)
df_costs = pd.DataFrame({
    "Item": list(cost_per_m2.keys()),
    "Unit": [units.get(item, "") for item in cost_per_m2.keys()],
    "Unit Cost ($)": [unit_costs.get(item, 0) for item in cost_per_m2.keys()],
    "Total Qty for m2": [quantities.get(item, 0) for item in cost_per_m2.keys()],
    "Cost per m² ($)": list(cost_per_m2.values())
})

# 📌 Agregar fila de total al final
df_costs = pd.concat([df_costs, pd.DataFrame({
    "Item": ["Total Cost"],
    "Unit": [""],
    "Unit Cost ($)": [""],
    "Total Qty for m2": [""],
    "Cost per m² ($)": [total_cost_per_m2]
})], ignore_index=True)



# 📌 Guardar en Excel con encabezado personalizado
output = BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    workbook = writer.book
    worksheet = workbook.add_worksheet("Report")
    writer.sheets["Report"] = worksheet

    # 🔹 Encabezado con código del proyecto en A1
    worksheet.write("A1", f"Project Code: {project_code}" if project_code else "Project Code: N/A")

    # 🔹 Descripción del refuerzo en A2
    worksheet.write("A2", f"Reinforcement: {reinforcement_desc}")

    # 🔹 Escribir tabla desde fila 4
    df_costs.to_excel(writer, sheet_name="Report", startrow=3, index=False)

# 📌 Botón único para descarga
st.download_button(
    label="📥 Download Excel Report",
    data=output.getvalue(),
    file_name="precast_cost_summary.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
