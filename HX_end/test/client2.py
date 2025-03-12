import asyncio
import websockets

async def keep_alive(websocket):
    # 每30秒发送一次心跳
    while True:
        await websocket.send("Ping")
        await asyncio.sleep(30)

async def client(websocket, name):
    try:
        await websocket.send(f"Hello Server, this is {name}")
        while True:
            message = await websocket.recv()
            print(f"Received from server: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection with server closed")

async def main():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # 在后台启动心跳任务
        asyncio.get_event_loop().create_task(keep_alive(websocket))
        await client(websocket, "Client2")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())