from database.duckdb_client import get_duckdb_connection


def analyze_categorical_columns(table_name):
    """
    Analyze categorical columns in a DuckDB table.

    Returns:
        A dictionary containing categorical columns and
        their value distributions.
    """

    connection = get_duckdb_connection()

    try:
        # Discover table columns
        columns = connection.execute(
            f"""
            DESCRIBE "{table_name}"
            """
        ).fetchall()

        # Identify categorical columns
        categorical_columns = []

        for column in columns:
            column_name = column[0]
            data_type = column[1]

            if data_type in (
                "VARCHAR",
                "TEXT"
            ):
                categorical_columns.append(column_name)

        distributions = {}

        # Calculate value counts
        for column_name in categorical_columns:

            results = connection.execute(
                f"""
                SELECT
                    "{column_name}",
                    COUNT(*) AS frequency
                FROM "{table_name}"
                WHERE "{column_name}" IS NOT NULL
                GROUP BY "{column_name}"
                ORDER BY frequency DESC
                """
            ).fetchall()

            distributions[column_name] = [
                {
                    "value": row[0],
                    "frequency": row[1]
                }
                for row in results
            ]

        return {
            "table_name": table_name,
            "categorical_columns": categorical_columns,
            "distributions": distributions
        }

    finally:
        connection.close()