import streamlit as st
import pandas as pd
from CoolProp.CoolProp import PropsSI
from Balances.Balances import material_balance, Boling_Point_Elevation, energy_balancem, COP
from Properties.Propertiesdef import properties_prediction, training
from pdf2image import convert_from_path

#---------------------------------------------------------------------------------
st.markdown("""
    <style>
    /* Fondo principal de la interfaz */
    .css-1v3fvcr {
        background-color: #524b7d; /* Blanco */
        color: black; /* Texto negro */
    }

    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #524b7d !important; /* Rojo oscuro */
        color: white; /* Texto blanco */
    }

    /* Botones de la barra lateral */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1C1C1C; /* Negro */
        color: white; /* Texto blanco */
        border-radius: 5px; /* Bordes redondeados */
        border: 3px solid white; /* Borde blanco */
        font-size: 16px; /* Tamaño del texto */
        margin: 10px 0; /* Espaciado entre botones */
    }

    /* Hover de los botones */
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #4682B4; /* Azul acero claro */
        color: white; /* Texto blanco */
        border: 1px solid #1E90FF; /* Borde azul brillante */
    }
    </style>
""", unsafe_allow_html=True)


st.image("logo.png", width=200)


def centered_image(image_path, width):

    col1, col2, col3 = st.columns([1, width / 100, 1])
    with col1:
        st.write("") 
    with col2:
        st.image(image_path, width=width)
    with col3:
        st.write("") 
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

def procedures():
    st.session_state.current_window = 'Procedures'

def visuals():
    st.session_state.current_window = 'Useful videos and pictures'

def Repository():
    st.session_state.current_window = 'Repository/Reports'

def Dashboard():
    st.session_state.current_window = 'Dashboard'

def Alerts():
    st.session_state.current_window = 'Alerts'

