import json
from channels.generic.websocket import AsyncWebsocketConsumer


class HeartRateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("bpm_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("bpm_group", self.channel_name)

    async def receive(self, text_data):
        pass  # frontend ne mora slati ništa

    async def send_bpm(self, event):
        await self.send(text_data=json.dumps({
            'device_id': event['device_id'],
            'bpm': event['bpm'],
            'timestamp': event['timestamp'],
        }))