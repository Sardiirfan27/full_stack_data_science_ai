import pandas as pd
import warnings

def validate_types(df, num_features, cat_features, cat_enc_features):
    # Check numeric columns
    for col in num_features:
        if not pd.api.types.is_numeric_dtype(df[col]):
            print(f"Warning: {col} should be numeric, current type: {df[col].dtype}")
            df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"{col} successfully converted to numeric.")

    # Check categorical columns
    for col in cat_features:
        if not pd.api.types.is_object_dtype(df[col]):
            print(f"Warning: {col} should be categorical/string, current type: {df[col].dtype}")
            df[col] = df[col].astype(str)
            print(f"{col} successfully converted to string.")

    # Check already encoded categorical columns
    for col in cat_enc_features:
        if not pd.api.types.is_numeric_dtype(df[col]):
            print(f"Warning: {col} should be numeric, current type: {df[col].dtype}")
            df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"{col} successfully converted to numeric.")
            
    return df


def transform_data(df):
    """Clean and prepare features for modeling."""
    try:
        # Drop ID
        if "customerID" in df.columns:
            df = df.drop(columns=["customerID"])
        
        # Map target
        if df["Churn"].dtype == "object":
            df["Churn"] = df["Churn"].map({"No":0, "Yes":1})
        
        # Impute TotalCharges
        mask = df["TotalCharges"].isna()
        df.loc[mask, "TotalCharges"] = df.loc[mask].apply(
            lambda row: 0 if row["tenure"]==0 else row["tenure"] * row["MonthlyCharges"],
            axis=1
        )

        # Features definition
        yes_no_map = ('No', 'Yes')
        internet_service_map = ('No', 'DSL', 'Fiber optic')
        add_service_map = ('No internet service', 'No', 'Yes')
        contract_map = ('Month-to-month', 'One year', 'Two year')
        payment_method_map = (
            'Electronic check', 'Mailed check', 'Bank transfer (automatic)',
            'Credit card (automatic)'
        )

        feature_groups = {
            yes_no_map: ['PaperlessBilling', 'Dependents', 'Partner'],
            add_service_map: ['OnlineSecurity', 'TechSupport', 'OnlineBackup',
                              'DeviceProtection', 'StreamingMovies', 'StreamingTV'],
            internet_service_map: ['InternetService'],
            contract_map: ['Contract'],
            payment_method_map: ['PaymentMethod']
        }

        cat_features = [
            'Contract', 'OnlineSecurity', 'TechSupport', 'InternetService', 'PaymentMethod',
            'OnlineBackup', 'DeviceProtection', 'StreamingMovies', 'StreamingTV',
            'PaperlessBilling', 'Dependents', 'Partner'
        ]
        cat_orders = [k for f in cat_features for k, v in feature_groups.items() if f in v]

        num_features = ['tenure', 'TotalCharges', 'MonthlyCharges']
        cat_enc_features = ['SeniorCitizen']
        features = num_features + cat_features + cat_enc_features

        # Validate types
        df = validate_types(df, num_features, cat_features, cat_enc_features)

        X = df[features]
        y = df['Churn']

        print("✅ Data transformation completed successfully.")
        return X, y, num_features, cat_features, cat_enc_features, cat_orders

    except Exception as e:
        warnings.warn(f"❌ Data transformation failed: {str(e)}")
        return None
