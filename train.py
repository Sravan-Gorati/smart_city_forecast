# train.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import joblib
import os
import etl # Our ETL script
import aws_utils # Our S3 script
import numpy as np # Make sure numpy is imported

LOCAL_DATA_FOLDER = "data"
LOCAL_MODEL_FOLDER = "models"
os.makedirs(LOCAL_MODEL_FOLDER, exist_ok=True)
os.makedirs(LOCAL_DATA_FOLDER, exist_ok=True) # Ensure data folder exists for download

def train_model(model_name, features_df, model_type='regressor'):
    """Helper function to train and save a model."""
    print(f"\n--- Training {model_name} ---")

    if features_df.empty:
        print(f"Skipping {model_name}: Input DataFrame is empty (ETL might have failed or data missing).")
        return

    # Split data into features (X) and target (y)
    X = features_df.drop('target', axis=1)
    y = features_df['target']

    # Ensure all feature names are strings (important for consistency)
    X.columns = X.columns.astype(str)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if model_type == 'regressor':
        # Use RandomForestRegressor for continuous values
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1, max_depth=10, min_samples_leaf=5)
        model.fit(X_train, y_train)

        # Evaluate
        preds = model.predict(X_test)
        mse = mean_squared_error(y_test, preds) # Calculate Mean Squared Error
        rmse = np.sqrt(mse)                     # Calculate Root Mean Squared Error
        print(f"Model RMSE (Root Mean Squared Error): {rmse:.2f}")

    else: # classifier
        # Use RandomForestClassifier for probabilities (emergency)
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, max_depth=10, min_samples_leaf=5)
        model.fit(X_train, y_train)

        # Evaluate
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"Model Accuracy: {acc*100:.2f}%")

    # Save model locally
    model_path = os.path.join(LOCAL_MODEL_FOLDER, f"{model_name}.joblib")
    joblib.dump(model, model_path)
    print(f"Model saved locally: {model_path}")

    # Also save the feature columns, we need them for prediction
    joblib.dump(list(X.columns), os.path.join(LOCAL_MODEL_FOLDER, f"{model_name}_features.joblib"))

if __name__ == "__main__":
    # 1. Download data from S3
    aws_utils.download_from_s3(LOCAL_DATA_FOLDER, aws_utils.DATA_BUCKET)

    # Check if data was downloaded before proceeding
    if not os.listdir(LOCAL_DATA_FOLDER):
        print("\nError: Data folder is empty after S3 download. Cannot proceed with training.")
        print(f"Please check S3 bucket '{aws_utils.DATA_BUCKET}' and credentials.")
    else:
        print("\nStarting ETL and Training process...")
        # 2. Run ETL (locally on downloaded data) and train models
        # Error handling for each ETL step
        try:
            train_model("traffic_model", etl.prepare_traffic_forecast(), model_type='regressor')
        except Exception as e:
            print(f"Error training traffic model: {e}")
        try:
            train_model("energy_model", etl.prepare_energy_forecast(), model_type='regressor')
        except Exception as e:
            print(f"Error training energy model: {e}")
        try:
            train_model("waste_model", etl.prepare_waste_forecast(), model_type='regressor')
        except Exception as e:
            print(f"Error training waste model: {e}")
        try:
            train_model("pollution_model", etl.prepare_pollution_forecast(), model_type='regressor')
        except Exception as e:
            print(f"Error training pollution model: {e}")
        try:
            train_model("emergency_model", etl.prepare_emergency_forecast(), model_type='classifier')
        except Exception as e:
            print(f"Error training emergency model: {e}")

        # 3. Upload trained models to S3 (only if models were created)
        if os.listdir(LOCAL_MODEL_FOLDER):
             aws_utils.upload_to_s3(LOCAL_MODEL_FOLDER, aws_utils.MODEL_BUCKET)
        else:
            print("\nNo models were trained successfully, skipping upload to S3.")