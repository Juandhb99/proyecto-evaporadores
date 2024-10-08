
from Balances.Balances import ask_for_inputs, material_balance, Boling_Point_Elevation, energy_balance
from intento import make_predictions
xf, Tf, P1, Ps, F, xL = ask_for_inputs()
L,V=material_balance(F,xf,xL)
BPE, T1=Boling_Point_Elevation(xf,P1)
Feed = [[Tf, xf]]
Liquor = [[T1, xL]]
#If the properties 
predictions_feed= make_predictions(models, Feed)
predictions_liquor= make_predictions(models, Liquor)
hf=predictions_feed['LIQUID HMX kJ/kmol']
hL=predictions_liquor['LIQUID HMX kJ/kmol']
S,Ts=energy_balance(xf, xL, hf, hL, P1, Ps, F, V, L)