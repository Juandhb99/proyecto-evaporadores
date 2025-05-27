
from CoolProp.CoolProp import PropsSI
import streamlit as st
import altair as alt
import pandas as pd
def material_balance(F:float,xf:float,xL:float):
    """
    Calculates the material balance in an evaporator.

    This function determines the liquor flow (L) and vapor flow (V) exiting an evaporator 
    based on the initial flow (F) and the concentrations of the inlet (xf) and outlet (xL) flows.
    Args:
        F (float): Initial flow in kg.
        xf (float): Concentration of the flow in % w/w.
        xL (float): Concentration of the output flow in % w/w.

    Returns:
        L (float): Liquor flow out of the evaporator in kg. 
        V (float): Vapor flow out of the evaporator in kg.
    """    
    L=F*xf/xL
    V=F-L
    print(f"Feed flow (F): {F} kg\nFeed concentration (xf): {xf} % w/w\nLiquor concentration (xL): {xL} % w/w")
    print(f"Liquor flow (L): {L:.2f} kg\nVapor flow (V): {V:.2f} kg")
    return L,V
def Boling_Point_Elevation(xf:float,P1: float):
    """
    Calculates the boiling point elevation (BPE) and the corresponding temperature inside a system (T1) 
    based on a given concentration of a solute (salt) and the absolute pressure of the system
    Args:
        xf (float): Concentration of the flow (% w/w).
        Tf (float): Feed temperature
        P1 (float): Absolute pressure inside the effect (Pa)

    Returns:
        BPE (float): Boiling point elevation (K). 
        T1 (float): Temperature inside the effect (K).
    """
    
    #Compute water properties
            #Q is quality, where 0 is saturated liquid and 1 is saturated vapor
    Tw= PropsSI('T', 'P', P1, 'Q', 0, 'Water')-273.15 #Boiling point of pure water at P1 (°C)
    A=8.325E-2+(1.883E-4*Tw)+(4.02E-6*(Tw**2))
    B=-7.625e-4+(9.02e-5*Tw)-(5.2e-7*(Tw**2))
    C=1.522E-4-(3E-6*Tw)-(3E-8*(Tw**2))
    BPE=A*xf+(B*(xf**2))+(C*(xf**3))
    T1= (Tw+BPE)+273.15 #Boiling point of the solution at P1 (K)
    print(f"Boiling Point Elevation (BPE): {BPE:.2f} °C\nTemperature inside the effect (T1): {T1:.2f} K")
    return BPE, T1
def energy_balance(xf:float,xL:float,hf:float,hL: float,P1: float,T1: float,Ps:float,F:float,V: float,L: float):

    """

    Calculates the energy balance in an evaporator.

    This function computes the temperature of the steam vapor (Ts) and the mass flow of steam (S) 
    based on the flow concentrations, temperatures, and pressures involved in the evaporation process.
    
    It also computes the overall heat transfer coefficient (U) based on the temperature of the steam (Ts)
    and the temperature inside the effect (T1) 

    Args:
        hf (float): Enthaply of feed (kJ/kmol).
        hL (float): Enthaply of feed (kJ/kmol).
        P1 (float): Pressure inside the effect (Pa)
        T1 (float): Temperature inside the effect (Pa)
        Ps (float): Steam pressure (Pa)
        L (float): Liquor flow out of the evaporator (kg). 
        V (float): Vapor flow out of the evaporator (kg). 
        F (float): Initial flow (kg).
    Returns:
        Ts (float): Temperature os the steam vapor (K).
        S (float): steam mass flow (kg).
        U (float): Overall heat transfer coefficient (J/K*cm^2).
    """
    #STEAM PROPERTIES
    Ts= PropsSI('T', 'P', Ps, 'Q', 0, 'Water')  #Boiling point of pure water at Ps (K)
    H_liq = PropsSI('H', 'P', Ps, 'Q', 0, 'Water')
    H_vap = PropsSI('H', 'P', Ps, 'Q', 1, 'Water')
    l_heat=H_vap - H_liq    #Latent heat of water vapor at Ps (J/kg)
    
    #Enthalpies of the process
    Hv=PropsSI('H', 'P', P1, 'Q', 1, 'Water') # Produced vapor at P1,T1 without solute
    #Convert from kJ/kmol to J/kg
    hf=(hf / ((((xf / 58.44) * 58.44) + (((100 - xf) / 18.015) * 18.015)) / ((xf / 58.44) + ((100 - xf) / 18.015))))*1000
    hL=(hL / ((((xL / 58.44) * 58.44) + (((100 - xL) / 18.015) * 18.015)) / ((xL / 58.44) + ((100 - xL) / 18.015))))*1000
    # Steam mass flow calculation
    S = ((L * hL) + (V * Hv) - (F * hf)) / l_heat

    #                                           Overall heat transfer coefficient
    # The area for evaporator one is defined
    A=3054 #cm^2
    U=(S*l_heat)/(A*(Ts-T1))    #J/K*cm^2
    print(f"Steam mass flow (S): {S:.2f} kg\nTemperature of the steam (Ts): {Ts:.2f} K\nThe overall heat transfer coefficient (U): {U:.2f} J/K*cm^2")

    return S,Ts,U
