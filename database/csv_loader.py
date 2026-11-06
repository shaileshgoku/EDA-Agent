import pandas as pd
from database.postgres import get_postgres_connection
from database.sync import sync_table


def load_file(file_path):
    """
    Load a CSV or Excel file into a Pandas DataFrame.
    """

    if file_path.endswith(".csv"):
        dataframe = pd.read_csv(file_path)

    elif file_path.endswith((".xlsx", ".xls")):
        dataframe = pd.read_excel(file_path)

    else:
        raise ValueError(
            "Unsupported file format. "
            "Only CSV and Excel files are supported."
        )

    return dataframe

def load_dataframe_to_postgres(dataframe, table_name):
    """
    Load a Pandas DataFrame into a PostgreSQL table.
    """

    connection = get_postgres_connection()

    try:
        columns = dataframe.columns.tolist()

        column_definitions = []

        for column in columns:
            postgres_type = pandas_dtype_to_postgres(
                dataframe[column].dtype
            )

            column_definitions.append(
                f'"{column}" {postgres_type}'
            )

        create_table_query = f"""
            DROP TABLE IF EXISTS "{table_name}";

            CREATE TABLE "{table_name}" (
                {", ".join(column_definitions)}
            )
        """

        with connection.cursor() as cursor:
            cursor.execute(create_table_query)

            for row in dataframe.itertuples(index=False, name=None):
                placeholders = ", ".join(["%s"] * len(columns))

                insert_query = f"""
                    INSERT INTO "{table_name}"
                    VALUES ({placeholders})
                """

                cursor.execute(insert_query, row)

        connection.commit()

    finally:
        connection.close()

def ingest_file(file_path, table_name):
    """
    Ingest a CSV or Excel file into PostgreSQL and DuckDB.
    """

    dataframe = load_file(file_path)

    load_dataframe_to_postgres(
        dataframe,
        table_name
    )

    sync_table(table_name)

    print(f"Successfully ingested {file_path}")

def pandas_dtype_to_postgres(dtype):
    """
    Map a Pandas dtype to a PostgreSQL data type.
    """

    if pd.api.types.is_integer_dtype(dtype):
        return "BIGINT"

    if pd.api.types.is_float_dtype(dtype):
        return "DOUBLE PRECISION"

    if pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"

    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "TIMESTAMP"

    return "TEXT"