from google.cloud import storage
import os
import streamlit as st
from google.cloud.exceptions import GoogleCloudError
from google.oauth2 import service_account


# This function ensures the bucket actually exists. If it doesn't it creates one.
def ensure_bucket_exists(
    client: storage.Client, bucket_name: str, location: str = "US"
) -> storage.Bucket:

    bucket = client.lookup_bucket(bucket_name)

    if bucket is None:
        bucket = client.create_bucket(bucket_name, location=location)
        print(f"Bucket '{bucket_name}' created in {location}.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")

    return bucket


# This function uploads only csv files into the cloud. It checks if the file is in fact a csv file, and in the event where it's not, it refuses upload.
def upload_file(
    client: storage.Client,
    bucket_name: str,
    file_path: str,
    destination_blob_name: str = None,
    file_obj=None,
) -> str:

    if file_obj is not None:
        if destination_blob_name.endswith(".csv"):
            content_type = "text/csv"
        elif destination_blob_name.endswith(".json"):
            content_type = "application/json"

        blob = client.bucket(bucket_name).blob(destination_blob_name)
        blob.upload_from_file(file_obj, rewind=True, content_type=content_type)
        return f"gs://{bucket_name}/{destination_blob_name}"

    file_path = file_path.lower()
    # if the file doesn't exist
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} was not found.")

    # if the file is not a csv or json
    if not file_path.endswith((".csv", ".json")):
        raise ValueError(f"Expected a CSV or JSON file, got {file_path} instead.")

    # setting the blob name for the file
    if destination_blob_name is None:
        destination_blob_name = os.path.basename(file_path)

    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        if file_path.endswith(".csv"):
            blob.upload_from_filename(file_path, content_type="text/csv")
        elif file_path.endswith(".json"):
            blob.upload_from_filename(file_path, content_type="application/json")

        gcs_uri = f"gs://{bucket_name}/{destination_blob_name}"
        print(f"Uploaded: {file_path} to {gcs_uri}")
        return gcs_uri

    except GoogleCloudError as e:
        raise RuntimeError(f"Upload failed for {file_path}: {e}")


# This function gets the client for the google cloud service.
def get_gcs_client() -> storage.Client:
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return storage.Client(credentials=credentials)
