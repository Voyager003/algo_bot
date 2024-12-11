import os
from app import app
import pandas as pd

from utils.error_handler import print_error
from utils.status_util import get_streak_message
from utils.slack_util import send_private_message

def init_status_handlers(app):
    @app.command("/알고조회")
    def view_streak(ack, body, client):
        ack()

        user_name = body["user_name"]
        csv_path = f'streak/{user_name}.csv'

        if not os.path.exists(csv_path):
            print_error(body, client, "아직 제출한 알고리즘 문제가 없습니다. 첫 문제를 풀어보세요! 💪")

            return

        try:
            df = pd.read_csv(csv_path)
            if df.empty:
                print_error(body, client, "아직 제출한 알고리즘 문제가 없습니다. 첫 문제를 풀어보세요! 💪")

                return

            message = get_streak_message(df)
            send_private_message(body, client, message)

        except Exception as e:
            print_error(body, client, f"❌ 조회 중 오류가 발생했습니다: {str(e)}")