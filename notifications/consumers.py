import json
from urllib import request
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User
from accounts.utils import get_model
from batch.models import Batch
from institute.models import Institute
from .models import ActiveUser


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

        await self.channel_layer.group_send(self.group_name, {"type": event_type, "message": ""})

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
        self.batch_code = self.scope['url_route']['kwargs']['batch_code']

        self.group_name = 'batchcode_'+self.batch_code  # Each Institute
        perm_to_connect = await self.has_perm_to_connect(self.batch_code)

        if(perm_to_connect):
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            self.close()

    @database_sync_to_async
    def has_perm_to_connect(self, batch_code):
        batch = get_model(Batch, batch_code=batch_code)
        user_role = self.user.role.lower()
        user = self.user

        if(batch["exist"]):
            batch = batch["data"]
            if(user_role == "teacher"):
                if(batch.teacher == user):
                    return True
                return False

            elif(user_role == "student"):
                student_exist = Batch.objects.filter(
                    batch_code=batch_code, students__in=[user]).exists()

                if(student_exist):
                    return True
                return False

            return False
        else:
            return False


class UserToUserRealTime(AsyncJsonWebsocketConsumer):
    async def connect(self):

        self.user = self.scope["user"]
        # Adding User to Channel
        await self.add_user()
        await self.accept()

        self.close()

    async def disconnect(self, code):
        await self.remove_user()
        await self.disconnect(code=code)

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        print(text_data)

    @database_sync_to_async
    def get_user_channel(self, to_user_id):
        to_user = get_model(User, id=int(to_user_id))
        if(not to_user["exist"]):
            return False, "The User Does Not Exist"

        user = self.user
        to_user = to_user['data']
        user_role = self.user.role.lower()
        to_user_role = to_user.role.lower()

        # if(user_role=="student" and to_user_role=="student"):
        #     return False,"You can't talk to student "

        active_to_user = ActiveUser.objects.filter(user__id=int(to_user_id))
        return active_to_user.channel_name, active_to_user.user

    @database_sync_to_async
    def add_user(self):
        self.clean_user()
        ActiveUser.objects.create(
            user=self.user, channel_name=self.channel_name)

    @database_sync_to_async
    def remove_user(self):
        self.clean_user()
