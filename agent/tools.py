from langchain_core.tools import tool

from database.duckdb_client import get_duckdb_tables
from database.duckdb_client import get_table_schema
from database.duckdb_client import execute_query

from analysis.profiling import profile_table
from analysis.statistics import calculate_numeric_statistics
from analysis.categorical import analyze_categorical_columns
from analysis.correlation import calculate_correlation
from analysis.outliers import detect_outliers


@tool
def list_tables():
    """
    List all tables available in DuckDB.
    """
    return get_duckdb_tables()


@tool
def get_schema(table_name: str):
    """
    Get the columns and data types of a DuckDB table.
    """
    return get_table_schema(table_name)


@tool
def run_sql(query: str):
    """
    Execute a read-only SQL query against DuckDB.

    Returns both the executed SQL and the query result.
    """

    query = query.strip()

    allowed = (
        query.upper().startswith("SELECT")
        or query.upper().startswith("WITH")
    )

    if not allowed:
        raise ValueError(
            "Only SELECT and WITH queries are allowed."
        )

    result = execute_query(query)

    return {
        "type": "table",
        "sql": query,
        "columns": result["columns"],
        "rows": [
            [
                str(value) if value is not None else None
                for value in row
            ]
            for row in result["rows"]
        ],
    }

@tool
def profile_dataset(table_name: str):
    """
    Profile a DuckDB table.

    Returns row count, column count, column details,
    and missing-value information.
    """
    return profile_table(table_name)


@tool
def numeric_statistics(table_name: str):
    """
    Calculate descriptive statistics for numeric columns
    in a DuckDB table.
    """
    return calculate_numeric_statistics(table_name)


@tool
def categorical_analysis(table_name: str):
    """
    Analyze categorical columns and return
    their value distributions.
    """
    return analyze_categorical_columns(table_name)


@tool
def correlation_analysis(table_name: str):
    """
    Calculate correlations between numeric columns
    in a DuckDB table.
    """
    return calculate_correlation(table_name)


@tool
def outlier_analysis(table_name: str):
    """
    Detect outliers in numeric columns using the IQR method.
    """
    return detect_outliers(table_name)


@tool
def histogram(table_name: str, column_name: str):
    """
    Request a histogram for a numeric column.
    """
    return {
        "type": "chart",
        "chart_type": "histogram",
        "table_name": table_name,
        "column_name": column_name,
    }


@tool
def bar_chart(table_name: str, column_name: str):
    """
    Request a bar chart for a categorical column.
    """
    return {
        "type": "chart",
        "chart_type": "bar",
        "table_name": table_name,
        "column_name": column_name,
    }


@tool
def pie_chart(table_name: str, column_name: str):
    """
    Request a pie chart for a categorical column.
    """
    return {
        "type": "chart",
        "chart_type": "pie",
        "table_name": table_name,
        "column_name": column_name,
    }


@tool
def scatter_plot(
    table_name: str,
    x_column: str,
    y_column: str
):
    """
    Request a scatter plot between two numeric columns.
    """
    return {
        "type": "chart",
        "chart_type": "scatter",
        "table_name": table_name,
        "x_column": x_column,
        "y_column": y_column,
    }


@tool
def line_chart(
    table_name: str,
    x_column: str,
    y_column: str
):
    """
    Request a line chart over an ordered column.
    """
    return {
        "type": "chart",
        "chart_type": "line",
        "table_name": table_name,
        "x_column": x_column,
        "y_column": y_column,
    }


@tool
def box_plot(table_name: str, column_name: str):
    """
    Request a box plot for a numeric column.
    """
    return {
        "type": "chart",
        "chart_type": "box_plot",
        "table_name": table_name,
        "column_name": column_name,
    }


@tool
def correlation_heatmap(table_name: str):
    """
    Request a correlation heatmap for numeric columns.
    """
    return {
        "type": "chart",
        "chart_type": "correlation_heatmap",
        "table_name": table_name,
    }


EDA_TOOLS = [
    list_tables,
    get_schema,
    run_sql,
    profile_dataset,
    numeric_statistics,
    categorical_analysis,
    correlation_analysis,
    outlier_analysis,
    histogram,
    bar_chart,
    pie_chart,
    scatter_plot,
    line_chart,
    box_plot,
    correlation_heatmap,
]