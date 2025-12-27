# etl.py
import pandas as pd
import os

LOCAL_DATA_FOLDER = "data"

def prepare_traffic_forecast():
    """Predict vehicle_count 1 hour from now."""
    filepath = os.path.join(LOCAL_DATA_FOLDER, "traffic_data.csv")
    if not os.path.exists(filepath): return pd.DataFrame() # Return empty if file missing
    df = pd.read_csv(filepath)

    # The "target" is the vehicle count 1 hour in the future
    df['target'] = df['vehicle_count'].shift(-1)

    # The "features" are the conditions we know *now*
    features_df = df[['hour', 'day_of_week', 'weather', 'vehicle_count', 'target']].copy()

    # One-hot encode categorical features
    features_df = pd.get_dummies(features_df, columns=['weather'], drop_first=True)

    # Remove the last row (it has no target)
    features_df = features_df.dropna()
    return features_df

def prepare_energy_forecast():
    """Predict grid_load_mw 24 hours from now."""
    filepath = os.path.join(LOCAL_DATA_FOLDER, "energy_data.csv")
    if not os.path.exists(filepath): return pd.DataFrame()
    df = pd.read_csv(filepath)

    # The "target" is the grid load 24 hours in the future
    df['target'] = df['grid_load_mw'].shift(-24)

    # The "features" are conditions we know *now*
    features_df = df[['hour', 'day_of_week', 'temperature', 'grid_load_mw', 'target']].copy()
    features_df = features_df.dropna()
    return features_df

def prepare_waste_forecast():
    """Predict fill_level_percent 1 day from now."""
    filepath = os.path.join(LOCAL_DATA_FOLDER, "waste_data.csv")
    if not os.path.exists(filepath): return pd.DataFrame()
    df = pd.read_csv(filepath)

    # Create "days_since_collection" feature (approximate)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by=['bin_id', 'timestamp'])
    # Find the last time the bin was near empty (likely after collection)
    df['last_empty_approx'] = df['timestamp'].where(df['fill_level_percent'] < 10).groupby(df['bin_id']).transform(lambda x: x.ffill())
    df['days_since_collection'] = (df['timestamp'] - df['last_empty_approx']).dt.days
    df = df.fillna(0) # Handle initial NaNs before first collection
    df['days_since_collection'] = df['days_since_collection'].clip(lower=0)

    # The "target" is the fill level 1 day in the future (within the same bin group)
    df['target'] = df.groupby('bin_id')['fill_level_percent'].shift(-1)

    features_df = df[['bin_type', 'fill_level_percent', 'days_since_collection', 'target']].copy()
    features_df = pd.get_dummies(features_df, columns=['bin_type'], drop_first=True)
    features_df = features_df.dropna()
    return features_df


def prepare_pollution_forecast():
    """Predict AQI 1 hour from now."""
    filepath = os.path.join(LOCAL_DATA_FOLDER, "pollution_data.csv")
    if not os.path.exists(filepath): return pd.DataFrame()
    df = pd.read_csv(filepath)

    df['target'] = df['aqi'].shift(-1)
    features_df = df[['hour', 'traffic_level', 'aqi', 'target']].copy()
    features_df = pd.get_dummies(features_df, columns=['traffic_level'], drop_first=True)
    features_df = features_df.dropna()
    return features_df

def prepare_emergency_forecast():
    """Predict probability of an incident in the next hour."""
    filepath = os.path.join(LOCAL_DATA_FOLDER, "emergency_data.csv")
    if not os.path.exists(filepath): return pd.DataFrame()
    df = pd.read_csv(filepath)

    # The target is already 0 or 1, so no shift is needed
    df['target'] = df['incident_happened']

    features_df = df[['hour', 'day_of_week', 'weather', 'traffic_level', 'target']].copy()
    features_df = pd.get_dummies(features_df, columns=['weather', 'traffic_level'], drop_first=True)
    features_df = features_df.dropna()
    return features_df

if __name__ == "__main__":
    print("Preparing all datasets for forecasting...")
    # Example of running one function if needed for testing
    # traffic_features = prepare_traffic_forecast()
    # if not traffic_features.empty:
    #     print("Traffic features prepared successfully.")
    #     print(traffic_features.head())
    print("(This script is normally called by train.py)")