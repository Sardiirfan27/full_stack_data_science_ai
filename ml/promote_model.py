import os
from mlflow.tracking import MlflowClient

# -------------------------
# Minimum metric thresholds
# -------------------------
MIN_RECALL = 0.80
MIN_F1 = 0.60
MIN_CV_RECALL = 0.80

def promote_model():
    """
    Evaluate the latest MLflow model version and promote it using aliases/tags.
    
    Note:
    - Previous method: client.transition_model_version_stage(...) → DEPRECATED
    - New recommended method (MLflow >= 2.9): use aliases + tags instead of stages
    """

    # Get MLflow tracking URI from environment
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not mlflow_uri:
        print("❌ MLFLOW_TRACKING_URI is not set in environment variables.")
        return

    client = MlflowClient(tracking_uri=mlflow_uri)
    model_name = "xgboost_best_model"

    # -------------------------
    # Retrieve latest model version
    # -------------------------
    # Deprecated: stages were previously used to promote models (None, Staging, Production)
    # latest_versions = client.get_latest_versions(name=model_name, stages=["None", "Staging"])
    
    all_versions = client.get_latest_versions(name=model_name, stages=[])
    if not all_versions:
        print("❌ No model versions found.")
        return

    latest = all_versions[0]

    # -------------------------
    # Retrieve metrics
    # -------------------------
    run = client.get_run(latest.run_id)
    metrics = run.data.metrics

    recall = metrics.get("test_recall_1", 0)
    f1 = metrics.get("test_f1_1", 0)
    cv_recall = metrics.get("best_cv_recall_score", 0)

    print("==== Model Promotion Evaluation ====")
    print(f"Recall Score:       {recall}")
    print(f"F1 Score:           {f1}")
    print(f"Cross-Validation:   {cv_recall}")

    # -------------------------
    # Decide promotion
    # -------------------------
    if recall >= MIN_RECALL and f1 >= MIN_F1 and cv_recall >= MIN_CV_RECALL:
        alias_name = "Production"
        promotion_status = "Promoted to production"
    else:
        alias_name = "Staging"
        promotion_status = "Promoted to staging"

    # -------------------------
    # Apply new promotion method
    # -------------------------
    # Set alias for this model version (new recommended way)
    client.set_registered_model_alias(
        name=model_name,
        alias=alias_name,
        version=latest.version
    )

    # Tag the model version for traceability (optional, recommended)
    client.set_model_version_tag(
        name=model_name,
        version=latest.version,
        key="promotion_status",
        value=promotion_status
    )

    print(f"✅ Model version {latest.version} promoted as alias '{alias_name}' with tag: {promotion_status}")


if __name__ == "__main__":
    promote_model()
