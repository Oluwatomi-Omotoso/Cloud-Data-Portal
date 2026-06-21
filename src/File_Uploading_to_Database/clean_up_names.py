import re


# This helper function cleans up the names of datasets and columns, making them compliant for an SQLite table or a column name.
def clean_up_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", "_", name)

    return name
