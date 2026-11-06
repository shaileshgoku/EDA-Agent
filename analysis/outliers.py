from database.duckdb_client import get_duckdb_connection


def detect_outliers(table_name):
    """
    Detect outliers in numeric columns using the IQR method.
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

        outliers = {}

        for column_name in numeric_columns:

            result = connection.execute(
                f"""
                SELECT
                    QUANTILE_CONT("{column_name}", 0.25),
                    QUANTILE_CONT("{column_name}", 0.75)
                FROM "{table_name}"
                WHERE "{column_name}" IS NOT NULL
                """
            ).fetchone()

            q1 = result[0]
            q3 = result[1]

            iqr = q3 - q1

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outlier_result = connection.execute(
                f"""
                SELECT COUNT(*)
                FROM "{table_name}"
                WHERE "{column_name}" < {lower_bound}
                   OR "{column_name}" > {upper_bound}
                """
            ).fetchone()

            outlier_count = outlier_result[0]

            outliers[column_name] = {
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "outlier_count": outlier_count
            }

        return {
            "table_name": table_name,
            "numeric_columns": numeric_columns,
            "outliers": outliers
        }

    finally:
        connection.close()