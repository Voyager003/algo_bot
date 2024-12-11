import os
from slack_bolt import App
from dotenv import load_dotenv

load_dotenv(verbose=True)

app = App(token=os.environ["SLACK_BOT_TOKEN"])