import re
import datetime

from configs import CHANNEL_ID
from utils.directory_util import normalize_directory_name
from utils.status_util import save_streak_data
from utils.github_util import create_and_merge_pr
from utils.error_handler import print_error
from utils.slack_util import send_public_message

def normalize_filename(name, timestamp):
    print(f"[DEBUG] 파일명 정규화 시작: {name}, {timestamp}")
    number = re.search(r'\d+', name)
    if number:
        safe_name = f"prob{number.group()}"
    else:
        safe_name = f"prob{hash(name) % 10000:04d}"

    result = f"{safe_name}_{timestamp}"
    print(f"[DEBUG] 정규화된 파일명: {result}")
    return result

def get_timestamp():
    now = datetime.datetime.now()
    timestamp = f"{now.hour:02d}{now.minute:02d}"
    print(f"[DEBUG] 타임스탬프 생성: {timestamp}")
    return timestamp

def handle_submission(body, view, client, needs_review):
    try:
        print("[DEBUG] 1. 제출 처리 시작")
        values = view["state"]["values"]

        print("[DEBUG] 2. 입력값 추출 시작")
        raw_directory = values["directory_name"]["directory_input"]["value"]
        directory = normalize_directory_name(raw_directory)
        problem_name = values["problem_name"]["problem_input"]["value"]
        problem_link = values["problem_link"]["link_input"]["value"]
        language = values["language"]["language_select"]["selected_option"]["value"]
        solution_process = values["solution_process"]["process_input"]["value"]
        code = values["code"]["code_input"]["value"]
        review_request = values.get("review_request", {}).get("request_input", {}).get("value", "")
        print(f"[DEBUG] 3. 기본 입력값 추출 완료 - 문제: {problem_name}, 언어: {language}")

        raw_comment = values.get("submission_comment", {}).get("comment_input", {}).get("value")
        submission_comment = "오늘도 알고리즘 문제를 풀었습니다! 👋" if not raw_comment or not raw_comment.strip() else raw_comment
        print("[DEBUG] 4. 코멘트 처리 완료")

        print("[DEBUG] 5. 스트릭 데이터 저장 시작")
        streak_data = save_streak_data(
            user_id=body["user"]["id"],
            user_name=body["user"]["username"],
            problem_link=problem_link,
            code=code
        )
        print("[DEBUG] 6. 스트릭 데이터 저장 완료")

        print("[DEBUG] 7. 파일명 생성 시작")
        timestamp = get_timestamp()
        normalized_problem_name = normalize_filename(problem_name, timestamp)
        print(f"[DEBUG] 8. 최종 파일명: {normalized_problem_name}")

        print("[DEBUG] 9. PR 본문 생성 시작")
        pr_body = f"""문제: [{problem_name}]({problem_link})\n언어: {language}\n"""

        if solution_process:
            pr_body += f"\n## 풀이 과정\n{solution_process}"

        if needs_review and review_request:
            pr_body += f"\n## 리뷰 요청 사항\n{review_request}"
        print("[DEBUG] 10. PR 본문 생성 완료")

        print("[DEBUG] 11. PR 생성 시작")
        pr_result = create_and_merge_pr(
            body,
            normalized_problem_name,
            language,
            pr_body,
            needs_review,
            directory,
            solution_process,
            submission_comment,
            code
        )
        compare_url = pr_result['pr_url']
        file_url = pr_result['file_url']
        print(f"[DEBUG] 12. PR URL 생성 완료 - URL: {compare_url}")

        print("[DEBUG] 13. 슬랙 메시지 생성 시작")
        problem_md_link = f"<{problem_link}|{problem_name}>"

        main_message = [
            f"<@{body['user']['id']}> 님이 오늘의 풀이를 공유해주셨어요. ({file_url})",
            f"[{language}] {problem_md_link}",
            f":speech_balloon: \"{submission_comment}\""
        ]

        if needs_review:
            main_message.append(f":white_check_mark: 리뷰도 함께 부탁하셨어요! PR을 생성하려면 다음 링크를 클릭해주세요: {compare_url}")
            print("[DEBUG] 14. 리뷰 요청 메시지와 PR 링크 추가됨")
        else:
            # 리뷰가 필요 없는 경우에도 PR 생성 링크는 제공
            main_message.append(f"PR을 생성하려면 다음 링크를 클릭해주세요: {compare_url}")
            print("[DEBUG] 14. PR 생성 링크 추가됨")

        print("[DEBUG] 15. 슬랙 메시지 전송 시작")
        send_public_message(
            client=client,
            channel=CHANNEL_ID,
            message="\n".join(main_message)
        )
        print("[DEBUG] 16. 슬랙 메시지 전송 완료")

    except Exception as e:
        print(f"[DEBUG] Error: 제출 처리 중 오류 발생: {str(e)}")
        message_body = {
            'channel_id': CHANNEL_ID,
            'user_id': body['user']['id']
        }
        print_error(message_body, client, f"❌ 오류가 발생했습니다: {str(e)}")