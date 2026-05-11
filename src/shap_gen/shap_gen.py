import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt

def extract_top_reasons(dataframe:pd.DataFrame,model):

    explainer = shap.TreeExplainer(model)

    shap_values = explainer(dataframe)

    fig, ax = plt.subplots(figsize=(12,6))
    
    shap.waterfall_plot(shap_values[0], show=False)

    return fig