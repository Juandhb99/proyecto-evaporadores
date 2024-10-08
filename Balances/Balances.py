import pandas as pd
import tkinter as tk
from tkinter import simpledialog
from CoolProp.CoolProp import PropsSI
import numpy as np
def ask_for_inputs():
    root = tk.Tk()
    root.withdraw()
    F = float(simpledialog.askstring("Input", "Enter the initial flow (kg):"))
    xf = float(simpledialog.askstring("Input", "Enter the concentration of the feed flow (% w/w):"))
    Tf = float(simpledialog.askstring("Input", "Enter the feed temperature (K):"))
    P1 = float(simpledialog.askstring("Input", "Enter the pressure inside the effect (Pa):"))
    Ps = float(simpledialog.askstring("Input", "Enter the steam pressure (Pa):"))
    xL = float(simpledialog.askstring("Input", "Enter the concentration of the output flow (% w/w):"))

    return xf, Tf, P1, Ps, F, xL
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
def energy_balance(xf:float,Tf: float,P1: float,T1: float,Ps:float,F:float,V: float,L: float):
    """

    Calculates the energy balance in an evaporator.

    This function computes the temperature of the steam vapor (Ts) and the mass flow of steam (S) 
    based on the flow concentrations, temperatures, and pressures involved in the evaporation process.

    Args:
        xf (float): Concentration of the flow (% w/w).
        Tf (float): Feed temperature
        P1 (float): Pressure inside the effect (Pa)
        T1 (float): Temperature inside the effect (Pa)
        Ps (float): Steam pressure (Pa)
        L (float): Liquor flow out of the evaporator (kg). 
        V (float): Vapor flow out of the evaporator (kg). 
        F (float): Initial flow (kg).
    Returns:
        Ts (float): Temperature os the steam vapor (K).
        S (float): steam mass flow (kg).
    """
    #STEAM PROPERTIES
    Ts= PropsSI('T', 'P', Ps, 'Q', 0, 'Water')  #Boiling point of pure water at Ps (K)
    H_liq = PropsSI('H', 'P', Ps, 'Q', 0, 'Water')
    H_vap = PropsSI('H', 'P', Ps, 'Q', 1, 'Water')
    l_heat=H_vap - H_liq    #Latent heat of water vapor at Ps (J/kg)
    
    #Enthalpies of the process
    Hv=PropsSI('H', 'P', P1, 'Q', 1, 'Water') # Produced vapor at P1,T1 without solute
    hf=PropsSI('H', 'T', Tf, 'P', 101325, 'Water')
    hL=PropsSI('H', 'T', T1, 'P', P1, 'Water')#Liquor entalphy at T1,xL
    # Steam mass flow calculation
    S = (L * hL + V * Hv - F * hf) / l_heat
    print(f"Steam mass flow (S): {S:.2f} kg\nTemperature of the steam (Ts): {Ts:.2f} K")
    return S, Ts
