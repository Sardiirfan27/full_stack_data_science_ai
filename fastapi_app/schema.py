# schema.py
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional

class PredictRequest(BaseModel):
    # Numerical
    tenure: int = Field(..., ge=0, le=240)
    TotalCharges: Optional[float] = Field(None, ge=0, le=100000)
    MonthlyCharges: float = Field(..., ge=0, le=1000)

    # Categorical
    Contract: Literal["Month-to-month", "One year", "Two year"]
    OnlineSecurity: Literal["Yes", "No", "No internet service"]
    TechSupport: Literal["Yes", "No", "No internet service"]
    InternetService: Literal["DSL", "Fiber optic", "No"]
    PaymentMethod: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ]
    OnlineBackup: Literal["Yes", "No", "No internet service"]
    DeviceProtection: Literal["Yes", "No", "No internet service"]
    StreamingMovies: Literal["Yes", "No", "No internet service"]
    StreamingTV: Literal["Yes", "No", "No internet service"]
    PaperlessBilling: Literal["Yes", "No"]
    Dependents: Literal["Yes", "No"]
    Partner: Literal["Yes", "No"]

    # Binary
    SeniorCitizen: Literal[0, 1]

    # ------------------------------
    # Normalization / Cleaning
    # ------------------------------
    @validator(
        "Contract", "OnlineSecurity", "TechSupport", "InternetService",
        "PaymentMethod", "OnlineBackup", "DeviceProtection", "StreamingMovies",
        "StreamingTV", "PaperlessBilling", "Dependents", "Partner",
        pre=True
    )
    def normalize_str(cls, v):
        """Strip leading/trailing whitespace for categorical fields"""
        if v is None:
            return v
        return str(v).strip()

    @validator("SeniorCitizen", pre=True)
    def normalize_senior(cls, v):
        """Convert 'yes', 'true', or '1' to 1, otherwise 0"""
        if str(v).lower() in ["yes", "1", "true"]:
            return 1
        return 0

    @validator("TotalCharges", pre=True)
    def empty_to_none(cls, v):
        """Convert empty string to None for TotalCharges"""
        if v == "" or v is None:
            return None
        return float(v)

    # Example for Swagger/OpenAPI documentation
    model_config = {
        "json_schema_extra": {
            "example": {
                "tenure": 12,
                "TotalCharges": 780.5,
                "MonthlyCharges": 65.3,
                "OnlineSecurity": "Yes",
                "TechSupport": "No",
                "OnlineBackup": "Yes",
                "DeviceProtection": "No",
                "StreamingTV": "Yes",
                "StreamingMovies": "No",
                "PaperlessBilling": "Yes",
                "Dependents": "No",
                "Partner": "Yes",
                "InternetService": "Fiber optic",
                "Contract": "Month-to-month",
                "PaymentMethod": "Electronic check",
                "SeniorCitizen": 0
            }
        }
    }

class PredictResponse(BaseModel):
    """
    Schema for customer churn prediction response.
    
    Fields:
        - prediction: Predicted class (0=No churn, 1=Churn)
        - probability: Probability of churn
    """
    prediction: int = Field(..., description="Predicted class: 0=No churn, 1=Churn")
    probability: float = Field(..., description="Probability that the customer will churn")
