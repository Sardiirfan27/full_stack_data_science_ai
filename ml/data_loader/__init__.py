from .load_bigquery import load_bigquery_data
from .validate_transform import transform_data

def load_data():
    """Load & transform data in one call."""
    df = load_bigquery_data()
    return transform_data(df)
