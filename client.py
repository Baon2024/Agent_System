





# client for sending messages to agent websocket
import websockets
import asyncio
import time

async def main():
    async with websockets.connect("ws://localhost:3013") as ws:
        print("connected")

        await ws.send("hello from Python")

        await ws.send("user_message: search to find Tottenham Hotspur's premier league position")

        await asyncio.sleep(1)

        await ws.send("user_message: wait, no, I meant search Arsenal's premier league position")

        # add message to trigger test run

        async for message in ws:
            print("received:", message)

asyncio.run(main())