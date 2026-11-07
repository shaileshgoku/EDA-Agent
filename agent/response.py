import json
import re

from agent.chart_renderer import render_chart


def remove_markdown_tables(text):
    """
    Remove Markdown table blocks from agent text.

    The actual table is rendered separately by the frontend,
    so Markdown tables inside text would be duplicates.
    """

    if not text:
        return text

    lines = text.splitlines()

    cleaned_lines = []

    i = 0

    while i < len(lines):

        line = lines[i]

        if (
            "|" in line
            and i + 1 < len(lines)
            and re.match(
                r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$",
                lines[i + 1]
            )
        ):
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

        # ==================================================
        # AI MESSAGE
        # ==================================================

        if message_type == "AIMessage":

            if message.content:
                final_text = message.content

        # ==================================================
        # TOOL MESSAGE
        # ==================================================

        elif message_type == "ToolMessage":

            content = message.content

            try:
                parsed_content = json.loads(content)

            except (TypeError, json.JSONDecodeError):

                parsed_content = content

            # --------------------------------------------------
            # CHART RESULT
            # --------------------------------------------------

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

            # --------------------------------------------------
            # SQL QUERY RESULT
            # --------------------------------------------------

            elif (
                isinstance(parsed_content, dict)
                and parsed_content.get("type") == "table"
                and parsed_content.get("sql")
            ):

                # Keep the generated SQL so the frontend
                # can display it in the Generated SQL sidebar.

                queries.append({
                    "sql": parsed_content["sql"]
                })

                # IMPORTANT:
                #
                # Do NOT add SQL results to `tables`.
                #
                # SQL results are already represented by
                # the generated SQL section in the sidebar.
                #
                # Adding them to `tables` causes the same
                # query results to appear again in the main
                # response area.

            # --------------------------------------------------
            # NON-SQL TABLE RESULT
            # --------------------------------------------------

            elif (
                isinstance(parsed_content, dict)
                and parsed_content.get("type") == "table"
            ):

                # Structured table results that are not
                # SQL query results can still be rendered
                # as tables in the main response area.

                tables.append(parsed_content)

            # --------------------------------------------------
            # OTHER ANALYSIS RESULT
            # --------------------------------------------------

            else:

                analysis.append(parsed_content)

    # ==================================================
    # CLEAN FINAL TEXT
    # ==================================================

    final_text = remove_markdown_tables(final_text)

    # ==================================================
    # STRUCTURED RESPONSE
    # ==================================================

    return {
        "type": "agent_response",
        "text": final_text,
        "charts": charts,
        "tables": tables,
        "analysis": analysis,
        "queries": queries,
    }