import duckdb

from config.settings import DUCKDB_PATH


def get_duckdb_connection():
    """
    Establish and return a DuckDB connection.
    """

    connection = duckdb.connect(DUCKDB_PATH)

    return connection


def get_duckdb_tables():
    """
    Return all tables available in DuckDB.
    """

    connection = get_duckdb_connection()

    try:
        result = connection.execute("""
            SHOW TABLES
        """).fetchall()

        tables = [row[0] for row in result]

        return tables

    finally:
        connection.close()

def get_table_schema(table_name):
    """
    Return a simplified schema for a DuckDB table.
    """

    connection = get_duckdb_connection()

    try:
        result = connection.execute(
            f"""
            DESCRIBE "{table_name}"
            """
        ).fetchall()

        schema = []

        for row in result:
            schema.append({
                "column_name": row[0],
                "data_type": row[1]
            })

        return schema

    finally:
        connection.close()

def execute_query(query):
    """
    Execute a SQL query against DuckDB and return
    a structured table result.
    """
    connection = get_duckdb_connection()

    try:
        result = connection.execute(query)

        columns = [
            column[0]
            for column in result.description
        ]

        rows = result.fetchall()

        return {
            "type": "table",
            "columns": columns,
            "rows": rows,
        }

    finally:
        connection.close()