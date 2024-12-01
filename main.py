import os
import csv

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime, timedelta
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
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)

    csv_filename = os.path.join(data_dir, f"{user_id}.csv")

    # CSV 파일이 존재하지 않으면 헤더와 함께 새로 생성
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "user_id",
                "user_name",
                "link",
                "created_at",
            ])

    # 사용자 데이터 추가
    with open(csv_filename, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            user_id,
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

    user_id = body["user"]["id"]
    user_info = client.users_info(user=user_id)
    user_name = user_info["user"]["real_name"]
    link = body["view"]["state"]["values"]["link_block_id"]["input_action_id"]["value"]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    handle_user_csv(user_id, user_name, link, created_at)

    text = f">>> *{user_name}*님이 문제를 제출했습니다!"
    client.chat_postMessage(channel=channel_id, text=text)

def get_motivational_message(streak):
    if streak == 0:
        return "오늘부터 다시 시작해볼까요? 화이팅!"
    elif streak <= 3:
        return "조금씩 습관을 만들어가고 있어요. 계속 달려보세요!"
    elif streak <= 7:
        return "멋져요! 꾸준함이 쌓여가고 있네요. 그 열정 멈추지 마세요!"
    elif streak <= 14:
        return "와우! 정말 대단해요. 알고리즘 마스터를 향해 가고 있어요!"
    else:
        return "믿을 수 없네요! 여러분은 진정한 알고리즘 전사입니다!"

@app.command("/알고조회")
def search_algo(ack, body, client):
    ack()

    # 사용자 정보 가져오기
    user_id = body["user_id"]
    user_info = client.users_info(user=user_id)
    user_name = user_info["user"]["real_name"]

    # 사용자의 CSV 파일 경로
    csv_filename = os.path.join("data", f"{user_id}.csv")

    # CSV 파일이 없는 경우 처리
    if not os.path.exists(csv_filename):
        client.chat_postMessage(
            channel=body["channel_id"],
            text=f"{user_name}님, 아직 제출하신 문제가 없습니다! 첫 문제에 도전해보세요."
        )
        return

    # CSV 파일에서 제출 기록 읽기
    submissions = []
    with open(csv_filename, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            submissions.append(datetime.strptime(row['created_at'], "%Y-%m-%d %H:%M:%S").date())

    submissions = sorted(list(set(submissions)), reverse=True)

    streak = 0
    max_streak = 0

    if submissions:
        prev_date = submissions[0]

        for submission_date in submissions:
            if (prev_date - submission_date).days == 1:
                streak += 1
                max_streak = max(max_streak, streak)
            elif (prev_date - submission_date).days == 0:
                continue
            else:
                streak = 0
            prev_date = submission_date

    # 메시지 구성
    motivational_message = get_motivational_message(streak)
    message = f"""
>>> *{user_name}님의 알고리즘 스트릭*
{streak}일 연속으로 문제를 풀었습니다!
{motivational_message}
지금까지 풀었던 문제: {len(submissions)}문제입니다.
"""

    # 메시지 전송
    client.chat_postMessage(
        channel=body["channel_id"],
        text=message
    )

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
