from CoolProp.CoolProp import PropsSI
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
    #print(f"Boiling Point Elevation (BPE): {BPE:.2f} °C\nTemperature inside the effect (T1): {T1:.2f} K")
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
    #print(f"Steam mass flow (S): {S:.2f} kg\nTemperature of the steam (Ts): {Ts:.2f} K\nThe overall heat transfer coefficient (U): {U:.2f} J/K*cm^2")

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
    #print(f"The coefficient of performance (COP): {COP:.3f}")
    return COP
def energy_balancem(xf:float,Tf: float,P1: float,T1: float,Ps:float,F:float,V: float,L: float,xL:float,option):
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
        T1 (float): Temperature inside the effect 
        Ps (float): Steam pressure (Pa)
        L (float): Liquor flow out of the evaporator (kg).
        xL (float): Concentration of the output flow in % w/w. 
        V (float): Vapor flow out of the evaporator (kg). 
        F (float): Initial flow (kg).
        option (str): Type of solution worked.
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
    hL=PropsSI('H', 'T', T1, 'P', P1, 'Water')#Liquor entalphy at T1
    if option=="Water-Salt":
        a1, a2, a3, a4, a5,a6,a7,a8,a9,a10 = (-2.348e4, 3.152e5, 2.803e6, -1.446e5, 7.826e03,-4.417e1,2.139e-1,-1.991e4,2.778e4,9.728e1)
        sF=xf/100
        sL=xL/100
        tf=Tf-273.15
        t1=T1-273.15
        hf=hf-(sF*(a1+(a2*sF)+(a3*(sF**2))+(a4*(sF**3))+(a5*tf)+(a6*(tf**2))+(a7*(tf**3))+(a8*tf*sF)+(a9*tf*(sF**2))+(a10*sF*(tf**2))))
        hL=hL-(sL*(a1+(a2*sL)+(a3*(sL**2))+(a4*(sL**3))+(a5*t1)+(a6*(t1**2))+(a7*(t1**3))+(a8*t1*sL)+(a9*t1*(sL**2))+(a10*sL*(t1**2))))
    else:
        pass
    
    # Steam mass flow calculation
    S = (L * hL + V * Hv - F * hf) / l_heat

    #                                           Overall heat transfer coefficient
    # The area for evaporator one is defined
    A=3054 #cm^2
    U=(S*l_heat)/(A*(Ts-T1))    #J/K*cm^2
    #print(f"Steam mass flow (S): {S:.2f} kg\nTemperature of the steam (Ts): {Ts:.2f} K\nThe overall heat transfer coefficient (U): {U:.2f} J/K*cm^2")
    return S, Ts,U