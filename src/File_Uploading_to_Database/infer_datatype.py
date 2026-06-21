# This function will be used to infer the datatype for a column, by comparing the datatype of some of the elements inside that column.
def infer_type(values: list[str]) -> str:

    non_empty = [v.strip() for v in values if v.strip() != ""]

    # If there is an empty value, set it to "TEXT" for now
    if not non_empty:
        return "TEXT"

    # Switches for checking integers and floats.
    is_int = True
    is_float = True

    for v in non_empty:
        # If the non-empty value is an incompatible float string for SQL, set it to "TEXT"
        if v.lower() in ("nan", "inf", "-inf", "infinity", "-infinity"):
            return "TEXT"

        # While the switch for integers is still active, check if the value can be parsed as an integer.
        if is_int:
            try:
                int(v)
            except ValueError:
                is_int = False  # If even one value is not an integer column, flip the switch for the integers off.

        # While the switch for floats is still active, check if the value can be parsed as a float.
        if is_float:
            try:
                float(v)
            except ValueError:
                is_float = False  # If even one value is not a float column, flip the switch for the floats off.

        # If both switches are now flipped, then we can safely say the column is a "TEXT" datatype.
        if not is_int and not is_float:
            return "TEXT"

    # Final check on the switches
    if is_int:
        return "INTEGER"
    if is_float:
        return "FLOAT"

    return "TEXT"
