from configs import CHANNEL_ID
from utils.directory_util import normalize_directory_name
from utils.status_util import save_streak_data
from utils.github_util import create_and_merge_pr
from utils.error_handler import print_error
from utils.slack_util import send_public_message

def normalize_filename(name):
    return name.replace(" ", "").lower()

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

        raw_comment = values.get("submission_comment", {}).get("comment_input", {}).get("value")
        submission_comment = "오늘도 알고리즘 문제를 풀었습니다! 👋" if not raw_comment or not raw_comment.strip() else raw_comment

        streak_data = save_streak_data(
            user_id=body["user"]["id"],
            user_name=body["user"]["username"],
            problem_link=problem_link,
            code=code
        )

        normalized_problem_name = normalize_filename(problem_name)
        pr_body = f"""문제: [{problem_name}]({problem_link})\n언어: {language}\n"""

        if solution_process:
            pr_body += f"\n## 풀이 과정\n{solution_process}"

        if needs_review and review_request:
            pr_body += f"\n## 리뷰 요청 사항\n{review_request}"

        pr_result = create_and_merge_pr(body, normalized_problem_name, language, pr_body, needs_review, directory, solution_process, submission_comment, code)
        pr = pr_result['pr']
        file_url = pr_result['file_url'].replace("https://", "")
        pr_url = pr.html_url.replace("https://", "")

        problem_md_link = f"<{problem_link}|{problem_name}>"

        main_message = [
            f"<@{body['user']['id']}> 님이 오늘의 풀이를 공유해주셨어요. ({file_url})",
            f"[{language}] {problem_md_link}",
            f":speech_balloon: \"{submission_comment}\" ({pr_url})"
        ]

        if needs_review:
            main_message[-1] = f":speech_balloon: \"{submission_comment}\""
            main_message.append(f":white_check_mark: 리뷰도 함께 부탁하셨어요! ({pr_url})")

        send_public_message(
            client=client,
            channel=CHANNEL_ID,
            message="\n".join(main_message)
        )

    except Exception as e:
        message_body = {
            'channel_id': CHANNEL_ID,
            'user_id': body['user']['id']
        }
        print_error(message_body, client, f"❌ 오류가 발생했습니다: {str(e)}")