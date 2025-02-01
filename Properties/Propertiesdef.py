
#Now we have an idea of each of the models behaviour
#For the models we must stablish which variables are indpendent and which arent

import math
import numpy as np
import sympy as sp 
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error,mean_absolute_error
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
def training(properties):
   
    X = properties[['TEMP K', 'Composition']]
    
    
    properties_list = ['LIQUID RHOMX kmol/cum', 'LIQUID CPMX kJ/kmol-K', 'LIQUID MUMX cP', 'LIQUID HMX kJ/kmol', 'LIQUID TBUB K', 'LIQUID KMX kW/m-K']
    
   
    polinomial_degrees = {
        'LIQUID RHOMX kmol/cum': 3,
        'LIQUID CPMX kJ/kmol-K': 3,
        'LIQUID MUMX cP': 4,
        'LIQUID HMX kJ/kmol': 3,
        'LIQUID TBUB K': 4,
        'LIQUID KMX kW/m-K': 1
    }
    
    
    models = {}
    
    
    errores = {}
    
    
    for property in properties_list:
        y = properties[property]
        
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
       
        degree = polinomial_degrees[property]
        
        
        model = make_pipeline(PolynomialFeatures(degree=degree), LinearRegression())
        model.fit(X_train, y_train)
        
        
        models[property] = model
        
        
        y_pred = model.predict(X_test)
        
        
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
       
        errores[property] = {'MSE': mse, 'MAE': mae}
    
    return models, errores

def properties_prediction(models, new_entry):
 
    predictions = {}
    
    for property, model in models.items():
        prediction = model.predict([new_entry])
        predictions[property] = prediction[0]
    
    return predictions
