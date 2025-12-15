from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_message(user_id, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        str(user_id),
        {
            "type": "chat.message",
            "message": data,
        },
    )
