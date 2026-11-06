from database.duckdb_client import get_duckdb_connection


def profile_table(table_name):
    """
    Return basic profiling information about a DuckDB table.
    """

    connection = get_duckdb_connection()

    try:
        # Get row count
        row_count = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM "{table_name}"
            """
        ).fetchone()[0]

        # Get column count
        column_count = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            """
        ).fetchone()[0]

        # Get column names and data types
        columns = connection.execute(
            f"""
            DESCRIBE "{table_name}"
            """
        ).fetchall()

        column_details = []

        for column in columns:
            column_details.append({
                "column_name": column[0],
                "data_type": column[1]
            })

        # Get missing values for each column
        missing_values = {}

        for column in column_details:
            column_name = column["column_name"]

            result = connection.execute(
                f"""
                SELECT COUNT(*)
                FROM "{table_name}"
                WHERE "{column_name}" IS NULL
                """
            ).fetchone()[0]

            missing_values[column_name] = result

        return {
            "table_name": table_name,
            "row_count": row_count,
            "column_count": column_count,
            "columns": column_details,
            "missing_values": missing_values
        }

    finally:
        connection.close()