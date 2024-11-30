import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv(verbose=True)

app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Add middleware / listeners here

if __name__ == "__main__":
    # export SLACK_APP_TOKEN=xapp-***
    # export SLACK_BOT_TOKEN=xoxb-***
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()