import os
import csv

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv(verbose=True)

app = App(token=os.environ["SLACK_BOT_TOKEN"])

if not os.path.exists('tokens'):
    os.makedirs('tokens')

@app.command("/알고토큰")
def handle_token_command(ack, body, client):
    # 커맨드 접수 확인
    ack()

    user_name = body['user_name']
    csv_path = f'tokens/{user_name}.csv'

    # 이미 토큰이 존재하는지 확인
    if os.path.exists(csv_path):
        client.chat_postEphemeral(
            channel=body['channel_id'],
            user=body['user_id'],
            text="이미 등록된 토큰이 있습니다. 관리자에게 문의해주세요."
        )
        return

    try:
        client.views_open(
            trigger_id=body['trigger_id'],
            view={
                "type": "modal",
                "callback_id": "token_submission",
                "title": {
                    "type": "plain_text",
                    "text": "Github 토큰 등록"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "등록"
                },
                "close": {
                    "type": "plain_text",
                    "text": "취소"
                },
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Github 토큰을 입력해주세요."
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "token_block",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "token_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Github 토큰을 입력하세요"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Github 토큰"
                        }
                    }
                ]
            }
        )
    except Exception as e:
        client.chat_postEphemeral(
            channel=body['channel_id'],
            user=body['user_id'],
            text=f"Modal 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.view("token_submission")
def handle_token_submission(ack, body, view, client):
    ack()

    user_name = body['user']['username']
    token = view['state']['values']['token_block']['token_input']['value']
    csv_path = f'tokens/{user_name}.csv'

    try:
        with open(csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([user_name, token])

        # DM으로 성공 메시지 전송
        client.chat_postMessage(
            channel=body['user']['id'],
            text="Github 토큰이 성공적으로 등록되었습니다. 등록된 토큰은 보안상의 이유로 변경할 수 없습니다."
        )
    except Exception as e:
        client.chat_postMessage(
            channel=body['user']['id'],
            text=f"토큰 등록 중 오류가 발생했습니다: {str(e)}"
        )

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()