def COP(V: float,S: float):
    """
    Calculates the coefficient of performance (COP) of the evaporator 1 as single effect wiht the steam used (S) and
    the vapor produced in the evaporator (V) 
    Args:
        S (float): steam mass flow (kg).
        V (float): Vapor flow out of the evaporator (kg)
    Returns:
        COP (float): coefficient of performance. 
    """
    COP=V/S
    print(f"The coefficient of performance (COP): {COP:.3f}")
    return COP
def energy_balancem(xf:float,Tf: float,P1: float,T1: float,Ps:float,F:float,V: float,L: float,xL:float):
    """

    Calculates the energy balance in an evaporator.

    This function computes the temperature of the steam vapor (Ts) and the mass flow of steam (S) 
    based on the flow concentrations, temperatures, and pressures involved in the evaporation process.

    It also computes the overall heat transfer coefficient (U) based on the temperature of the steam (Ts)
    and the temperature inside the effect (T1) 

    Args:
        xf (float): Concentration of the flow (% w/w).
        Tf (float): Feed temperature
        P1 (float): Pressure inside the effect (Pa)
        T1 (float): Temperature inside the effect (Pa)
        Ps (float): Steam pressure (Pa)
        L (float): Liquor flow out of the evaporator (kg).
        xL (float): Concentration of the output flow in % w/w. 
        V (float): Vapor flow out of the evaporator (kg). 
        F (float): Initial flow (kg).
    Returns:
        Ts (float): Temperature os the steam vapor (K).
        S (float): steam mass flow (kg).
        U (float): Overall heat transfer coefficient (J/K*cm^2).
    """
    #STEAM PROPERTIES
    Ts= PropsSI('T', 'P', Ps, 'Q', 0, 'Water')  #Boiling point of pure water at Ps (K)
    H_liq = PropsSI('H', 'P', Ps, 'Q', 0, 'Water')
    H_vap = PropsSI('H', 'P', Ps, 'Q', 1, 'Water')
    l_heat=H_vap - H_liq    #Latent heat of water vapor at Ps (J/kg)
    
    #Enthalpies of the process
    Hv=PropsSI('H', 'P', P1, 'Q', 1, 'Water') # Produced vapor at P1,T1 without solute
    hf=PropsSI('H', 'T', Tf, 'P', 101325, 'Water')
    hL=PropsSI('H', 'T', T1, 'Q', 0, 'Water')#Liquor entalphy at T1,xL
    a1, a2, a3, a4, a5,a6,a7,a8,a9,a10 = (-2.348e4, 3.152e5, 2.803e6, -1.446e5, 7.826e03,-4.417e1,2.139e-1,-1.991e4,2.778e4,9.728e1)
    sF=xf/100
    sL=xL/100
    tf=Tf-273.15
    t1=T1-273.15
    hf=hf-(sF*(a1+(a2*sF)+(a3*(sF**2))+(a4*(sF**3))+(a5*tf)+(a6*(tf**2))+(a7*(tf**3))+(a8*tf*sF)+(a9*tf*(sF**2))+(a10*sF*(tf**2))))
    hL=hL-(sL*(a1+(a2*sL)+(a3*(sL**2))+(a4*(sL**3))+(a5*t1)+(a6*(t1**2))+(a7*(t1**3))+(a8*t1*sL)+(a9*t1*(sL**2))+(a10*sL*(t1**2))))
    # Steam mass flow calculation
    S = (L * hL + V * Hv - F * hf) / l_heat

    #                                           Overall heat transfer coefficient
    # The area for evaporator one is defined
    A=3054 #cm^2
    U=(S*l_heat)/(A*(Ts-T1))    #J/K*cm^2
    print(f"Steam mass flow (S): {S:.2f} kg\nTemperature of the steam (Ts): {Ts:.2f} K\nThe overall heat transfer coefficient (U): {U:.2f} J/K*cm^2")
    return S, Ts,U
