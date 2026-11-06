import os
import tempfile

from fastapi import UploadFile, File
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database.duckdb_client import (
    get_duckdb_tables,
    get_table_schema,
    execute_query,
)

from agent.agent import get_eda_agent
from agent.response import extract_agent_response

from agent.memory import (
    get_conversation,
    save_conversation,
)


app = FastAPI(
    title="EDA Agent API",
    description="Agentic AI-powered Exploratory Data Analysis API",
    version="0.1.0",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request Models
# --------------------------------------------------

class QuestionRequest(BaseModel):
    session_id: str
    question: str


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "EDA Agent API",
    }


# --------------------------------------------------
# List DuckDB Tables
# --------------------------------------------------

@app.get("/tables")
def list_tables():
    """
    Return all tables available in DuckDB.
    """

    tables = get_duckdb_tables()

    return {
        "tables": tables
    }


# --------------------------------------------------
# Get Table Schema
# --------------------------------------------------

@app.get("/schema/{table_name}")
def get_schema(table_name: str):
    """
    Return the schema of a DuckDB table.
    """

    schema = get_table_schema(table_name)

    return {
        "table_name": table_name,
        "schema": schema
    }


# --------------------------------------------------
# Execute Read-Only SQL Query
# --------------------------------------------------

@app.post("/query")
def run_query(query: str):
    """
    Execute a read-only SQL query against DuckDB.
    """

    query = query.strip()

    allowed = (
        query.upper().startswith("SELECT")
        or query.upper().startswith("WITH")
    )

    if not allowed:
        return {
            "error": "Only SELECT and WITH queries are allowed."
        }

    return execute_query(query)


# --------------------------------------------------
# Ask EDA Agent
# --------------------------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):
    """
    Send a natural-language question to the EDA agent.
    """

    try:

        agent = get_eda_agent()

        # Get conversation history for this session
        conversation = get_conversation(
            request.session_id
        )

        # Add the current user question
        conversation.append({
            "role": "user",
            "content": request.question
        })

        # Send the complete conversation to the agent
        response = agent.invoke({
            "messages": conversation
        })

        # Save the updated conversation history
        save_conversation(
            request.session_id,
            response["messages"]
        )

        # Convert raw agent response into
        # application-friendly structured output
        result = extract_agent_response(response)

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(error)}"
        )

# --------------------------------------------------
# Upload CSV / Excel Dataset
# --------------------------------------------------

@app.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...)
):
    """
    Upload a CSV or Excel file.

    The uploaded file is saved temporarily,
    ingested into PostgreSQL,
    and synchronized into DuckDB.
    """

    filename = file.filename or ""

    allowed_extensions = (
        ".csv",
        ".xlsx",
        ".xls"
    )

    if not filename.lower().endswith(
        allowed_extensions
    ):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and Excel files are supported."
        )

    table_name = os.path.splitext(filename)[0]

    table_name = (
        table_name
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )

    try:

        file_content = await file.read()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(filename)[1]
        ) as temp_file:

            temp_file.write(file_content)
            temp_file_path = temp_file.name

        from database.csv_loader import ingest_file

        ingest_file(
            temp_file_path,
            table_name
        )

        return {
            "status": "success",
            "message": "Dataset uploaded successfully.",
            "filename": filename,
            "table_name": table_name
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Dataset ingestion failed: {str(error)}"
        )

    finally:

        if "temp_file_path" in locals() and os.path.exists(
            temp_file_path
        ):
            os.remove(temp_file_path)