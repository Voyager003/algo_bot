from configs import CHANNEL_ID
from utils.status_util import save_streak_data
from utils.github_util import create_and_merge_pr
from utils.error_handler import print_error

def handle_submission(body, view, client, needs_review):
    try:

        # 입력값 추출
        values = view["state"]["values"]
        directory = values["directory_name"]["directory_input"]["value"]
        problem_name = values["problem_name"]["problem_input"]["value"]
        problem_link = values["problem_link"]["link_input"]["value"]
        language = values["language"]["language_select"]["selected_option"]["value"]
        solution_process = values["solution_process"]["process_input"]["value"]
        code = values["code"]["code_input"]["value"]  # 코드 추출
        review_request = values.get("review_request", {}).get("request_input", {}).get("value", "")

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
        if needs_review:
            pr_body = f"""문제: [{problem_name}]({problem_link})
언어: {language}

## 풀이 과정
{solution_process}

## 리뷰 요청 사항
{review_request}
"""
        else:
            pr_body = f"""문제: [{problem_name}]({problem_link})
언어: {language}

## 풀이 과정
{solution_process}
"""
        pr = create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process, code)

        user_id = body['user']['id']

        if needs_review:
            client.chat_postMessage(
                channel=CHANNEL_ID,
                text=f"✨ 코드 리뷰 요청이 들어왔습니다!\n*<{pr.html_url}|[{language}] {problem_name}>*"
            )
        else:
            client.chat_postEphemeral(
                channel=CHANNEL_ID,
                user=user_id,
                text=f"✅ [{problem_name}] 문제가 제출되었습니다!"
            )

    except Exception as e:
        message_body = {
            'channel_id': CHANNEL_ID,
            'user_id': body['user']['id']
        }
        print_error(message_body, client, f"❌ 오류가 발생했습니다: {str(e)}")