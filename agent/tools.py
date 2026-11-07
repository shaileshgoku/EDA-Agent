from langchain_core.tools import tool

from database.duckdb_client import (
    get_duckdb_connection,
    get_duckdb_tables,
    get_table_schema,
    execute_query,
)

from analysis.profiling import profile_table
from analysis.statistics import calculate_numeric_statistics
from analysis.categorical import analyze_categorical_columns
from analysis.correlation import calculate_correlation
from analysis.outliers import detect_outliers


# ==================================================
# VALIDATION HELPERS
# ==================================================


def validate_table_name(table_name):
    """
    Validate that a table exists in DuckDB.
    """

    if not table_name:
        raise ValueError(
            "table_name is required."
        )

    tables = get_duckdb_tables()

    if table_name not in tables:
        raise ValueError(
            f"Table '{table_name}' does not exist in DuckDB."
        )


def get_valid_columns(table_name):
    """
    Return the valid column names for a DuckDB table.
    """

    validate_table_name(table_name)

    schema = get_table_schema(table_name)

    return [
        column["column_name"]
        for column in schema
    ]


def validate_column_name(
    table_name,
    column_name,
):
    """
    Validate that a column exists in a DuckDB table.
    """

    if not column_name:
        raise ValueError(
            "column_name is required."
        )

    columns = get_valid_columns(table_name)

    if column_name not in columns:
        raise ValueError(
            f"Column '{column_name}' does not exist "
            f"in table '{table_name}'."
        )


def validate_group_by_column(
    table_name,
    group_by_column,
):
    """
    Validate that a group-by column exists
    in a DuckDB table.
    """

    if not group_by_column:
        raise ValueError(
            "group_by_column is required."
        )

    columns = get_valid_columns(table_name)

    if group_by_column not in columns:
        raise ValueError(
            f"Column '{group_by_column}' does not exist "
            f"in table '{table_name}'."
        )


# ==================================================
# DATABASE DISCOVERY TOOLS
# ==================================================


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

    validate_table_name(table_name)

    return get_table_schema(table_name)


# ==================================================
# SQL TOOL
# ==================================================


