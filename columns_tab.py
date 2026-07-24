"""
columns_tab.py
================
Standalone Columns cost-estimation module for the Precast Wall Estimator app.

This file is kept completely separate from app.py on purpose, so the
already-validated Walls calculation logic is never touched. app.py only
needs two small additions — nothing inside app.py's existing Walls code
changes at all.

HOW TO WIRE THIS INTO app.py (2 edits, both additions — nothing removed
from the Walls logic):

1) Near the top of app.py, alongside the other imports:

       from columns_tab import render_columns_tab

2) Inside `with tab_columnas:`, call:

       with tab_columnas:
           render_columns_tab(cost_dict, steel_weight_lookup, bar_diameter_lookup,
                               concrete_options, float_input, safe_div)

   IMPORTANT — placement: `cost_dict` is only built inside `with st.sidebar:`,
   further down in app.py. This block must run AFTER that sidebar block ends,
   and BEFORE `with tab_muros:` starts — that is the only place in app.py
   where `cost_dict`, `steel_weight_lookup`, `bar_diameter_lookup`,
   `concrete_options` and `float_input` already exist.

Conventions matched to the Walls module for consistency:
- All length inputs are entered in millimetres (mm), exactly like Walls'
  "Wall Thickness (mm)" — converted to metres internally wherever the maths
  needs metres. Only volumes (m³) are entered directly in m³ (matching the
  CostX convention), since those aren't a length.
- Every input starts at zero / blank — nothing is pre-filled, exactly like
  Walls (Number of Panels = 0, Wall Area = 0.0000, Wall Thickness = 0, bar
  type dropdowns start blank).
- Results follow the same sidebar pattern as Walls: a "Show Results" and a
  "Show Cost Breakdown" toggle in the sidebar, plus a single always-visible
  metric card at the bottom — for Columns that card shows only the
  estimated fabrication cost per m³ (no per-column or per-group total in
  the card, matching how Walls only shows "Total cost per m²").

Every column-specific variable, dropdown key, and calculation lives inside
this file's function, under its own `col_` prefixed names, so nothing here
can collide with any variable used by the Walls module in app.py.
"""

import streamlit as st
import pandas as pd
from io import BytesIO


