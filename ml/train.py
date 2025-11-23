import os
import joblib
import json
import warnings
from datetime import datetime
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

import xgboost as xgb
from skopt import BayesSearchCV
from skopt.space import Real, Integer, Categorical

import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
import shap

from data_loader import load_data
from preprocessor_pipeline import build_preprocessor
from evaluate import plot_confusion_matrix

# -----------------------------
# Environment & reproducibility
# -----------------------------
# Directory to save models, confusion matrix, SHAP plots, etc.
model_dir = os.getenv("MODEL_PATH")

# Suppress warnings for cleaner logs
warnings.filterwarnings("ignore")

# Set global seed for reproducibility
random.seed(42)
np.random.seed(42)

# Lock dependencies for MLflow
os.environ["MLFLOW_LOCK_MODEL_DEPENDENCIES"] = "true"

# Fix compatibility for NumPy >=1.24 (np.int deprecated)
if not hasattr(np, "int"):
    np.int = int

# ===============================
# Utility function: log metrics to MLflow
# ===============================
def log_metrics(prefix, y_true, y_pred, y_proba):
    """
    Log metrics to MLflow for train or test sets.
    
    Args:
        prefix: "train" or "test" to distinguish metrics
        y_true: true labels
        y_pred: predicted labels
        y_proba: predicted probabilities
    Returns:
        report: classification_report as dict
        auc: ROC AUC score
        cm: confusion matrix
    """
    report = classification_report(y_true, y_pred, output_dict=True)
    auc = roc_auc_score(y_true, y_proba)
    cm = confusion_matrix(y_true, y_pred)

    # Log metrics to MLflow
    mlflow.log_metric(f"{prefix}_accuracy", report["accuracy"])
    mlflow.log_metric(f"{prefix}_roc_auc", auc)
    for cls in ["0", "1"]:
        mlflow.log_metric(f"{prefix}_precision_{cls}", report[cls]["precision"])
        mlflow.log_metric(f"{prefix}_recall_{cls}", report[cls]["recall"])
        mlflow.log_metric(f"{prefix}_f1_{cls}", report[cls]["f1-score"])

    return report, auc, cm

