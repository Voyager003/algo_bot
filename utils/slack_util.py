from configs import CHANNEL_ID

def send_public_message(client, channel, message:str):
    client.chat_postMessage(
        channel,
        message,
    )

def send_private_message(body, client, message:str):
    client.chat_postEphemeral(
        channel=CHANNEL_ID,
        user=body['user_id'],
        text=message
    )

def show_modal(body, client, callback_id, title:str, submit_title:str, blocks, close_title:str = None):
    view = {
        "type": "modal",
        "callback_id": callback_id,
        "title": { "type": "plain_text", "text": title },
        "submit": { "type": "plain_text", "text": submit_title },
        "blocks": blocks
    }
    
    if close_title:
        view["close"] = { "type": "plain_text", "text": close_title }

    client.views_open(
        trigger_id=body['trigger_id'],
        view=view
    )