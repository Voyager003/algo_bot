from configs import CHANNEL_ID
from utils.directory_util import normalize_directory_name
from utils.status_util import save_streak_data
from utils.github_util import create_and_merge_pr
from utils.error_handler import print_error
from utils.slack_util import send_public_message

def handle_submission(body, view, client, needs_review):
    try:
        values = view["state"]["values"]

        raw_directory = values["directory_name"]["directory_input"]["value"]
        directory = normalize_directory_name(raw_directory)
        problem_name = values["problem_name"]["problem_input"]["value"]
        problem_link = values["problem_link"]["link_input"]["value"]
        language = values["language"]["language_select"]["selected_option"]["value"]
        solution_process = values["solution_process"]["process_input"]["value"]
        code = values["code"]["code_input"]["value"]
        review_request = values.get("review_request", {}).get("request_input", {}).get("value", "")

        # 제출 코멘트 - 비어있으면 default
        raw_comment = values.get("submission_comment", {}).get("comment_input", {}).get("value")
        submission_comment = "오늘도 알고리즘 문제를 풀었습니다! 👋" if not raw_comment or not raw_comment.strip() else raw_comment

        streak_data = save_streak_data(
            user_id=body["user"]["id"],
            user_name=body["user"]["username"],
            problem_link=problem_link,
            code=code
        )

        # PR 본문 생성
        pr_body = f"""문제: [{problem_name}]({problem_link})\n언어: {language}\n"""

        if solution_process:
            pr_body += f"\n## 풀이 과정\n{solution_process}"

        if needs_review and review_request:
            pr_body += f"\n## 리뷰 요청 사항\n{review_request}"

        pr = create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process, submission_comment, code)

        # 기본 메시지 구성
        base_message = f"<@{body['user']['id']}> 님이 오늘의 풀이를 공유해주셨어요\n[{language}] {problem_name}\n:speech_balloon: \"{submission_comment}\""

        if needs_review:
            pr_url = pr.html_url.replace("https://", "")
            send_public_message(
                client=client,
                channel=CHANNEL_ID,
                message=f"{base_message}\n:white_check_mark: 리뷰도 함께 부탁하셨어요! ({pr_url})"
            )
        else:
            send_public_message(
                client=client,
                channel=CHANNEL_ID,
                message=base_message
            )

    except Exception as e:
        message_body = {
            'channel_id': CHANNEL_ID,
            'user_id': body['user']['id']
        }
        print_error(message_body, client, f"❌ 오류가 발생했습니다: {str(e)}")