# ===============================
# Train model function
# ===============================
def train_model():
    # ------------------------
    # Load and split data
    # ------------------------
    X, y, num_features, cat_features, cat_enc_features, cat_orders = load_data()
    
    # Split into train and test while preserving class distribution
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Compute scale_pos_weight to handle class imbalance
    scale_pos_weight = sum(y == 0) / sum(y == 1)

    # ------------------------
    # Define pipeline
    # ------------------------
    xgb_clf = xgb.XGBClassifier(
        objective="binary:logistic",
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False,
        scale_pos_weight=scale_pos_weight
    )

    # Build preprocessing pipeline for numerical and categorical features
    preprocessor = build_preprocessor(
        num_features=num_features,
        cat_features=cat_features,
        cat_enc_features=cat_enc_features,
        cat_orders=cat_orders
    )

    # Combine preprocessing and model into one pipeline
    pipeline = Pipeline([
        ("preprocessor", preprocessor), 
        #("feature_selector", SelectFromModel(estimator=selector_model, threshold="median")),
        ("model", xgb_clf)
        ])

    # ------------------------
    # Bayesian hyperparameter search
    # ------------------------
    search_spaces = {
        "model__n_estimators": Integer(6, 15),
        "model__max_depth": Integer(3, 10),
        "model__learning_rate": Categorical([0.1, 0.2, 0.3]),
        "model__subsample": Categorical([0.8, 1.0]),
        "model__colsample_bytree": Categorical(list(np.arange(0.6, 1.01, 0.1))),
        "model__min_child_weight": Integer(1, 5)
    }

    # Use stratified 5-fold cross-validation
    cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Bayesian Optimization using scikit-optimize
    opt = BayesSearchCV(
        estimator=pipeline,
        search_spaces=search_spaces,
        scoring="recall",  # optimize primarily for recall
        cv=cv_strategy,
        n_jobs=5,
        n_iter=20,
        random_state=42,
        refit=True,        # retrain best model after search
        return_train_score=True,
        verbose=1
    )
    opt.fit(X_train, y_train)
    # ------------------------
    # MLflow experiment tracking
    # ------------------------
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME"))
    model_name = "xgboost_best_model"

    with mlflow.start_run(run_name="XGBoost Model") as run:
        # ------------------------
        # Log best model to MLflow
        # ------------------------
        sample_input = X_train.sample(5, random_state=42)
        signature = infer_signature(sample_input, opt.predict(sample_input))
        mlflow.sklearn.log_model(
            sk_model=opt.best_estimator_,
            name="best_model",
            signature=signature,
            input_example=sample_input,
            registered_model_name=model_name
        )
        mlflow.log_metric("best_cv_recall_score", opt.best_score_)
        mlflow.log_params(opt.best_params_)
        mlflow.log_param("train_timestamp", datetime.now().isoformat())
        
        # ------------------------
        # Evaluate metrics on train and test
        # ------------------------
        y_train_pred = opt.predict(X_train)
        y_train_proba = opt.predict_proba(X_train)[:,1]
        train_report, train_auc, train_cm = log_metrics("train", y_train, y_train_pred, y_train_proba)

        y_test_pred = opt.predict(X_test)
        y_test_proba = opt.predict_proba(X_test)[:,1]
        test_report, test_auc, test_cm = log_metrics("test", y_test, y_test_pred, y_test_proba)

        # ------------------------
        # Plot and save confusion matrix
        # ------------------------
        plot_confusion_matrix(models_preds=[y_test_pred], y_true=y_test, titles=[model_name])
        cm_path = os.path.join(model_dir, "cm_test.png")
        plt.savefig(cm_path)
        plt.close()
        mlflow.log_artifact(cm_path, artifact_path="evaluation_results")

        # ------------------------
        # Save cross-validation results
        # ------------------------
        cv_df = pd.DataFrame(opt.cv_results_).sort_values(
            "mean_test_score", ascending=False)
        cv_df = cv_df[
            [
                "params", "mean_test_score", "mean_train_score",
                "std_test_score", "std_train_score",
                "mean_fit_time", "mean_score_time", "rank_test_score"
            ]
        ]
        cv_df["score_gap"] = cv_df["mean_train_score"] - cv_df["mean_test_score"]
        
        # Save local CSV file & Log CV results to MLflow as artifact
        cv_results_path = os.path.join(model_dir, "hyperparam_results.csv")
        cv_df.to_csv(cv_results_path, index=False)
        mlflow.log_artifact(cv_results_path,artifact_path="evaluation_results")
        

        # ------------------------
        # SHAP feature importance
        # ------------------------
        preprocessor = opt.best_estimator_.named_steps["preprocessor"]
        X_test_transformed = preprocessor.transform(X_test)
        cols = preprocessor.get_feature_names_out()
        fitted_model = opt.best_estimator_.named_steps["model"]
        explainer = shap.TreeExplainer(fitted_model)
        shap_values = explainer.shap_values(X_test_transformed)

        plt.figure()
        plt.title("SHAP Feature Importance", fontsize=14, fontweight='bold')
        shap.summary_plot(shap_values, X_test_transformed, feature_names=cols, plot_type='dot')
        shap_path = os.path.join(model_dir, "shap_summary.png")
        plt.savefig(shap_path)
        plt.close()
        mlflow.log_artifact(shap_path, artifact_path="evaluation_results")

        # ------------------------
        # Save metrics backup locally
        # ------------------------
        metrics_path = os.path.join(model_dir, "metrics_summary.json")
        with open(metrics_path, "w") as f:
            json.dump({
                "best_params": opt.best_params_,
                "best_cv_score": opt.best_score_,
                "train_metrics": train_report,
                "test_metrics": test_report,
                "train_auc": train_auc,
                "test_auc": test_auc,
                "train_confusion_matrix": train_cm.tolist(),
                "test_confusion_matrix": test_cm.tolist()
            }, f, indent=4)
        mlflow.log_artifact(metrics_path, artifact_path="evaluation_results")

        # ------------------------
        # Save local backup of the model
        # ------------------------
        model_path = os.path.join(model_dir, f"best_model_{datetime.now().strftime('%Y%m%d')}.joblib")
        joblib.dump(opt.best_estimator_, model_path, compress=3)
        print(f"💾 Model backup saved: {model_path}")

if __name__ == "__main__":
    train_model()
