# simulate.py
import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import os
import aws_utils # Our S3 script

# --- Configuration ---
NUM_RECORDS = 5000
START_DATE = datetime(2025, 1, 1)
LOCAL_DATA_FOLDER = "data"
fake = Faker()

os.makedirs(LOCAL_DATA_FOLDER, exist_ok=True)

# --- 1. Traffic Simulation ---
def generate_traffic_data(num, start):
    print("Generating traffic data...")
    data = []
    for i in range(num):
        timestamp = start + timedelta(hours=i)
        hour, day = timestamp.hour, timestamp.weekday()
        weather = random.choice(["Clear", "Rain", "Fog"])

        count = 100 # Base
        if 6 <= hour <= 9 or 16 <= hour <= 19: count += random.randint(100, 200) # Rush hour
        if day >= 5: count = int(count * 0.7) # Weekend
        if weather == "Rain": count = int(count * 0.8) # Bad weather

        data.append({
            "timestamp": timestamp, "hour": hour, "day_of_week": day,
            "weather": weather, "vehicle_count": max(20, count + random.randint(-20, 20))
        })
    pd.DataFrame(data).to_csv(os.path.join(LOCAL_DATA_FOLDER, "traffic_data.csv"), index=False)

# --- 2. Energy Simulation ---
def generate_energy_data(num, start):
    print("Generating energy data...")
    data = []
    for i in range(num):
        timestamp = start + timedelta(hours=i)
        hour, day = timestamp.hour, timestamp.weekday()
        temp = 15 + np.sin(i / (24 * 7)) * 10 + random.uniform(-2, 2)

        load = 500 # Base load
        if 17 <= hour <= 21: load += 300 # Evening peak
        if temp > 22: load += (temp - 22) * 20 # AC
        if temp < 10: load += (10 - temp) * 15 # Heating

        data.append({
            "timestamp": timestamp, "hour": hour, "day_of_week": day,
            "temperature": round(temp, 2), "grid_load_mw": max(300, int(load + random.randint(-30, 30)))
        })
    pd.DataFrame(data).to_csv(os.path.join(LOCAL_DATA_FOLDER, "energy_data.csv"), index=False)

# --- 3. Waste Simulation ---
def generate_waste_data(num, start):
    print("Generating waste data...")
    BINS = [f"bin_{i}" for i in range(1, 50)]
    data = []
    bin_states = {bin_id: {'fill': 0, 'type': random.choice(["Landfill", "Recycling"])} for bin_id in BINS}

    for i in range(num // 50): # Simulate daily updates per bin type
        timestamp = start + timedelta(days=i)
        for bin_id, state in bin_states.items():
            # Simulate fill rate variation
            fill_increase = random.randint(3, 15) if state['type'] == "Landfill" else random.randint(2, 10)
            state['fill'] += fill_increase
            if state['fill'] > 100: state['fill'] = 100

            data.append({
                "timestamp": timestamp, "bin_id": bin_id, "bin_type": state['type'],
                "fill_level_percent": state['fill']
            })
            # Simulate collection based on fill level and randomness
            if state['fill'] > random.randint(75, 95) and random.random() > 0.1:
                state['fill'] = 0 # Bin collected

    pd.DataFrame(data).to_csv(os.path.join(LOCAL_DATA_FOLDER, "waste_data.csv"), index=False)

# --- 4. Pollution Simulation ---
def generate_pollution_data(num, start):
    print("Generating pollution data...")
    data = []
    for i in range(num):
        timestamp = start + timedelta(hours=i)
        hour = timestamp.hour
        traffic_level = "Low"
        if 6 <= hour <= 9 or 16 <= hour <= 19: traffic_level = "High"

        aqi = 30 # Base
        if traffic_level == "High": aqi += random.randint(20, 50)
        aqi += (np.sin(i / 24) * 10) # Simulate daily cycle variation

        data.append({
            "timestamp": timestamp, "hour": hour, "traffic_level": traffic_level,
            "aqi": max(20, int(aqi + random.randint(-5, 5)))
        })
    pd.DataFrame(data).to_csv(os.path.join(LOCAL_DATA_FOLDER, "pollution_data.csv"), index=False)

# --- 5. Emergency Simulation ---
def generate_emergency_data(num, start):
    print("Generating emergency data...")
    data = []
    for i in range(num):
        timestamp = start + timedelta(hours=i)
        hour, day = timestamp.hour, timestamp.weekday()
        weather = random.choice(["Clear", "Rain", "Fog"])
        traffic_level = "Low"
        if 6 <= hour <= 9 or 16 <= hour <= 19: traffic_level = "High"

        # Calculate probability based on factors
        prob = 0.01 # Base probability
        if weather == "Rain": prob += 0.05
        if traffic_level == "High": prob += 0.03
        if hour > 22 or hour < 6: prob += 0.02 # Night time increases risk

        incident_happened = 1 if random.random() < prob else 0

        data.append({
            "timestamp": timestamp, "hour": hour, "day_of_week": day,
            "weather": weather, "traffic_level": traffic_level,
            "incident_happened": incident_happened
        })
    pd.DataFrame(data).to_csv(os.path.join(LOCAL_DATA_FOLDER, "emergency_data.csv"), index=False)

# --- Main Executor ---
if __name__ == "__main__":
    generate_traffic_data(NUM_RECORDS, START_DATE)
    generate_energy_data(NUM_RECORDS, START_DATE)
    generate_waste_data(NUM_RECORDS, START_DATE)
    generate_pollution_data(NUM_RECORDS, START_DATE)
    generate_emergency_data(NUM_RECORDS, START_DATE)

    print(f"\nAll 5 datasets generated in '{LOCAL_DATA_FOLDER}' folder.")

    # --- UPLOAD TO CLOUD (S3) ---
    aws_utils.upload_to_s3(LOCAL_DATA_FOLDER, aws_utils.DATA_BUCKET)