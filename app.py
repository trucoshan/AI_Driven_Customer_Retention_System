import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from pathlib import Path
import sys
base_dir = Path(__file__).resolve().parent
sys.path.append(str(base_dir / "src"))
from shap_gen.shap_gen import extract_top_reasons
from ai_gen.ai_gen import generate_churn_explanation

# Page configuration
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📉",
    layout="wide"
)

# Loading the saved model
model = joblib.load("model/xgb_churn_model.pkl")

# Title
st.title("📉 Customer Churn Prediction Dashboard")

# Sidebar section
st.sidebar.header("Customer Features")

# 1
gender = st.sidebar.radio(
    "Gender",
    ["Male", "Female"]
)

gender = 1 if gender == "Male" else 0

# 2
SeniorCitizen = st.sidebar.radio(
    "Senior Citizen",
    ["Yes", "No"]
)

SeniorCitizen = 1 if SeniorCitizen == "Yes" else 0

# 3
Partner = st.sidebar.radio(
    "Partner",
    ["Yes", "No"]
)

Partner = 1 if Partner == "Yes" else 0

# 4
Dependents = st.sidebar.radio(
    "Dependents",
    ["Yes", "No"]
)

Dependents = 1 if Dependents == "Yes" else 0

# 5
tenure = st.sidebar.slider(
    "Tenure",
    min_value=0,
    max_value=72,
    value=12
)

tenure_input = st.sidebar.number_input(
    "Or Enter Tenure Directly",
    min_value=0.0,
    max_value=72.0,
    value=float(tenure),
    step=1.0
)

tenure = int(round(tenure_input))

# 6
PhoneService = st.sidebar.radio(
    "Phone Service",
    ["Yes", "No"]
)

PhoneService = 1 if PhoneService == "Yes" else 0

# 7
if PhoneService == 0:

    st.sidebar.radio(
        "Multiple Lines",
        ["No"],
        disabled=True
    )

    MultipleLines = 0

else:

    MultipleLines = st.sidebar.radio(
        "Multiple Lines",
        ["Yes", "No"]
    )

    MultipleLines = 1 if MultipleLines == "Yes" else 0

# 8
internet_service = st.sidebar.selectbox(
    "Internet Service",
    [
        "DSL",
        "Fiber optic",
        "No internet service"
    ]
)

InternetService_DSL = 0
InternetService_Fiber_optic = 0
InternetService_No = 0

if internet_service == "DSL":
    InternetService_DSL = 1

elif internet_service == "Fiber optic":
    InternetService_Fiber_optic = 1

else:
    InternetService_No = 1

# Internet dependent features

internet_disabled = internet_service == "No internet service"

def internet_feature(label):

    if internet_disabled:

        st.sidebar.radio(
            label,
            ["No"],
            disabled=True
        )

        return 0

    else:

        value = st.sidebar.radio(
            label,
            ["Yes", "No"]
        )

        return 1 if value == "Yes" else 0

# 9-14
OnlineSecurity = internet_feature("Online Security")
OnlineBackup = internet_feature("Online Backup")
DeviceProtection = internet_feature("Device Protection")
TechSupport = internet_feature("Tech Support")
StreamingTV = internet_feature("Streaming TV")
StreamingMovies = internet_feature("Streaming Movies")

# Contract

contract = st.sidebar.selectbox(
    "Contract",
    [
        "Month-to-month",
        "One year",
        "Two year"
    ]
)

Contract_Month_to_month = 0
Contract_One_year = 0
Contract_Two_year = 0

if contract == "Month-to-month":
    Contract_Month_to_month = 1

elif contract == "One year":
    Contract_One_year = 1

else:
    Contract_Two_year = 1

# Paperless Billing
PaperlessBilling = st.sidebar.radio(
    "Paperless Billing",
    ["Yes", "No"]
)

PaperlessBilling = 1 if PaperlessBilling == "Yes" else 0

# Payment Method
payment_method = st.sidebar.selectbox(
    "Payment Method",
    [
        "Bank transfer (automatic)",
        "Credit card (automatic)",
        "Electronic check",
        "Mailed check"
    ]
)

PaymentMethod_Bank_transfer = 0
PaymentMethod_Credit_card = 0
PaymentMethod_Electronic_check = 0
PaymentMethod_Mailed_check = 0

if payment_method == "Bank transfer (automatic)":
    PaymentMethod_Bank_transfer = 1

elif payment_method == "Credit card (automatic)":
    PaymentMethod_Credit_card = 1

elif payment_method == "Electronic check":
    PaymentMethod_Electronic_check = 1

else:
    PaymentMethod_Mailed_check = 1

# Monthly Charges
MonthlyCharges = st.sidebar.slider(
    "Monthly Charges",
    min_value=0.0,
    max_value=200.0,
    value=70.0
)

MonthlyCharges_input = st.sidebar.number_input(
    "Or Enter Monthly Charges Directly",
    min_value=0.0,
    max_value=200.0,
    value=float(MonthlyCharges),
    step=0.1
)

