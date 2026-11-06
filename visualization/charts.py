import pandas as pd
import plotly.express as px

from database.duckdb_client import get_duckdb_connection


def create_histogram(table_name, column_name):
    """
    Create a histogram for a numeric column.
    """

    connection = get_duckdb_connection()

    try:
        dataframe = connection.execute(
            f"""
            SELECT "{column_name}"
            FROM "{table_name}"
            WHERE "{column_name}" IS NOT NULL
            """
        ).fetchdf()

    finally:
        connection.close()

    figure = px.histogram(
        dataframe,
        x=column_name,
        title=f"Distribution of {column_name}"
    )

    return figure

def create_bar_chart(table_name, column_name):
    """
    Create a bar chart showing the frequency
    of values in a categorical column.
    """

    connection = get_duckdb_connection()

    try:
        dataframe = connection.execute(
            f"""
            SELECT
                "{column_name}",
                COUNT(*) AS frequency
            FROM "{table_name}"
            WHERE "{column_name}" IS NOT NULL
            GROUP BY "{column_name}"
            ORDER BY frequency DESC
            """
        ).fetchdf()

    finally:
        connection.close()

    figure = px.bar(
        dataframe,
        x=column_name,
        y="frequency",
        title=f"Distribution of {column_name}"
    )

    return figure

def create_scatter_plot(table_name, x_column, y_column):
    """
    Create a scatter plot between two numeric columns.
    """

    connection = get_duckdb_connection()

    try:
        dataframe = connection.execute(
            f"""
            SELECT
                "{x_column}",
                "{y_column}"
            FROM "{table_name}"
            WHERE "{x_column}" IS NOT NULL
              AND "{y_column}" IS NOT NULL
            """
        ).fetchdf()

    finally:
        connection.close()

    figure = px.scatter(
        dataframe,
        x=x_column,
        y=y_column,
        title=f"{x_column} vs {y_column}"
    )

    return figure

def create_line_chart(table_name, x_column, y_column):
    """
    Create a line chart using a time/date column
    and a numeric column.
    """

    connection = get_duckdb_connection()

    try:
        dataframe = connection.execute(
            f"""
            SELECT
                "{x_column}",
                "{y_column}"
            FROM "{table_name}"
            WHERE "{x_column}" IS NOT NULL
              AND "{y_column}" IS NOT NULL
            ORDER BY "{x_column}"
            """
        ).fetchdf()

    finally:
        connection.close()

    figure = px.line(
        dataframe,
        x=x_column,
        y=y_column,
        title=f"{y_column} over {x_column}"
    )

    return figure

def create_box_plot(table_name, column_name):
    """
    Create a box plot for a numeric column.
    """

    connection = get_duckdb_connection()

    try:
        dataframe = connection.execute(
            f"""
            SELECT "{column_name}"
            FROM "{table_name}"
            WHERE "{column_name}" IS NOT NULL
            """
        ).fetchdf()

    finally:
        connection.close()

    figure = px.box(
        dataframe,
        y=column_name,
        title=f"Box Plot of {column_name}"
    )

    return figure

def create_correlation_heatmap(table_name):
    """
    Create a heatmap showing correlations
    between numeric columns.
    """

    connection = get_duckdb_connection()

    try:
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

        if len(numeric_columns) < 2:
            raise ValueError(
                "At least two numeric columns are required "
                "to create a correlation heatmap."
            )

        column_list = ", ".join(
            f'"{column}"' for column in numeric_columns
        )

        dataframe = connection.execute(
            f"""
            SELECT {column_list}
            FROM "{table_name}"
            """
        ).fetchdf()

    finally:
        connection.close()

    correlation_matrix = dataframe.corr(numeric_only=True)

    figure = px.imshow(
        correlation_matrix,
        text_auto=True,
        title=f"Correlation Heatmap — {table_name}"
    )

    return figure

def create_pie_chart(table_name, column_name):
    """
    Create a pie chart showing the proportion
    of values in a categorical column.
    """

    connection = get_duckdb_connection()

    try:
        dataframe = connection.execute(
            f"""
            SELECT
                "{column_name}",
                COUNT(*) AS frequency
            FROM "{table_name}"
            WHERE "{column_name}" IS NOT NULL
            GROUP BY "{column_name}"
            ORDER BY frequency DESC
            """
        ).fetchdf()

    finally:
        connection.close()

    figure = px.pie(
        dataframe,
        names=column_name,
        values="frequency",
        title=f"Distribution of {column_name}"
    )

    return figure