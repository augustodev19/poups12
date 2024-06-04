import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://127.0.0.1:8976/ws/pedidos/2/"
    async with websockets.connect(uri) as websocket:
        # Enviar uma mensagem JSON válida
        message = json.dumps({"message": "Hello, WebSocket!"})
        await websocket.send(message)
        
        # Receber a resposta
        response = await websocket.recv()
        print(response)

asyncio.run(test_websocket())