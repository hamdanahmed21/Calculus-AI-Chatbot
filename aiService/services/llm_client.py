import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load .env file
load_dotenv("aiService/.env")

# Toggle between mock and OpenAI
USE_MOCK = True

# Create OpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


async def ask_mock(
    message: str,
    topic: str = "",
    history: list = None
):
    """
    Mock AI response for testing without OpenAI.
    """

    if history is None:
        history = []

    return f"""
Mock AI Response

Topic: {topic}

Question:
{message}

History Length:
{len(history)} messages

This is a placeholder response.
OpenAI integration will be used when USE_MOCK=False.
"""


async def ask_openai(
    message: str,
    topic: str = "",
    history: list = None
):
    """
    Send request to OpenAI.
    """

    if history is None:
        history = []

    messages = []

    # Previous conversation
    for item in history:

        messages.append(
            {
                "role": item["role"],
                "content": item["content"]
            }
        )

    # Current user message
    messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=1000
    )

    return response.choices[0].message.content


async def ask_llm(
    message: str,
    topic: str = "",
    history: list = None
):
    """
    Main function used by chatbot.py.
    Switches between mock and OpenAI.
    """

    if USE_MOCK:

        return await ask_mock(
            message,
            topic,
            history
        )

    return await ask_openai(
        message,
        topic,
        history
    )