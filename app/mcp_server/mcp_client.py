import sys
from pathlib import Path

from fastapi import Depends
from sqlalchemy.orm import Session

from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.ai.providers.gemini import client
from app.core.database import get_db

server_params = StdioServerParameters(
    command=sys.executable,
    args=["-m", "app.mcp_server.server"],
    cwd=str(Path(__file__).resolve().parents[2]),
)


ALLOWED_INVENTORY_TOOLS = [
    "add_product",
    "list_products",
    "edit_product",
    "delete_product",
    "lookup_product_by_name",
]


SYSTEM_PROMPT = Path("app/mcp_server/prompts/inventory_assistant.md").read_text(
    encoding="utf-8"
)


def build_tool_config():
    return types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode=types.FunctionCallingConfigMode.ANY,
            allowed_function_names=ALLOWED_INVENTORY_TOOLS,
        )
    )


def convert_mcp_tools_to_gemini(mcp_tools):
    function_declarations = []

    for tool in mcp_tools:
        if tool.name not in ALLOWED_INVENTORY_TOOLS:
            continue

        function_declarations.append(
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description or "",
                parameters_json_schema=tool.inputSchema,
            )
        )

    return [types.Tool(function_declarations=function_declarations)]


def mcp_result_to_text(result):
    parts = []

    for content in result.content:
        if hasattr(content, "text"):
            parts.append(content.text)

    return "\n".join(parts)


async def chat(
    prompt: str,
    db: Session = Depends(get_db),
):
    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # 1. Initialize MCP connection
            await session.initialize()

            # 2. Get tools from the MCP server
            mcp_result = await session.list_tools()

            # 3. Convert MCP tools into Gemini tools
            gemini_tools = convert_mcp_tools_to_gemini(mcp_result.tools)

            # 4. Start the conversation
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                )
            ]

            # 5. Gemini <-> MCP tool-calling loop
            while True:

                response = await client.aio.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        tools=gemini_tools,
                        system_instruction=SYSTEM_PROMPT,
                        tool_config=build_tool_config(),
                    ),
                )

                # If Gemini has no tool call, we're done
                if not response.function_calls:
                    return response.text

                # Add Gemini's response to the conversation
                contents.append(response.candidates[0].content)

                # Execute every requested tool
                for function_call in response.function_calls:

                    tool_name = function_call.name
                    tool_args = function_call.args or {}

                    # Safety check
                    if tool_name not in ALLOWED_INVENTORY_TOOLS:
                        tool_result = {"error": f"Tool '{tool_name}' is not allowed."}

                    else:
                        try:
                            # Call the actual MCP tool
                            result = await session.call_tool(
                                tool_name,
                                arguments=tool_args,
                            )

                            tool_result = {"result": mcp_result_to_text(result)}

                        except Exception as e:
                            tool_result = {"error": str(e)}

                    # Send MCP result back to Gemini
                    contents.append(
                        types.Content(
                            role="tool",
                            parts=[
                                types.Part.from_function_response(
                                    name=tool_name,
                                    response=tool_result,
                                )
                            ],
                        )
                    )
