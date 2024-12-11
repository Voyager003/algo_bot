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
        # 먼저 ack를 호출
        ack()

        try:
            # tokens 디렉토리가 없으면 생성
            if not os.path.exists('tokens'):
                os.makedirs('tokens')

            user_name = body['user']['username']
            user_id = body['user']['id']  # DM용 채널 ID
            token = view['state']['values']['token_block']['token_input']['value']
            csv_path = f'tokens/{user_name}.csv'

            with open(csv_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([user_name, token])

            # body를 조작하여 send_private_message가 작동하도록 함
            message_body = {
                'channel_id': user_id,
                'user_id': user_id
            }
            send_private_message(message_body, client, "✨ GitHub 토큰이 성공적으로 등록되었습니다!")

        except Exception as e:
            try:
                message_body = {
                    'channel_id': user_id,
                    'user_id': user_id
                }
                send_private_message(message_body, client, f"❌ 토큰 등록 중 오류가 발생했습니다: {str(e)}")
            except:
                # 에러 로깅만 하고 진행
                print(f"Error sending message: {str(e)}")