from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

from gmail import GoogleMailAPI

mcp = FastMCP(name="gmail", host="127.0.0.1", port="8123")
# mcp = FastMCP("drive")

@mcp.tool()
def list_message(arg):
    """List the email in gmail account
    
    Args:
    """
    try:
        email = GoogleMailAPI()    
        return email.list_messages()
    except Exception as e:
        print("Error encountered in app.list_message: " + str(e))
        return str(e)

@mcp.tool()
def send_message(arg):
    """Send a message using my gmail account
    
    Args: an object with the following properties: recipient<string>, subject<string>, content<string>
    """
    try:
        
        print(arg["recipient"], arg["subject"], arg["content"])
        
        email = GoogleMailAPI()    
        email.send_message(recipient=arg["recipient"], subject=arg["subject"], content=arg["content"])
        
        return "" 
    except Exception as e:
        print("Error encountered in app.send_message: " + str(e))
        return str(e)

if __name__ == "__main__":
    # gmail = GoogleMailAPI()
    # gmail.send_message('liew.tp@grenapps.com.my', 'testing', 'testing content')
    # Initialize and run the server
    # mcp.run(transport='stdio')
    transport = "stdio"
    # transport = "sse"
    if transport == "stdio":
        print("Running server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Running server with SSE transport")
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Unknown transport: {transport}")