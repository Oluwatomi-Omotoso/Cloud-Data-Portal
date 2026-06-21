import os
import io
import sys
import streamlit as st
import pandas as pd
import json
from dotenv import load_dotenv
import warnings
from src.File_Uploading_to_Cloud.Upload import get_gcs_client
from src.File_Uploading_to_Cloud.Upload import upload_file
from src.File_Uploading_to_Cloud.Upload import ensure_bucket_exists
from src.File_Downloading_From_Cloud.Download import (
    list_files,
    load_file,
    download_file,
    preview_file_as_json,
)
from src.File_Uploading_to_Database.database_creation import store_data, fetch_all

# SETUP WORKSPACE PATHS.
current_dir = os.getcwd()
root_dir = os.path.abspath(os.path.join(current_dir, "."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# LOAD ENVIRONMENTAL VARIABLES (.env)

warnings.filterwarnings("ignore")
BUCKET_NAME = st.secrets["BUCKET_NAME"]


# APP CONFIGURATION
client = get_gcs_client()
ensure_bucket_exists(client, BUCKET_NAME)
st.set_page_config(
    page_title="Cloud Interaction Portal",
    page_icon="☁️",
    layout="wide",
)


# --------------------------- PAGE SETUP ---------------------------
st.title("☁️ Cloud Interaction Control Center")


# TABS
tab_upload, tab_inventory = st.tabs(
    [
        "📤 Upload Data",
        "📋 Preview Data",
    ]
)


# OPERATIONAL SPACE 1: UPLOAD PIPELINE
# --- Data Uploading to cloud and a local database will be handled here.
with tab_upload:
    st.subheader("Upload Local Dataset Assets")
    st.write(
        "This space will handle uploading datasets to the cloud and to a local database."
    )

    uploaded_file = st.file_uploader("Choose a file", type=["csv", "json"])

    if uploaded_file is not None:

        if st.button("Upload to Bucket"):
            with st.spinner(f"Uploading  {uploaded_file.name}"):

                upload_file(
                    client,
                    BUCKET_NAME,
                    file_path=None,
                    destination_blob_name=uploaded_file.name,
                    file_obj=uploaded_file,
                )

            st.success(f"'{uploaded_file.name}' uploaded successfully!")


# OPERATIONAL SPACE 2 INVENTORY & PREVIEW
# --- Inventory previewing & Download logic will be handled here.
with tab_inventory:
    st.subheader("Current Bucket Contents")
    st.write("This space will handle listing objects and rendering previews.")

    if st.button("Show Bucket Contents"):
        with st.spinner("Loading bucket contents..."):
            st.session_state.files = list_files(client=client, bucket_name=BUCKET_NAME)

    if "files" in st.session_state and st.session_state.files:
        df = pd.DataFrame(st.session_state.files)

        # Displaying and Selecting a row
        selection = st.dataframe(
            df,
            on_select="rerun",
            selection_mode="single-row",
            use_container_width=True,
        )

        # Grab the selected file name
        selected_rows = selection.selection.rows
        if selected_rows:
            selected_file = df.iloc[selected_rows[0]]["name"]
            st.session_state.selected_file = selected_file

    if st.button("Preview File"):
        with st.spinner("Loading file contents"):
            if "selected_file" in st.session_state:
                st.write(f"Previewing: {st.session_state.selected_file}")
                result = preview_file_as_json(
                    client, BUCKET_NAME, st.session_state.selected_file
                )
                print(f"Here's the result : {result}")
                st.json(json.loads(result))

    if st.button("Download File"):
        with st.spinner(f"Fetching file for download"):
            if "selected_file" in st.session_state:
                df = load_file(
                    client=client,
                    bucket_name=BUCKET_NAME,
                    file_name=st.session_state.selected_file,
                )

                st.session_state.download_df = df
                st.session_state.download_name = st.session_state.selected_file

    if "download_df" in st.session_state:
        file_name = st.session_state.download_name

        if file_name.endswith(".csv"):
            data = st.session_state.download_df.to_csv(index=False)
            mime = "text/csv"
        elif file_name.endswith(".json"):
            data = st.session_state.download_df.to_json(orient="records", indent=4)
            mime = "application/json"

        st.download_button(
            label=f" Download {file_name}",
            data=data,
            file_name=file_name,
            mime=mime,
        )

    if st.button("Store to Database"):
        if "selected_file" in st.session_state:
            with st.spinner(f"Storing {st.session_state.selected_file} to database"):
                df = load_file(
                    client=client,
                    bucket_name=BUCKET_NAME,
                    file_name=st.session_state.selected_file,
                )

                file_name = st.session_state.selected_file

                if file_name.endswith(".csv"):
                    file_bytes = io.StringIO(df.to_csv(index=False))
                elif file_name.endswith(".json"):
                    file_bytes = io.StringIO(df.to_json(orient="records"))
                else:
                    st.error("Unsupported file type for database storage.")
                    st.stop()

                result = store_data(file_bytes, file_name)
                st.success(
                    f"Stored {result['rows_inserted']} rows into table '{result['table']}'"
                )
        else:
            st.warning("Please select a file from the table first.")
