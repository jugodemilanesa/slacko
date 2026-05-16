import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for real-time chat with Slacko."""

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive_json(self, content: dict):
        message = content.get("message", "")

        # TODO: route through orchestrator
        await self.send_json(
            {
                "type": "message",
                "role": "assistant",
                "content": f"[Slacko] Recibido: {message}",
            }
        )
