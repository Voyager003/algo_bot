from slack_bolt import App
from datetime import datetime

from .data_management import handle_user_csv, get_user_submissions
from .utils import get_motivational_message, calculate_streak

def register_handlers(app: App):

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

    @app.command("/알고조회")
    def search_algo(ack, body, client):
        ack()

        user_id = body["user_id"]
        user_info = client.users_info(user=user_id)
        user_name = user_info["user"]["real_name"]

        submissions = get_user_submissions(user_id)

        if not submissions:
            client.chat_postMessage(
                channel=body["channel_id"],
                text=f"{user_name}님, 아직 제출하신 문제가 없습니다! 첫 문제에 도전해보세요."
            )
            return

        streak, max_streak = calculate_streak(submissions)
        motivational_message = get_motivational_message(streak)

        message = f"""
>>> *{user_name}님의 알고리즘 스트릭*
{streak}일 연속으로 문제를 풀었습니다!
{motivational_message}
지금까지 풀었던 문제: {len(submissions)}문제입니다.
"""

        client.chat_postMessage(
            channel=body["channel_id"],
            text=message
        )