def simulate_evaporation(total_time, M_init, M_salt_init, T_init, P1, Ps, P, x_f, T_f):
            """
            Simulates an evaporation process with feed flow hysteresis.

            Parameters:
                total_time (float): Total simulation time in seconds.
                M_init (float): Initial mass in the evaporator (kg).
                M_salt_init (float): Initial salt mass (kg).
                T_init (float): Initial temperature in Kelvin.
                P1 (float): Operating pressure of the evaporator (Pa).
                Ps (float): Steam pressure (Pa).
                P (float): Feed pressure (Pa).
                x_f (float): Feed salt concentration (mass fraction).
                T_f (float): Feed temperature (K).

            Returns:
                dict: Dictionary containing time-series data for plotting or analysis.
            """
            def enthalpy_salt(h,sF,tf):
                tf=T-273.15
                a1, a2, a3, a4, a5,a6,a7,a8,a9,a10 = (-2.348e4, 3.152e5, 2.803e6, -1.446e5, 7.826e03,-4.417e1,2.139e-1,-1.991e4,2.778e4,9.728e1)
                h=h-(sF*(a1+(a2*sF)+(a3*(sF**2))+(a4*(sF**3))+(a5*tf)+(a6*(tf**2))+(a7*(tf**3))+(a8*tf*sF)+(a9*tf*(sF**2))+(a10*sF*(tf**2))))
                return h

            # System parameters
            F_max = 0.067666667       # Maximum inlet flow (kg/s)
            V_base = 0.00975959

            S = 0.011714928           # Steam flow rate (kg/s)
            M_max = 7.7              # Maximum evaporator mass (kg)
            M_min = 5.09             # Minimum evaporator mass (kg)
            c_j = 4.2                 # Heat capacity of solution (kJ/kg·K)
            dt = 5                    # Time step (s)
            steps = int(total_time / dt)

            # Steam energy calculations

            H_liq = PropsSI('H', 'P', Ps, 'Q', 0, 'Water')               # Enthalpy of saturated liquid at Ps
            H_vap = PropsSI('H', 'P', Ps, 'Q', 1, 'Water')               # Enthalpy of saturated vapor at Ps
            latent_heat = H_vap - H_liq                                 # Latent heat (J/kg)
            Q = S * (latent_heat / 1000)                                # Heat input from steam (kJ/s)


            # Boiling point elevation

            Tw = PropsSI('T', 'P', P1, 'Q', 0, 'Water') - 273.15         # Saturation temp. of water at P1 (°C)
            A = 8.325e-2 + 1.883e-4 * Tw + 4.02e-6 * Tw**2               # BPE coefficients (empirical)
            B = -7.625e-4 + 9.02e-5 * Tw - 5.2e-7 * Tw**2
            C = 1.522e-4 - 3e-6 * Tw - 3e-8 * Tw**2
            BPE = A * x_f + B * x_f**2 + C * x_f**3                      # Boiling Point Elevation (°C)
            T_eb = Tw + BPE + 273.15                                     # Final boiling point in Kelvin


            # Enthalpy  functions

            def h_liquid(T):
                return PropsSI('H', 'T', T, 'Q', 0, 'Water')

            def h_vapor(P1):
                return PropsSI('H', 'P', P1, 'Q', 1, 'Water') / 1000

            def h_liquid_feed(T, P):
                return PropsSI('H', 'T', T, 'P', P, 'Water')

            # -------------------------
            # Initialization
            # -------------------------
            M = M_init
            M_salt = M_salt_init
            T = T_init
            F = F_max

            time_list = []
            M_list = []
            M_salt_list = []
            T_list = []
            F_list = []
            V_list = []
            concentration_list = []

            # Main Euler integration loop

            for step in range(steps):
                t = step * dt

                # Feed valve control (hysteresis)
                if M >= M_max:
                    F = 0
                elif M <= M_min:
                    F = F_max

                # Vapor production if temperature exceeds boiling point
                V = V_base if T_eb - 5 <= T <= T_eb + 3 else 0

                # Enthalpy values
                h_v = h_vapor(P1)
                h_f_in = h_liquid_feed(T_f, P)
                h_f_in = enthalpy_salt(h_f_in, x_f, T_f) / 1000

                if t > 0:
                    h_i = h_liquid(T)
                    concentration1 = concentration / 100
                    h_i = enthalpy_salt(h_i, concentration1, T) / 1000
                else:
                    h_i = h_liquid(T)/1000

                h_v = h_vapor(P1)

                # Differential equations
                dM_dt = F - V
                dM_salt_dt = F * x_f
                dT_dt = ((F * (h_f_in - h_i)) - (V * (h_v - h_i)) + Q - 6.7613179704011435) / (M * c_j)

                # Euler integration
                M += dM_dt * dt
                M_salt += dM_salt_dt * dt
                T += dT_dt * dt
                #target_salt_mass=x_L*M
                #if M_salt >= target_salt_mass:
                #    break

                # Store results
                time_list.append(t)
                M_list.append(M)
                M_salt_list.append(M_salt)
                T_list.append(T - 273.15)  # Convert to °C
                F_list.append(F)
                V_list.append(V)
                concentration = (M_salt / (M+M_salt)) * 100 if M > 0 else 0

                concentration_list.append(concentration)

            # -------------------------
            # Return all collected data
            # -------------------------
            return {
                "time": time_list,
                "mass": M_list,
                "salt_mass": M_salt_list,
                "temperature_C": T_list,
                "feed_flow": F_list,
                "vapor_flow": V_list,
                "concentration_pct": concentration_list,
                "T_eb": T_eb  # Include boiling point in the output
            }
