import streamlit as st
import pandas as pd
from Balances.Balances import ask_for_inputs, material_balance, Boling_Point_Elevation, energy_balance,energy_balancem,COP
from Properties.Propertiesdef import properties_prediction,training
#-----------------------------------------------------------
ruta="logo.png"
st.image(ruta,width=200)
#-----------------------------------------------------------
# Define the kind of simulation to be done
st.header("App for the evaporator system")
simulation_type = st.selectbox(
    "Choose the simulation type",
    ("Select an option", "Stationary state", "Transient state"),
)

# Different displays
if simulation_type == "Stationary state":
    option= st.selectbox(
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
            st.error("Error: The initial flow must be greater than 0 kg.")
        elif xf < 0 or xf > 100:
            st.error("Error: The concentration of the feed flow must be between 0 and 100 % w/w.")
        elif Tf <= 273.153:
            st.error("Error: The feed temperature must be greater than 273.153 K.")
        elif P1 <=611.655 or P1 > 2.2064e+07:
            st.error("Error: The pressure inside the effect must be greater than 611.655 Pa.")
        elif Ps <=611.655 or Ps > 2.2064e+07:
            st.error("Error: The steam pressure must be greater than 611.655 Pa.")
        elif xL < 0 or xL > 100:
            st.error("Error: The concentration of the output flow must be between 0 and 100 % w/w.")
        else:
            st.success("The initial data has been successfully uploaded.")
            #Apply the functions
            L,V=material_balance(F,xf,xL)
            BPE, T1=Boling_Point_Elevation(xf,P1)
            S,Ts,U=energy_balancem(xf,Tf,P1,T1,Ps,F,V,L,xL,option)
            cop=COP(V,S)
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
                    "Value": [
                        f"{L:.2f} kg",
                        f"{V:.2f} kg",
                        f"{BPE:.2f} °C",
                        f"{T1:.2f} K",
                        f"{S:.2f} kg",
                        f"{Ts:.2f} K",
                        f"{U:.2f} J/K*cm²",
                        f"{cop:.2f}"
                    ]
                }
            results_df = pd.DataFrame(results)
            st.markdown("## **Calculated Values**")
            st.table(results_df)  # Muestra la tabla sin la columna experimental

    
elif simulation_type == "Transient state":
    st.header("Transient state simulation")
    option= st.selectbox(
    "Choose the solution",
    ("Select an option", "Water-Water", "Water-Salt"),)
    if option == "Select an option":
        st.error("Error: Please select a valid solution option to continue.")
else:
    st.error("Error: Please select a valid simulation type to continue.")
#streamlit run app.py