import os

from slack_bolt.adapter.socket_mode import SocketModeHandler
from app import app
from initializer import initialize_handlers, initialize_directories

initialize_directories()
initialize_handlers(app)

if not os.path.exists('tokens'):
    os.makedirs('tokens')

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()