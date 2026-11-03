
import streamlit as st
import pandas as pd

from app.modules.electrical_design.load_calculations import (
    calculate_electrical_load,
)
from app.modules.electrical_design.load_schedule import (
    calculate_load_schedule,
)

from app.modules.electrical_design.schedule_reports import (
    generate_excel_report,
    generate_pdf_report,
)


MODULES = {
    "Electrical Design": [
        "Electrical Load Analysis",
        "Electrical Load Schedule",
        "Cable Sizing",
        "Transformer Sizing",
        "Voltage Drop",
        "Lighting Design",
    ],
    "Power Systems": [
        "Load Flow Analysis",
        "Short Circuit Analysis",
        "Protection Coordination",
        "Arc Flash Analysis",
    ],
    "Substations": [
        "Substation Design",
        "Equipment Sizing",
        "Earthing and Grounding",
        "Busbar Sizing",
    ],
    "Data Centers": [
        "UPS Sizing",
        "Generator Sizing",
        "PDU Distribution",
        "Electrical Redundancy",
    ],
    "Renewable Energy": [
        "Solar PV Sizing",
        "Battery Energy Storage",
        "Microgrid Analysis",
    ],
    "BOQ & Estimation": [
        "Electrical Quantity Takeoff",
        "Material Estimation",
        "Cost Estimation",
    ],
}


