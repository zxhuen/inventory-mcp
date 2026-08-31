import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from app.ai.providers.gemini import client
from google.genai import types

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)


async def chat(prompt: str):

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[session],
                ),
            )

            return response.text
