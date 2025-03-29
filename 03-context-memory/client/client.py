import os
import asyncio
import json
import openai
from dotenv import load_dotenv
from mcp import Message, connect

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL", "gpt-4o")

async def main():
    tools = []

    async def on_receive(msg):
        nonlocal tools
        if msg.type == "tool.callable":
            tools.append(msg.content)
        elif msg.type == "tool.response":
            print("Tool Response:", msg.content)

    async def on_open(send):
        await asyncio.sleep(1)
        tool_spec = [{"type": "function", "function": t} for t in tools]
        user_input = input("What would you like the assistant to do? ")
        completion = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_input}],
            tools=tool_spec,
            tool_choice="auto"
        )
        for tool_call in completion.choices[0].message.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            await send(Message(
                type="tool.invoke",
                content={"name": name, "arguments": arguments},
                ref="abc123"
            ))

    await connect("ws://localhost:8000", on_open=on_open, on_receive=on_receive)

asyncio.run(main())
