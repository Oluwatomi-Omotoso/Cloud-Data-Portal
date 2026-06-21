import os
import io
import streamlit as st
import pandas as pd
from src.File_Uploading_to_Cloud.Upload import get_gcs_client
from google.cloud import storage
from pathlib import Path
from google.cloud.exceptions import NotFound



# Environment variables
BUCKET_NAME = st.secrets["BUCKET_NAME"]
# CREDENTIALS = os.getenv("CREDENTIALS_PATH")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")


# listing every CSV or JSON file in the bucket
def list_files(client: storage.Client, bucket_name: str) -> list[dict]:
    bucket = client.bucket(bucket_name)
    blobs = client.list_blobs(bucket_name)

    files = []
    for blob in blobs:
        if (
            blob.name.endswith(".csv")
            or blob.name.endswith(".json")
            or blob.name.endswith
        ):
            files.append(
                {
                    "name": blob.name,
                    "size_kb": round(blob.size / 1024, 2),
                    "updated": blob.updated.isoformat() if blob.updated else None,
                }
            )

    return files


# Reads a specified CSV or JSON file from the bucket: Saves the file as bytes, and loads it into a pandas dataFrame.
def load_file(
    client: storage.Client,
    bucket_name: str,
    file_name: str,
    orient: str = "records",
    lines: bool = False,
) -> pd.DataFrame:
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    try:
        content = blob.download_as_bytes()
    except NotFound:
        raise FileNotFoundError(f"'{file_name}' not found in bucket '{bucket_name}'.")

    if file_name.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))
    if file_name.endswith(".json"):
        df = pd.read_json(io.BytesIO(content), orient=orient, lines=lines)

    return df


def preview_file_as_json(
    client: storage.Client,
    bucket_name: str,
    file_name: str,
    orient: str = "records",
    lines: bool = False,
):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    try:
        content = blob.download_as_bytes()
    except NotFound:
        raise FileNotFoundError(f"'{file_name}' not found in bucket '{bucket_name}'.")

    if file_name.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))
    elif file_name.endswith(".json"):
        df = pd.read_json(io.BytesIO(content), orient=orient, lines=lines)
    else:
        raise ValueError("Unsupported file format. Use a csv or json file")

    return df.to_json(orient=orient, lines=lines, indent=4)


# Downloads a specified CSV or JSON file as a JSON
def download_file(
    client: storage.Client,
    bucket_name: str,
    file_name: str,
    destination=DOWNLOAD_DIR,
):

    output_dir = Path(destination)
    output_file = output_dir / f"{file_name}"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_file(client=client, bucket_name=bucket_name, file_name=file_name)

    # If it's sucessfully stored as a dataframe
    if isinstance(df, pd.DataFrame):
        if file_name.endswith(".csv"):
            df.to_csv(output_file, index=False)
            return f"file '{file_name}' successfully stored in {output_dir}"
        elif file_name.endswith(".json"):
            df.to_json(output_file, orient="records", index=False, indent=4)
            return f"file '{file_name}' successfully stored in {output_dir}"
        else:
            return "file type is not supported."
