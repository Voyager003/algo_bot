import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

from .handlers import register_handlers
from .token_handler import register_token_handlers  # 새로 추가

def create_app():
    load_dotenv(verbose=True)
    app = App(token=os.environ["SLACK_BOT_TOKEN"])
    register_handlers(app)
    register_token_handlers(app)
    return app

def start_bot():
    app = create_app()
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()