def plot_evaporation_with_altair(results):
            time_min = [t / 60 for t in results["time"]]
            df = pd.DataFrame({
                "Time (min)": time_min,
                "Mass (kg)": results["mass"],
                "Temperature (°C)": results["temperature_C"],
                "Salt Concentration (%)": results["concentration_pct"],
                "Feed Flow (kg/s)": results["feed_flow"],
                "Vapor Flow (kg/s)": results["vapor_flow"]
            })

            M_max = 7.7
            M_min = 5.09
            T_eb = results["T_eb"] - 273.15

            # --- Mass plot ---
            mass_chart = alt.Chart(df).mark_line(color='blue').encode(
                x=alt.X('Time (min)', title='Time (min)'),
                y=alt.Y('Mass (kg)', title='Mass (kg)')
            ).properties(title='Mass in Evaporator')

            mass_lines = alt.Chart(pd.DataFrame({'y': [M_max, M_min]})).mark_rule(
                strokeDash=[4, 4], color='gray'
            ).encode(y='y')

            st.altair_chart(mass_chart + mass_lines, use_container_width=True)

            # --- Temperature plot with boiling range lines ---
            temp_chart = alt.Chart(df).mark_line(color='red').encode(
                x=alt.X('Time (min)', title='Time (min)'),
                y=alt.Y('Temperature (°C)', title='Temperature (°C)')
            ).properties(
                title='Temperature in Evaporator'
            )

            # Two lines: T_eb + 3 and T_eb - 5
            temp_lines = alt.Chart(pd.DataFrame({
                'y': [T_eb + 3, T_eb - 5]
            })).mark_rule(
                strokeDash=[4, 4], color='gray'
            ).encode(
                y='y:Q'
            )

            st.altair_chart(temp_chart + temp_lines, use_container_width=True)

            # --- Salt concentration plot ---
            conc_chart = alt.Chart(df).mark_line(color='purple').encode(
                x=alt.X('Time (min)', title='Time (min)'),
                y=alt.Y('Salt Concentration (%)', title='Concentration (%)')
            ).properties(title='Salt Concentration in Evaporator')

            st.altair_chart(conc_chart, use_container_width=True)

            # --- Flow plot with legend ---
            flow_chart = alt.Chart(df).transform_fold(
                ['Feed Flow (kg/s)', 'Vapor Flow (kg/s)'],
                as_=['Flow Type', 'Flow']
            ).mark_line().encode(
                x=alt.X('Time (min):Q', title='Time (min)'),
                y=alt.Y('Flow:Q', title='Flow (kg/s)'),
                color=alt.Color('Flow Type:N', title='Type of Flow')
            ).properties(
                title='Feed and Vapor Flow Rates'
            )

            st.altair_chart(flow_chart, use_container_width=True)

