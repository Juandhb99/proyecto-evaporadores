
from Balances.Balances import ask_for_inputs, material_balance, Boling_Point_Elevation, energy_balance
from Properties.Propertiesdef import properties_prediction,training
import pandas as pd
#xf, Tf, P1, Ps, F, xL = ask_for_inputs()
#Initial conditions
F=20.4
xf=5
Tf=298.15
P1=74000 #Atmospheric Pressure
Ps=131000
xL=11.2
#Calculate balances an elevation of the boiling point
L,V=material_balance(F,xf,xL)
BPE, T1=Boling_Point_Elevation(xf,P1)

#Predict the properties 
#Feed = [Tf, xf/100]
#Liquor = [T1, xL/100]
#properties_final = pd.read_csv('c:/Users/ASUS/OneDrive/Documentos/Proyecto de evaporadores/proyecto-evaporadores/Properties/properties_final.csv')
#properties_final = pd.read_csv('Properties/properties_final.csv')   #Read clean dataframe
#models, errores=training(properties_final)
#predictions_feed= properties_prediction(models, Feed)
#predictions_liquor= properties_prediction(models, Liquor)
#hf=predictions_feed['LIQUID HMX kJ/kmol']
#hL=predictions_liquor['LIQUID HMX kJ/kmol']
#S,Ts=energy_balance(xf, xL, hf, hL, P1, Ps, F, V, L)
S,Ts=energy_balance(xf,Tf,P1,T1,Ps,F,V,L,xL)
#print properties
#for property, value in predictions_feed.items():
#    print(f"For the feed flow {property}: {value}")
#for property, value in predictions_liquor.items():
#    print(f"For the liquor flow {property}: {value}")