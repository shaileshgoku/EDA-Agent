from database.duckdb_client import get_duckdb_connection


def calculate_correlation(table_name):
    """
    Calculate correlation between numeric columns
    in a DuckDB table.
    """

    connection = get_duckdb_connection()

    try:
        # Discover numeric columns
        columns = connection.execute(
            f"""
            DESCRIBE "{table_name}"
            """
        ).fetchall()

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

        # Calculate correlation matrix
        correlation_matrix = {}

        for column_a in numeric_columns:

            correlation_matrix[column_a] = {}

            for column_b in numeric_columns:

                result = connection.execute(
                    f"""
                    SELECT CORR(
                        "{column_a}",
                        "{column_b}"
                    )
                    FROM "{table_name}"
                    """
                ).fetchone()

                correlation_matrix[column_a][column_b] = result[0]

        return {
            "table_name": table_name,
            "numeric_columns": numeric_columns,
            "correlation_matrix": correlation_matrix
        }

    finally:
        connection.close()