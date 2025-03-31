import asyncio
import websockets
from urllib.parse import urljoin

uri = "ws://localhost:8000/morse_code"

BASE_URL = "ws://localhost:8000/"
ENDPOINT_MORSE_CODE = "morse_code"
ENDPOINT_TOTAL_PEOPLE = "total_people"

async def test_websocket():
    async with websockets.connect(urljoin(BASE_URL, ENDPOINT_MORSE_CODE)) as websocket:
        print("✅ WebSocket 연결됨!")
        await websocket.send("Hello, Server!")  # 메시지 보내기
        while True:
            response = await websocket.recv()  # 서버 응답 받기
            print("📩 서버 응답:", response)

asyncio.run(test_websocket())
