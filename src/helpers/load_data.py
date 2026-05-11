import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, LabelEncoder, StandardScaler

main_dir = Path(__file__).resolve().parent.parent.parent

notebook = main_dir / "notebooks"
src = main_dir / "src"
data = main_dir / "data"

def load_data(dataset:str):

    df = pd.read_csv(f"{data}/{dataset}")
    print(f"Dataset '{dataset}' loaded successfully.\n")
    
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    print("TotalCharges was typecasted to numerical.\n")

    df.dropna(inplace=True)
    print("Null values were removed.\n")
    print(f"\nDataset size : \n{df.shape[0]} rows\n{df.shape[1]} columns\n\n")

    df.drop(columns=["customerID",
                     "gender",
                     "PhoneService",
                     "TotalCharges"], inplace=True)
    print("Successfully dropped the columns\n" \
    "   -customerID\n" \
    "   -gender\n" \
    "   -PhoneService\n" \
    "   -TotalCharges\n\n"
    )
    
    X = df.drop(columns=["Churn"])
    y = df["Churn"]
    X_train_init, X_test_init, y_train_init, y_test_init = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42
        )
    
    print("Dataset split complete.")
    
    # one hot encoder
    ohe = OneHotEncoder(
        handle_unknown="error",
        sparse_output=False
        ).set_output(transform="pandas")
    
    # ordinal encoder
    oe = OrdinalEncoder(
        handle_unknown="error"
        ).set_output(transform="pandas")
    
    # label encoder
    le = LabelEncoder()

    # standard scaler
    ss = StandardScaler().set_output(transform="pandas")

    # adjusting the classes in each feature
    for col in X_train_init.columns.tolist():
        if col in ["OnlineSecurity", "OnlineBackup",
                   "DeviceProtection", "TechSupport",
                   "StreamingTV", "StreamingMovies"]:
            X_train_init[col] = X_train_init[col].apply(
                lambda x: "No" if x=="No internet service" else x
            )
            X_test_init[col] = X_test_init[col].apply(
                lambda x: "No" if x=="No internet service" else x
            )
        elif col=="MultipleLines":
            X_train_init[col] = X_train_init[col].apply(
                lambda x: "No" if x=="No phone service" else x
            )
            X_test_init[col] = X_test_init[col].apply(
                lambda x: "No" if x=="No phone service" else x
            )
    
    # creating list to separate data types
    categorical_columns = []
    numerical_columns = []
    
    # running a for loop to append the lists
    for col in X_train_init.columns.tolist():
        if col=="SeniorCitizen":
            continue
        elif X_train_init[col].dtype=="str":
            categorical_columns.append(col)
        else:
            numerical_columns.append(col)

    # columns to be one hot encoded
    OneHot = ["InternetService", "Contract", "PaymentMethod"]

    # columns to be ordinally encoded
    # Note: Even though some columns here are nominal, they are binary, and can be encoded as ordinal
    Ordinal = [col for col in categorical_columns if col not in OneHot]

    X_train = X_train_init[["SeniorCitizen"]]
    X_test = X_test_init[["SeniorCitizen"]]

    for col in X_train_init.columns.tolist():
        if col in OneHot:
            interim_train = ohe.fit_transform(X_train_init[[col]])
            X_train = pd.concat([X_train, interim_train], axis=1)
            interim_test = ohe.transform(X_test_init[[col]])
            X_test = pd.concat([X_test, interim_test], axis=1)
        elif col in Ordinal:
            interim_train = oe.fit_transform(X_train_init[[col]])
            X_train = pd.concat([X_train, interim_train], axis=1)
            interim_test = oe.transform(X_test_init[[col]])
            X_test = pd.concat([X_test, interim_test], axis=1)
        elif col in numerical_columns:
            interim_train = ss.fit_transform(X_train_init[[col]])
            X_train = pd.concat([X_train, interim_train], axis=1)
            interim_test = ss.transform(X_test_init[[col]])
            X_test = pd.concat([X_test, interim_test], axis=1)
        elif col=="SeniorCitizen":
            X_train[col] = X_train[col].astype("float64")
            X_test[col] = X_test[col].astype("float64")
        else:
            print(f"Error encoding column : {col}")

    X_train.drop(columns=["InternetService_No", "Contract_Two year",
                      "PaymentMethod_Mailed check"],inplace=True)
    
    X_test.drop(columns=["InternetService_No", "Contract_Two year",
                      "PaymentMethod_Mailed check"],inplace=True)

    y_train_interim = le.fit_transform(y_train_init)
    y_test_interim = le.transform(y_test_init)

    y_train = pd.Series(
        data=y_train_interim,
        index=y_train_init.index
    )

    y_test = pd.Series(
        data=y_test_interim,
        index=y_test_init.index
    )

    return X_train, X_test, y_train, y_test