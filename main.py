import os
import csv

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(verbose=True)

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.command("/알고풀이")
def submit_algo(ack, body, client):
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

def handle_user_csv(user_id, user_name, link, created_at):
    # Data 디렉토리 생성 (없는 경우)
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)

    # 사용자 이름으로 된 CSV 파일 경로 생성
    csv_filename = os.path.join(data_dir, f"{user_name}.csv")

    # CSV 파일이 존재하지 않으면 헤더와 함께 새로 생성
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "user_name",
                "link",
                "created_at",
            ])

    # 사용자 데이터 추가
    with open(csv_filename, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            user_name,
            link,
            created_at,
        ])

@app.view("submit_view")
def handle_view_algo(ack, body, client):
    channel_id = body["view"]["private_metadata"]
    if channel_id != "C081J5M7UUC":
        ack(
            response_action="errors",
            errors={"code_block_id": "#오늘도한문제풀어또 채널에서만 제출할 수 있습니다."},
        )
        return None
    ack()

    # 데이터 추출
    user_id = body["user"]["id"]
    user_info = client.users_info(user=user_id)
    user_name = user_info["user"]["real_name"]
    link = body["view"]["state"]["values"]["link_block_id"]["input_action_id"]["value"]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    handle_user_csv(user_id, user_name, link, created_at)
    # 완료메시지 가공 및 슬랙으로 전송
    text = f">>> *{user_name}*님이 문제를 제출했습니다!"
    client.chat_postMessage(channel=channel_id, text=text)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