#  Navigation menu options
st.sidebar.title("Navigation Menu")
st.sidebar.button("General information", on_click=go_to_home)
st.sidebar.button("Simulation", on_click=simulation_module)
st.sidebar.button("Equipment Usage Recommendations", on_click=recommendations)
st.sidebar.button("Useful videos and pictures", on_click=visuals)
st.sidebar.button("Procedures", on_click=procedures)
st.sidebar.button("Repository/Reports", on_click=Repository)
st.sidebar.button("Dashboard", on_click=Dashboard)
st.sidebar.button("Alerts",on_click=Alerts)
#-------------------------------------------------------------------------------------
# Content based on the window selected in the navigation menu
if st.session_state.current_window == 'General information':
    st.title("Chemical engineering Lab - Multieffect Evaporator Digital Twin")
    centered_image('eq.jpg',width=600)

    st.write("""El banco de evaporadores en los laboratorios de ingeniería química ha sido seleccionado como la 
             piedra angular para inaugurar la era de los modelos digitales en la facultad. Este equipo desempeña un 
             papel fundamental en los experimentos relacionados con la concentración de soluciones, especialmente salmueras, }
             debido a su capacidad para simular procesos industriales a escala de laboratorio.""")
    
    st.write("""The evaporator bank in the chemical engineering laboratories has been chosen as the cornerstone 
             to inaugurate the era of digital models in the faculty. This equipment plays a fundamental role 
             in experiments related to the concentration of solutions, especially brines, due to its ability to 
             simulate industrial processes on a laboratory scale.""")

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
            st.error("Please select a valid solution option to continue.")
        else:
            st.header("Stationary state simulation")
            # Asking for values from the user as numbers
            st.subheader("Enter Initial Conditions")
            F = st.number_input("Enter the initial mass (kg):", min_value=0.0, format="%.2f")
            Tf = st.number_input("Enter the feed temperature (K):", min_value=0.0, format="%.2f")
            P1 = st.number_input("Enter the absolute pressure inside the effect (Pa):", min_value=0.0, format="%.2f")
            Ps = st.number_input("Enter the steam absolute pressure (Pa):", min_value=0.0, format="%.2f")
            if option=="Water-Water":
                V = st.number_input("Enter the vapor mass to be collected (kg):", min_value=0.0, format="%.2f")
            else:
                xf = st.number_input("Enter the concentration of the feed flow (% w/w):", min_value=0.0, format="%.2f")
                xL = st.number_input("Enter the concentration of the output flow (% w/w):", min_value=0.0, format="%.2f")
                    
            
            if st.button("Submit"):
                # Validate inputs
                if F <= 0:
                    st.error("Error: The flow must be greater than 0 kg.")
                elif Tf < 273.153:
                    st.error("Error: The feed temperature must be greater than 273.153 K.")
                elif P1 < 611.655 or P1 > 2.2064e+07:
                    st.error("Error: The pressure inside the effect must be greater than 611.655 Pa.")
                elif Ps < 611.655 or Ps > 2.2064e+07:
                    st.error("Error: The steam pressure must be greater than 611.655 Pa.")
                if option=="Water-Salt":
                    if xL < 0 or xL > 16:
                        st.error("Error: The concentration of the output flow must be between 0 and 16 % w/w.")
                    elif xf < 0 or xf > 16:
                        st.error("Error: The concentration of the feed flow must be between 0 and 16 % w/w.")

                st.success("The initial data has been successfully uploaded.")

                    # Apply the functions
                    
                if option=="Water-Water":
                        L = F-V
                        BPE="N/A"
                        xf=0
                        xL=0
                        T1=PropsSI('T', 'P', P1, 'Q', 0, 'Water')+0.01 #Boiling point of pure water at P1 (°C)
                else:
                        L, V = material_balance(F, xf, xL)
                        BPE, T1 = Boling_Point_Elevation(xf, P1)
                        
                S, Ts, U = energy_balancem(xf, Tf, P1, T1, Ps, F, V, L, xL)
                cop = COP(V, S)
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
                        "Unit": ["kg", "kg", "°C", "K", "kg", "K", "J/K*cm²", "N/A"],
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

                        elif T1e <= 273.153:
                            st.error("Error: The feed temperature must be greater than 273.153 K.")
                        
                        else:
                            st.success("The experimental data has been successfully uploaded.")
                            results_dfc = st.session_state.results_df.rename(columns={"Value": "Calculated Value"})
                            tolerance = 0.05 * F  # 5% of F
                            if abs((Le + Ve) - F) > tolerance:
                                st.warning("Warning: The sum of liquor flow (L) and vapor flow (V) differs from the initial flow (F) by more than 5%. Please check your balances.")
                            # Find the steam temperature at Ps
                            Tse = PropsSI('T', 'P', Ps, 'Q', 0, 'Water')  # Boiling point of pure water at Ps (K)
                            H_liq = PropsSI('H', 'P', Ps, 'Q', 0, 'Water')
                            H_vap = PropsSI('H', 'P', Ps, 'Q', 1, 'Water')
                            l_heat = H_vap - H_liq 
                            Ue = (Se * l_heat) / (3054 * (Tse - T1e))
                            cope = COP(Ve, Se)
                            BPEe = T1e - (PropsSI('T', 'P', P1, 'Q', 0, 'Water'))
                            results_dfc["Experimental Values"] = [Le, Ve, BPEe, T1e, Se, Tse, Ue, cope] 
                            if option == "Water-Water":
                                results_dfc = results_dfc[results_dfc["Variable"] != "Boiling Point Elevation (BPE)"]                       
                            results_dfc["Error (%)"] = abs((results_dfc["Experimental Values"] - results_dfc["Calculated Value"])/results_dfc["Calculated Value"]) * 100

                            # Format absolute error to 2 decimals
                            results_dfc["Experimental Values"] = results_dfc["Experimental Values"].map(lambda x: f"{x:.2f}")
                            results_dfc["Calculated Value"] = results_dfc["Calculated Value"].map(lambda x: f"{x:.2f}")
                            results_dfc["Error (%)"] = results_dfc["Error (%)"].map(lambda x: f"{x:.1f}")
                            results_dfc=results_dfc.style.set_properties(**{'text-align': 'center'}).set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
                            st.markdown("## *Calculated Values*")
                            st.write(results_dfc.to_html(), unsafe_allow_html=True)

                elif compare == "No":
                    st.markdown("## *Calculated Values*")
                    results_df_display = st.session_state.results_df.copy()
                    results_df_display["Value"] = pd.to_numeric(results_df_display["Value"], errors="coerce")
                    results_df_display["Value"] = results_df_display["Value"].map(lambda x: f"{x:.2f}")  # Use 3 decimals
                    results_df_display=results_df_display.style.set_properties(**{'text-align': 'center'}).set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
                    st.write(results_df_display.to_html(), unsafe_allow_html=True)

