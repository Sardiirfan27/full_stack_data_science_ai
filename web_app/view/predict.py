import streamlit as st
import requests
import pandas as pd
import os


API_KEY=os.getenv("API_KEY_FASTAPI")
API_URL = os.getenv("FASTAPI_URL_DOCKER") #st.secrets.get("FASTAPI_URL_DOCKER") # use the URL of the docker container instead of localhost

def render():
    st.title("🔮 Customer Churn Prediction")

    # Tabs
    tab1, tab2 = st.tabs(["🧾 Manual Input", "📁 Batch Prediction via CSV"])

    # ------------------------------------------------------------------------
    # TAB 1: MANUAL INPUT
    # ------------------------------------------------------------------------
    with tab1:
        with st.form(key="predict_form"):
            tenure = st.number_input("Tenure (months)", min_value=0, max_value=240, value=12)
            monthly_charges = st.number_input("Monthly Charges", min_value=0.0, max_value=1000.0, value=65.0)
            total_charges = st.number_input("Total Charges", min_value=0.0, max_value=100000.0, value=780.0)

            contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
            internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No internet service"])
            online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
            tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
            online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
            device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])
            streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
            streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])
            paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
            dependents = st.selectbox("Dependents", ["Yes", "No"])
            partner = st.selectbox("Partner", ["Yes", "No"])
            payment_method = st.selectbox(
                "Payment Method",
                ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]
            )
            senior_citizen = st.selectbox("Senior Citizen", [0, 1])

            submitted = st.form_submit_button("Predict")

        if submitted:
            payload = {
                "tenure": tenure,
                "TotalCharges": total_charges,
                "MonthlyCharges": monthly_charges,
                "Contract": contract,
                "InternetService": internet_service,
                "OnlineSecurity": online_security,
                "TechSupport": tech_support,
                "OnlineBackup": online_backup,
                "DeviceProtection": device_protection,
                "StreamingTV": streaming_tv,
                "StreamingMovies": streaming_movies,
                "PaperlessBilling": paperless_billing,
                "Dependents": dependents,
                "Partner": partner,
                "PaymentMethod": payment_method,
                "SeniorCitizen": senior_citizen
            }

            headers = {"api-key": API_KEY}

            try:
                response = requests.post(API_URL, json=payload, headers=headers)

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Prediction Successful!")
                    st.subheader(f"Predicted Class: **{result['prediction']}**")
                    st.subheader(f"Churn Probability: {result['probability']*100:.2f}%")
                    st.subheader(f"Churn Risk Level: **{ 'High' if result['probability'] >= 0.75 else 'Medium' if result['probability'] >= 0.5 else 'Low' }**")
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")

    # ------------------------------------------------------------------------
    # TAB 2: BATCH PREDICTION
    # ------------------------------------------------------------------------
    with tab2:
        st.subheader("📁 Upload CSV")

        st.info("Upload CSV with the same column structure as your training data.")

        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())

            if st.button("Run Batch Prediction"):
                predictions = []

                headers = {"api-key": API_KEY}

                for _, row in df.iterrows():
                    payload = row.to_dict()
                    try:
                        response = requests.post(API_URL, json=payload, headers=headers)
                        if response.status_code == 200:
                            result = response.json()
                            predictions.append({
                                **payload,
                                "prediction": result["prediction"],
                                "probability": result["probability"],
                                "Churn Risk": "High" if result["probability"] >= 0.75 else 'medium' if result["probability"] >= 0.5 else 'low'
                            })
                        else:
                            predictions.append({**payload, "error": response.text})
                    except Exception as e:
                        predictions.append({**payload, "error": str(e)})

                result_df = pd.DataFrame(predictions)
                st.success("✅ Batch Prediction Complete")
                st.dataframe(result_df)

                # Optionally, download output
                csv = result_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Results CSV",
                    csv,
                    "batch_predictions.csv",
                    "text/csv",
                    key="download-csv"
                )
