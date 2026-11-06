import pandas as pd
from psycopg import sql

from database.postgres import get_postgres_connection
from database.duckdb_client import get_duckdb_connection

def extract_table(table_name):
    """
    Extract data from PostgreSQL into a Pandas DataFrame.
    """

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            query = sql.SQL("SELECT * FROM {}").format(
                sql.Identifier(table_name)
            )

            cursor.execute(query)

            rows = cursor.fetchall()

            columns = [column.name for column in cursor.description]

            dataframe = pd.DataFrame(rows, columns=columns)

        return dataframe

    finally:
        connection.close()

def load_table_to_duckdb(dataframe, table_name):
    """
    Load a Pandas DataFrame into a DuckDB table.
    """

    connection = get_duckdb_connection()

    connection.register("temp_dataframe", dataframe)

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE {table_name}
        AS SELECT * FROM temp_dataframe
        """
    )

    connection.unregister("temp_dataframe")

    connection.close()

def sync_table(table_name):
    """
    Synchronize a PostgreSQL table into DuckDB.
    """

    dataframe = extract_table(table_name)

    if dataframe.empty:
        print(f"Skipping empty table: {table_name}")
        return

    load_table_to_duckdb(dataframe, table_name)

    print(f"Successfully synced {table_name}")

def sync_all_tables():
    """
    Synchronize all required PostgreSQL tables into DuckDB.
    """

    tables = get_postgres_tables()

    for table_name in tables:
        sync_table(table_name)


def get_postgres_tables():
    """
    Get all table names from the PostgreSQL public schema.
    """

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)

            tables = [row[0] for row in cursor.fetchall()]

        return tables

    finally:
        connection.close()