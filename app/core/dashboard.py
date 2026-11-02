
import streamlit as st


MODULES = {
    "Electrical Design": [
        "Electrical Load Analysis",
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

        .dashboard-subtitle {
            color: #94a3b8;
            font-size: 15px;
        }

        .section-heading {
            font-weight: 600;
            font-size: 21px;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("EEIP")
    st.sidebar.caption("Electrical Engineering Intelligence Platform")
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
    st.sidebar.caption("EEIP Development Version 0.1")

    if selected_page == "Overview":
        render_overview()

    elif selected_page in MODULES:
        render_module(selected_page)

    elif selected_page == "Reports":
        st.title("Engineering Reports")
        st.info("Automated PDF and Excel reporting will be developed here.")

    elif selected_page == "Settings":
        st.title("Platform Settings")
        st.info("Engineering standards and project configuration will be developed here.")


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

    module_columns = st.columns(3)

    module_names = list(MODULES.keys())

    for index, module in enumerate(module_names):

        with module_columns[index % 3]:

            with st.container(border=True):

                st.subheader(module)

                st.caption(
                    f"{len(MODULES[module])} planned engineering tools"
                )

                for tool in MODULES[module]:
                    st.write(f"- {tool}")

    st.divider()

    st.subheader("Platform Status")

    st.success(
        "EEIP application environment is operational."
    )

    st.caption(
        "Engineering calculations are under development. "
        "Displayed dashboard metrics are initial placeholders."
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
        "This module is currently under development. "
        "Validated calculation engines will be introduced progressively."
    )
