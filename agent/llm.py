from langchain_openrouter import ChatOpenRouter

from config.settings import (
    OPENROUTER_API_KEY,
    MODEL_NAME,
)

def get_llm():
    """
    Create and return the OpenRouter LLM.
    """

    llm = ChatOpenRouter(
        model=MODEL_NAME,
        api_key=OPENROUTER_API_KEY,
        temperature=0,
    )

    return llm