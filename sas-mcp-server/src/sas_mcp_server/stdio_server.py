#!/usr/bin/env python3
# Copyright © 2025, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Stdio MCP Server for SAS Viya.
Authenticates directly to Viya using password grant, allowing MCP clients
to start the server on demand without a pre-running HTTP server.
"""

import os
import time
import httpx
from dotenv import load_dotenv
from fastmcp import Context, FastMCP
from fastmcp.exceptions import FastMCPError
from .config import VIYA_ENDPOINT, CLIENT_ID, SSL_VERIFY
from .viya_utils import logger
from .tools import register_tools
from .prompts import register_prompts

load_dotenv()

VIYA_USERNAME = os.getenv("VIYA_USERNAME", "")
VIYA_PASSWORD = os.getenv("VIYA_PASSWORD", "")


class AuthenticationError(FastMCPError):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"AuthenticationError: {self.message}"


def _get_viya_token() -> str:
    """Return the access token. Token refreshing is handled dynamically by viya_utils._make_client."""
    token = os.getenv("VIYA_ACCESS_TOKEN")
    if not token:
        raise AuthenticationError("VIYA_ACCESS_TOKEN is not set. Please run auth_setup.py first!")
    return token

async def _stdio_get_token(ctx: Context) -> str:
    return _get_viya_token()


# Initialize the FastMCP server (no auth — stdio clients handle auth differently)
logger.info(f"Connecting to SAS Viya at {VIYA_ENDPOINT}")
mcp = FastMCP("SAS Viya Execution MCP Server")

# Register all tools and prompts
register_tools(mcp, _stdio_get_token)
register_prompts(mcp)


def run_heartbeat_loop():
    """Background thread to keep the Viya sessions alive and trigger token refreshes if idle."""
    import os
    if os.getenv("KEEP_ALIVE_HEARTBEAT", "true").lower() != "true":
        return
        
    import asyncio
    
    async def heartbeat():
        from .viya_utils import _make_client
        while True:
            await asyncio.sleep(300) # Ping every 5 minutes
            try:
                token = os.getenv("VIYA_ACCESS_TOKEN")
                if token:
                    # Using _make_client automatically triggers our 401 refresh logic if needed!
                    async with _make_client(token) as client:
                        resp = await client.get(f"{VIYA_ENDPOINT}/casManagement/servers")
                        logger.info("Background heartbeat sent successfully to keep session alive.")
            except Exception as e:
                logger.debug(f"Background heartbeat silent error: {e}")
                
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(heartbeat())


def main():
    """Run the MCP server in stdio mode with a keep-alive background thread."""
    import threading
    t = threading.Thread(target=run_heartbeat_loop, daemon=True)
    t.start()
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
