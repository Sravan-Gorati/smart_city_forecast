# aws_utils.py
import boto3
import os

# --- CONFIGURE YOUR BUCKET NAMES HERE ---
# Replace with your actual S3 bucket names
DATA_BUCKET = "rk-digital-twin-data"
MODEL_BUCKET = "rk-digital-twin-models"
# ----------------------------------------

s3_client = boto3.client('s3')

def upload_to_s3(local_folder, bucket_name):
    """Uploads all files from a local folder to an S3 bucket."""
    print(f"Uploading files from '{local_folder}' to S3 bucket '{bucket_name}'...")
    if not os.path.exists(local_folder):
        print(f"  Error: Local folder '{local_folder}' does not exist.")
        return
    for filename in os.listdir(local_folder):
        local_path = os.path.join(local_folder, filename)
        if os.path.isfile(local_path):
            print(f"  Uploading {filename}...")
            try:
                s3_client.upload_file(local_path, bucket_name, filename)
            except Exception as e:
                print(f"    Error uploading {filename}: {e}")
    print("Upload complete.")

def download_from_s3(local_folder, bucket_name):
    """Downloads all files from an S3 bucket to a local folder."""
    print(f"Downloading files from S3 bucket '{bucket_name}' to '{local_folder}'...")
    os.makedirs(local_folder, exist_ok=True)

    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' not in page:
                 print(f"  Warning: Bucket '{bucket_name}' might be empty or inaccessible.")
                 continue
            for obj in page.get('Contents', []):
                filename = obj['Key']
                local_path = os.path.join(local_folder, filename)
                # Ensure subdirectories exist if needed (though not expected for this project)
                # os.makedirs(os.path.dirname(local_path), exist_ok=True)
                print(f"  Downloading {filename}...")
                try:
                    s3_client.download_file(bucket_name, filename, local_path)
                except Exception as e:
                    print(f"    Error downloading {filename}: {e}")
    except Exception as e:
        print(f"Error listing objects in bucket {bucket_name}: {e}")
    print("Download complete.")

if __name__ == "__main__":
    # This allows you to run this file directly to test S3
    print("This is a utility script. Run simulate.py, then train.py.")
    print(f"Data Bucket: {DATA_BUCKET}")
    print(f"Model Bucket: {MODEL_BUCKET}")