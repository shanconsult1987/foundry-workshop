import json
import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

from tools import (
    get_request,
    search_requests,
    get_summary,
    WEB_SEARCH_TOOL,
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
# Instructions
# --------------------------------------------------

SYSTEM_INSTRUCTIONS = """
You are a Citizen Service Assistant.

You have access to two types of tools:

1. Local citizen-service tools
2. Web search

Use the local tools when the user asks about
citizen service requests.

Use web search when the user asks for current,
recent, or publicly available information.

Rules:

- Never invent citizen request information.
- Use get_request when a request ID is provided.
- Use search_requests for category searches.
- Use get_summary for overall statistics.
- Use web search for current information.
- Clearly distinguish local application data from
  information found on the web.
- The application is read-only.
- Never claim that a citizen request was modified.
- Keep answers concise and professional.
"""


# --------------------------------------------------
# Local function tools
# --------------------------------------------------

LOCAL_TOOLS = [
    {
        "type": "function",
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
    },
    {
        "type": "function",
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
    },
    {
        "type": "function",
        "name": "get_summary",
        "description": "Get overall citizen service request statistics.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


# --------------------------------------------------
# Execute local tools
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
# Ask GPT-5
# --------------------------------------------------

def ask_agent(user_message: str):

    response = client.responses.create(
        model=MODEL,

        instructions=SYSTEM_INSTRUCTIONS,

        input=user_message,

        tools=[
            *LOCAL_TOOLS,
            WEB_SEARCH_TOOL,
        ],
    )

    # Process local function calls
    while True:

        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            break

        tool_outputs = []

        for call in function_calls:

            arguments = json.loads(
                call.arguments
            )

            result = execute_tool(
                call.name,
                arguments
            )

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result)
                }
            )

        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_INSTRUCTIONS,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=[
                *LOCAL_TOOLS,
                WEB_SEARCH_TOOL,
            ],
        )

    return response.output_text


# --------------------------------------------------
# Main application
# --------------------------------------------------

def main():

    print()
    print("======================================")
    print(" Citizen Service Assistant")
    print(" GPT-5 + Microsoft Foundry")
    print(" Local Tools + Web Search")
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