
from Balances.Balances import ask_for_inputs, material_balance, Boling_Point_Elevation, energy_balance

xf, Tf, P1, Ps, F, xL = ask_for_inputs()
L,V=material_balance(F,xf,xL)
BPE, T1=Boling_Point_Elevation(xf,P1)
S,Ts=energy_balance(xf,Tf,P1,T1,Ps,F,V,L)