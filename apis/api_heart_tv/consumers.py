import json
from django.utils import timezone
import jwt
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from django.conf import settings
from django.db import connection
from gym.models import GymTenant
import time

from training_session.models import TrainingSession

User = get_user_model()


class CoachPreviewConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_name = None
        self.user = None

    # async def connect(self):
    #     self.group_name = "bpm_group"
    #     await self.channel_layer.group_add("bpm_group", self.channel_name)
    #     await self.accept()

    async def connect(self):
        print(time.time(), "start connect")
        query_string = self.scope["query_string"].decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]

        if not token:
            await self.close()
            return

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            print(time.time(), "after jwt")
            self.user_id = payload.get("user_id")

            tenant_id = payload.get("tenant_id")
            tenant = await sync_to_async(GymTenant.objects.get)(id=tenant_id)

            def load_user():
                from django_tenants.utils import tenant_context
                with tenant_context(tenant):
                    return User.objects.select_related("coach__gym").get(id=self.user_id)

            self.user = await sync_to_async(load_user)()
            print(time.time(), "after user")
            if not self.user.coach:
                await self.close(code=4003)
                return

            self.group_name = f"coach_preview_{self.user.coach.gym.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            print(time.time(), "before accept")
            await self.accept()

        except jwt.ExpiredSignatureError:
            await self.close(code=4001)
        except jwt.InvalidTokenError:
            await self.close(code=4002)

    async def disconnect(self, close_code):
        print(f"WS disconnected, code: {close_code}")
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        # await self.channel_layer.group_discard("bpm_group", self.channel_name)

    async def receive(self, text_data):
        pass  # nije potrebno slati sa fronta ništa

    async def send_bpm(self, event):
        await self.send(text_data=json.dumps({
            "current_calories": event["current_calories"],
            "client_id": event["client_id"],
            "bpm": event["bpm"],
        }))

    async def receive(self, text_data):
        pass

    def calculate_calories_from_bpm(self, bpm, user):
        weight = user.weight or 70  # kg
        age = user.age or 30  # godine
        gender = user.gender  # npr. "M" ili "F"

        if gender == "M":
            calories = (age * 0.2017 - weight * 0.09036 + bpm * 0.6309 - 55.0969) * 1 / 4.184
        else:
            calories = (age * 0.074 - weight * 0.05741 + bpm * 0.4472 - 20.4022) * 1 / 4.184

        return round(max(calories, 0), 2)

    @staticmethod
    async def get_user(user_id):
        try:
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            return None

    async def get_schema_from_tenant_id(self, tenant_id: int) -> str:
        """
        Vrati schema_name za dati tenant_id.
        """
        try:
            tenant = await sync_to_async(GymTenant.objects.get)(id=tenant_id)
            return tenant.schema_name  # ili field koji čuva ime schema
        except GymTenant.DoesNotExist:
            raise ValueError(f"Tenant sa id {tenant_id} ne postoji")

    @database_sync_to_async
    def set_current_schema(self, schema_name: str):
        with connection.cursor() as cursor:
            cursor.execute(f'SET search_path TO "{schema_name}"')


class GymConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_name = None
        self.user = None

    async def connect(self):
        query_string = self.scope["query_string"].decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]

        if not token:
            await self.close()
            return

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            self.user_id = payload.get("user_id")

            tenant_id = payload.get("tenant_id")
            tenant = await sync_to_async(GymTenant.objects.get)(id=tenant_id)

            def load_user():
                from django_tenants.utils import tenant_context
                with tenant_context(tenant):
                    return User.objects.select_related("coach__gym").get(id=self.user_id)

            self.user = await sync_to_async(load_user)()
            if not self.user.coach:
                await self.close(code=4003)
                return

            self.group_name = f"gym_{self.user.coach.gym.id}"
            print(self.group_name, "GROUP NAME")
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            """
            We are used to send seconds through websockets, but that is not good practice.
            So now in LiveTV we are using time when Training session is started and based on that 
            calculating time spent in training session.
            Down below is function when we first start session on CoachPreview, than after that we open LiveTV tab
            it pull all the active training session and their start data.
            If CoachPreview and LiveTV are opened in same time, we dont need this.
            """
            def load_sessions():
                from django_tenants.utils import tenant_context
                with tenant_context(tenant):
                    now = timezone.now()
                    twenty_four_hours_ago = now - timezone.timedelta(hours=24)

                    training_sessions = TrainingSession.objects.filter(
                        is_active=True,
                        start__gte=twenty_four_hours_ago,
                        start__lte=now,
                    ).select_related("client")

                    return [
                        {
                            "event": "initial",
                            "client_name": training_session.client.name,
                            "client_id": training_session.client.id,
                            "started_at": training_session.start.isoformat(),
                            "max_heart_rate": training_session.client.max_heart_rate_value
                        }
                        for training_session in training_sessions
                    ]

            sessions = await sync_to_async(load_sessions)()

            for session in sessions:
                await self.gym_data_initial(session)

        except jwt.ExpiredSignatureError:
            await self.close(code=4001)
        except jwt.InvalidTokenError:
            await self.close(code=4002)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Ovde LiveTV ne šalje ništa, samo sluša
        pass

    async def gym_data(self, event):
        """Handler za slanje podataka u grupu"""
        await self.send(text_data=json.dumps({
            "event": event.get("event"),
            "current_calories": event.get("current_calories"),
            "client_id": event.get("client_id"),
            "bpm": event.get("bpm"),
            "coach_id": event.get("coach_id"),
        }))

    async def gym_data_initial(self, event):
        await self.send(text_data=json.dumps({
            "event": "initial",
            "client_id": event.get("client_id"),
            "client_name": event.get("client_name"),
            "started_at": event.get("started_at"),
            "max_heart_rate": event.get("max_heart_rate"),
        }))
