import math
import requests
import signal
import sys
import logging
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Keep console output as well
    ]
)
logger = logging.getLogger(__name__)

mcp= FastMCP("Math")
# mcp.settings.port = 8002

@mcp.tool()
def add(a: int, b: int) -> int:
   logger.info(f"Server received add request: {a}, {b}")
   return a + b
@mcp.tool()
def multiply(a: int, b: int) -> int:
   logger.info(f"Server received multiply request: {a}, {b}")
   return a * b
@mcp.tool()
def sine(a: int) -> int:
   logger.info(f"Server received sine request: {a}")
   return math.sin(a)


def signal_handler(sig, frame):
   logger.info("Received interrupt signal. Shutting down gracefully...")
   sys.exit(0)


if __name__ =="__main__":
   # Set up signal handler for graceful shutdown
   signal.signal(signal.SIGINT, signal_handler)
   signal.signal(signal.SIGTERM, signal_handler)
   
   print("Starting MCP Server with SSE transport....")
   print("Server will be available at http://localhost:8002/sse")
   print("Press Ctrl+C to stop the server")
#    mcp.run(transport="sse")
   mcp.run(transport="stdio")