from database.duckdb_client import get_duckdb_connection


def calculate_numeric_statistics(table_name):
    """
    Calculate descriptive statistics for numeric columns
    in a DuckDB table.
    """

    connection = get_duckdb_connection()

    try:
        # Discover table columns
        columns = connection.execute(
            f"""
            DESCRIBE "{table_name}"
            """
        ).fetchall()

        # Identify numeric columns
        numeric_columns = []

        for column in columns:
            column_name = column[0]
            data_type = column[1]

            if data_type in (
                "BIGINT",
                "INTEGER",
                "DOUBLE",
                "DECIMAL",
                "FLOAT"
            ):
                numeric_columns.append(column_name)

        statistics = {}

        # Calculate statistics for each numeric column
        for column_name in numeric_columns:

            result = connection.execute(
                f"""
                SELECT
                    COUNT("{column_name}"),
                    AVG("{column_name}"),
                    MEDIAN("{column_name}"),
                    STDDEV("{column_name}"),
                    MIN("{column_name}"),
                    MAX("{column_name}")
                FROM "{table_name}"
                """
            ).fetchone()

            statistics[column_name] = {
                "count": result[0],
                "mean": result[1],
                "median": result[2],
                "stddev": result[3],
                "min": result[4],
                "max": result[5]
            }

        return statistics

    finally:
        connection.close()