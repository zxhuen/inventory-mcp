from mcp.server.fastmcp import FastMCP
from mcp_server.tools.product_tools import register_product_tools

mcp = FastMCP("Inventory MCP")


@mcp.tool()
def hello():
    return "Hello from Inventory MCP"


register_product_tools(mcp)

if __name__ == "__main__":
    mcp.run()
