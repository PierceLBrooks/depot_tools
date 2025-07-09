import asyncio
from fastmcp import Client
from fastmcp.client.logging import LogMessage

async def log_handler(message: LogMessage):
    print(f"Server log: {message.data}")

# Local Python script
client = Client("server.py", log_handler=log_handler)

async def main():
    async with client:
        # Basic server interaction
        await client.ping()
        
        # List available operations
        tools = await client.list_tools()
        print(f'tools:{tools}')
        resources = await client.list_resources()
        print(f'resources:{resources}')
        prompts = await client.list_prompts()
        print(f'prompts: {prompts}')
        
        # Execute operations
        result = await client.call_tool("get_build", {"request": {"id": "8709987193266782721"}})
        print(result)
        result = await client.call_tool("try_results", {"checkout": "/usr/local/google/home/sshrimp/chromium-checkouts/chromium/src"})
        print(result)

asyncio.run(main())