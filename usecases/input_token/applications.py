from app import app
import csv
import os
from utils.error_handler import print_error
from utils.slack_util import send_private_message
from usecases.input_token.modals import show_input_token_modal

def init_token_handlers(app):
    @app.command("/알고토큰")
    def handle_token_command(ack, body, client):
        ack()

        user_name = body['user_name']
        csv_path = f'tokens/{user_name}.csv'

        if os.path.exists(csv_path):
            print_error(body, client, "이미 등록된 토큰이 있습니다. 관리자에게 문의해주세요.")

            return

        try:
            show_input_token_modal(body, client, callback_id="token_submission")

        except Exception as e:
            print_error(body, client, f"Modal 생성 중 오류가 발생했습니다: {str(e)}")

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

            send_private_message(body, client, "✨ GitHub 토큰이 성공적으로 등록되었습니다!")

        except Exception as e:
            print_error(body, client, f"토큰 등록 중 오류가 발생했습니다: {str(e)}")