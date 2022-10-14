import json
from urllib import request
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User
from accounts.utils import get_model
from batch.models import Batch
from institute.models import Institute


class InstituteNotifications(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.institute_code = self.scope['url_route']['kwargs']['institute_code']

        self.group_name = 'insitute_'+self.institute_code  # Each Institute
        perm_to_connect = await self.has_perm_to_connect()

        if(perm_to_connect):
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            self.close()

    async def disconnect(self):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        text_data_json = json.loads(text_data)
        event_type = text_data_json["event_type"]
        data = text_data_json["data"]
        user_role = await self.get_role()

        if(user_role != 'owner'):
            self.send(
                {"success": False,
                 "msg": None,
                 "error": "You are not owner"}
            )

        await self.channel_layer.group_send(self.group_name,)

    @database_sync_to_async
    def get_role(self):
        return self.user.role

    @database_sync_to_async
    def has_perm_to_connect(self, institute_code):
        institute = get_model(Institute, institute_code=institute_code)
        user_role = self.user.role.lower()
        user = self.user

        if(institute["exist"]):
            institute = institute["data"]
            if(user_role == "owner"):
                if(institute.owner == user):
                    return True
                return False

            elif(user_role == "student"):
                student_exist = Batch.objects.filter(
                    institute=institute, students__in=[user]).exists()

                if(student_exist):
                    return True
                return False

            elif(user_role == "teacher"):
                teacher_exist = Batch.objects.filter(
                    institute=institute, teacher=user).exists()

                if(teacher_exist):
                    return True
                return False

            return False
        else:
            return False


class BatchNotifications(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.institute_code = self.scope['url_route']['kwargs']['batch_code']

        self.group_name = 'insitute_'+self.institute_code  # Each Institute
        perm_to_connect = await self.has_perm_to_connect()

        if(perm_to_connect):
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            self.close()
