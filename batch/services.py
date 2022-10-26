
from re import M
from tokenize import Triple
from accounts.utils import get_model
from batch.models import Batch, Blocked, Message
from accounts.models import User
from batch.serializers import MessageSerializer
from institute.services import get_insitute


# Check For Blocked MSGS
def is_blocked(sender, receiver):

    sender_blocked = Blocked.objects.filter(
        blocked_by=receiver, victim=sender).exists()

    if(sender_blocked):
        return {
            "blocked": True,
            "error": "You can't send msg to the user"
        }
    else:
        receiver_blocked = Blocked.objects.filter(
            blocked_by=sender, victim=receiver).exists()

        if(receiver_blocked):
            return {
                "blocked": True,
                "error": "Unblock The User First.."
            }
    return {
        "blocked": False,
    }

# Creates OR Sent Msg Personal


def create_msg(request, msg, reciever_id):
    user = request.user
    reciever_user = get_model(User, pk=int(reciever_id))
    is_reply = request.data.get("is_reply", None)
    parent_msg_id = request.data.get("parent_msg", None)

    if(not reciever_user['exist']):
        return {
            "success": False,
            "msg": None,
            "error": "There Is No Such User."
        }

    reciever_user = reciever_user["data"]

    user_type = user.role.lower()
    reciever_user_type = reciever_user.role.lower()

    # IF Communication is Std -> Std
    if(user_type == "student" and reciever_user_type == "student"):
        return {
            "success": False,
            "msg": None,
            "error": "You Can't Chat To Another Student..."
        }

    # Checking Blockage
    has_blocked = is_blocked(user, reciever_user)
    if(has_blocked["blocked"]):
        return {
            "success": False,
            "msg": None,
            "error": has_blocked["error"]
        }

    # Creating Msg
    message = Message(message=msg, sender=user, reciever=reciever_user)

    if(is_reply and parent_msg_id):
        parent_msg = get_model(Message, pk=int(parent_msg_id))
        if(parent_msg["exist"]):
            parent_msg = parent_msg["data"]
            message.parent_msg = parent_msg
            message.is_reply = True

            message.save()

    message.save()
    msg_data = MessageSerializer(message, many=False).data

    return {
        "success": True,
        "msg": msg_data
    }

# Check Permission Of Sending MSG


def has_msg_perm_batch(batch, user):
    user_type = user.role.lower()

    if(user_type == "owner"):
        if(user == batch.institute.owner):
            True
        return False

    if(user_type == "teacher"):
        if(batch.teacher == user):
            return True
        return False

    if(user_type == "student"):
        if user in batch.students.all():
            if(user not in batch.blacklist_students.all()):
                return True
            return False
        return False
    return False

# Creates MSG for Batch


def create_batch_msg(request, msg, batch_id):
    user = request.user
    batch = get_model(Batch, pk=int(batch_id))
    is_reply = request.data.get("is_reply", None)
    parent_msg_id = request.data.get("parent_msg", None)

    if(not batch['exist']):
        return {
            "success": False,
            "msg": None,
            "error": "There Is No Such Batch."
        }

    batch = batch["data"]

    if not has_msg_perm_batch(batch, user):
        return {
            "success": False,
            "error": "You are not authorized",
            "msg": None
        }

    message = Message(message=msg, sender=user, batch=batch)

    if(is_reply and parent_msg_id):
        parent_msg = get_model(Message, pk=int(parent_msg_id))
        if(parent_msg["exist"]):
            parent_msg = parent_msg["data"]
            message.parent_msg = parent_msg
            message.is_reply = True

            message.save()

    message.save()
    msg_data = MessageSerializer(message, many=False).data

    return {
        "success": True,
        "msg": msg_data
    }


# Retrieve MSGS
def get_convs(user):
    sent_msgs_recivers = Message.objects.filter(
        is_batch_msg=False, sender=user).values_list("receiver")
    received_msgs_senders = Message.objects.filter(
        is_batch_msg=False, receiver=user).values_list("sender")
