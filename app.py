import streamlit as st
import pandas as pd
import numpy as np
from CoolProp.CoolProp import PropsSI
from Balances.Balances import material_balance, Boling_Point_Elevation, energy_balancem, COP,simulate_evaporation,plot_evaporation_with_altair
#import fitz  # PyMuPDF
from PIL import Image
import time
import plotly.graph_objects as go
from stl import mesh as stl_mesh
import streamlit.components.v1 as components
from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile
import os

#---------------------------------------------------------------------------------
st.markdown("""
    <style>
    /* Fondo principal de la interfaz */
    .css-1v3fvcr {
        background-color: #3c3cb9; /* Blanco */
        color: black; /* Texto negro */
    }

   

    /* Botones de la barra lateral */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1C1C1C; /* Negro */
        color: white; /* Texto blanco */
        border-radius: 5px; /* Bordes redondeados */
        border: 1px solid white; /* Borde blanco */
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
#Set hover color to blue in all cases
st.markdown("""
    <style>
    /* Hover de todos los botones */
    .stButton > button:hover {
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
    st.session_state.current_window = 'Información general'

# Functions to change the window
def go_to_home():
    st.session_state.current_window = 'Información general'
import streamlit as st

def show_help_button():
    # Inicializar el estado si no existe
    if "show_help" not in st.session_state:
        st.session_state.show_help = False

    # CSS para el botón flotante
    st.markdown("""
        <style>
        #help-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #1E90FF;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            border-radius: 8px;
            z-index: 1000;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    # Botón como HTML + Streamlit callback
    clicked = st.button("Help", key="help_button", help="Click for guidance")

    if clicked:
        st.session_state.show_help = not st.session_state.show_help

    if st.session_state.show_help:
        with st.expander("Guía de la Interfaz del Gemelo Digital"):
            st.markdown("""
            Usa el menú de la izquierda para navegar por el gemelo digital:

            - **Información General:** visión general y objetivos de la unidad de evaporación.
            - **Simulación:** ejecuta casos en estado estacionario y transitorio.
            - **Videos, Imágenes y Repositorio:** revisa material y ejecuciones pasadas.
            - **Procedimientos:** instrucciones de laboratorio y pasos operativos.
            - **Visualización 3D:** explora un modelo espacial del equipo.
            - **Verificación de Seguridad:** lista de chequeo previa a la operación para concientización estudiantil.
            """)



def simulation_module():
    st.session_state.current_window = 'Simulation'

def procedures():
    st.session_state.current_window = 'Procedimientos'

def visuals():
    st.session_state.current_window = 'Videos, imagenes y planos'


def Visualización_3D():
    st.session_state.current_window = 'Visualización 3D'

def Safetycheck():
    st.session_state.current_window = 'Safety check'


def generate_simulation_pdf(sim_inputs, sim_results, df_results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_title("Simulation Report")

    # Título
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(0, 10, "Evaporator Simulation Summary", ln=True, align="C")
    pdf.ln(5)

    # Datos de entrada
    pdf.set_font("Arial", style="", size=12)
    pdf.cell(0, 10, "Input Conditions:", ln=True)
    for key, value in sim_inputs.items():
        pdf.cell(0, 8, f"- {key}: {value}", ln=True)

    pdf.ln(5)

    # KPIs
    pdf.cell(0, 10, "Key Performance Indicators (KPIs):", ln=True)
    for key, value in sim_results.items():
        pdf.cell(0, 8, f"- {key}: {value}", ln=True)

    pdf.ln(5)

    # Gráfico de concentración
    fig, ax = plt.subplots()
    ax.plot(df_results["time"], df_results["concentration_pct"], label="Concentration")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Concentration (% w/w)")
    ax.set_title("Concentration Profile")
    ax.grid(True)

    # Guardar imagen temporalmente
    tmpdir = tempfile.gettempdir()
    img_path = os.path.join(tmpdir, "temp_plot.png")
    plt.savefig(img_path)
    plt.close()

    # Agregar imagen
    pdf.image(img_path, x=10, w=180)

    # Observaciones
    pdf.ln(10)
    pdf.cell(0, 10, "Remarks:", ln=True)
    if float(sim_results["COP (%)"]) > 70:
        pdf.multi_cell(0, 8, "Excellent energy performance. This condition shows high efficiency.")
    elif float(sim_results["COP (%)"]) > 50:
        pdf.multi_cell(0, 8, "Acceptable performance. The operation is moderately efficient.")
    else:
        pdf.multi_cell(0, 8, "Low performance. Consider adjusting feed or steam parameters.")

    # Guardar PDF
    output_path = os.path.join(tmpdir, "simulation_summary.pdf")
    pdf.output(output_path)
    return output_path

#  Navigation menu options
st.sidebar.title("Navigation Menu")
st.sidebar.button("Información general", on_click=go_to_home)
st.sidebar.button("Simulation", on_click=simulation_module)
st.sidebar.button("Videos, imagenes y planos", on_click=visuals)
st.sidebar.button("Procedimientos", on_click=procedures)
st.sidebar.button("Visualización 3D", on_click=Visualización_3D)
st.sidebar.button("Safety check",on_click=Safetycheck)
#-------------------------------------------------------------------------------------
# Content based on the window selected in the navigation menu
if st.session_state.current_window == 'Información general':
    st.title("Gemelo digital-Evaporador multiefecto- Laboratorios de ingeniería química")
    centered_image('eq.jpg',width=600)

    st.write("""El banco de evaporadores en los laboratorios de ingeniería química ha sido seleccionado como la 
             piedra angular para inaugurar la era de los modelos digitales en la facultad. Este equipo desempeña un 
             papel fundamental en los experimentos relacionados con la concentración de soluciones, especialmente salmueras,
             debido a su capacidad para simular procesos industriales a escala de laboratorio.""")
    
    st.markdown("""
        ---

        ### Objetivos de aprendizaje

        - Comprender el principio de funcionamiento de un evaporador multiefecto.
        - Identificar las variables de operación críticas en procesos de concentración.
        - Analizar balances de materia y energía aplicados a evaporación.
        - Evaluar la eficiencia térmica (COP) bajo distintas condiciones.
        - Comparar resultados experimentales y simulados con soporte visual e interactivo.

        ---

        ### Aplicaciones industriales reales

        Este tipo de evaporadores se encuentra comúnmente en industrias como:

        - **Alimentaria**: concentración de jugos, leche, extractos naturales.
        - **Química**: recuperación de sales, concentración de soluciones inorgánicas.
        - **Farmacéutica**: preparación de compuestos sensibles a la temperatura.
        - **Tratamiento de aguas**: desalinización por evaporación.

        ---
        """)
    
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
    
    if simulation_type == "Transient state":
        # Inicializar repositorio si no existe
        if 'sim_repo' not in st.session_state:
            try:
                df_preloaded = pd.read_csv("evaporation_repository.csv")
                st.session_state.sim_repo = df_preloaded.to_dict(orient='records')
                st.success(" Preloaded simulation repository loaded.")
            except FileNotFoundError:
                st.session_state.sim_repo = []

        st.header("Trasient state simulation")
        st.write("This simulation is prepared for salt-water mixtures")
        # Asking for values from the user as numbers
        st.subheader("Enter Initial Conditions")
        M_init = st.number_input("Enter the initial mass (kg):", min_value=0.0, format="%.2f")
        T_init = st.number_input("Enter the initial temperature inside the effect (K):", min_value=0.0, format="%.2f")
        time_s = st.number_input("Enter the time for the simulation (min):", min_value=0.0, format="%.2f")
        T_f = st.number_input("Enter the feed temperature (K):", min_value=0.0, format="%.2f")
        P1 = st.number_input("Enter the absolute pressure inside the effect (Pa):", min_value=0.0, format="%.2f")
        Ps = st.number_input("Enter the steam absolute pressure (Pa):", min_value=0.0, format="%.2f")
        xf = st.number_input("Enter the concentration of the feed flow (% w/w):", min_value=0.0, format="%.2f")
                    
        if st.button("Submit", key="submit_simulation"):
            # Validación de entradas
            valid_inputs = True

            if M_init <= 0:
                st.error("Error: The flow must be greater than 0 kg.")
                valid_inputs = False
            if T_f < 273.153:
                st.error("Error: The feed temperature must be greater than 273.153 K.")
                valid_inputs = False
            if time_s < 5:
                st.error("Error: The time for the simulation must be greater than 5 min.")
                valid_inputs = False
            if T_init < 273.153:
                st.error("Error: The feed temperature must be greater than 273.153 K.")
                valid_inputs = False
            if P1 < 611.655 or P1 > 2.2064e+07:
                st.error("Error: The pressure inside the effect must be greater than 611.655 Pa.")
                valid_inputs = False
            if Ps < 611.655 or Ps > 2.2064e+07:
                st.error("Error: The steam pressure must be greater than 611.655 Pa.")
                valid_inputs = False
            if xf < 0 or xf > 16:
                st.error("Error: The concentration of the feed flow must be between 0 and 16 % w/w.")
                valid_inputs = False

            if valid_inputs:
                st.success("The initial data has been successfully uploaded.")

                P = 74000  # Atmospheric pressure (Pa)
                x_f = xf / 100
                M_salt_init = M_init * x_f
                total_time = time_s * 60

                results = simulate_evaporation(total_time, M_init, M_salt_init, T_init, P1, Ps, P, x_f, T_f)
                st.header("Plots for the evaporation process")
                plot_evaporation_with_altair(results)
                st.header("For this operation:")
                last_concentration = results["concentration_pct"][-1]
                cop_t=(results['total_vapor_evaporated']/results['total_steam_used'])*100
                summary_data = {
                    "Variable": [
                        "Final concentration in the evaporator",
                        "Total steam used (S)",
                        "Total vapor evaporated from the solution (V)",
                        "Coefficient of performance (COP)"
                    ],
                    "Value": [
                        f"{last_concentration:.2f}",
                        f"{results['total_steam_used']:.2f}",
                        f"{results['total_vapor_evaporated']:.2f}",
                        f"{cop_t:.2f}"
                    ],
                    "Unit": [
                        "% w/w",
                        "kg",
                        "kg",
                        "%"
                    ]
                }

                df_summary = pd.DataFrame(summary_data)
                

                from datetime import datetime

# Guardar esta simulación en el repositorio
                st.session_state.sim_repo.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Initial mass (kg)": M_init,
                "Feed temperature (K)": T_f,
                "Steam pressure (Pa)": Ps,
                "Effect pressure (Pa)": P1,
                "Feed concentration (% w/w)": xf,
                "Final concentration (% w/w)": last_concentration,
                "Total steam used (kg)": results['total_steam_used'],
                "Total vapor evaporated (kg)": results['total_vapor_evaporated'],
                "COP (%)": cop_t
                })

                # Display the table in HTML with center alignment
                st.markdown(
                    df_summary.style
                        .set_table_styles([
                            {"selector": "th", "props": [("text-align", "center")]}
                        ])
                        .set_properties(**{
                            "text-align": "center",
                            "padding": "6px"
                        })
                        .hide(axis="index")
                        .to_html(),
                    unsafe_allow_html=True
                )


                # Convertir el diccionario de resultados a DataFrame para exportar
                df_results = pd.DataFrame(results)

                # Botón de descarga de los datos simulados
                st.markdown("###  Export Options")
                st.markdown("Download the summary and full time series of the evaporation simulation:")

                csv_results = df_results.to_csv(index=False).encode('utf-8')
                st.download_button(
                label=" Download simulation data (full time series)",
                data=csv_results,
                file_name='evaporation_timeseries.csv',
                mime='text/csv'
                )
                
                with st.expander("Simulation results"):
                    tab1, tab2 = st.tabs(["Summary graphic", " Previous Simulations"])

                    with tab1:
                        # Gráfico resumen
                        if st.session_state.sim_repo:
                            import pandas as pd
                            import plotly.express as px
                            df_repo = pd.DataFrame(st.session_state.sim_repo)
                            fig = px.scatter_3d(
                                df_repo,
                                x="Effect pressure (Pa)",
                                y="Feed temperature (K)",
                                z="COP (%)",
                                color="Feed concentration (% w/w)",
                                size="Total vapor evaporated (kg)",
                                hover_name="Timestamp",
                                title="COP as function of Effect Pressure and Feed Concentration",
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            csv_repo = df_repo.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="Export repository as CSV",
                                data=csv_repo,
                                file_name='evaporation_repository.csv',
                                mime='text/csv'
                            )

                    with tab2:
                        # Resultados por simulación (NO usar expander aquí)
                        for i, sim in enumerate(st.session_state.sim_repo):
                            st.markdown(f"### Simulation {i+1} – {sim['Timestamp']}")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("COP (%)", f"{sim['COP (%)']:.2f}")
                            col2.metric("Final Conc. (% w/w)", f"{sim['Final concentration (% w/w)']:.2f}")

                            status = (
                                "🟢 Excellent" if sim['COP (%)'] > 70
                                else "🟠 Aceptable" if sim['COP (%)'] > 50
                                else "🔴 Bad"
                            )
                            col3.markdown(f"**Status:** {status}")

                            st.markdown(f"""
                            - **Initial mass:** {sim['Initial mass (kg)']} kg  
                            - **Feed T:** {sim['Feed temperature (K)']} K  
                            - **Steam P:** {sim['Steam pressure (Pa)']} Pa  
                            - **Effect P:** {sim['Effect pressure (Pa)']} Pa  
                            - **Feed concentration:** {sim['Feed concentration (% w/w)']} %  
                            - **Total steam used:** {sim['Total steam used (kg)']} kg  
                            - **Vapor evaporated:** {sim['Total vapor evaporated (kg)']} kg
                            """)

                # PDF actual
                sim_inputs = {
                    "Initial mass (kg)": M_init,
                    "Feed temperature (K)": T_f,
                    "Steam pressure (Pa)": Ps,
                    "Effect pressure (Pa)": P1,
                    "Feed concentration (% w/w)": xf,
                    "Simulation time (min)": time_s,
                }

                sim_results = {
                    "Final concentration (% w/w)": f"{last_concentration:.2f}",
                    "Total steam used (kg)": f"{results['total_steam_used']:.2f}",
                    "Total vapor evaporated (kg)": f"{results['total_vapor_evaporated']:.2f}",
                    "COP (%)": f"{cop_t:.2f}",
                }

                pdf_path = generate_simulation_pdf(sim_inputs, sim_results, df_results)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="Download Simulation Report (PDF)",
                        data=f,
                        file_name="simulation_summary.pdf",
                        mime="application/pdf"
                    )




elif st.session_state.current_window == 'Videos, imagenes y planos':
    st.markdown("""Esta sección presenta imágenes relevantes relacionadas con los tanques, válvulas y componentes del sistema de evaporación. 
                Estas imágenes proporcionan un soporte visual para comprender mejor el funcionamiento del equipo, identificar posibles fallas y 
                reforzar las recomendaciones de uso. A través de estas representaciones visuales, el objetivo es simplificar la interpretación técnica de aspectos 
                clave del sistema, desde la alimentación del tanque hasta las conexiones críticas del equipo.""" )
 # Buttons centered and in the same leves
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = None 

    col4, col5,col6 = st.columns(3)
    with col4:
        if st.button("Videos", key="videos", help="Videos", use_container_width=True):
            st.session_state.button_clicked = "Videos"
            
    with col5:
        if st.button("Imágenes", key="imágenes", help="Imágenes", use_container_width=True):
            st.session_state.button_clicked = "Imágenes"
    with col6:
        if st.button("Planos del equipo", key="planos del equipo", help="Planos del equipo", use_container_width=True):
            st.session_state.button_clicked = "Planos del equipo"   

            # Specific color whe the mouse hovers
    st.markdown("""
        <style>
        /* Estilos para los tres botones específicos */
        div[class="stButton"] button:nth-of-type(1):hover,
        div[class="stButton"] button:nth-of-type(2):hover,
        div[class="stButton"] button:nth-of-type(3):hover {
            background-color: #4682B4; /* Azul acero claro */
            color: white; /* Texto blanco */
            border: 1px solid #1E90FF; /* Borde azul brillante */
        }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.button_clicked == "Videos": 
        
        st.subheader("Video tutorial de operación")
        

    elif st.session_state.button_clicked == "Planos del equipo":

                    # Specific color whe the mouse hovers
            st.markdown("""
                <style>
                /* Estilos para los tres botones específicos */
                div[class="stButton"] button:nth-of-type(1):hover,
                div[class="stButton"] button:nth-of-type(2):hover,
                div[class="stButton"] button:nth-of-type(3):hover {
                    background-color: #4682B4; /* Azul acero claro */
                    color: white; /* Texto blanco */
                    border: 1px solid #1E90FF; /* Borde azul brillante */
                }
                </style>
            """, unsafe_allow_html=True)

            if st.session_state.button_clicked == "Planos del equipo":
                    st.subheader("Planos del equipo")
                    centered_image(r"Evaporador - planos_page-0001.jpg", 950)
                    centered_image(r"Evaporador - planos_page-0002.jpg", 950)
                    centered_image(r"Evaporador - planos_page-0003.jpg", 950)
                    centered_image(r"Evaporador - planos_page-0004.jpg", 950)
                    centered_image(r"Evaporador - planos_page-0005.jpg", 950)
                    centered_image(r"Evaporador - planos_page-0006.jpg", 950)
                    centered_image(r"Evaporador - planos_page-0007.jpg", 950)
                    centered_image(r"Evaporador - planos_page-0008.jpg", 950)

            

    elif st.session_state.button_clicked == "Imágenes":
        st.header(" Documentación visual del equipo")

        st.markdown("""
                    Esta sección brinda un tour visual por los principales componentes y condiciones del sistema de evaporación
        """)

        image_data = [
            ("Tanques de alimento y condensado", "feed.jpg", "Los tanques a continuación presentan el tanque en que se alimenta la solución y donde se recoge el vapor condensado"),
            ("Valvula de vapor 1", "EntradaVapor.jpeg", "Esta es la primera valvula a abrir para permitir el flujo de vapor vivo al sistema de evaporación"),
            ("Valvula de vapor 2", "EntradaVapor2.jpeg", "Esta es la segunda valvula a abrir para permitir el flujo de vapor vivo al sistema de evaporación"),
            ("Valvula con fallas", "LlaveDanada.jpeg", "Esta valvula presenta fallas visibles "),
            ("Tapes on the Lines", "ReferenciasMarcadas.jpeg", "Tapes mark operational references. Se recomienda cuidado al manejarla, ya que esta permite el flujo de agua fresca"),
            ("Balanzas", "NuevasBalanzas.jpeg", "Las balanzas presentadas indican la masa del tanque+su contenido interno"),
            ("Tubería de salida del condensado", "TuberiaCorta.jpeg", "Este segmento de tubería corresponde a la tubería para vaciar el condensado"),
            ("Tubería peligrosa y caliente", "TuberiaPeligrosa.jpeg", "Esta tubería es peligrosa, tiene superficies muy calientes"),
            ("Manometro", "Manometro.jpeg", "Instrumento para medir la presión del vapor, se encuentra presente en varias partes del equipo"),
        ]

        # Mostrar en filas de 3 columnas
        for i in range(0, len(image_data), 3):
            cols = st.columns(3)
            for col, (title, img_path, caption) in zip(cols, image_data[i:i+3]):
                with col:
                    st.image(img_path, caption=f" {caption}", use_column_width=True)
                    st.markdown(f"**{title}**", unsafe_allow_html=True)



   

   
elif st.session_state.current_window == 'Procedimientos':
    st.title("Procesos importantes")
    st.write("""En esta sección presione el botón de la información que desea consultar""")
    # Create columns to display the buttons
    if "button_clicked" not in st.session_state:
     st.session_state.button_clicked = None  # o cualquier valor predeterminado
     
     
    col1, col2, col3 = st.columns(3)

    # Buttons centered and in the same leves
    with col1:
        if st.button("Manual de operación", key="manual_operacion", help="Manual de operación", use_container_width=True):
            st.session_state.button_clicked = "Manual de operación"
            
    with col2:
        if st.button("Recomendaciones", key="recomendaciones", help="Recomendaciones", use_container_width=True):
            st.session_state.button_clicked = "Recomendaciones"
            
    with col3:
        if st.button("Diagramas de flujo", key="diagramas_flujo", help="Diagramas de flujo", use_container_width=True):
            st.session_state.button_clicked = "Diagramas de flujo"
            # Specific color whe the mouse hovers
    st.markdown("""
        <style>
        /* Estilos para los tres botones específicos */
        div[class="stButton"] button:nth-of-type(1):hover,
        div[class="stButton"] button:nth-of-type(2):hover,
        div[class="stButton"] button:nth-of-type(3):hover {
            background-color: #4682B4; /* Azul acero claro */
            color: white; /* Texto blanco */
            border: 1px solid #1E90FF; /* Borde azul brillante */
        }
        </style>
    """, unsafe_allow_html=True)

    # Information depending on the button clicked
    if st.session_state.button_clicked == "Manual de operación":
            st.write("""Para facilitar el acceso al protocolo de quienes usen el banco de evaporadores ésta sección se suministra en español únicamente""")
            st.header("Protocolo de encendido")

            st.write("1. Antes de iniciar la práctica cercióese de que todos los tanques de recolección se encuentren vacíos, al igual que el cuerpo del evaporador.")

            st.write("2. Identificación de válvulas para efecto simple con el Evaporador 1, se identifican las válvulas que deben estar abiertas durante la operación con cinta de color azul.")
            centered_image(r"cinta.jpg", width=200)

            st.write("3. Control de nivel de los tanques")
            st.write("- Las válvulas del control de nivel del tanque de recolección del vapor producido en el efecto deben permanecer cerradas.")
            st.write("- Las válvulas del control de nivel del tanque de alimentación deben permanecer abiertas.")

            st.write("4. Permita el paso de agua al cuerpo del evaporador abriendo las válvulas mostradas a continuación:")
            centered_image(r"agua.jpg", width=400)

            st.write("5. Encienda y tare todas las balanzas en los tanques de recolección")

            st.write("6. Llene el tanque con al menos 20 kg de la solución a evaporar. No debe estar vacío durante la práctica.")

            st.write("7. Conecte el enchufe trifásico para encender el equipo")

            st.write("8. Conecte el computador al equipo y confirme que el computador tiene carga antes de iniciar.")
            centered_image(r"conectar.png", width=400)


            st.write("""
            9. Para encender debe girar por completo hacia la derecha la perilla, 
            **<font color="blue">en color azul</font>** está el encendido general del equipo, 
            el recuadro **<font color="ForestGreen">de color verde</font>** es el encendido de la bomba de alimento, 
            el recuadro **<font color="orange">de color naranja</font>** es el indicador de luz que permite saber si la electroválvula está activa y llenando el evaporador 1, 
            en el momento en que el evaporador esté lleno esta luz se apagará.
            """, unsafe_allow_html=True)

            centered_image(r"tablero.png", width=500)

            st.write("10. Encienda la \textbf{bomba de alimento} para cargar el evaporador con la solución a usar, este se llena con aproximadamente 8 kg de solución")

            st.write("11. Acceda al programa **ASTRA RUN** el cual permite ver las temperaturas a lo largo del equipo.")
            centered_image(r"sw.png", width=400)

            st.write("12. Activación de la línea de vapor")
            st.write("""**<font color="red">La línea de vapor que proviene de la caldera debe ser la última en ser activada 
                        y la primera en cerrarse, recuerde obtener autorización del docente para permitir el paso de vapor al equipo 
                        y previamente debe solicitar que se encienda la caldera del LIQ.</font>**""", unsafe_allow_html=True)
            st.write("13. Realice la apertura de las válvulas de la línea de vapor de forma lenta. El procedimiento a seguir es" )
            st.write("a)  Antes de permitir el flujo de vapor por el equipo cargue todo el cuerpo del efecto con la solución a trabajar.")
            st.write("**b)** Primer manómetro (naranja): mantener cerca a 20psi.")
            centered_image(r"llavenaranja.jpg", width=400)
            st.write("**c)** Segundo manómetro (azul): Manipular hasta aproximadamente 10psi.")
            centered_image(r"azul.jpg", width=400)
            st.write("**d)** Manómetro con válvula roja abajo 5-10 psi")
            centered_image(r"roja.jpg", width=400)

            st.write("14. Permitir el paso de vapor al equipo, registrando la temperatura del evaporador en función del tiempo, al igual que el vapor de alta usado.")
            st.write("15. La evaporación de la solución se evidencia al obtener masa en el tanque de recolección del condensado, registre la temperatura en la cual se empieza a recoger este vapor condensado.")
            centered_image(r"condensado.png", width=400)
            st.markdown("""
            Tanque de recolección del vapor condensado (**<font color="red">recuadro rojo</font>**), 
            Tanque de alimentación (**<font color="yellow">recuadro amarillo</font>**)
            """, unsafe_allow_html=True)
            st.write("""16. Se debe considerar que el acero como tal del equipo debe tener un pre-calentamiento para asegurar un buen desarrollo de la práctica. 
                        Mientras mayor sea el tiempo de este pre-calentamiento mejores serán los resultados, se recomienda que sea de mínimo 20 min.""")
            st.write("""17. Si el equipo es utilizado con fines de llegar a una concentración en específico, se pueden utilizar las muestras
                        obtenidas del licor final para someterlas a una cromatografía, espectrofotometría e incluso a un difractómetro
                        para ver con precisión cuál es la concentración de la solución final. Adicional, en caso de trabajar con solución 
                        salina se propone la opción de realizar este análisis de la concentración haciendo uso de la conductividad.""")
            #In the case they are using vaccum pressre___________________________________________________________________________
            st.subheader("Para ensayos a vacío")
            st.write("""
            A partir del **paso 11** de la sección de **_Protocolo de encendido_** se debe seguir el siguiente proceso:

            1. Abra las válvulas que permiten el paso de agua a la bomba de vacío, son las que se muestran
                        **<font color="red">**Sin verificar que las válvulas estén abiertas no encienda la bomba de vacío**</font>.

            2. Luego de verificar el suministro de agua a la bomba de vacío, encienda la bomba girando hacia la derecha la 
                        perilla presente en el tablero, encerrada en el 
                        recuadro **<font color="Plum">morado</font>** la cual se encuentra etiquetada como **_Bomba vacío_**.

            3. El control del vacío se realiza cerrando la válvula mostrada en la imagen a continuación. 
                        Cierre lentamente hasta llegar al vacío deseado que se recomienda esté entre -0.3 bar y -0.4 bar.

            Si genera más vacío del deseado no abra inmediatamente para presurizar el sistema, deje el valor en el que se encuentra y rectifique sus cálculos según corresponda.
            """, unsafe_allow_html=True)
            centered_image(r"tanquevcon.png", width=400)

            st.write("4. A partir de este punto, continúe con el paso 12 de la sección de **_Protocolo de encendido_**.")
            #----------------------------------------------
            st.subheader("Protocolo de operación")
            st.write("1. Mantener el tanque de alimentación con líquido.")
            st.write("2. Monitorear constantemente las válvulas de la línea de vapor vivo.")
            st.write("3. Tomar datos en función del tiempo de las variables de proceso.")

            st.subheader("Protocolo de apagado")
            st.write("1. Cerrar la línea de vapor en orden inverso al encendido.")
            st.write("2. Apagar la bomba de vacío si está en uso.")
            st.write("3. Apagar la bomba de alimento.")
            st.write("4. Realizar el apagado general del equipo en el tablero.")
            st.write("5. Desconectar el enchufe trifásico.")
            st.write("6. Cerrar las válvulas de paso de agua.")
            st.write("7. Vaciar todos los tanques, incluyendo el cuerpo del efecto.")
        
            with st.expander("Manual de operación y respositorio de prácticas anteriores"):
                st.markdown("###Documentos disponibles")
                st.write(
                    "Estos documentos corresponden a manual de operación del gemelo digital "
                    "Puedes usarlos como guía para estructurar tus propios informes."
                )

                col1, col2 = st.columns(2)

                with col1:
                    with open("Manual_de_uso (1).pdf", "rb") as file1:
                        st.download_button(
                            label=" Descargar Manual de operación",
                            data=file1,
                            file_name="Manual_de_uso (1).pdf",
                            mime="application/pdf"
                        )
                    st.caption(
                        "Contiene uso del gemelo, del sistema y demás "
                    )


    elif st.session_state.button_clicked == "Recomendaciones":
        
        # Verificar el estado del idioma dentro de Procedures
        if 'language_Equipment' not in st.session_state:
            st.session_state.language_Equipment = 'English'  # Idioma predeterminado para esta sección

        # Botón para cambiar idioma dentro de Procedures
        if st.button("Español" if st.session_state.language_Equipment == 'English' else "English"):
            st.session_state.language_Equipment = 'Español' if st.session_state.language_Equipment == 'English' else 'English'

        # Mostrar contenido según el idioma seleccionado
        if st.session_state.language_Equipment == 'English':
            st.title("General recomendations to use the Equipment")
            st.markdown("""
        - It should be considered that the steel of the equipment requires preheating to ensure the practice runs smoothly.
        - Taking into account the initial temperature of the solution in the feed tank may explain the need for a higher amount of steam from the boiler.
        - The level control valves of the tank that collects the steam produced in the effect must always remain closed to avoid breaking its glass. The feed tank level valves should remain open.
        - For the steam from the boiler, it is recommended to maintain line pressure between 10psig ; the valves required to achieve this should be controlled by **one person only**.
        - **The steam line from the boiler should be the last to be activated and requires prior authorization from the instructor.**
        """)
        else:
            st.title("Información y recomendaciones generales ")
            st.markdown("""
        - Identificar muy bien cada corriente, recuerde que esto ayuda a garantizar las condiciones de seguridad para todos en el laboratorio, con este propósito se marcaron las válvulas que deben usarse durante la operación de un efecto con cinta de color azul.
        - Antes de iniciar la práctica cerciórese de que todos los tanques de recolección se encuentren vacíos y al finalizar vacié todo incluyendo el cuerpo del efecto, esto garantiza conservar los equipos en estado óptimo.
        - La línea de vapor que proviene de la caldera debe ser la última en ser activada y la primera en cerrarse, recuerde obtener autorización del docente para permitir el paso de vapor al equipo""")
        

    elif st.session_state.button_clicked == "Diagramas de flujo":
        st.write("""Para facilitar el acceso al protocolo de quienes usen el banco de evaporadores la sección se suministra en español únicamente""")
        st.subheader("Diagrama de flujo")
        centered_image(r"Diagrama de flujo_OperacionAGUA.png", 950)
    

elif st.session_state.current_window == 'Visualización 3D':
    
    st.title("Visualización 3D del Evaporador")
    components.html(
    """
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>

    <model-viewer 
        src="https://raw.githubusercontent.com/Juandhb99/proyecto-evaporadores/main/Evaporador2.glb"
        alt="Modelo 3D del Evaporador"
        auto-rotate
        camera-controls
        auto-rotate-delay="1000"
        rotation-per-second="30deg"
        environment-image="legacy"
        exposure="1"
        shadow-intensity="1"
        shadow-softness="0.8"
        style="width: 100%; height: 700px; background-color: #111111;"
    >
    </model-viewer>
    """,
    height=750,
)

    

elif st.session_state.current_window == 'Safety check':
    st.title("🔴 Control de Seguridad del Evaporador")

    # *Rangos de Seguridad*
    TEMP_MIN, TEMP_MAX = 15, 100  # Temperatura en °C (ejemplo)
    VPRESSURE_MIN, VPRESSURE_MAX = -0.4, 0  # Presión manometrica de vacio bar (ejemplo)
    PRESSURE_MIN, PRESSURE_MAX = 39000, 77000  # Presión en Pascales (ejemplo)
    SPRESSURE_MIN, SPRESSURE_MAX = 5, 20  # Presión en psig (ejemplo)

    # *Inputs de usuario*
    st.sidebar.header("Parámetros de Operación")
    temperature = st.sidebar.number_input(" Temperatura en el efecto (°C)")
    pressure = st.sidebar.number_input(" Presión en el efecto (Pa)")
    S_presure = st.sidebar.number_input(" Presión del vapor de la caldera (psig)")
    V_presure = st.sidebar.number_input(" Presión manométrica de vacío (bar)",max_value=0.0)

    # *Registro de Alertas*
    alerts = []

    # *Verificación de Seguridad*
    st.subheader(" Estado del Sistema")

    if temperature < TEMP_MIN:
        alerts.append(f"⚠️ *Temperatura muy baja*: {temperature} °C (mínimo permitido {TEMP_MIN} °C)")
    elif temperature > TEMP_MAX:
        alerts.append(f"🚨 *Temperatura demasiado alta*: {temperature} °C (máximo permitido {TEMP_MAX} °C)")

    if pressure < PRESSURE_MIN:
        alerts.append(f"⚠️ *Presión demasiado baja*: {pressure} Pa (mínimo permitido {PRESSURE_MIN} Pa)")
    elif pressure > PRESSURE_MAX:
        alerts.append(f"🚨 *Presión excesiva*: {pressure} Pa (máximo permitido {PRESSURE_MAX} Pa)")

    if S_presure < SPRESSURE_MIN:
        alerts.append(f"⚠️ *Presión del vapor muy baja*: {S_presure} psig (mínimo permitido {SPRESSURE_MIN} psig)")
    elif S_presure > SPRESSURE_MAX:
        alerts.append(f"🚨 *Presión del vapor muy alta*: {S_presure} psig (máximo permitido {SPRESSURE_MAX} psig)")
    if V_presure < VPRESSURE_MIN:
        alerts.append(f"⚠️ *Presión del vapor muy baja*: {V_presure} psig (mínimo permitido {VPRESSURE_MIN} psig)")
    elif V_presure > VPRESSURE_MAX:
        alerts.append(f"🚨 *Presión del vapor muy alta*: {V_presure} psig (máximo permitido {VPRESSURE_MAX} psig)")

    # *Mostrar Alertas*
    if alerts:
        st.warning("⚠️ *ALERTA*: Se han detectado condiciones fuera de los límites seguros.")
        for alert in alerts:
            st.markdown(alert)
    else:
        st.success("✅ *Sistema en condiciones óptimas para operar*.")

    # *Historial de Alertas*
    st.subheader("📋 Registro de Eventos de Seguridad")
    df_alerts = pd.DataFrame(alerts, columns=["Mensaje de Alerta"])

    if not df_alerts.empty:
        st.write(df_alerts)
        
    else:
        st.info("No se han registrado alertas hasta el momento.")

# Llamar a la función para mostrar el botón al final de la página
show_help_button()

#streamlit run app.py

