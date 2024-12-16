from configs import CHANNEL_ID
from utils.status_util import save_streak_data
from utils.github_util import create_and_merge_pr
from utils.error_handler import print_error
from utils.slack_util import send_public_message

def handle_submission(body, view, client, needs_review):
    try:
        # 입력값 추출
        values = view["state"]["values"]
        directory = values["directory_name"]["directory_input"]["value"]
        problem_name = values["problem_name"]["problem_input"]["value"]
        problem_link = values["problem_link"]["link_input"]["value"]
        language = values["language"]["language_select"]["selected_option"]["value"]
        solution_process = values["solution_process"]["process_input"]["value"]
        code = values["code"]["code_input"]["value"]
        review_request = values.get("review_request", {}).get("request_input", {}).get("value", "")
        submission_comment = values["submission_comment"]["comment_input"]["value"]

        streak_data = save_streak_data(
            user_id=body["user"]["id"],
            user_name=body["user"]["username"],
            problem_link=problem_link,
            code=code
        )

        message_body = {
            'channel_id': CHANNEL_ID,
            'user_id': body['user']['id']
        }

        # PR 본문 생성
        pr_body = f"""문제: [{problem_name}]({problem_link})\n언어: {language}\n"""

        if solution_process:
            pr_body += f"\n## 풀이 과정\n{solution_process}"

        if needs_review and review_request:
            pr_body += f"\n## 리뷰 요청 사항\n{review_request}"

        pr = create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process, submission_comment, code)

        text = f"<@{body['user']['id']}> 님이 오늘의 풀이를 공유해주셨어요"
        text += f"\n[{language}] {problem_name}"
        
        if submission_comment:
            text += f"\n:speech_balloon: \"{submission_comment}\""

        if needs_review:
            pr_url = pr.html_url.replace("https://", "")
            text += f"\n:white_check_mark: 리뷰도 함께 부탁하셨어요! ({pr_url})"

        send_public_message(
            client=client,
            channel=CHANNEL_ID,
            text=text,
        )

    except Exception as e:
        message_body = {
            'channel_id': CHANNEL_ID,
            'user_id': body['user']['id']
        }
        print_error(message_body, client, f"❌ 오류가 발생했습니다: {str(e)}")