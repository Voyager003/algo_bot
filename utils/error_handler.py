from utils.slack_util import send_private_message

def print_error(body, client, message: str):
    send_private_message(body, client, message)