elif st.session_state.current_window == 'Equipment Usage Recommendations':
    st.title("General recomendations to use the Equipment/Información y recomendaciones generales ")
    st.write("SOME INFO")
     # Verificar el estado del idioma dentro de Procedures
    if 'language_Equipment' not in st.session_state:
        st.session_state.language_Equipment = 'English'  # Idioma predeterminado para esta sección

    # Botón para cambiar idioma dentro de Procedures
    if st.button("Español" if st.session_state.language_Equipment == 'English' else "English"):
        st.session_state.language_Equipment = 'Español' if st.session_state.language_Equipment == 'English' else 'English'

    # Mostrar contenido según el idioma seleccionado
    if st.session_state.language_Equipment == 'English':
        st.markdown("""
    - It should be considered that the steel of the equipment requires preheating to ensure the practice runs smoothly.
    - Taking into account the initial temperature of the solution in the feed tank may explain the need for a higher amount of steam from the boiler.
    - The level control valves of the tank that collects the steam produced in the effect must always remain closed to avoid breaking its glass. The feed tank level valves should remain open.
    - For the steam from the boiler, it is recommended to maintain line pressure between 0.3 and 0.4; the valves required to achieve this should be controlled by **one person only**.
    - **The steam line from the boiler should be the last to be activated and requires prior authorization from the instructor.**
    """)
    else:
        st.markdown("""
    - Identificar muy bien cada corriente, recuerde que esto ayuda a garantizar las condiciones de seguridad para todos en el laboratorio, con este propósito se marcaron las válvulas que deben usarse durante la operación de un efecto con cinta de color azul.
    - Antes de iniciar la práctica cerciórese de que todos los tanques de recolección se encuentren vacíos y al finalizar vacié todo incluyendo el cuerpo del efecto, esto garantiza conservar los equipos en estado óptimo.
    - La línea de vapor que proviene de la caldera debe ser la última en ser activada y la primera en cerrarse, recuerde obtener autorización del docente para permitir el paso de vapor al equipo""")
    
    st.title("Changes made")
    st.markdown("""A steam flow control loop regulates the amount of steam in a pipe through an adjustable valve. It includes 
    sensors and a controller that monitor the flow. The control strategy would be feedback control, where the measurement is taken at the pressure at the inlet of the effect, 
    and the final action is performed on an automatic flow valve that restricts the steam entering the equipment. Thus, this control loop is classified as a system where the controlled variable 
    is the pressure at the inlet of the effect, and the objective is to maintain it within a desired range to ensure efficient and safe operation of the equipment. The controller compares the actual pressure measurement
     with the reference value or setpoint, generating a correction signal that adjusts the opening of the automatic valve to regulate the steam flow. This allows for compensation of external disturbances or changes in operating
     conditions, ensuring stable and optimal process performance.""")
    
elif st.session_state.current_window == 'Useful videos and pictures':
    st.markdown("""This section features relevant images related to the tanks, valves, and components of the evaporation system. 
    These images provide visual support to better understand the operation of the equipment, identify potential failures, and 
    reinforce usage recommendations. Through these visual representations, the goal is to simplify the technical interpretation 
    of key aspects of the system, from tank feed to critical equipment connections.""" )

    st.header("Tanks")
    # Feed Tank
    st.subheader("Feed Tank")
    centered_image(r"Images_Evaporador\feed.jpg", 400)
    # Condensed Steam Tank
    st.subheader("Vapor valve")
    centered_image(r"Images_Evaporador\EntradaVapor.jpeg", 400)
    st.subheader("Second vapor valve")
    centered_image(r"Images_Evaporador\EntradaVapor2.jpeg", 400)

    # Condensed Vapor Tank
    st.subheader("Broken valve")
    centered_image(r"Images_Evaporador\LlaveDanada.jpeg", 400)

    st.subheader("Tapes on the lines")
    centered_image(r"Images_Evaporador\ReferenciasMarcadas.jpeg", 400)

    st.subheader("New balances")
    centered_image(r"Images_Evaporador\NuevasBalanzas.jpeg", 400)

    st.subheader("Short pipe")
    centered_image(r"Images_Evaporador\TuberiaCorta.jpeg", 400)

    st.subheader("Dangerous pipe")
    centered_image(r"Images_Evaporador\TuberiaPeligrosa.jpeg", 400)

    st.subheader("Manometer")
    centered_image(r"Images_Evaporador\Manometro.jpeg", 400)

