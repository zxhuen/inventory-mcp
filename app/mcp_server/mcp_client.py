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

SYSTEM_PROMPT = Path(
    "inventory-mcp/app/mcp_server/prompts/inventory_assistant.md"
).read_text(encoding="utf-8")


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
                ),
            )

            return response.text
