import json
from channels.generic.websocket import AsyncWebsocketConsumer

# Async 方法
class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('mqtt_group', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('mqtt_group', self.channel_name)

    async def receive(self, text_data=None):
        await self.send(text_data)

    async def mqtt_msg_broadcast(self, event):
        await self.send(text_data=json.dumps(event))

