import os
import mlflow
import pandas as pd
import logging
from mlflow.tracking import MlflowClient
from datetime import datetime
from mlflow.sklearn import load_model as sklearn_load_model

logger = logging.getLogger("uvicorn")

class ModelService:
    """
    Service class to load a model from MLflow Model Registry
    and run inference (predicted class + probability).

    Attributes:
        model (sklearn-like model): Loaded scikit-learn/XGBoost model.
        model_name (str): Name of the model in MLflow registry.
        alias (str): Stage/alias of the model, e.g., "Production".
        model_uri (str): MLflow model URI to load.
        client (MlflowClient): MLflow client to get model metadata.
    """
    def __init__(self):
        self.model = None
        self.model_name = "xgboost_best_model"
        self.alias = "Production"
        self.model_uri = f"models:/{self.model_name}@{self.alias}"
        self.client = MlflowClient()

    def load(self):
        """
        Load the model from MLflow Model Registry and log metadata.

        Raises:
            RuntimeError: If model cannot be loaded or MLflow registry is unreachable.
        """
        logger.info(f"[ModelService] Loading model from registry: {self.model_uri}")
        try:
            # Load model object
            # mlflow.pyfunc.load_model(self.model_uri) is not supported predict_proba
            # Use sklearn_load_model to access predict_proba (required for probability output)
            self.model = sklearn_load_model(self.model_uri) # mlflow.pyfunc.load_model(self.model_uri) 

            # Get metadata using MLflowClient
            mv = self.client.get_model_version_by_alias(self.model_name, self.alias)
            ts = mv.creation_timestamp / 1000 # ms to seconds
            readable_time = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

            logger.info(f"[ModelService] ✅ Model loaded successfully!")
            logger.info(f"[ModelService] Run ID: {mv.run_id}")
            logger.info(f"[ModelService] Version: {mv.version}")
            logger.info(f"[ModelService] Current Stage/Alias: {self.alias}")
            logger.info(f"[ModelService] Source Artifact: {mv.source}")
            logger.info(f"[ModelService] Creation Time: {readable_time}")

        except Exception as e:
            logger.error(f"[ModelService] ❌ Fail load: {e}")
            raise RuntimeError("MLflow registry unreachable or model missing")

    def predict(self, data: dict):
        """
        Perform prediction using the loaded model.

        Args:
            data (dict): Input features as a dictionary.

        Returns:
            dict: {
                "prediction": int (0 or 1),
                "probability": float (probability of positive class)
            }

        Raises:
            RuntimeError: If model is not loaded or prediction fails.
        """
        if not self.model:
            raise RuntimeError("Model not loaded. Call load() first.")

        try:
            # Convert input dict to DataFrame
            df = pd.DataFrame([data])
            logger.info(f"[ModelService] Incoming inference data: {data}")

            # Predict class and probability
            pred_class = int(self.model.predict(df)[0])
            pred_proba = float(self.model.predict_proba(df)[:, 1][0])

            # Log results
            logger.info(f"[ModelService] Prediction class: {pred_class}, Probability: {pred_proba}")

            return {"prediction": pred_class, "probability": pred_proba}

        except Exception as e:
            logger.error(f"[ModelService] ❌ Prediction error: {e}")
            raise RuntimeError("Prediction failed. Check schema or registry version")
