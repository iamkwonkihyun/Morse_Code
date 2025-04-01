import asyncio
import websockets

BASE_URL = "ws://ec2-3-37-123-222.ap-northeast-2.compute.amazonaws.com:8000/morse_code"

async def websocket():
    async with websockets.connect(BASE_URL) as websocket:
        while True:
            response = await websocket.recv()  # 서버 응답 받기
            print(response)

asyncio.run(websocket())