@tool
def run_sql(query: str):
    """
    Execute a read-only SQL query against DuckDB.

    Returns both the executed SQL and the query result.

    Only SELECT and WITH queries are allowed.
    """

    query = query.strip()

    # Remove leading SQL comments before checking
    # the first SQL keyword.
    cleaned_query = query

    while cleaned_query.startswith("--"):
        if "\n" in cleaned_query:
            cleaned_query = (
                cleaned_query.split("\n", 1)[1].strip()
            )
        else:
            cleaned_query = ""

    allowed = (
        cleaned_query.upper().startswith("SELECT")
        or cleaned_query.upper().startswith("WITH")
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


# ==================================================
# CONTROLLED PANDAS ANALYSIS TOOL
# ==================================================


@tool
def pandas_analysis(
    table_name: str,
    operation: str,
    column_name: str = "",
    group_by_column: str = "",
):
    """
    Perform controlled Pandas analysis on a DuckDB table.

    The agent can dynamically choose the analysis operation.

    Supported operations:

    describe
    value_counts
    groupby_mean
    groupby_sum
    groupby_count
    correlation
    missing_values
    """

    # --------------------------------------------------
    # VALIDATE TABLE
    # --------------------------------------------------

    validate_table_name(table_name)

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------

    connection = get_duckdb_connection()

    try:

        dataframe = connection.execute(
            f'SELECT * FROM "{table_name}"'
        ).fetchdf()

    finally:

        connection.close()

    operation = operation.lower().strip()

    # --------------------------------------------------
    # DESCRIBE
    # --------------------------------------------------

    if operation == "describe":

        result = dataframe.describe(
            include="all"
        ).transpose()

        return {
            "type": "pandas_analysis",
            "operation": operation,
            "table_name": table_name,
            "result": result.reset_index().to_dict(
                orient="records"
            ),
        }

    # --------------------------------------------------
    # VALUE COUNTS
    # --------------------------------------------------

    elif operation == "value_counts":

        validate_column_name(
            table_name,
            column_name
        )

        result = (
            dataframe[column_name]
            .value_counts(dropna=False)
            .reset_index()
        )

        result.columns = [
            column_name,
            "count",
        ]

        return {
            "type": "pandas_analysis",
            "operation": operation,
            "table_name": table_name,
            "column": column_name,
            "result": result.to_dict(
                orient="records"
            ),
        }

    # --------------------------------------------------
    # GROUP BY MEAN
    # --------------------------------------------------

    elif operation == "groupby_mean":

        validate_group_by_column(
            table_name,
            group_by_column
        )

        validate_column_name(
            table_name,
            column_name
        )

        result = (
            dataframe
            .groupby(group_by_column)[column_name]
            .mean()
            .reset_index()
        )

        return {
            "type": "pandas_analysis",
            "operation": operation,
            "table_name": table_name,
            "group_by": group_by_column,
            "column": column_name,
            "result": result.to_dict(
                orient="records"
            ),
        }

    # --------------------------------------------------
    # GROUP BY SUM
    # --------------------------------------------------

    elif operation == "groupby_sum":

        validate_group_by_column(
            table_name,
            group_by_column
        )

        validate_column_name(
            table_name,
            column_name
        )

        result = (
            dataframe
            .groupby(group_by_column)[column_name]
            .sum()
            .reset_index()
        )

        return {
            "type": "pandas_analysis",
            "operation": operation,
            "table_name": table_name,
            "group_by": group_by_column,
            "column": column_name,
            "result": result.to_dict(
                orient="records"
            ),
        }

    # --------------------------------------------------
    # GROUP BY COUNT
    # --------------------------------------------------

    elif operation == "groupby_count":

        validate_group_by_column(
            table_name,
            group_by_column
        )

        result = (
            dataframe
            .groupby(group_by_column)
            .size()
            .reset_index(name="count")
        )

        return {
            "type": "pandas_analysis",
            "operation": operation,
            "table_name": table_name,
            "group_by": group_by_column,
            "result": result.to_dict(
                orient="records"
            ),
        }

    # --------------------------------------------------
    # CORRELATION
    # --------------------------------------------------

    elif operation == "correlation":

        result = dataframe.corr(
            numeric_only=True
        )

        return {
            "type": "pandas_analysis",
            "operation": operation,
            "table_name": table_name,
            "result": result.reset_index().to_dict(
                orient="records"
            ),
        }

    # --------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------

    elif operation == "missing_values":

        result = (
            dataframe.isnull()
            .sum()
            .reset_index()
        )

        result.columns = [
            "column",
            "missing_count",
        ]

        return {
            "type": "pandas_analysis",
            "operation": operation,
            "table_name": table_name,
            "column": "missing_values",
            "result": result.to_dict(
                orient="records"
            ),
        }

    # --------------------------------------------------
    # INVALID OPERATION
    # --------------------------------------------------

    else:

        raise ValueError(
            f"Unsupported Pandas operation: {operation}"
        )


# ==================================================
# STANDARD EDA ANALYSIS TOOLS
# ==================================================


@tool
def profile_dataset(table_name: str):
    """
    Profile a DuckDB table.

    Returns row count, column count, column details,
    and missing-value information.
    """

    validate_table_name(table_name)

    return profile_table(table_name)


@tool
def numeric_statistics(table_name: str):
    """
    Calculate descriptive statistics for numeric columns
    in a DuckDB table.
    """

    validate_table_name(table_name)

    return calculate_numeric_statistics(table_name)


@tool
def categorical_analysis(table_name: str):
    """
    Analyze categorical columns and return
    their value distributions.
    """

    validate_table_name(table_name)

    return analyze_categorical_columns(table_name)


@tool
def correlation_analysis(table_name: str):
    """
    Calculate correlations between numeric columns
    in a DuckDB table.
    """

    validate_table_name(table_name)

    return calculate_correlation(table_name)


@tool
def outlier_analysis(table_name: str):
    """
    Detect outliers in numeric columns using the IQR method.
    """

    validate_table_name(table_name)

    return detect_outliers(table_name)


# ==================================================
# VISUALIZATION TOOLS
# ==================================================


@tool
def histogram(
    table_name: str,
    column_name: str,
):
    """
    Request a histogram for a numeric column.
    """

    validate_table_name(table_name)

    validate_column_name(
        table_name,
        column_name
    )

    return {
        "type": "chart",
        "chart_type": "histogram",
        "table_name": table_name,
        "column_name": column_name,
    }


@tool
def bar_chart(
    table_name: str,
    column_name: str,
):
    """
    Request a bar chart for a categorical column.
    """

    validate_table_name(table_name)

    validate_column_name(
        table_name,
        column_name
    )

    return {
        "type": "chart",
        "chart_type": "bar",
        "table_name": table_name,
        "column_name": column_name,
    }


@tool
def pie_chart(
    table_name: str,
    column_name: str,
):
    """
    Request a pie chart for a categorical column.
    """

    validate_table_name(table_name)

    validate_column_name(
        table_name,
        column_name
    )

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
    y_column: str,
):
    """
    Request a scatter plot between two numeric columns.
    """

    validate_table_name(table_name)

    validate_column_name(
        table_name,
        x_column
    )

    validate_column_name(
        table_name,
        y_column
    )

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
    y_column: str,
):
    """
    Request a line chart over an ordered column.
    """

    validate_table_name(table_name)

    validate_column_name(
        table_name,
        x_column
    )

    validate_column_name(
        table_name,
        y_column
    )

    return {
        "type": "chart",
        "chart_type": "line",
        "table_name": table_name,
        "x_column": x_column,
        "y_column": y_column,
    }


@tool
def box_plot(
    table_name: str,
    column_name: str,
):
    """
    Request a box plot for a numeric column.
    """

    validate_table_name(table_name)

    validate_column_name(
        table_name,
        column_name
    )

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

    validate_table_name(table_name)

    return {
        "type": "chart",
        "chart_type": "correlation_heatmap",
        "table_name": table_name,
    }


# ==================================================
# TOOL REGISTRY
# ==================================================


EDA_TOOLS = [
    # Database discovery
    list_tables,
    get_schema,

    # Data access
    run_sql,

    # Dynamic Python/Pandas analysis
    pandas_analysis,

    # Standard EDA analysis
    profile_dataset,
    numeric_statistics,
    categorical_analysis,
    correlation_analysis,
    outlier_analysis,

    # Visualization
    histogram,
    bar_chart,
    pie_chart,
    scatter_plot,
    line_chart,
    box_plot,
    correlation_heatmap,
]