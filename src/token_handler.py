import os
import csv
from slack_bolt import App

def register_token_handlers(app: App):
    @app.command("/알고토큰")
    def submit_token(ack, body, client):
        ack()

        user_id = body["user_id"]
        user_info = client.users_info(user=user_id)
        user_name = user_info["user"]["real_name"]

        token_filename = os.path.join("tokens", f"{user_id}_token.csv")

        if os.path.exists(token_filename):
            client.chat_postMessage(
                channel=body["channel_id"],
                text=f">>> *{user_name}*님, 이미 토큰이 등록되어 있어 변경할 수 없습니다. 관리자에게 문의해주세요."
            )
            return

        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "submit_token_view",
                "private_metadata": body["channel_id"],
                "title": {"type": "plain_text", "text": "토큰 저장"},
                "submit": {"type": "plain_text", "text": "저장"},
                "close": {"type": "plain_text", "text": "취소"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "token_block_id",
                        "label": {
                            "type": "plain_text",
                            "text": "토큰 입력",
                        },
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "token_input_action_id",
                            "multiline": False,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "사용할 토큰을 입력해주세요.",
                            },
                        },
                    },
                ],
            },
        )

    @app.view("submit_token_view")
    def handle_token_submission(ack, body, client):
        channel_id = body["view"]["private_metadata"]
        if channel_id != "C081J5M7UUC":
            ack(
                response_action="errors",
                errors={"token_block_id": "#오늘도한문제풀어또 채널에서만 제출할 수 있습니다."},
            )
            return None

        ack()

        user_id = body["user"]["id"]
        user_info = client.users_info(user=user_id)
        user_name = user_info["user"]["real_name"]
        token = body["view"]["state"]["values"]["token_block_id"]["token_input_action_id"]["value"]

        os.makedirs("tokens", exist_ok=True)

        token_filename = os.path.join("tokens", f"{user_name}_token.csv")

        if os.path.exists(token_filename):
            client.chat_postMessage(
                channel=channel_id,
                text=f">>> *{user_name}*님, 이미 토큰이 등록되어 있어 변경할 수 없습니다. 관리자에게 문의해주세요."
            )
            return

        with open(token_filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["user_id", "user_name", "token"])
            writer.writerow([user_id, user_name, token])

        text = f">>> *{user_name}*님의 토큰이 성공적으로 저장되었습니다!"
        client.chat_postMessage(channel=channel_id, text=text)