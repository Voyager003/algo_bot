import os

from slack_bolt.adapter.socket_mode import SocketModeHandler
from app import app

if not os.path.exists('tokens'):
    os.makedirs('tokens')

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()