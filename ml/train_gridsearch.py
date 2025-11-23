# train.py

import joblib
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import make_scorer, f1_score, recall_score
from sklearn.pipeline import Pipeline
import xgboost as xgb

from data_loader import load_data
from preprocessor_pipeline import build_preprocessor
import json


def train_model():
    """
    Main function to load data, build pipeline, perform GridSearchCV, 
    and save the best model.
    """
    # 1. Load data
    X, y, num_features, cat_features, cat_enc_features, cat_orders = load_data()

    # 2. Define scoring metrics
    scoring = {
        'f1': make_scorer(f1_score, pos_label=1),
        'recall': make_scorer(recall_score, pos_label=1)
    }

    # 3. Calculate scale_pos_weight for XGBoost
    scale_pos_weight = sum(y == 0) / sum(y == 1)

    # 4. Define base XGBoost model
    xgb_clf = xgb.XGBClassifier(
        objective='binary:logistic',
        random_state=42,
        eval_metric='logloss',
        use_label_encoder=False,
        scale_pos_weight=scale_pos_weight
    )

    # 5. Build preprocessing pipeline
    preprocessor = build_preprocessor(
        num_features=num_features,
        cat_features=cat_features,
        cat_enc_features=cat_enc_features,
        cat_orders=cat_orders,
    )

    # 6. Combine preprocessor + model into final pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', xgb_clf)
    ])

    # 7. Define hyperparameter grid
    param_grid = {
        'model__n_estimators': range(8, 15),
        'model__max_depth': range(3, 8),
        'model__learning_rate': [0.1, 0.2, 0.3],
        'model__subsample': [0.8, 1.0],
        'model__colsample_bytree': [0.8, 1.0],
        'model__min_child_weight': [1, 3, 5]
    }

    # 8. Cross-validation strategy
    cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # 9. Grid search
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring=scoring,
        refit='recall',
        #return_train_score=True,
        cv=cv_strategy,
        n_jobs=-1
    )

    # 10. Fit pipeline
    grid_search.fit(X, y)

    # 11. Save best pipeline
    joblib.dump(grid_search.best_estimator_, '../models/best_pipeline.pkl')

    # 12. Print results
    print("Training completed. Model saved to 'models/best_pipeline.pkl'")
    print("Best hyperparameters:", grid_search.best_params_)
    print("Best recall score:", grid_search.best_score_)

    
    # 13. Save metrics
    metrics = {
    "best_params": grid_search.best_params_,
    "best_recall": grid_search.best_score_
    }
    with open("/opt/project/models/metrics.json", "w") as f:
        json.dump(metrics, f)

if __name__ == "__main__":
    train_model()
