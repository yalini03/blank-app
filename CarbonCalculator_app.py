import streamlit as st
import math
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title = "Tree Carbon Calculator", layout = "centered")
st.title("Biofilters: Tree Carbon Calculator")

#Declaring Formula Functions

def equation_A(dbh, wood_density):
    """AGB for DBH > 25 cm"""
    if dbh <= 0 or wood_density <= 0:
        raise ValueError ("DBH & Wood Density must be greater than 0")
    #agb = wood_density * math.exp(-1.499 + 2.148 * math.log(dbh)+ 0.207 * (math.log(dbh) ** 2)- 0.0281 * (math.log(dbh) ** 3))
    agb = wood_density * np.exp(-1.499 + 2.148 * np.log(dbh) + 0.207 * (np.log(dbh))**2 - 0.0281 * (np.log(dbh))**3)
    return agb

def equation_B(dbh):
    """LB for DBH > 25 cm & <= 25 cm"""
    if dbh <= 0:
        raise ValueError ("DBH must be greater than 0")
    #lb = math.exp(-5.136 + 2.882 * math.log(dbh)- 0.156 * (math.log(dbh) ** 2))
    lb = np.exp(-5.136 + 2.882 * np.log(dbh) - 0.156 * (np.log(dbh))**2)
    return lb

def equation_C(dbh, wood_density):
    """AGB for DBH <= 25 cm"""
    if dbh <= 0 or wood_density <= 0:
        raise ValueError ("DBH & Wood Density must be greater than 0")
    #agb = math.exp(-1.130 + (2.267 * math.log(dbh))+ (1.186 * math.log(wood_density)))
    agb = np.exp(-1.130 + 2.267 * np.log(dbh) + 1.186 * np.log(wood_density))
    return agb

def calculate_Simulated_dbh(dbh, t=1):
    if dbh < 20:
        r = 0.0525
        c = 0.636
    else:
        r = 0.101
        c = 0.554
        
    Dt = (dbh ** (1 - c) + r * (1 - c) * t)**(1 / (1 - c))
    return Dt

#Declaring Calculation Functions

def calculate_AGB_LB(dbh, wood_density):
    if dbh > 25:
        agb = equation_A(dbh, wood_density)
        lb = equation_B(dbh)
        equation_used = "Equation AGB and Equation B"
    else:
        agb = equation_C(dbh, wood_density)
        lb = equation_B(dbh)
        equation_used = "Equation C and Equation B"
    return agb, lb, equation_used

def Urban_Tree_AGB(agb):
    return agb * 0.8

def calculate_carbon_storage(Urban_Tree_AGB):
    return 0.47 * Urban_Tree_AGB

health_factor_dict = {
    "Excellent": 1.00,
    "Good": 0.42,
    "Fair": 0.15,
    "Dead": 0
}

if "results_log" not in st.session_state:
    st.session_state.results_log = []


st.subheader("Input Tree Information")

species = st.text_input("Species Name")
col1, col2 = st.columns(2)
with col1:
    dbh = st.number_input("DBH (cm)", min_value=0.1, value=25.0, step=0.1)
    #carbon_type = st.selectbox("Select Carbon Factor",["General Tree [0.47]", "Urban Tree [0.8]"])
with col2:
    wood_density = st.number_input("Wood density, ρ (g/cm³)", min_value=0.08, max_value=1.39, value=0.1, step=0.01)
    #health_Level = st.selectbox("Tree Health Level",["Excellent", "Good", "Fair", "Poor"])
    
health_Level = st.selectbox("Tree Health Level",["Excellent", "Good", "Fair", "Poor"])
health_factor = health_factor_dict[health_Level]

# if carbon_type == "General Tree [0.47]":
#         carbon_factor = 0.47
# else:
#     carbon_factor = 0.8

if st.button("Calculate Carbon Storage, Sequestration & CO2 Equivalent"):

    # Current DBH calculation
    agb, lb, equation_used = calculate_AGB_LB(dbh, wood_density)
    urban_tree_agb = Urban_Tree_AGB(agb)
    carbon_storage = calculate_carbon_storage(urban_tree_agb)

    # Simulated DBH after 1 year
    Dt = calculate_Simulated_dbh(dbh, t=1)

    # AGB and LB using simulated DBH
    agb_dt, lb_dt, equation_used_dt = calculate_AGB_LB(Dt, wood_density)
    urban_tree_agb_dt = Urban_Tree_AGB(agb_dt)
    carbon_storage_dt = calculate_carbon_storage(urban_tree_agb_dt)

    carbon_sequestration = (carbon_storage_dt - carbon_storage) * health_factor
    co2_equivalent = carbon_sequestration * (44 / 12)

    result = {
        "Species": species,
        "DBH (cm)": dbh,
        "Wood Density (g/cm³)": wood_density,
        "Tree Health Level": health_Level,
        #"Carbon Factor": carbon_factor,
        #"Current AGB (kg/tree)": agb,
        #"Current LB (kg/tree)": lb,
        "Urban Tree AGB (kg tree)": urban_tree_agb,
        "Current Carbon Storage (kg C/tree)": carbon_storage,
        "Simulated DBH After 1 Year (cm)": Dt,
        #"Simulated AGB (kg/tree)": agb_dt,
        #"Simulated LB (kg/tree)": lb_dt,
        "Simulated Urban Tree AGB (kg tree)": urban_tree_agb_dt,
        "Simulated Carbon Storage (kg C/tree)": carbon_storage_dt,
        "Carbon Sequestration (kg C/tree/year)": carbon_sequestration,
        "CO2 Equivalent (kg CO2/tree/year)": co2_equivalent

    }

    st.session_state.results_log.append(result)

    st.subheader("Results")

    st.write(f"Species: **{species}**")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Current DBH")
        st.write(f"DBH (cm): {dbh:.2f}")
        #st.write(f"Equation used: {equation_used}")
        #st.write("AGB (kg/tree):", f"{agb:.2f}")
        #st.write("LB (kg/tree):", f"{lb:.2f}")
        st.write("Urban Tree AGB (kg/tree):", f"{urban_tree_agb:.2f}")
        st.success(f"Carbon Storage: **{carbon_storage:.2f} kg C/tree**")

    with col2:
        st.markdown("### Simulated DBH After 1 Year")
        st.write(f"Simulated DBH, (cm): {Dt:.2f}")
        #st.write(f"Equation used: {equation_used_dt}")
        #st.write("Simulated AGB (kg/tree):", f"{agb_dt:.2f}")
        #st.write("Simulated LB (kg/tree):", f"{lb_dt:.2f}")
        st.write("Simulated Urban Tree AGB (kg/tree):", f"{urban_tree_agb_dt:.2f}")
        st.success(f"Simulated Carbon Storage: **{carbon_storage_dt:.2f} kg C/tree**")
    
    st.success(f"Carbon Sequestration: **{carbon_sequestration:.2f} kg C/tree/year**")
    st.success(f"CO2 Equivalent: **{co2_equivalent:.2f} kg CO2/tree/year**")

    st.info("This result has been added to the saved results log.")

if len(st.session_state.results_log) > 0:

    st.subheader("Saved Results Log")

    log_df = pd.DataFrame(st.session_state.results_log)

    st.dataframe(log_df)

    csv = log_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download All Results as CSV",
        data=csv,
        file_name="tree_carbon_results_log.csv",
        mime="text/csv"
    )

    if st.button("Clear Results Log"):
        st.session_state.results_log = []
        st.warning("Results log cleared. Please refresh or calculate again.")  
