Project Workflow (Step-by-Step)


Step 1: Data Simulation

Synthetic data is generated for five smart city domains: traffic, energy, waste, pollution, and emergency incidents. This simulates real-world city conditions such as rush hours, weather impact, energy demand, and emergency risks.

Step 2: Cloud Storage (AWS S3)

The generated datasets are uploaded to AWS S3, which acts as centralized cloud storage for both raw data and trained machine learning models.

Step 3: ETL (Extract, Transform, Load)

Data is downloaded from S3 and processed using an ETL pipeline. This includes feature selection, handling categorical variables, shifting targets for forecasting, and preparing clean datasets for model training.

Step 4: Model Training

Machine learning models (Random Forest Regressors and Classifiers) are trained for each domain. After training, models and their feature lists are saved locally and uploaded back to S3 for reuse.

Step 5: Model Serving with FastAPI

A FastAPI backend loads the trained models from S3 at startup and exposes REST APIs for real-time predictions such as traffic volume, energy load, waste fill level, pollution index, and emergency probability.

Step 6: Interactive Dashboard (Streamlit)

A Streamlit web dashboard interacts with the FastAPI endpoints. Users input current conditions, and the system displays future predictions in an easy-to-understand interface.

Step 7: End-to-End Forecasting

The complete system enables real-time smart city forecasting by integrating data simulation, cloud storage, machine learning, APIs, and visualization into one unified workflow.
