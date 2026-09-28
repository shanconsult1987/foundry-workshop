import json
import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

from tools import (
    get_request,
    search_requests,
    get_summary,
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
MODEL = os.environ["FOUNDRY_MODEL"]


# --------------------------------------------------
# Azure authentication
# --------------------------------------------------

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default",
)


# --------------------------------------------------
# OpenAI client
# --------------------------------------------------

client = OpenAI(
    base_url=PROJECT_ENDPOINT.rstrip("/") + "/openai/v1",
    api_key=token_provider,
)


# --------------------------------------------------
# System instructions
# --------------------------------------------------

SYSTEM_INSTRUCTIONS = """
You are a Citizen Service Assistant.

Your job is to help users understand citizen service requests.

Rules:

1. Use tools when factual request information is required.
2. Never invent request information.
3. If a request ID is provided, use the get_request tool.
4. If the user asks about a category, use the search_requests tool.
5. If the user asks for overall statistics, use the get_summary tool.
6. The application is read-only.
7. Never claim that a request was modified.
8. If information is unavailable, clearly say so.
9. Keep responses concise and professional.
"""


# --------------------------------------------------
# Tool definitions
# --------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_request",
            "description": "Retrieve a citizen service request by request ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "The citizen service request ID."
                    }
                },
                "required": ["request_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_requests",
            "description": "Find citizen service requests by category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The request category."
                    }
                },
                "required": ["category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Get overall citizen service request statistics.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# --------------------------------------------------
# Tool execution
# --------------------------------------------------

def execute_tool(name, arguments):

    if name == "get_request":
        return get_request(**arguments)

    if name == "search_requests":
        return search_requests(**arguments)

    if name == "get_summary":
        return get_summary()

    return {
        "error": f"Unknown tool: {name}"
    }


# --------------------------------------------------
# AI application
# --------------------------------------------------

def ask_agent(user_message: str):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_INSTRUCTIONS
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    message = response.choices[0].message

    # No tool required
    if not message.tool_calls:
        return message.content

    messages.append(message)

    # Execute requested tools
    for tool_call in message.tool_calls:

        tool_name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments
        )

        result = execute_tool(
            tool_name,
            arguments
        )

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            }
        )

    # Ask the model to generate the final answer
    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    return final_response.choices[0].message.content


# --------------------------------------------------
# Command-line application
# --------------------------------------------------

def main():

    print()
    print("======================================")
    print(" Citizen Service Assistant")
    print(" GPT-5 + Microsoft Foundry")
    print("======================================")
    print()
    print("Type 'exit' to quit.")
    print()

    while True:

        question = input("You: ")

        if question.lower() == "exit":
            break

        try:

            answer = ask_agent(question)

            print()
            print("Assistant:")
            print(answer)
            print()

        except Exception as error:

            print()
            print("Application error:")
            print(error)
            print()


if __name__ == "__main__":
    main()