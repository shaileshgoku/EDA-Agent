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