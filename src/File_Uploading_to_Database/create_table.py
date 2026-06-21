import streamlit as st
from sqlalchemy import text


def get_connection():
    return st.connection("supabase_db", type="sql")


def create_table(table_name: str, schema: dict[str, str]) -> None:
    columns_sql = ",\n".join(f'"{col}" {dtype}' for col, dtype in schema.items())
    conn = get_connection()
    with conn.session as session:
        session.execute(
            text(
                f"""CREATE TABLE IF NOT EXISTS "{table_name}" (id SERIAL PRIMARY KEY, {columns_sql});"""
            )
        )
        session.commit()
    print(f"Table '{table_name}' is ready with columns: {list(schema.keys())}")


def insert_rows(table_name: str, headers: list[str], rows: list[list[str]]):
    if not rows:
        print(f"No rows to insert into table '{table_name}'")
        return 0

    columns = ", ".join(f'"{h}"' for h in headers)
    param_keys = [f"v{i}" for i in range(len(headers))]
    placeholders = ", ".join(f":{k}" for k in param_keys)
    insert_sql = text(f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders})')

    def clean_row(row):
        return {
            f"v{i}": (None if v.strip() == "" else v.strip()) for i, v in enumerate(row)
        }

    conn = get_connection()
    with conn.session as session:
        session.execute(insert_sql, [clean_row(row) for row in rows])
        session.commit()
    print(f"Inserted {len(rows)} row(s) into table '{table_name}'")


def get_number_of_rows(rows: list[list[str]]):
    return len(rows)
