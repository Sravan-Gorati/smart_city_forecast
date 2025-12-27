# app.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import os
import aws_utils # Our S3 script

app = FastAPI(title="Smart City Forecasting API")

# --- Model Loading ---
LOCAL_MODEL_FOLDER = "models"
models = {}
features = {}

@app.on_event("startup")
def load_models():
    """Download models from S3 and load them into memory."""
    os.makedirs(LOCAL_MODEL_FOLDER, exist_ok=True) # Ensure folder exists
    aws_utils.download_from_s3(LOCAL_MODEL_FOLDER, aws_utils.MODEL_BUCKET)

    print("Loading models into memory...")
    if not os.listdir(LOCAL_MODEL_FOLDER):
        print("Warning: No models found in local models folder after S3 download.")
        return

    for filename in os.listdir(LOCAL_MODEL_FOLDER):
        if filename.endswith(".joblib") and not filename.endswith("_features.joblib"):
            model_name = filename.split('.')[0]
            try:
                model_path = os.path.join(LOCAL_MODEL_FOLDER, filename)
                features_path = os.path.join(LOCAL_MODEL_FOLDER, f"{model_name}_features.joblib")

                if os.path.exists(model_path):
                    models[model_name] = joblib.load(model_path)
                    if os.path.exists(features_path):
                         features[model_name] = joblib.load(features_path)
                         print(f"  Loaded {model_name} with features.")
                    else:
                        # Attempt to load model even if features are missing, log warning
                        print(f"  Warning: Loaded {model_name} but feature file missing: {features_path}")
                        features[model_name] = [] # Assign empty list to avoid key errors later

                else:
                     print(f"  Warning: Model file not found during loading: {model_path}")

            except Exception as e:
                print(f"Error loading model {model_name} from {model_path}: {e}")

# --- Pydantic Input Models (for validation) ---
class TrafficInput(BaseModel):
    hour: int
    day_of_week: int
    weather: str # "Clear", "Rain", "Fog"
    vehicle_count: int

class EnergyInput(BaseModel):
    hour: int
    day_of_week: int
    temperature: float
    grid_load_mw: int

class WasteInput(BaseModel):
    bin_type: str # "Landfill", "Recycling"
    fill_level_percent: int
    days_since_collection: int

class PollutionInput(BaseModel):
    hour: int
    traffic_level: str # "Low", "High"
    aqi: int

class EmergencyInput(BaseModel):
    hour: int
    day_of_week: int
    weather: str # "Clear", "Rain", "Fog"
    traffic_level: str # "Low", "High"

# --- Helper Function to prepare features ---
def prepare_features(input_data, model_name):
    """Converts API input into a DataFrame suitable for the model."""
    if model_name not in features:
        raise ValueError(f"Feature list for model '{model_name}' not loaded.")

    df = pd.DataFrame([input_data])
    df_dummies = pd.get_dummies(df) # Handles categorical to numeric

    model_features = features[model_name]
    # Reindex ensures all expected columns are present, filled with 0 if missing
    # Important: Only use columns the model expects, in the correct order
    df_prepared = df_dummies.reindex(columns=model_features, fill_value=0)

    # Ensure final columns match exactly, handling potential type issues implicitly allowed by reindex
    return df_prepared[model_features]


# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "Smart City Forecasting API is running", "models_loaded": list(models.keys())}

@app.post("/predict/traffic")
def predict_traffic(data: TrafficInput):
    model_key = "traffic_model"
    if model_key not in models: return {"error": f"{model_key} not loaded"}
    try:
        model = models[model_key]
        input_df = prepare_features(data.model_dump(), model_key)
        prediction = model.predict(input_df)
        return {"predicted_vehicle_count_in_1_hr": round(prediction[0], 2)}
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

@app.post("/predict/energy")
def predict_energy(data: EnergyInput):
    model_key = "energy_model"
    if model_key not in models: return {"error": f"{model_key} not loaded"}
    try:
        model = models[model_key]
        input_df = prepare_features(data.model_dump(), model_key)
        prediction = model.predict(input_df)
        return {"predicted_grid_load_mw_in_24_hrs": round(prediction[0], 2)}
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

@app.post("/predict/waste")
def predict_waste(data: WasteInput):
    model_key = "waste_model"
    if model_key not in models: return {"error": f"{model_key} not loaded"}
    try:
        model = models[model_key]
        input_df = prepare_features(data.model_dump(), model_key)
        prediction = model.predict(input_df)
        # Ensure prediction is within reasonable bounds for fill level
        predicted_fill = max(0, min(100, prediction[0]))
        return {"predicted_fill_level_in_1_day": round(predicted_fill, 2)}
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

@app.post("/predict/pollution")
def predict_pollution(data: PollutionInput):
    model_key = "pollution_model"
    if model_key not in models: return {"error": f"{model_key} not loaded"}
    try:
        model = models[model_key]
        input_df = prepare_features(data.model_dump(), model_key)
        prediction = model.predict(input_df)
        return {"predicted_aqi_in_1_hr": round(prediction[0], 2)}
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

@app.post("/predict/emergency")
def predict_emergency(data: EmergencyInput):
    model_key = "emergency_model"
    if model_key not in models: return {"error": f"{model_key} not loaded"}
    try:
        model = models[model_key]
        input_df = prepare_features(data.model_dump(), model_key)
        # For classifier, predict_proba gives [[prob_class_0, prob_class_1]]
        prediction_prob = model.predict_proba(input_df)
        # Return the probability of class '1' (incident happened)
        return {"predicted_incident_probability_in_1_hr": round(prediction_prob[0][1], 4)}
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

if __name__ == "__main__":
      # This part is only for running locally without uvicorn command
      import uvicorn
      load_models() # Manually load for local test before starting server
      uvicorn.run(app, host="127.0.0.1", port=8000)