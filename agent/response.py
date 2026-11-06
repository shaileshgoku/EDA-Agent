import json
import re

from agent.chart_renderer import render_chart


def remove_markdown_tables(text):
    """
    Remove Markdown table blocks from agent text.

    The actual table is rendered separately by the frontend,
    so Markdown tables inside the LLM response would be duplicates.
    """

    if not text:
        return text

    lines = text.splitlines()

    cleaned_lines = []

    i = 0

    while i < len(lines):

        line = lines[i]

        # Detect a possible Markdown table header.
        if (
            "|" in line
            and i + 1 < len(lines)
            and re.match(
                r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$",
                lines[i + 1]
            )
        ):

            # Skip the entire Markdown table.
            i += 2

            while (
                i < len(lines)
                and "|" in lines[i]
                and lines[i].strip()
            ):
                i += 1

            continue

        cleaned_lines.append(line)

        i += 1

    return "\n".join(cleaned_lines).strip()


def extract_agent_response(response):
    """
    Convert the raw LangChain agent response into
    application-friendly structured output.
    """

    messages = response["messages"]

    final_text = ""
    charts = []
    tables = []
    analysis = []
    queries = []

    for message in messages:

        message_type = type(message).__name__

        if message_type == "AIMessage":

            if message.content:
                final_text = message.content

        elif message_type == "ToolMessage":

            content = message.content

            try:
                parsed_content = json.loads(content)

            except (TypeError, json.JSONDecodeError):

                parsed_content = content

            if (
                isinstance(parsed_content, dict)
                and parsed_content.get("type") == "chart"
            ):

                chart = render_chart(parsed_content)

                charts.append({
                    "type": "chart",
                    "chart_type": parsed_content["chart_type"],
                    "figure": chart,
                })

            elif (
                isinstance(parsed_content, dict)
                and parsed_content.get("type") == "table"
                and parsed_content.get("sql")
            ):

                queries.append({
                    "sql": parsed_content["sql"]
                })

                tables.append(parsed_content)

            elif (
                isinstance(parsed_content, dict)
                and parsed_content.get("type") == "table"
            ):

                tables.append(parsed_content)

            else:

                analysis.append(parsed_content)

    # Remove Markdown tables from the LLM's text.
    final_text = remove_markdown_tables(final_text)

    return {
        "type": "agent_response",
        "text": final_text,
        "charts": charts,
        "tables": tables,
        "analysis": analysis,
        "queries": queries,
    }