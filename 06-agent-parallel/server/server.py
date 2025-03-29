import asyncio
from datetime import datetime
from mcp import Message, serve

TOOL = Message(type="tool.callable", content={
    "name": "get_time",
    "description": "Returns the current time",
    "parameters": {"type": "object", "properties": {}}
})

async def on_open(send):
    await send(TOOL)

async def on_receive(msg, send):
    if msg.type == "tool.invoke" and msg.content["name"] == "get_time":
        now = datetime.now().strftime("%H:%M:%S")
        await send(Message(
            type="tool.response",
            content={"output": f"The time is {now}"},
            ref=msg.ref
        ))

async def main():
    await serve(on_open=on_open, on_receive=on_receive)

if __name__ == "__main__":
    asyncio.run(main())
