import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from app.ai.providers.gemini import client
from google.genai import types
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database import get_db

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
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
            mode=types.FunctionCallingConfigMode.AUTO,
            allowed_function_names=ALLOWED_INVENTORY_TOOLS,
        )
    )


async def chat(prompt: str, db: Session = Depends(get_db)):

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[session],
                    system_instruction=SYSTEM_PROMPT,
                    tool_config=build_tool_config(),
                ),
            )

            return response.text
