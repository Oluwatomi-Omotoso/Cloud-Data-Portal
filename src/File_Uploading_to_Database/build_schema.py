from src.File_Uploading_to_Database.clean_up_names import clean_up_name
from src.File_Uploading_to_Database.infer_datatype import infer_type


# This function builds the schema for the database, sampling elements from several rows from the csv file and determining the datatype for each column in the schema.
def build_schema(headers: list[str], sample_rows: list[list[str]]):
    schema = {}
    for i, header in enumerate(headers):
        # Sorts through the sample rows and attends to the columns one at a time.
        column_values = [row[i] for row in sample_rows if i < len(row)]
        # Gives the selected column a name
        col_name = clean_up_name(header)
        # Infer the datatype of the column
        col_type = infer_type(column_values)

        # And finally creates a column in the schema.
        schema[col_name] = col_type

    return schema
