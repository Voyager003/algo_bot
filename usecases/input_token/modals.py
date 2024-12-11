from utils.slack_util import show_modal

def show_input_token_modal(body ,client, callback_id):
    show_modal(
        body=body,
        client=client,
        callback_id=callback_id,
        title="Github 토큰 등록",
        submit_title="등록",
        blokcs=[
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
        ],
        close_title="취소")