def render_columns_tab(cost_dict, steel_weight_lookup, bar_diameter_lookup,
                        concrete_options, float_input, safe_div):
    """Renders the full Columns cost-estimation UI and calculations.

    Parameters are the exact same shared objects already built in app.py —
    passed in rather than imported, so this module has no hidden dependency
    on app.py's internals beyond what's listed here.
    """

    st.caption(
        "Fabrication cost per m³ for an individual precast column, or a group "
        "of columns that share the same geometry and reinforcement."
    )

    col_project_code = st.session_state.get("project_code_menu", "")
    st.caption(f"Project Code: **{col_project_code or 'N/A'}**")
    col_group_id = st.text_input("Enter Column Group ID", placeholder="e.g. PC-01", key="col_group_id")

    col_sub_geom, col_sub_reo, col_sub_costs = st.tabs(["Geometry", "Reinforcement", "Costs & Extras"])

    # ------------------------------------------------------------------ #
    # GEOMETRY
    # ------------------------------------------------------------------ #
    with col_sub_geom:
        with st.expander("Column Dimensions", icon=":material/straighten:", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                col_width_mm = st.number_input("Width (mm)", min_value=0, value=0, step=10, key="col_width_mm")
            with c2:
                col_depth_mm = st.number_input("Depth (mm)", min_value=0, value=0, step=10, key="col_depth_mm")
            with c3:
                col_concrete_type = st.selectbox("Concrete Type", [""] + concrete_options, index=0, key="col_concrete_type")

            col_width = col_width_mm / 1000
            col_depth = col_depth_mm / 1000

            col_geom_mode = st.radio(
                "How is the column height known?",
                ["Volume & Quantity (from CostX)", "Direct Average Height"],
                index=0,
                key="col_geom_mode",
                help=(
                    "Volume & Quantity is the most common case: enter the total group "
                    "volume and column count from CostX, and the average height is "
                    "derived automatically. Direct Average Height is for the less "
                    "common case where the real average height of the group is "
                    "already known (e.g. columns confined to a single level)."
                ),
            )

            if col_geom_mode == "Volume & Quantity (from CostX)":
                c4, c5 = st.columns(2)
                with c4:
                    col_group_volume = float_input(
                        "Total Group Volume (m³)", key="col_group_vol_text", default=0.0, decimals=3, min_value=0.0
                    )
                with c5:
                    col_group_qty = st.number_input(
                        "Number of Columns in Group", min_value=0, value=0, step=1, key="col_group_qty_a"
                    )
                if col_group_qty > 0 and col_width > 0 and col_depth > 0:
                    col_avg_height = (col_group_volume / col_group_qty) / (col_width * col_depth)
                else:
                    col_avg_height = 0.0
                st.caption(f"Derived average height: {col_avg_height * 1000:,.0f} mm")
            else:
                col_avg_height_mm = st.number_input(
                    "Average Height (mm)", min_value=0, value=0, step=10, key="col_avg_height_mm"
                )
                col_avg_height = col_avg_height_mm / 1000
                col_group_qty = st.number_input(
                    "Number of Columns in Group (optional, for the total cost roll-up)",
                    min_value=0, value=0, step=1, key="col_group_qty_b",
                )
                col_group_volume = 0.0

            col_volume_per_column = col_width * col_depth * col_avg_height

            col_cover_known = st.radio(
                "Is the reinforcement cover known?", ["No", "Yes"], index=0, key="col_cover_known", horizontal=True
            )
            if col_cover_known == "Yes":
                col_cover_mm = st.number_input("Reo Cover (mm)", min_value=0, value=0, step=1, key="col_cover_mm")
                col_cover = col_cover_mm / 1000
            else:
                col_cover = 0.03
                st.warning(
                    "Using an assumed minimum cover of 30mm — not confirmed from drawings.",
                    icon=":material/warning:",
                )

            if col_volume_per_column > 0:
                st.markdown(
                    f'<div class="pw-metric-row"><div class="pw-metric">'
                    f'<div class="pw-metric-icon"><span class="pw-icon">foundation</span></div>'
                    f'<p class="pw-metric-label">Volume per column</p>'
                    f'<p class="pw-metric-value">{col_volume_per_column:.3f} m³</p>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

    # ------------------------------------------------------------------ #
    # REINFORCEMENT
    # ------------------------------------------------------------------ #
    with col_sub_reo:
        with st.expander("Steel Costing Method", icon=":material/settings:", expanded=True):
            col_steel_mode = st.radio(
                "How should reinforcing steel be costed?",
                ["Bar Detail (configure below)", "General Reo Rate (kg/m³)"],
                index=0,
                key="col_steel_mode",
                help=(
                    "Bar Detail costs steel using the longitudinal/tie/lig bars configured "
                    "below. General Reo Rate costs directly from a single kg/m³ figure off "
                    "the drawing, for when the detailed reinforcement breakdown isn't "
                    "available — in that case the bar configuration below is skipped "
                    "entirely and only Dowels still needs setting up."
                ),
            )
            if col_steel_mode == "General Reo Rate (kg/m³)":
                col_reo_rate_given = st.number_input(
                    "Reo Rate Given (kg/m³) — from drawing", min_value=0.0, value=0.0, key="col_reo_rate_given"
                )
            else:
                col_reo_rate_given = 0.0
                st.caption("Configure the longitudinal, tie and lig reinforcement below — the steel rate will be calculated from it.")

        if col_steel_mode == "Bar Detail (configure below)":
            with st.expander("Longitudinal Reinforcement", icon=":material/construction:", expanded=True):
                c1, c2 = st.columns(2)
                with c1:
                    col_long_qty = st.number_input("Number of Longitudinal Bars", min_value=0, value=0, step=1, key="col_long_qty")
                with c2:
                    col_long_bar = st.selectbox("Longitudinal Bar Type", [""] + list(steel_weight_lookup.keys()), key="col_long_bar")

                st.caption("Optional second longitudinal bar group — leave the bar type blank if all longitudinal bars are the same diameter.")
                c3, c4 = st.columns(2)
                with c3:
                    col_long_qty2 = st.number_input("Number of Longitudinal Bars (Group 2)", min_value=0, value=0, step=1, key="col_long_qty2")
                with c4:
                    col_long_bar2 = st.selectbox("Longitudinal Bar Type (Group 2)", [""] + list(steel_weight_lookup.keys()), key="col_long_bar2")

                col_apply_lap = st.checkbox("Apply Lap Splice (40 x bar diameter)", value=True, key="col_apply_lap")

            with st.expander("Transverse Reinforcement (Ties & Ligs)", icon=":material/window:", expanded=True):
                st.markdown("###### Closed Ties")
                c1, c2, c3 = st.columns(3)
                with c1:
                    col_tie_bar = st.selectbox("Tie Bar Type", [""] + list(steel_weight_lookup.keys()), key="col_tie_bar")
                with c2:
                    col_tie_spacing_mm = st.number_input("Tie Spacing (mm)", min_value=0, value=0, step=10, key="col_tie_spacing_mm")
                with c3:
                    col_tie_perimeter_override_mm = st.number_input(
                        "Measured Tie Perimeter (mm)", min_value=0, value=0, step=1, key="col_tie_perim_mm"
                    )
                st.caption(
                    "Leave the measured perimeter at 0 to calculate it from Width, Depth and Cover. "
                    "Enter it only if a detailed cross-section is available and a single tie's real "
                    "perimeter (including hooks/crossties) can be measured directly."
                )
                col_tie_perimeter_override = col_tie_perimeter_override_mm / 1000

                st.markdown("###### Ligs")
                c4, c5 = st.columns(2)
                with c4:
                    col_lig_qty = st.number_input("Number of Ligs per Tie Level", min_value=0, value=0, step=1, key="col_lig_qty")
                with c5:
                    col_lig_bar = st.selectbox("Lig Bar Type", [""] + list(steel_weight_lookup.keys()), key="col_lig_bar")
        else:
            # General Reo Rate mode — bar-level detail isn't needed for costing,
            # so these stay at safe defaults (0 / blank) for the calculations below.
            col_long_qty, col_long_bar = 0, ""
            col_long_qty2, col_long_bar2 = 0, ""
            col_apply_lap = True
            col_tie_bar, col_tie_spacing_mm, col_tie_perimeter_override_mm = "", 0, 0
            col_tie_perimeter_override = 0.0
            col_lig_qty, col_lig_bar = 0, ""

        with st.expander("Dowels", icon=":material/link:", expanded=True):
            col_dowel_mode = st.radio(
                "Dowel information",
                ["Exclude", "Estimate (1 per longitudinal bar)", "I know the details"],
                index=0,
                key="col_dowel_mode",
                help=(
                    "Exclude — use only if the drawing confirms dowels don't apply. "
                    "Estimate assumes one dowel per longitudinal bar (only available "
                    "when Steel Costing Method is Bar Detail, since that's the only way "
                    "the longitudinal bar count is known). "
                    "I know the details lets the real quantity be entered."
                ),
            )
            c1, c2 = st.columns(2)
            with c1:
                col_dowel_bar = st.selectbox("Dowel Bar Type", [""] + list(steel_weight_lookup.keys()), key="col_dowel_bar")
            with c2:
                col_dowel_qty_manual = st.number_input(
                    "Dowels per Column (if 'I know the details')", min_value=0, value=0, step=1, key="col_dowel_qty_manual"
                )
            col_dowel_length_override_mm = st.number_input(
                "Dowel Length Override (mm)", min_value=0, value=0, step=1, key="col_dowel_len_mm"
            )
            col_dowel_length_override = col_dowel_length_override_mm / 1000
            st.caption("Leave the length override at 0 to calculate it automatically as 2 x 40 x bar diameter + 20mm.")

    # ------------------------------------------------------------------ #
    # CALCULATIONS (bar weights, ties, dowels, reo rate)
    # ------------------------------------------------------------------ #
    def _col_bar_length_with_lap(qty, base_length, bar_type, apply_lap):
        if not bar_type or qty <= 0:
            return 0.0
        diameter = bar_diameter_lookup.get(bar_type, 0)
        lap_length = (40 * diameter / 1000) if apply_lap else 0.0
        return qty * (base_length + lap_length)

    col_long_length_1 = _col_bar_length_with_lap(col_long_qty, col_avg_height, col_long_bar, col_apply_lap)
    col_long_weight_1 = col_long_length_1 * steel_weight_lookup.get(col_long_bar, 0)

    col_long_length_2 = _col_bar_length_with_lap(col_long_qty2, col_avg_height, col_long_bar2, col_apply_lap)
    col_long_weight_2 = col_long_length_2 * steel_weight_lookup.get(col_long_bar2, 0)

    col_tie_spacing_m = col_tie_spacing_mm / 1000
    col_tie_count = int(-(-col_avg_height // col_tie_spacing_m)) if col_tie_spacing_m > 0 and col_avg_height > 0 else 0
    if col_tie_perimeter_override > 0:
        col_tie_perimeter = col_tie_perimeter_override
    else:
        col_tie_perimeter = 2 * ((col_width - 2 * col_cover) + (col_depth - 2 * col_cover)) + 0.14  # 0.14 = 2 x 7cm hooks
    col_tie_length = col_tie_perimeter * col_tie_count
    col_tie_weight = col_tie_length * steel_weight_lookup.get(col_tie_bar, 0)

    col_lig_length = ((col_width - 2 * col_cover) + 0.14) * (col_tie_count * col_lig_qty)
    col_lig_weight = col_lig_length * steel_weight_lookup.get(col_lig_bar, 0)

    col_reo_weight_from_bars = col_long_weight_1 + col_long_weight_2 + col_tie_weight + col_lig_weight
    col_reo_rate_estimated = safe_div(col_reo_weight_from_bars, col_volume_per_column)

    if col_steel_mode == "Bar Detail (configure below)":
        col_reo_rate_used = col_reo_rate_estimated
        col_reo_weight_used = col_reo_weight_from_bars
    else:
        col_reo_rate_used = col_reo_rate_given
        col_reo_weight_used = col_reo_rate_given * col_volume_per_column

    if col_reo_rate_given > 0 and col_reo_rate_estimated > 0:
        col_reo_rate_diff_pct = (col_reo_rate_estimated - col_reo_rate_given) / col_reo_rate_given
        if abs(col_reo_rate_diff_pct) > 0.10:
            st.warning(
                f"Reo Rate difference of {col_reo_rate_diff_pct:+.1%} between the "
                f"General Rate given ({col_reo_rate_given:.1f} kg/m³) and the rate "
                f"estimated from bar detail ({col_reo_rate_estimated:.1f} kg/m³) — "
                f"worth reviewing before pricing.",
                icon=":material/warning:",
            )

    # Dowels
    if col_dowel_mode == "Exclude":
        col_dowel_qty_used = 0
    elif col_dowel_mode == "Estimate (1 per longitudinal bar)":
        col_dowel_qty_used = col_long_qty
    else:
        col_dowel_qty_used = col_dowel_qty_manual

    if col_dowel_length_override > 0:
        col_dowel_length = col_dowel_length_override
    elif col_dowel_bar:
        col_dowel_length = (2 * 40 * bar_diameter_lookup.get(col_dowel_bar, 0)) / 1000 + 0.02
    else:
        col_dowel_length = 0.0

    col_dowel_weight = col_dowel_qty_used * col_dowel_length * steel_weight_lookup.get(col_dowel_bar, 0)

    # ------------------------------------------------------------------ #
    # COSTS & EXTRAS
    # ------------------------------------------------------------------ #
    with col_sub_costs:
        with st.expander("Lifting & Accessories", icon=":material/build:", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                col_lifting_qty = st.number_input("Lifting Points per Column", min_value=0, value=0, step=1, key="col_lifting_qty")
            with c2:
                col_accessories_qty = st.number_input("Special Accessories per Column", min_value=0, value=0, step=1, key="col_accessories_qty")

        with st.expander("Additional Consumables", icon=":material/inventory_2:", expanded=False):
            st.caption(
                "Add any consumables shown on the structural drawing that aren't covered above "
                "— e.g. chamfer strips, embedded base plates/inserts, grout/dry-pack, corbels, "
                "bar chairs/spacers, corrosion protection, surface finish. Leave empty if not required."
            )
            col_num_consumables = st.number_input(
                "How many additional consumables do you want to add?", min_value=0, max_value=10, value=0, key="col_num_consumables"
            )
            col_consumables = {}
            for i in range(col_num_consumables):
                cc1, cc2, cc3 = st.columns([3, 1, 1])
                item_label = cc1.text_input(f"Description {i+1}", key=f"col_consumable_label_{i}")
                item_unit = cc2.selectbox("Unit", ["$/column", "$/ea"], key=f"col_consumable_unit_{i}")
                item_cost = cc3.number_input("Unit Cost", min_value=0.0, step=0.1, key=f"col_consumable_cost_{i}")
                item_qty = 1
                if item_unit == "$/ea":
                    item_qty = st.number_input(f"Qty for '{item_label or f'Item {i+1}'}'", min_value=0, step=1, value=1, key=f"col_consumable_qty_{i}")
                if item_label.strip():
                    col_consumables[item_label.strip()] = item_cost * item_qty

        with st.expander("Waste Factors (Optional)", icon=":material/recycling:"):
            st.caption("Enter a waste percentage for each applicable item (leave at 0 if not needed).")
            col_waste_items = {
                "Concrete": col_volume_per_column,
                "Reinforcing Steel": col_reo_weight_used,
                "Dowels": col_dowel_weight,
            }
            col_waste_pct = {}
            for label, qty in col_waste_items.items():
                if qty > 0:
                    col_waste_pct[label] = st.number_input(
                        f"Waste % for {label}", min_value=0.0, value=0.0, step=0.1, key=f"col_waste_{label.replace(' ', '_')}"
                    )
            col_waste_concrete = col_waste_pct.get("Concrete", 0.0)
            col_waste_steel = col_waste_pct.get("Reinforcing Steel", 0.0)
            col_waste_dowel = col_waste_pct.get("Dowels", 0.0)

    # ------------------------------------------------------------------ #
    # COST BUILD-UP (per column)
    # ------------------------------------------------------------------ #
    col_concrete_qty = col_volume_per_column * (1 + col_waste_concrete / 100)
    col_concrete_cost = col_concrete_qty * cost_dict.get(col_concrete_type, 0)
    col_testing_cost = col_volume_per_column * cost_dict.get("Concrete Testing", 0)
    col_steel_qty = col_reo_weight_used * (1 + col_waste_steel / 100)
    col_steel_cost = col_steel_qty * cost_dict.get("Steel Bars", 0)
    col_dowel_qty_kg = col_dowel_weight * (1 + col_waste_dowel / 100)
    col_dowel_cost = col_dowel_qty_kg * cost_dict.get("Steel Bars", 0)
    col_lifting_cost = col_lifting_qty * cost_dict.get("Lifting", 0)
    col_accessories_cost = col_accessories_qty * cost_dict.get("Special Accessories", 0)
    col_consumables_cost = sum(col_consumables.values())

    col_wages_cost = cost_dict.get("Wages", 0)
    col_shopdrawings_cost = cost_dict.get("Shopdrawings", 0)
    col_formwork_cost = cost_dict.get("Formwork", 0)
    col_patching_cost = cost_dict.get("Patching", 0)
    col_perimeter = 2 * (col_width + col_depth)
    col_surface_area = col_perimeter * col_avg_height
    col_labour_cost = (col_wages_cost + col_shopdrawings_cost + col_formwork_cost + col_patching_cost) * col_surface_area

    col_materials_total = (
        col_concrete_cost + col_testing_cost + col_steel_cost + col_dowel_cost
        + col_lifting_cost + col_accessories_cost + col_consumables_cost
    )
    col_price_per_column = col_materials_total + col_labour_cost
    col_price_per_m3 = safe_div(col_price_per_column, col_volume_per_column)

    if col_group_qty > 0:
        col_total_group_cost = col_price_per_column * col_group_qty
    elif col_group_volume > 0:
        col_total_group_cost = col_price_per_m3 * col_group_volume
    else:
        col_total_group_cost = 0.0

    # ------------------------------------------------------------------ #
    # RESULTS — same sidebar pattern as Walls (Show Results / Show Cost
    # Breakdown toggles), and a single always-visible metric card showing
    # only the fabrication cost per m³ (no per-column or per-group total
    # in the card, matching how Walls only shows "Total cost per m²").
    # ------------------------------------------------------------------ #
    col_df_costs = pd.DataFrame({
        "Item": ["Concrete", "Concrete Testing", "Reinforcing Steel", "Dowels", "Lifting", "Special Accessories",
                 *col_consumables.keys(), "Wages", "Shopdrawings", "Formwork", "Patching"],
        "Unit": ["m³", "m³", "kg", "kg", "ea", "ea",
                 *(["$"] * len(col_consumables)), "m²", "m²", "m²", "m²"],
        "Qty": [col_concrete_qty, col_volume_per_column, col_steel_qty, col_dowel_qty_kg, col_lifting_qty, col_accessories_qty,
                *([1] * len(col_consumables)), col_surface_area, col_surface_area, col_surface_area, col_surface_area],
        "Cost per Column ($)": [col_concrete_cost, col_testing_cost, col_steel_cost, col_dowel_cost,
                                 col_lifting_cost, col_accessories_cost, *col_consumables.values(),
                                 col_wages_cost * col_surface_area, col_shopdrawings_cost * col_surface_area,
                                 col_formwork_cost * col_surface_area, col_patching_cost * col_surface_area],
    })
    col_df_costs.loc[len(col_df_costs.index)] = ["Total Cost", "", "", round(col_price_per_column, 2)]

    if col_volume_per_column > 0:
        st.info("Results and the cost breakdown are available in the sidebar on the left.", icon=":material/arrow_back:")
        st.sidebar.markdown("---")
        st.sidebar.caption("Columns — view options")
        col_show_results = st.sidebar.toggle(":material/bar_chart: Show Column Results", value=False, key="col_show_results")

        if col_show_results:
            st.markdown("## :material/bar_chart: Results")
            with st.expander("View Reinforcement Breakdown", icon=":material/table_rows:", expanded=False):
                st.markdown(f"""
                <div class="card">
                    <div class="subtitle"><span class="pw-icon-badge"><span class="pw-icon">hardware</span></span>Reinforcement Breakdown</div>
                    <ul>
                        <li><b>Longitudinal (Group 1):</b> {col_long_weight_1:.2f} kg</li>
                        <li><b>Longitudinal (Group 2):</b> {col_long_weight_2:.2f} kg</li>
                        <li><b>Closed Ties:</b> {col_tie_weight:.2f} kg ({col_tie_count} ties)</li>
                        <li><b>Ligs:</b> {col_lig_weight:.2f} kg</li>
                        <li><b>Reo Rate Estimated:</b> {col_reo_rate_estimated:.1f} kg/m³</li>
                        <li><b>Reo Rate Used for Costing:</b> {col_reo_rate_used:.1f} kg/m³ ({col_steel_mode})</li>
                        <li><b>Dowels:</b> {col_dowel_weight:.2f} kg ({col_dowel_qty_used} dowels, {col_dowel_mode})</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        if st.sidebar.toggle(":material/payments: Show Column Cost Breakdown", value=False, key="col_show_breakdown"):
            st.markdown("### :material/payments: Cost Breakdown (per column)")
            st.dataframe(
                col_df_costs,
                hide_index=True,
                use_container_width=True,
                column_config={"Cost per Column ($)": st.column_config.NumberColumn(format="$%.2f")},
            )

        st.markdown(f"""
            <div class="pw-metric pw-metric-accent" style="text-align:center; padding: 1.5rem;">
                <div class="pw-metric-icon" style="margin: 0 auto 10px;"><span class="pw-icon">payments</span></div>
                <p class="pw-metric-label" style="font-size:14px;">Estimated fabrication cost per m³</p>
                <p class="pw-metric-value" style="font-size:32px;">${col_price_per_m3:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

        # -------------------------------------------------------------- #
        # EXCEL EXPORT — the full per-column and per-group totals still
        # go into the download (useful for the project record), even
        # though they're no longer shown as cards on screen.
        # -------------------------------------------------------------- #
        col_output = BytesIO()
        with pd.ExcelWriter(col_output, engine="xlsxwriter") as writer:
            workbook = writer.book
            col_df_costs.to_excel(writer, sheet_name="Report", startrow=6, index=False)
            worksheet = writer.sheets["Report"]
            worksheet.write("A1", f"Project Code: {col_project_code}" if col_project_code else "Project Code: N/A")
            worksheet.write("A2", f"Column Group ID: {col_group_id}" if col_group_id else "Column Group ID: N/A")
            worksheet.write("A3", f"Width x Depth: {col_width_mm} x {col_depth_mm} mm, Avg Height: {col_avg_height * 1000:.0f} mm")
            worksheet.write("A4", f"Concrete: {col_concrete_type}, Reo Rate Used: {col_reo_rate_used:.1f} kg/m3")
            worksheet.write("A5", f"Price per Column: ${col_price_per_column:,.2f} | Price per m3: ${col_price_per_m3:,.2f}")
            if col_total_group_cost > 0:
                worksheet.write("A6", f"Estimated Total Group Cost: ${col_total_group_cost:,.2f}")

            bold_format = workbook.add_format({"bold": True})
            money_format = workbook.add_format({"num_format": "$#,##0.00"})
            total_row_format = workbook.add_format({"bold": True, "top": 1})
            total_format = workbook.add_format({"bold": True, "top": 1, "num_format": "$#,##0.00"})

            audit_sheet = workbook.add_worksheet("Audit")
            audit_sheet.write("A1", f"Column Group ID: {col_group_id}" if col_group_id else "Column Group ID: N/A", bold_format)
            audit_sheet.write("A3", "COLUMN INPUTS", bold_format)
            audit_rows = [
                ("Width (mm)", col_width_mm), ("Depth (mm)", col_depth_mm),
                ("Geometry Mode", col_geom_mode), ("Average Height Used (mm)", round(col_avg_height * 1000, 0)),
                ("Volume per Column (m3)", col_volume_per_column),
                ("Reo Cover Known", col_cover_known), ("Reo Cover Used (mm)", round(col_cover * 1000, 0)),
                ("Longitudinal Bars (Group 1)", f"{col_long_qty} x {col_long_bar}"),
                ("Longitudinal Bars (Group 2)", f"{col_long_qty2} x {col_long_bar2}" if col_long_bar2 else "n/a"),
                ("Tie Bar / Spacing", f"{col_tie_bar} @ {col_tie_spacing_mm}mm"),
                ("Tie Perimeter (measured override, mm)", col_tie_perimeter_override_mm if col_tie_perimeter_override_mm > 0 else "auto"),
                ("Lig Bar / Qty per Level", f"{col_lig_bar} x {col_lig_qty}"),
                ("Steel Costing Mode", col_steel_mode),
                ("Reo Rate Given (kg/m3)", col_reo_rate_given),
                ("Reo Rate Estimated (kg/m3)", round(col_reo_rate_estimated, 2)),
                ("Dowel Mode", col_dowel_mode), ("Dowel Bar", col_dowel_bar),
                ("Dowels per Column (used)", col_dowel_qty_used),
                ("Lifting Points per Column", col_lifting_qty),
                ("Special Accessories per Column", col_accessories_qty),
                ("Price per Column ($)", round(col_price_per_column, 2)),
                ("Price per m3 ($)", round(col_price_per_m3, 2)),
                ("Estimated Total Group Cost ($)", round(col_total_group_cost, 2) if col_total_group_cost > 0 else "n/a"),
            ]
            r = 4
            for label, value in audit_rows:
                audit_sheet.write(r, 0, label)
                audit_sheet.write(r, 1, str(value))
                r += 1

        st.download_button(
            label="Download Excel Report",
            icon=":material/download:",
            data=col_output.getvalue(),
            file_name=f"{col_project_code}_{col_group_id}.xlsx" if col_project_code or col_group_id else "columns_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="col_download_button",
        )
    else:
        st.warning(
            "Enter the column width, depth, and either the group volume & quantity, "
            "or a direct average height, to start calculating.",
            icon=":material/warning:",
        )