elif st.session_state.current_window == 'Procedures':
    st.subheader("Flow Diagram")
    centered_image(r"Images_Evaporador\Diagrama de flujo_OperacionAGUA.png", 950)
    st.subheader("Dlow Fiagram")
    centered_image(r"Images_Evaporador\SolucionAgua.png", 950)

    # Verificar el estado del idioma dentro de Procedures
    if 'language_procedures' not in st.session_state:
        st.session_state.language_procedures = 'English'  # Idioma predeterminado para esta sección

    # Botón para cambiar idioma dentro de Procedures
    if st.button("Español" if st.session_state.language_procedures == 'English' else "English"):
        st.session_state.language_procedures = 'Español' if st.session_state.language_procedures == 'English' else 'English'

    # Mostrar contenido según el idioma seleccionado
    if st.session_state.language_procedures == 'English':
        st.markdown("""
            The procedure to open the steam line is as follows: Before allowing steam to flow through the equipment, fill the entire effect body with the solution to be processed.
            - First orange pressure gauge: Maintain close to 20 psi.
            - Second blue pressure gauge: Adjust to approximately 10 psi.
            - Pressure gauge with red valve below: Set between 5-10 psi.
            After completing the practice, follow this same sequence.

            The proper way to operate is as follows:

            1. Load the evaporator with the solution to be used. Approximately 7.6 kg of solution is added, allowing the liquid to flow through the feed pump.

            2. Allow steam to flow into the equipment, recording the evaporator's temperature as a function of time, as well as the amount of high-pressure steam used.

            3. The evaporation of the solution will be evident when mass is collected in the vapor collection tank. Record the temperature at which vapor begins to be collected. Perform measurements at intervals of 1-2 minutes until the practice is completed.
        """)
    else:
        st.markdown("""
            El procedimiento para abrir la línea de vapor es el siguiente: Antes de permitir el flujo de vapor por el equipo, cargue todo el cuerpo del efecto con la solución a trabajar.
            - Primer manómetro naranja: mantener cerca a 20 psi.
            - Segundo manómetro azul: Manipular hasta aproximadamente 10 psi.
            - Manómetro con válvula roja abajo: entre 5-10 psi.
            Al acabar la práctica siga esta misma secuencia.

            La manera adecuada de operar es:

            1. Cargar el evaporador con la solución a usar. Este se llena con aproximadamente 7.6 kg de solución, permitiendo el flujo de líquido a través de la bomba de alimento.

            2. Permitir el paso de vapor al equipo, registrando la temperatura del evaporador en función del tiempo, así como el vapor de alta usado.

            3. La evaporación de la solución se evidenciará al obtener masa en el tanque de recolección del vapor. Registre la temperatura en la cual se empieza a recoger este vapor. Realizar mediciones en intervalos de 1-2 minutos hasta acabar la práctica.
        """)


elif st.session_state.current_window == 'Repository/Reports':
    st.title("Visualizar PDF como imágenes")
    import fitz  # PyMuPDF
    from PIL import Image

    pdf_path = "Images_Evaporador/Evaporador - planos.pdf"

    doc = fitz.open(pdf_path)
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        st.image(img, use_column_width=True)




elif st.session_state.current_window == 'Dashboard':
    st.title("Real-Time Dashboard")
    st.write("This dashboard monitors key system parameters in real-time.")

    # Simulación de datos en tiempo real
    import numpy as np
    import time

    data = pd.DataFrame(columns=["Time", "Pressure (Pa)", "Temperature (K)"])
    for i in range(10):  # Simula 10 iteraciones
        new_row = {
            "Time": i,
            "Pressure (Pa)": np.random.uniform(1e5, 2e5),  # Presión aleatoria
            "Temperature (K)": np.random.uniform(273, 373),  # Temperatura aleatoria
        }
        data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
        st.line_chart(data[["Pressure (Pa)", "Temperature (K)"]])
        time.sleep(1)


#streamlit run app.py

#Images_Evaporador