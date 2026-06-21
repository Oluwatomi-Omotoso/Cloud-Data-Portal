# Cloud Data Portal

A Streamlit app for uploading, previewing, and storing datasets between Google Cloud Storage, Supabasee PostgreSQL and on your local machine. The project was to simulate the full ETL pipeline for data science.

## Features

- **Managed Backend:** Utilizes Supabase's hosted PostgreSQL database for instant data persistence.
- **Secure API Access:** Communicates safely with the backend using Row Level Security (RLS) and auto-generated REST APIs.
- **Rapid UI Rendering:** Streamlit instantly reflects backend database changes directly in the user interface.
- **File Uploads:** Raw CSV and JSON files can be uploaded to the Google Cloud Storage, this location is intended for unprocessed and dirty data sets.
- **File Preview:** Files uploaded to the bucket (CSV and JSON inclusive) can be previewed in a JSON format, showcasing each row as an "object" with each column serving as an atrribute for said object.
- **File Download:** Files saved in the cloud can be downloaded locally perhaps for data cleaning or manipulation, or just for local storage. And then reuploaded back to the Google cloud storage.
- **Database storage**: And finally the cleaned up dataset can be stored in a PostgreSQL database hosted on Supabase.
- **Direct GCP Integration:** Authenticates securely using dedicated Google Service Accounts.
- **Robust Error Handling:** Catches and displays `GoogleCloudError` exceptions directly in the UI for seamless debugging.
- **Streamlined UI:** Lightweight interface for uploading files without needing access to the GCP console.
- **Dynamic Data Fetching:** Executes server-side SQL queries dynamically based on user input.
- **SQL Injection Protection:** Utilizes SQLAlchemy's `text()` construct for safe, parameterized queries.

## Tech Stack

- **Language:** Python
- **UI framework:** Streamlit
- **Backend-as-a-service (BAAS):**Supabase (PostgreSQL)
- **Authentication:** Google Auth (`google-oauth2`)
- **Libraries/Frameworks:** Pandas, Streamlit, Google Cloud Storage,

## Installation & SetUp

### Prerequisites
1. Python 3.8+
2. A free or paid account on [Supabase](https://supabase.com/) with a project intialised.
3. A Google Cloud Platform (GCP) Account:** * An active GCS bucket.
A Service Account Key file (`.json`) with **Storage Object Creator/Admin** permissions.

### Step-by-step Guide

1. **Clone the repository:**

```bash
    git clone [https://github.com/Oluwatomi-Omotoso/Cloud-Data-Portal.git](https://github.com/Oluwatomi-Omotoso/Cloud-Data-Portal.git)

    cd Cloud-Data-Portal
```

2. **Install dependencies**
   pip install -r requirements.txt

3. **Environment configuration**
   Create a .streamlit folder in your root directory, and then a .secrets.toml file (inside the .stremlit folder)to hold your environment variables.

Ensure these contents are in your toml file

```
BUCKET_NAME = "your-bucket-name"
[connections.supabase_db]

url = 'your-postgres-url'
dialect = "postgresql"
host = "host"
port = 5432
database = "postgres"
username = "username"
password = "password"
connect_args = {keepalives = 1, keepalives_idle = 30, keepalives_interval = 10, keepalives_count = 5}
pool_pre_ping = true

[gcp_service_account]
type = "service_account"
project_id = "project id"
private_key_id = "private key ID"
client_email = "client email"
client_id = "client id"
auth_uri= "auth_uri"
token_uri = "token_uri"
auth_provider_x509_cert_url = "auth_provider_certificate_url"
client_x509_cert_url = "client_provider_certificate_url"
universe_domain = "googleapis.com"
```

### Run the program

```
streamlit run app.py
```
