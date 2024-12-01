import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv(verbose=True)

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.message("hi")
def say_hello(message, say):
    user = message['user']
    print(user)
    say(f"Hi there, <@{user}>!")

@app.command("/알고풀이")
def handle_some_command(ack, body, client):
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "submit_view",
            "private_metadata": body["channel_id"],
            "title": {"type": "plain_text", "text": "제출하기"},
            "submit": {"type": "plain_text", "text": "제출"},
            "close": {"type": "plain_text", "text": "취소"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "link_block_id",
                    "label": {
                        "type": "plain_text",
                        "text": "문제 링크(URL)",
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input_action_id",
                        "multiline": False,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "풀었던 알고리즘 문제의 주소(URL)을 입력해주세요.",
                        },
                    },
                },
                {
                    "type": "input",
                    "block_id": "address_block_id",
                    "label": {
                        "type": "plain_text",
                        "text": "문제 풀이",
                    },
                    "optional": True,
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input_action_id",
                        "multiline": False,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "문제의 풀이를 담은 블로그 주소를 입력해주세요.",
                        },
                    },
                },
                {
                    "type": "input",
                    "block_id": "code_block_id",
                    "label": {
                        "type": "plain_text",
                        "text": "코드",
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input_action_id",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "오늘 풀었던 알고리즘의 풀이 코드를 올려주세요.",
                        },
                    },
                },
            ],
        },
    )




if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()