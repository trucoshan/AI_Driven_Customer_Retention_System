from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent.parent
data_dir = base_dir / "data"

dataset = data_dir / "telco_customer_churn_clean.csv"

def cat_boost_data(dataset):

    df = pd.read_csv(dataset)
    print(f"Dataset '{dataset}' loaded successfully.\n")

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    print("TotalCharges Column Dropped.\n")

    df.dropna(inplace=True)
    print("All null values were dropped.")

    df.drop(columns=["customerID"], inplace=True)
    print("customerID column was dropped.\n")

    df["SeniorCitizen"] = df["SeniorCitizen"].apply(lambda x: "Yes" if x==1 else "No")
    print("Successfully encoded the SeniorCitizen column.\n")

    cat_cols = []
    num_cols = []
    
    for col in df.columns.to_list():
        if col == "Churn":
            continue
        elif df[col].dtype=="str":
            cat_cols.append(col)
        elif df[col].dtype in ("int", "int64", "float", "float64"):
            num_cols.append(col)
        else:
            print(f"Error parsing column(s) : {col}")

    print("Successfully identified categorical columns.")

    X = df.drop(columns=["Churn"])
    y = df["Churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        stratify=y,
        test_size=0.2,
        random_state=42
    )

    print(f"Dataset Split complete.\n")

    print(f"Returned X_train, X_test, y_train, y_test, cat_cols")

    return X_train, X_test, y_train, y_test, cat_cols