def render_dashboard():

    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            background-color: #111827;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #F8FAFC !important;
        }

        .dashboard-subtitle {
            color: #64748b;
            font-size: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("EEIP")
    st.sidebar.caption(
        "Electrical Engineering Intelligence Platform"
    )
    st.sidebar.divider()

    pages = [
        "Overview",
        "Electrical Design",
        "Power Systems",
        "Substations",
        "Data Centers",
        "Renewable Energy",
        "BOQ & Estimation",
        "Reports",
        "Settings",
    ]

    selected_page = st.sidebar.radio(
        "NAVIGATION",
        pages
    )

    st.sidebar.divider()
    st.sidebar.caption("EEIP Development Version 0.2")

    if selected_page == "Overview":
        render_overview()

    elif selected_page == "Electrical Design":
        render_electrical_design()

    elif selected_page in MODULES:
        render_module(selected_page)

    elif selected_page == "Reports":
        st.title("Engineering Reports")
        st.info("PDF and Excel reporting is planned.")

    elif selected_page == "Settings":
        st.title("Platform Settings")
        st.info("Engineering standards and configuration are planned.")


def render_overview():

    st.title("Electrical Engineering Intelligence Platform")

    st.markdown(
        '<p class="dashboard-subtitle">'
        'Integrated electrical design, engineering calculations, '
        'power systems and project intelligence.'
        '</p>',
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("Engineering Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Active Projects", "0")
    col2.metric("Calculations", "0")
    col3.metric("Engineering Modules", "6")
    col4.metric("Reports Generated", "0")

    st.divider()

    st.subheader("Engineering Modules")

    columns = st.columns(3)

    for index, (module, tools) in enumerate(MODULES.items()):

        with columns[index % 3]:

            with st.container(border=True):

                st.subheader(module)

                st.caption(f"{len(tools)} engineering tools")

                for tool in tools:
                    st.write(f"- {tool}")

    st.divider()

    st.success("EEIP application environment is operational.")

    st.caption(
        "Development version 0.2. "
        "Engineering calculation modules are being implemented progressively."
    )


# def render_electrical_design():

#     st.title("Electrical Design")

#     st.caption(
#         "Electrical load analysis and engineering calculations"
#     )

#     st.divider()

#     selected_tool = st.selectbox(
#         "Select Engineering Tool",
#         MODULES["Electrical Design"]
#     )

#     if selected_tool == "Electrical Load Analysis":
#         render_load_calculator()

#     else:
#         st.info(
#             f"{selected_tool} is planned for a future development milestone."
#         )


def render_electrical_design():

    st.title("Electrical Design")

    st.caption(
        "Electrical design calculations and load scheduling"
    )

    st.divider()

    selected_tool = st.selectbox(
        "Select Engineering Tool",
        MODULES["Electrical Design"]
    )

    if selected_tool == "Electrical Load Analysis":

        render_load_calculator()

    elif selected_tool == "Electrical Load Schedule":

        render_equipment_load_schedule()

    else:

        st.info(
            f"{selected_tool} is planned for a future milestone."
        )


def render_equipment_load_schedule():

    st.subheader("Equipment-wise Electrical Load Schedule")

    st.caption(
        "Commercial building | IEC-oriented preliminary design"
    )

    project_name = st.text_input(
        "Project Name",
        value="Commercial Building - Project 001"
    )

    st.divider()

    default_records = [
        {
            "equipment": "Lighting",
            "distribution_board": "DB-L01",
            "quantity": 100,
            "unit_kw": 0.020,
            "demand_factor": 1.0,
            "power_factor": 0.95,
            "phase": "Single Phase",
            "voltage": 230.0,
        },
        {
            "equipment": "Socket Outlets",
            "distribution_board": "DB-P01",
            "quantity": 40,
            "unit_kw": 0.200,
            "demand_factor": 0.6,
            "power_factor": 0.90,
            "phase": "Single Phase",
            "voltage": 230.0,
        },
        {
            "equipment": "Air Conditioners",
            "distribution_board": "DB-M01",
            "quantity": 10,
            "unit_kw": 2.0,
            "demand_factor": 0.9,
            "power_factor": 0.90,
            "phase": "Three Phase",
            "voltage": 400.0,
        },
        {
            "equipment": "Water Pumps",
            "distribution_board": "DB-M01",
            "quantity": 2,
            "unit_kw": 5.5,
            "demand_factor": 1.0,
            "power_factor": 0.85,
            "phase": "Three Phase",
            "voltage": 400.0,
        },
        {
            "equipment": "Elevators",
            "distribution_board": "DB-M01",
            "quantity": 2,
            "unit_kw": 7.5,
            "demand_factor": 1.0,
            "power_factor": 0.85,
            "phase": "Three Phase",
            "voltage": 400.0,
        },
    ]

    if "schedule_editor_data" not in st.session_state:

        st.session_state["schedule_editor_data"] = (
            pd.DataFrame(default_records)
        )

    st.subheader("Equipment Registration")

    st.caption(
        "Edit the sample records or add your own equipment."
    )

    edited_df = st.data_editor(
        st.session_state["schedule_editor_data"],
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        key="equipment_schedule_editor",
        column_config={
            "equipment": st.column_config.TextColumn(
                "Equipment",
                required=True,
            ),
            "distribution_board": st.column_config.TextColumn(
                "Distribution Board",
                required=True,
            ),
            "quantity": st.column_config.NumberColumn(
                "Quantity",
                min_value=1,
                step=1,
                format="%d",
            ),
            "unit_kw": st.column_config.NumberColumn(
                "Unit Load (kW)",
                min_value=0.001,
                format="%.3f",
            ),
            "demand_factor": st.column_config.NumberColumn(
                "Demand Factor",
                min_value=0.01,
                max_value=1.0,
                format="%.2f",
            ),
            "power_factor": st.column_config.NumberColumn(
                "Power Factor",
                min_value=0.01,
                max_value=1.0,
                format="%.2f",
            ),
            "phase": st.column_config.SelectboxColumn(
                "Phase",
                options=["Single Phase", "Three Phase"],
                required=True,
            ),
            "voltage": st.column_config.NumberColumn(
                "Voltage (V)",
                min_value=1.0,
                format="%.0f",
            ),
        },
    )

    st.session_state["schedule_editor_data"] = edited_df.copy()

    st.divider()

    st.subheader("Distribution Board Configuration")

    db_names = sorted(
        edited_df["distribution_board"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    diversity_by_db = {}

    for db in db_names:

        if not db:
            continue

        diversity_by_db[db] = st.number_input(
            f"{db} - Diversity Factor",
            min_value=1.0,
            value=1.0,
            step=0.1,
            key=f"diversity_{db}",
        )

    st.caption(
        "A default diversity factor of 1.0 means no diversity "
        "reduction. Change it only when supported by the project design basis."
    )

    st.divider()

    if st.button(
        "Generate Electrical Load Schedule",
        type="primary",
    ):

        try:

            if not project_name.strip():
                raise ValueError("Enter a project name.")

            records = edited_df.to_dict(orient="records")

            results = calculate_load_schedule(
                records,
                diversity_by_db,
            )

            st.session_state["schedule_results"] = results
            st.session_state["schedule_project"] = project_name

            st.success(
                "Electrical load schedule generated successfully."
            )

        except (ValueError, TypeError, KeyError) as error:

            st.error(f"Calculation error: {error}")

    if "schedule_results" in st.session_state:

        results = st.session_state["schedule_results"]

        project = st.session_state["schedule_project"]

        st.divider()

        st.subheader("Load Schedule Results")

        total = results["totals"]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Connected Load",
            f'{total["connected_kw"]:.2f} kW'
        )

        col2.metric(
            "Maximum Demand",
            f'{total["maximum_demand_kw"]:.2f} kW'
        )

        col3.metric(
            "Sum of DB Apparent Powers",
            f'{total["apparent_power_kva"]:.2f} kVA'
        )

        st.subheader("Equipment-wise Schedule")

        equipment_df = pd.DataFrame(results["equipment"])

        st.dataframe(
            equipment_df,
            width="stretch",
            hide_index=True,
        )

        st.subheader("Distribution Board Summary")

        db_df = pd.DataFrame(results["distribution_boards"])

        st.dataframe(
            db_df,
            width="stretch",
            hide_index=True,
        )

        st.warning(
            "Preliminary engineering calculations. Verify design "
            "assumptions, equipment ratings, phase allocation, "
            "protection and applicable IEC requirements before approval."
        )

        st.divider()

        st.subheader("Export Engineering Reports")

        col1, col2 = st.columns(2)

        try:

            excel_data = generate_excel_report(
                results,
                project,
            )

            pdf_data = generate_pdf_report(
                results,
                project,
            )

            with col1:

                st.download_button(
                    "Download Excel Schedule",
                    data=excel_data,
                    file_name="EEIP_Electrical_Load_Schedule.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    width="stretch",
                )

            with col2:

                st.download_button(
                    "Download PDF Report",
                    data=pdf_data,
                    file_name="EEIP_Electrical_Load_Schedule.pdf",
                    mime="application/pdf",
                    width="stretch",
                )

        except Exception as error:

            st.error(f"Report generation failed: {error}")


def render_load_calculator():

    st.subheader("Electrical Load Calculation")

    st.write(
        "Enter the connected electrical load and design parameters."
    )

    col1, col2 = st.columns(2)

    with col1:

        connected_load = st.number_input(
            "Connected Load (kW)",
            min_value=0.1,
            value=100.0,
            step=1.0
        )

        demand_factor = st.number_input(
            "Demand Factor",
            min_value=0.01,
            max_value=1.0,
            value=0.8,
            step=0.05
        )

        diversity_factor = st.number_input(
            "Diversity Factor",
            min_value=1.0,
            value=1.2,
            step=0.1
        )

    with col2:

        power_factor = st.number_input(
            "Power Factor",
            min_value=0.01,
            max_value=1.0,
            value=0.9,
            step=0.01
        )

        voltage = st.number_input(
            "System Voltage (V)",
            min_value=1.0,
            value=400.0,
            step=10.0
        )

        phase = st.selectbox(
            "Supply Configuration",
            ["Three Phase", "Single Phase"]
        )

    if st.button("Calculate Electrical Load", type="primary"):

        try:

            result = calculate_electrical_load(
                connected_load_kw=connected_load,
                demand_factor=demand_factor,
                diversity_factor=diversity_factor,
                power_factor=power_factor,
                voltage=voltage,
                phase=phase,
            )

            st.session_state["load_result"] = result

        except ValueError as error:

            st.error(str(error))

    if "load_result" in st.session_state:

        result = st.session_state["load_result"]

        st.divider()

        st.subheader("Calculation Results")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Connected Load",
            f"{result['connected_load_kw']:.2f} kW"
        )

        col2.metric(
            "Maximum Demand",
            f"{result['maximum_demand_kw']:.2f} kW"
        )

        col3.metric(
            "Apparent Power",
            f"{result['apparent_power_kva']:.2f} kVA"
        )

        col4, col5 = st.columns(2)

        col4.metric(
            "Calculated Current",
            f"{result['current_a']:.2f} A"
        )

        col5.metric(
            "Power Factor",
            f"{result['power_factor']:.2f}"
        )

        st.subheader("Calculation Summary")

        summary = pd.DataFrame([
            ["Connected Load", result["connected_load_kw"], "kW"],
            ["Demand Load", result["demand_load_kw"], "kW"],
            ["Maximum Demand", result["maximum_demand_kw"], "kW"],
            ["Apparent Power", result["apparent_power_kva"], "kVA"],
            ["Full Load Current", result["current_a"], "A"],
        ], columns=["Parameter", "Value", "Unit"])

        st.dataframe(
            summary,
            width="stretch",
            hide_index=True
        )

        st.info(
            "Preliminary calculation only. Confirm the demand and "
            "diversity factors against the actual load groups and "
            "applicable design standard before using the result."
        )

        csv = summary.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Calculation as CSV",
            data=csv,
            file_name="eeip_load_calculation.csv",
            mime="text/csv"
        )


def render_module(module_name):

    st.title(module_name)

    st.caption(
        "Electrical Engineering Intelligence Platform"
    )

    st.divider()

    st.subheader("Available Engineering Tools")

    for tool in MODULES[module_name]:

        with st.container(border=True):

            st.write(f"**{tool}**")
            st.caption("Implementation planned.")

    st.info(
        "This module is under development. "
        "Validated engineering calculation engines will be introduced progressively."
    )
