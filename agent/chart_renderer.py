import json

from visualization.charts import (
    create_histogram,
    create_bar_chart,
    create_pie_chart,
    create_scatter_plot,
    create_line_chart,
    create_box_plot,
    create_correlation_heatmap,
)


def render_chart(chart_instruction):
    """
    Convert a structured chart instruction
    into Plotly JSON.
    """

    chart_type = chart_instruction["chart_type"]

    if chart_type == "histogram":
        figure = create_histogram(
            chart_instruction["table_name"],
            chart_instruction["column_name"],
        )

    elif chart_type == "bar":
        figure = create_bar_chart(
            chart_instruction["table_name"],
            chart_instruction["column_name"],
        )

    elif chart_type == "pie":
        figure = create_pie_chart(
            chart_instruction["table_name"],
            chart_instruction["column_name"],
        )

    elif chart_type == "scatter":
        figure = create_scatter_plot(
            chart_instruction["table_name"],
            chart_instruction["x_column"],
            chart_instruction["y_column"],
        )

    elif chart_type == "line":
        figure = create_line_chart(
            chart_instruction["table_name"],
            chart_instruction["x_column"],
            chart_instruction["y_column"],
        )

    elif chart_type == "box_plot":
        figure = create_box_plot(
            chart_instruction["table_name"],
            chart_instruction["column_name"],
        )

    elif chart_type == "correlation_heatmap":
        figure = create_correlation_heatmap(
            chart_instruction["table_name"]
        )

    else:
        raise ValueError(
            f"Unsupported chart type: {chart_type}"
        )

    return json.loads(figure.to_json())