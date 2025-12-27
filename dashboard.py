# dashboard.py
import streamlit as st
import requests
import json

# --- Page Config ---
st.set_page_config(
    page_title="Smart City Forecast",
    page_icon="🏙️",
    layout="wide"
)

# --- API Endpoints ---
API_BASE_URL = "http://127.0.0.1:8000" # For local execution
API_ENDPOINTS = {
    "traffic": f"{API_BASE_URL}/predict/traffic",
    "energy": f"{API_BASE_URL}/predict/energy",
    "waste": f"{API_BASE_URL}/predict/waste",
    "pollution": f"{API_BASE_URL}/predict/pollution",
    "emergency": f"{API_BASE_URL}/predict/emergency"
}

# --- Main Dashboard ---
st.title("🏙️ Smart City Future Forecaster")
st.caption("Using AI to predict the future of city operations. Cloud data from S3.")

# --- Create Tabs ---
tab_traffic, tab_energy, tab_waste, tab_pollution, tab_emergency = st.tabs([
    "🚗 Traffic", "💡 Energy", "🗑️ Waste", "💨 Pollution", "🚨 Emergency"
])

# --- 1. Traffic Tab ---
with tab_traffic:
    st.header("Predict Future Traffic")
    with st.form(key="traffic_form"):
        st.write("Enter current conditions to predict traffic in 1 hour:")
        col1, col2, col3, col4 = st.columns(4)
        with col1: hour = st.slider("Current Hour", 0, 23, 8)
        with col2: day = st.selectbox("Day of Week", (0, 1, 2, 3, 4, 5, 6),
                                      format_func=lambda x: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][x])
        with col3: weather = st.selectbox("Current Weather", ("Clear", "Rain", "Fog"))
        with col4: count = st.number_input("Current Vehicle Count", 0, 1000, 150)

        traffic_submit = st.form_submit_button(label="Predict")

    if traffic_submit:
        payload = {"hour": hour, "day_of_week": day, "weather": weather, "vehicle_count": count}
        try:
            response = requests.post(API_ENDPOINTS["traffic"], data=json.dumps(payload))
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            result = response.json()
            if "error" in result: st.error(f"API Error: {result['error']}")
            else: st.success(f"**Predicted Vehicle Count in 1 Hour: {result['predicted_vehicle_count_in_1_hr']:.0f}**")
        except requests.exceptions.RequestException as e:
            st.error(f"API Connection Error: {e}")

# --- 2. Energy Tab ---
with tab_energy:
    st.header("Predict Future Energy Load")
    with st.form(key="energy_form"):
        st.write("Enter current conditions to predict grid load in 24 hours:")
        col1, col2, col3, col4 = st.columns(4)
        with col1: hour = st.slider("Current Hour", 0, 23, 19, key="energy_hr")
        with col2: day = st.selectbox("Day of Week", (0, 1, 2, 3, 4, 5, 6), key="energy_day")
        with col3: temp = st.number_input("Current Temperature (°C)", -10.0, 40.0, 22.0)
        with col4: load = st.number_input("Current Grid Load (MW)", 0, 1000, 650)

        energy_submit = st.form_submit_button(label="Predict")

    if energy_submit:
        payload = {"hour": hour, "day_of_week": day, "temperature": temp, "grid_load_mw": load}
        try:
            response = requests.post(API_ENDPOINTS["energy"], data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            if "error" in result: st.error(f"API Error: {result['error']}")
            else: st.success(f"**Predicted Grid Load in 24 Hours: {result['predicted_grid_load_mw_in_24_hrs']:.0f} MW**")
        except requests.exceptions.RequestException as e:
            st.error(f"API Connection Error: {e}")

# --- 3. Waste Tab ---
with tab_waste:
    st.header("Predict Future Waste Levels")
    with st.form(key="waste_form"):
        st.write("Enter current bin status to predict fill level in 1 day:")
        col1, col2, col3 = st.columns(3)
        with col1: bin_type = st.selectbox("Bin Type", ("Landfill", "Recycling"))
        with col2: fill = st.slider("Current Fill Level %", 0, 100, 75)
        with col3: days_since = st.number_input("Days Since Last Collection", 0, 30, 4)

        waste_submit = st.form_submit_button(label="Predict")

    if waste_submit:
        payload = {"bin_type": bin_type, "fill_level_percent": fill, "days_since_collection": days_since}
        try:
            response = requests.post(API_ENDPOINTS["waste"], data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            if "error" in result: st.error(f"API Error: {result['error']}")
            else:
                pred_fill = result['predicted_fill_level_in_1_day']
                st.success(f"**Predicted Fill Level in 1 Day: {pred_fill:.0f}%**")
                if pred_fill > 85:
                    st.error("ACTION: This bin will likely need collection tomorrow.")
        except requests.exceptions.RequestException as e:
            st.error(f"API Connection Error: {e}")

# --- 4. Pollution Tab ---
with tab_pollution:
    st.header("Predict Future Pollution")
    with st.form(key="pollution_form"):
        st.write("Enter current conditions to predict AQI in 1 hour:")
        col1, col2, col3 = st.columns(3)
        with col1: hour = st.slider("Current Hour", 0, 23, 17, key="poll_hr")
        with col2: traffic = st.selectbox("Current Traffic", ("Low", "High"))
        with col3: aqi = st.number_input("Current AQI", 0, 300, 70)

        pollution_submit = st.form_submit_button(label="Predict")

    if pollution_submit:
        payload = {"hour": hour, "traffic_level": traffic, "aqi": aqi}
        try:
            response = requests.post(API_ENDPOINTS["pollution"], data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            if "error" in result: st.error(f"API Error: {result['error']}")
            else: st.success(f"**Predicted AQI in 1 Hour: {result['predicted_aqi_in_1_hr']:.0f}**")
        except requests.exceptions.RequestException as e:
            st.error(f"API Connection Error: {e}")

# --- 5. Emergency Tab ---
with tab_emergency:
    st.header("Predict Future Emergency Risk")
    with st.form(key="emergency_form"):
        st.write("Enter current conditions to predict incident probability in the next hour:")
        col1, col2, col3, col4 = st.columns(4)
        with col1: hour = st.slider("Current Hour", 0, 23, 23, key="em_hr")
        with col2: day = st.selectbox("Day of Week", (0, 1, 2, 3, 4, 5, 6), 5, key="em_day")
        with col3: weather = st.selectbox("Current Weather", ("Clear", "Rain", "Fog"), key="em_weather")
        with col4: traffic = st.selectbox("Current Traffic", ("Low", "High"), key="em_traffic")

        emergency_submit = st.form_submit_button(label="Predict")

    if emergency_submit:
        payload = {"hour": hour, "day_of_week": day, "weather": weather, "traffic_level": traffic}
        try:
            response = requests.post(API_ENDPOINTS["emergency"], data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            if "error" in result: st.error(f"API Error: {result['error']}")
            else:
                prob = result['predicted_incident_probability_in_1_hr'] * 100
                st.success(f"**Predicted Incident Risk in 1 Hour: {prob:.2f}%**")
                if prob > 10:
                    st.error("RISK: High probability. Consider pre-allocating resources.")
                elif prob > 5:
                    st.warning("RISK: Elevated probability.")
        except requests.exceptions.RequestException as e:
            st.error(f"API Connection Error: {e}")