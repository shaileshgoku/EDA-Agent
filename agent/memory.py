"""
Conversation memory for EDA Agent sessions.

Each session_id has its own conversation history.
"""

conversation_store = {}


def get_conversation(session_id):
    """
    Return the conversation history for a session.

    If the session does not exist yet,
    create an empty conversation.
    """

    if session_id not in conversation_store:
        conversation_store[session_id] = []

    return conversation_store[session_id]


def save_message(session_id, message):
    """
    Save one message to a session's conversation history.
    """

    conversation = get_conversation(session_id)

    conversation.append(message)

def save_conversation(session_id, conversation):
    """
    Save the complete conversation history for a session.
    """

    conversation_store[session_id] = conversation


def clear_conversation(session_id):
    """
    Clear the conversation history for a session.
    """

    if session_id in conversation_store:
        del conversation_store[session_id]


