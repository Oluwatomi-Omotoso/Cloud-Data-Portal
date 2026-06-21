import json
import os
import io
import csv
from src.File_Uploading_to_Database.clean_up_names import clean_up_name
from src.File_Uploading_to_Database.create_table import (
    create_table,
    insert_rows,
    get_number_of_rows,
    get_connection,
)
from src.File_Uploading_to_Database.build_schema import build_schema


def store_csv_data(file_obj, file_name: str, sample_size: int = 100) -> dict:
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    table_name = clean_up_name(base_name)

    if isinstance(file_obj, str):

        with open(file_obj, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            raw_headers = next(reader)
            all_rows = list(reader)
    else:
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        raw_headers = next(reader)
        all_rows = list(reader)

    cleaned_up_headers = [clean_up_name(h) for h in raw_headers]

    sample = all_rows[:sample_size]
    schema = build_schema(raw_headers, sample)
    create_table(table_name, schema)
    insert_rows(table_name, cleaned_up_headers, all_rows)
    row_count = get_number_of_rows(all_rows)

    return {"table": table_name, "columns": schema, "rows_inserted": row_count}


def store_json_data(file_obj, file_name: str, sample_size: int = 100) -> dict:
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    table_name = clean_up_name(base_name)

    if isinstance(file_obj, str):
        with open(file_obj, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        data = json.loads(content)

    if not data:
        return {"table": table_name, "columns": {}, "rows_inserted": 0}

    raw_headers = list(data[0].keys())
    cleaned_up_headers = [clean_up_name(h) for h in raw_headers]

    all_rows = []
    for item in data:
        row = [str(item.get(header, "")) for header in raw_headers]
        all_rows.append(row)

    sample = all_rows[:sample_size]
    schema = build_schema(raw_headers, sample)
    create_table(table_name, schema)
    insert_rows(table_name, cleaned_up_headers, all_rows)
    row_count = get_number_of_rows(all_rows)

    return {"table": table_name, "columns": schema, "rows_inserted": row_count}


def store_data(file_obj, file_name: str, sample_size: int = 100) -> dict:
    if file_name.endswith(".csv"):
        return store_csv_data(file_obj, file_name, sample_size)
    elif file_name.endswith(".json"):
        return store_json_data(file_obj, file_name, sample_size)
    else:
        raise ValueError(f"{file_name} is an unsupported file type.")


def fetch_all(table_name: str) -> list[dict]:
    table_name = clean_up_name(table_name)
    conn = get_connection()

    df = conn.query(f'SELECT * FROM "{table_name}"', tt1=0)
    return df.to_dict(orient="records")