MonthlyCharges = MonthlyCharges_input

# Total charges
adjustment = MonthlyCharges * tenure * 0.0001422
TotalCharges = (MonthlyCharges * tenure) - adjustment

# DataFrame
input_data = pd.DataFrame({

    "SeniorCitizen": [SeniorCitizen],
    "gender": [gender],
    "Partner": [Partner],
    "Dependents": [Dependents],
    "tenure": [tenure],
    "PhoneService": [PhoneService],
    "MultipleLines": [MultipleLines],

    "InternetService_DSL": [InternetService_DSL],
    "InternetService_Fiber optic": [InternetService_Fiber_optic],
    "InternetService_No": [InternetService_No],

    "OnlineSecurity": [OnlineSecurity],
    "OnlineBackup": [OnlineBackup],
    "DeviceProtection": [DeviceProtection],
    "TechSupport": [TechSupport],
    "StreamingTV": [StreamingTV],
    "StreamingMovies": [StreamingMovies],

    "Contract_Month-to-month": [Contract_Month_to_month],
    "Contract_One year": [Contract_One_year],
    "Contract_Two year": [Contract_Two_year],

    "PaperlessBilling": [PaperlessBilling],

    "PaymentMethod_Bank transfer (automatic)": [PaymentMethod_Bank_transfer],
    "PaymentMethod_Credit card (automatic)": [PaymentMethod_Credit_card],
    "PaymentMethod_Electronic check": [PaymentMethod_Electronic_check],
    "PaymentMethod_Mailed check": [PaymentMethod_Mailed_check],

    "MonthlyCharges": [MonthlyCharges],
    "TotalCharges": [TotalCharges]

})

# Main section
st.markdown("---")

predict_button = st.button("🚀 PREDICT")

if not predict_button:

    st.subheader(
        "Select customer features to predict churn probability."
    )

else:

    prediction = model.predict(input_data)[0]

    probability = model.predict_proba(input_data)[0][1]

    probability_percent = round(probability * 100, 2)

    # Gauge chart
    color = "red" if prediction == 1 else "green"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability_percent,

        title={
            "text": "Churn Probability (%)"
        },

        gauge={
            "axis": {
                "range": [0, 100]
            },

            "bar": {
                "color": color
            }
        }
    ))

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    
    # Prediction text
    if prediction == 1:

        st.error(
            f"⚠️ There is a {round(float(probability_percent),2)}% chance the Customer will Churn."
        )

    else:

        st.success(
            f"✅ Customer is likely to stay with a "
            f"({round(100 - float(probability_percent),2)}%) chance."
        )

    # Top reasons for churn
    top_reasons = extract_top_reasons(dataframe = input_data,model = model)

    st.markdown("## SHAP Waterfall plot")
    st.pyplot(top_reasons)

    reasons = []

    for col in input_data.columns.to_list():
        if input_data[col].iloc[0] == 1:
            reasons.append(col)

    risk_factors = ["InternetService_Fiber optic",
                    "Contract_Month-to-month",
                    "PaymentMethod_Electronic check"]
    risk_reasons = ["Fiber optic customer",
                    "Month to month customer",
                    "Customer paying via electronic check"]
    safe_factors = ["Partner", "Dependents", "OnlineSecurity",
                  "OnlineBackup", "DeviceProtection",
                  "TechSupport", "Contract_One year",
                  "Contract_Two year"]
    safe_reasons = ["Has partners",
                    "Has dependents",
                    "Has online security",
                    "Has online backup",
                    "Has device protection",
                    "Has tech support",
                    "Has a one year contract",
                    "Has a two year contract"]
    
    risks = dict(zip(risk_factors,risk_reasons))
    safeties = dict(zip(safe_factors,safe_reasons))

    churn_risks = []
    churn_safes = []
    
    for risk,risk_reason in risks.items():
        if risk in reasons:
            churn_risks.append(risk_reason)

    for safety,safety_reason in safeties.items():
        if safety in reasons:
            churn_safes.append(safety_reason)

    risky = (", ").join(churn_risks)
    safe = (", ").join(churn_safes)

    # AI driven insights
    if probability_percent > 50:
        response = generate_churn_explanation(
            probability=round(float(probability_percent),2),
            good_signs=safe,
            bad_signs=risky
        )

        st.markdown("## AI Insights")
        st.markdown(f"‼️ {response}")

    elif probability_percent > 41:

        st.markdown('## Insight')
        st.markdown("⚠️ Altough customer is low risk, use caution.\n"
                    "Send a feedback form via mail and warm call after response.")
        if len(churn_risks)>0:
            st.markdown(f"Risk factors are this customer is a {risky}")
        if len(churn_safes)>0:
            st.markdown(f"Positive points are the customer {safe}")
        
    else:
        st.markdown("## Insight")
        st.markdown("✅ Customer is safe, and not likely to churn.")
        if len(churn_risks)>0:
            st.markdown(f"Risk factors however are this customer is a {risky}")
        if len(churn_safes)>0:
            st.markdown(f"Positive points are the customer {safe}")