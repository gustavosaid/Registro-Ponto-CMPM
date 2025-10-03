from channels.generic.websocket import AsyncWebsocketConsumer
import json


class CameraConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("✅ WebSocket conectado!")
        await self.send(text_data=json.dumps({"message": "WebSocket conectado!"}))

    async def disconnect(self, close_code):
        print("⚠️ WebSocket desconectado")
        await self.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"📩 Mensagem recebida: {data}")

        # Simula resposta ao frontend
        await self.send(text_data=json.dumps({"response": "Mensagem recebida"}))
