from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer


def build_preprocessor(num_features, cat_features, cat_enc_features, cat_orders=None, remainder='drop'):
    """
    Build preprocessing pipeline combining numerical, categorical, and already encoded categorical features.

    Parameters
    ----------
    num_features : list
        List of numerical feature names.
    cat_features : list
        List of categorical feature names.
    cat_enc_features : list
        List of already encoded categorical feature names.
    cat_orders : list of lists, optional
        List of categories in order for ordinal encoding.
    remainder : str, default 'drop'
        What to do with remaining columns. Options: 'drop', 'passthrough'

    Returns
    -------
    ColumnTransformer
        Preprocessing pipeline
    """

    # Pipeline for numerical features
    numerical_pipeline = Pipeline([
        ('imputer', IterativeImputer(random_state=0, min_value=0)),
        ('scaler', MinMaxScaler())
    ])

    # Pipeline for categorical features
    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OrdinalEncoder(
            categories=cat_orders,
            handle_unknown='use_encoded_value',
            unknown_value=-1
        ))
    ])

    # Pipeline for already encoded categorical features
    categorical_encoded_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent'))
    ])

    # Combine all pipelines
    preprocessor = ColumnTransformer([
        ('num', numerical_pipeline, num_features),
        ('cat', categorical_pipeline, cat_features),
        ('cat_enc', categorical_encoded_pipeline, cat_enc_features)
    ],
    verbose=0,
    remainder=remainder  # drop or passthrough
    )

    return preprocessor

