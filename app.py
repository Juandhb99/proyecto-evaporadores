import streamlit as st
import pandas as pd

from CoolProp.CoolProp import PropsSI
from Balances.Balances import ask_for_inputs, material_balance, Boling_Point_Elevation, energy_balancem, COP
from Properties.Propertiesdef import properties_prediction, training
#-----------------------------------------------------------

#To make the color of the background black 

st.markdown(
     """
     <style>
     body {
         background-color: black;
         color: white; /* Para que el texto sea visible */
     }
     .stApp {
         background-color: black;
     }
     </style>
     """,
     unsafe_allow_html=True
 )
#-------------------------------------------------------------------------------------
ruta = "logo.png"
st.image(ruta, width=200)
#----------------------------------------------------------------------------
if 'current_window' not in st.session_state:
    st.session_state.current_window = 'General information'

# Functions to change the window
def go_to_home():
    st.session_state.current_window = 'General information'

def simulation_module():
    st.session_state.current_window = 'Simulation'

def recommendations():
    st.session_state.current_window = 'Equipment Usage Recommendations'

#  Navigation menu options
st.sidebar.title("Navigation Menu")
st.sidebar.button("General information", on_click=go_to_home)
st.sidebar.button("Simulation", on_click=simulation_module)
st.sidebar.button("Equipment Usage Recommendations", on_click=recommendations)
#-------------------------------------------------------------------------------------
# Content based on the window selected in the navigation menu
if st.session_state.current_window == 'General information':
    st.title("Some general information about the evaporator system")
    st.write("SOME INFO")
