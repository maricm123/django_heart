import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
User = get_user_model()
import asyncio
import random
from datetime import datetime


class BPMConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("bpm_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("bpm_group", self.channel_name)

    async def receive(self, text_data):
        pass  # nije potrebno slati sa fronta ništa

    async def send_bpm(self, event):
        await self.send(text_data=json.dumps({
            "current_calories": event["current_calories"],
            "client_id": event["client_id"],
        }))

    async def receive(self, text_data):
        # ne koristiš trenutno, ali možeš ovde parsirati primljene poruke
        pass

    def calculate_calories_from_bpm(self, bpm, user):
        # 👇 Primer formule - prilagodi prema polu, visini, težini...
        weight = user.weight or 70  # kg
        age = user.age or 30  # godine
        gender = user.gender  # npr. "M" ili "F"

        # Primer kalkulacije (iz literature, prilagodi!)
        if gender == "M":
            calories = (age * 0.2017 - weight * 0.09036 + bpm * 0.6309 - 55.0969) * 1 / 4.184
        else:
            calories = (age * 0.074 - weight * 0.05741 + bpm * 0.4472 - 20.4022) * 1 / 4.184

        return round(max(calories, 0), 2)