elif st.session_state.current_window == 'Simulation':

    # Define the kind of simulation to be done
    st.title("Simulation app for the evaporator system")

    #Choose the simulation type to be done
    simulation_type = st.selectbox(
        "Choose the simulation type",
        ("Select an option", "Stationary state", "Transient state"),
    )

    # Initialize a session state variable to hold results
    if 'results_df' not in st.session_state:
        st.session_state.results_df = None

    # Different displays
    if simulation_type == "Stationary state":
        option = st.selectbox(
            "Choose the solution",
            ("Select an option", "Water-Water", "Water-Salt"),
        )
        
        if option == "Select an option":
            st.error("Error: Please select a valid solution option to continue.")

        st.header("Stationary state simulation")
        # Asking for values from the user as numbers
        st.subheader("Enter Initial Conditions")
        F = st.number_input("Enter the initial flow (kg):", min_value=0.0, format="%.2f")
        xf = st.number_input("Enter the concentration of the feed flow (% w/w):", min_value=0.0, format="%.2f")
        Tf = st.number_input("Enter the feed temperature (K):", min_value=0.0, format="%.2f")
        P1 = st.number_input("Enter the absolute pressure inside the effect (Pa):", min_value=0.0, format="%.2f")
        Ps = st.number_input("Enter the steam absolute pressure (Pa):", min_value=0.0, format="%.2f")
        xL = st.number_input("Enter the concentration of the output flow (% w/w):", min_value=0.0, format="%.2f")
        
        if st.button("Submit"):
            # Validate inputs
            if F <= 0:
                st.error("Error: The flow must be greater than 0 kg.")
            elif xf < 0 or xf > 16:
                st.error("Error: The concentration of the feed flow must be between 0 and 16 % w/w.")
            elif Tf < 273.153:
                st.error("Error: The feed temperature must be greater than 273.153 K.")
            elif P1 < 611.655 or P1 > 2.2064e+07:
                st.error("Error: The pressure inside the effect must be greater than 611.655 Pa.")
            elif Ps < 611.655 or Ps > 2.2064e+07:
                st.error("Error: The steam pressure must be greater than 611.655 Pa.")
            elif xL < 0 or xL > 16:
                st.error("Error: The concentration of the output flow must be between 0 and 16 % w/w.")
            else:
                st.success("The initial data has been successfully uploaded.")

                # Apply the functions
                L, V = material_balance(F, xf, xL)
                BPE, T1 = Boling_Point_Elevation(xf, P1)
                S, Ts, U = energy_balancem(xf, Tf, P1, T1, Ps, F, V, L, xL, option)
                cop = COP(V, S)
                if option=="Water-Water":
                    BPE="NA"
                # Create a DataFrame to show the results
                results = {
                    "Variable": [
                        "Liquor Flow (L)",
                        "Vapor Flow (V)",
                        "Boiling Point Elevation (BPE)",
                        "Temperature inside the effect (T1)",
                        "Steam Mass Flow (S)",
                        "Temperature of the Steam (Ts)",
                        "Overall Heat Transfer Coefficient (U)",
                        "Coefficient of Performance (COP)"
                    ],
                    "Unit": ["kg", "kg", "°C", "K", "kg", "K", "J/K*cm²", "NA"],
                    "Value": [L, V, BPE, T1, S, Ts, U, cop]
                }
                #Save the data to use later
                st.session_state.results_df = pd.DataFrame(results) 

        # Compare section only shows after submit
        if st.session_state.results_df is not None:
            st.subheader("Experimental data")
            compare = st.radio(
                "Do you want to compare your experimental data?",
                ( "Yes", "No"),
            )

            if compare == "Yes":
                st.subheader("Please ensure that the experimental data are collected under the same conditions as specified above.")
                Le = st.number_input("Enter the amount of liquor collected (kg):", min_value=0.0, format="%.2f")
                Ve = st.number_input("Enter the amount of vapor collected (kg):", min_value=0.0, format="%.2f")
                Se = st.number_input("Enter the amount of steam collected (kg):", min_value=0.0, format="%.2f")
                T1e = st.number_input("Enter the temperature inside the effect (K):", min_value=273.153, format="%.2f")
                

                if st.button("Submit experimental data"):
                    if Le <= 0 or Ve <= 0 or Se <= 0:
                        st.error("Error: The flow must be greater than 0 kg.")
                    tolerance = 0.05 * F  # 5% of F
                    if abs((Le + Ve) - F) > tolerance:
                        st.warning("Warning: The sum of liquor flow (L) and vapor flow (V) differs from the initial flow (F) by more than 5%. Please check your balances.")
                    elif T1e <= 273.153:
                        st.error("Error: The feed temperature must be greater than 273.153 K.")
                    
                    else:
                        st.success("The experimental data has been successfully uploaded.")
                        results_dfc = st.session_state.results_df.rename(columns={"Value": "Calculated Value"})

                        # Find the steam temperature at Ps
                        Tse = PropsSI('T', 'P', Ps, 'Q', 0, 'Water')  # Boiling point of pure water at Ps (K)
                        H_liq = PropsSI('H', 'P', Ps, 'Q', 0, 'Water')
                        H_vap = PropsSI('H', 'P', Ps, 'Q', 1, 'Water')
                        l_heat = H_vap - H_liq 
                        Ue = (Se * l_heat) / (3054 * (Tse - T1e))
                        cope = COP(Ve, Se)
                        BPEe = T1e - (PropsSI('T', 'P', P1, 'Q', 0, 'Water'))
                        results_dfc["Experimental Values"] = [Le, Ve, BPEe, T1e, Se, Tse, Ue, cope]
                        results_dfc["Error (%)"] = abs((results_dfc["Experimental Values"] - results_dfc["Calculated Value"])/results_dfc["Calculated Value"]) * 100

                        # Format absolute error to 2 decimals
                        results_dfc["Experimental Values"] = results_dfc["Experimental Values"].map(lambda x: f"{x:.2f}")
                        results_dfc["Calculated Value"] = results_dfc["Calculated Value"].map(lambda x: f"{x:.2f}")
                        results_dfc["Error (%)"] = results_dfc["Error (%)"].map(lambda x: f"{x:.2f}")
                        results_dfc=results_dfc.style.set_properties(**{'text-align': 'center'}).set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
                        st.markdown("## **Calculated Values**")
                        st.write(results_dfc.to_html(), unsafe_allow_html=True)

            elif compare == "No":
                st.markdown("## **Calculated Values**")
                results_df_display = st.session_state.results_df.copy()
                results_df_display["Value"] = results_df_display["Value"].map(lambda x: f"{x:.2f}")  # Use 3 decimals
                results_df_display=results_df_display.style.set_properties(**{'text-align': 'center'}).set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
                st.write(results_df_display.to_html(), unsafe_allow_html=True)

        
    elif simulation_type == "Transient state":
        st.header("Transient state simulation")
        option= st.selectbox(
        "Choose the solution",
        ("Select an option", "Water-Water", "Water-Salt"),)
        if option == "Select an option":
            st.error("Error: Please select a valid solution option to continue.")
        st.subheader("Working on it...")
    else:
        st.error("Error: Please select a valid simulation type to continue.")
elif st.session_state.current_window == 'Equipment Usage Recommendations':
    st.title("General recomendations to use the Equipment")
    st.write("SOME INFO")
    st.markdown("""
    - It should be considered that the steel of the equipment requires preheating to ensure the practice runs smoothly.
    - Taking into account the initial temperature of the solution in the feed tank may explain the need for a higher amount of steam from the boiler.
    - The level control valves of the tank that collects the steam produced in the effect must always remain closed to avoid breaking its glass. The feed tank level valves should remain open.
    - For the steam from the boiler, it is recommended to maintain line pressure between 0.3 and 0.4; the valves required to achieve this should be controlled by **one person only**.
    - **The steam line from the boiler should be the last to be activated and requires prior authorization from the instructor.**
    """)

#streamlit run app.py