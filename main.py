import os
import csv
import base64
import pandas as pd
import calendar

from datetime import datetime, timedelta
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from github import Github



load_dotenv(verbose=True)

app = App(token=os.environ["SLACK_BOT_TOKEN"])

if not os.path.exists('tokens'):
    os.makedirs('tokens')

@app.command("/알고토큰")
def handle_token_command(ack, body, client):
    ack()

    user_name = body['user_name']
    csv_path = f'tokens/{user_name}.csv'

    if os.path.exists(csv_path):
        client.chat_postEphemeral(
            channel=body['channel_id'],
            user=body['user_id'],
            text="이미 등록된 토큰이 있습니다. 관리자에게 문의해주세요."
        )
        return

    try:
        client.views_open(
            trigger_id=body['trigger_id'],
            view={
                "type": "modal",
                "callback_id": "token_submission",
                "title": {
                    "type": "plain_text",
                    "text": "Github 토큰 등록"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "등록"
                },
                "close": {
                    "type": "plain_text",
                    "text": "취소"
                },
                "blocks": [
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
                ]
            }
        )
    except Exception as e:
        client.chat_postEphemeral(
            channel=body['channel_id'],
            user=body['user_id'],
            text=f"Modal 생성 중 오류가 발생했습니다: {str(e)}"
        )

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

        client.chat_postMessage(
            channel=body['user']['id'],
            text="토큰이 성공적으로 등록되었습니다."
        )
    except Exception as e:
        client.chat_postMessage(
            channel=body['user']['id'],
            text=f"토큰 등록 중 오류가 발생했습니다: {str(e)}"
        )

@app.command("/알고풀이")
def handle_submit_command(ack, body, client):
    ack()

    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "algorithm_submission",
                "title": {"type": "plain_text", "text": "알고리즘 풀이 제출"},
                "submit": {"type": "plain_text", "text": "제출"},
                "close": {"type": "plain_text", "text": "취소"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "problem_link",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "link_input",
                            "placeholder": {"type": "plain_text", "text": "문제 링크를 입력하세요"}
                        },
                        "label": {"type": "plain_text", "text": "문제 링크"}
                    },
                    {
                        "type": "input",
                        "block_id": "problem_name",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "name_input",
                            "placeholder": {"type": "plain_text", "text": "문제 이름을 입력하세요"}
                        },
                        "label": {"type": "plain_text", "text": "문제 이름"}
                    },
                    {
                        "type": "input",
                        "block_id": "language",
                        "element": {
                            "type": "static_select",
                            "action_id": "language_select",
                            "placeholder": {"type": "plain_text", "text": "언어를 선택하세요"},
                            "options": [
                                {"text": {"type": "plain_text", "text": lang}, "value": lang.lower()}
                                for lang in ["Java", "JavaScript", "Python", "Swift", "Kotlin", "Rust"]
                            ]
                        },
                        "label": {"type": "plain_text", "text": "언어 선택"}
                    },
                    {
                        "type": "input",
                        "block_id": "code",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "code_input",
                            "multiline": True,
                            "placeholder": {"type": "plain_text", "text": "코드를 입력하세요"}
                        },
                        "label": {"type": "plain_text", "text": "코드"}
                    },
                    {
                        "type": "input",
                        "block_id": "submission_text",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "text_input",
                            "placeholder": {"type": "plain_text", "text": "채널에 표시될 제출 문구를 입력하세요"}
                        },
                        "label": {"type": "plain_text", "text": "제출 문구"}
                    },
                    {
                        "type": "input",
                        "block_id": "need_review",
                        "element": {
                            "type": "radio_buttons",
                            "action_id": "review_select",
                            "options": [
                                {
                                    "text": {"type": "plain_text", "text": "네! 필요해요"},
                                    "value": "yes"
                                },
                                {
                                    "text": {"type": "plain_text", "text": "아니요~ 괜찮아요"},
                                    "value": "no"
                                }
                            ]
                        },
                        "label": {"type": "plain_text", "text": "코드 리뷰가 필요하신가요?"}
                    }
                ]
            }
        )
    except Exception as e:
        client.chat_postEphemeral(
            channel=body['channel_id'],
            user=body['user_id'],
            text=f"Modal 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.view("algorithm_submission")
def handle_submission(ack, body, view, client):
    ack()

    channel_id = body["user"]["id"]
    user_name = body["user"]["username"]

    # 토큰 읽기
    try:
        with open(f'tokens/{user_name}.csv', 'r') as file:
            reader = csv.reader(file)
            _, token = next(reader)
    except Exception as e:
        client.chat_postMessage(
            channel=channel_id,
            text="토큰을 찾을 수 없습니다. '/알고토큰' 명령어로 먼저 토큰을 등록해주세요."
        )
        return

    # 입력값 추출
    values = view["state"]["values"]
    problem_link = values["problem_link"]["link_input"]["value"]
    problem_name = values["problem_name"]["name_input"]["value"]
    language = values["language"]["language_select"]["selected_option"]["value"]
    code = values["code"]["code_input"]["value"]
    submission_text = values["submission_text"]["text_input"]["value"]
    need_review = values["need_review"]["review_select"]["selected_option"]["value"] == "yes"

    try:
        # 스트릭 데이터 저장
        streak_data = save_streak_data(
            user_id=body["user"]["id"],
            user_name=body["user"]["username"],
            problem_link=problem_link,
            code=code
        )

        # PR 생성 후 메시지에 스트릭 정보 포함
        client.chat_postMessage(
            channel=channel_id,
            text=f"""✅ Pull Request가 생성되었습니다!\n*<{problem_link}|PR 보러가기>*
               
        현재까지 {streak_data['submit_count']}개의 문제를 제출하셨습니다.
        {streak_data['current_streak']}일 연속으로 문제를 풀고 계십니다!
        (최대 {streak_data['max_streak']}일 연속 제출)
        작성하신 리뷰: {streak_data['review_count']}개
               """
        )


        # Github 연동
        g = Github(token)

        github_user = g.get_user()
        github_username = github_user.login

        # 사용자의 fork된 레포지토리 가져오기
        user_fork = g.get_repo(f"{github_username}/daily-solvetto")

        # 브랜치 이름 생성
        branch_name = f"feature/algo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # base 브랜치(main) 가져오기
        base_branch = user_fork.get_branch("main")

        # 새 브랜치 생성
        user_fork.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_branch.commit.sha
        )

        # 파일 경로 생성과 base64 인코딩
        file_path = f"{problem_name}/{language.lower()}/solution.{get_file_extension(language)}"
        content = base64.b64encode(code.encode('utf-8')).decode('utf-8')

        geultto_token = os.environ.get("GEULTTO_GITHUB_TOKEN")
        g_geultto = Github(geultto_token)
        archive_repo = g_geultto.get_repo("geultto/daily-solvetto")

        # 파일 생성
        file_result = user_fork.create_file(
            path=file_path,
            message=f"Add solution for {problem_name}",
            content=content,
            branch=branch_name
        )

        # PR 생성
        pr = archive_repo.create_pull(
            base="main",
            head=f"{github_username}:{branch_name}",
            body=f"""
        문제: {problem_link}
        작성자: @{github_username}
        언어: {language}
        
        이 PR은 Slack에서 자동으로 생성되었습니다.
        파일: {file_path}
        커밋: {file_result['commit'].sha}
                """
        )

        # PR 생성 성공 메시지
        client.chat_postMessage(
            channel=channel_id,
            text=f"✅ Pull Request가 생성되었습니다! 코드 리뷰 요청을 완료했습니다.\n*<{pr.html_url}|PR 보러가기>*"
        )

    except Exception as e:
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ 오류가 발생했습니다: {str(e)}"
        )

def get_file_extension(language):
    extensions = {
        "java": "java",
        "javascript": "js",
        "python": "py",
        "swift": "swift",
        "kotlin": "kt",
        "rust": "rs"
    }
    return extensions.get(language.lower(), "txt")

def init_streak_directory():
    if not os.path.exists('streak'):
        os.makedirs('streak')

def save_streak_data(user_id, user_name, problem_link, code):
    init_streak_directory()
    today = datetime.now().date()
    submit_date = datetime.now()
    weekday = submit_date.strftime('%A')
    csv_path = f'streak/{user_name}.csv'

    new_data = {
        'user_id': user_id,
        'user_name': user_name,
        'submit_date': submit_date.strftime('%Y-%m-%d'),
        'weekday': weekday,
        'problem_link': problem_link,
        'point': 10,
        'total_point': 0,
        'submit_count': 1,
        'current_streak': 1,
        'max_streak': 1,
        'review_count': 0
    }

    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=new_data.keys())
            writer.writeheader()
            writer.writerow(new_data)
        return new_data

    # 기존 데이터 읽기 및 정렬
    df = pd.read_csv(csv_path)
    if not df.empty:
        df['submit_date'] = pd.to_datetime(df['submit_date'])
        df = df.sort_values('submit_date')
        last_submit = df['submit_date'].iloc[-1].date()

        # 마지막 제출일과의 차이 계산
        days_diff = (today - last_submit).days

        # 스트릭 계산 개선
        if days_diff == 1:  # 연속 제출
            new_data['current_streak'] = df['current_streak'].iloc[-1] + 1
            new_data['max_streak'] = max(new_data['current_streak'], df['max_streak'].iloc[-1])
        elif days_diff == 0:  # 같은 날 제출
            new_data['current_streak'] = df['current_streak'].iloc[-1]
            new_data['max_streak'] = df['max_streak'].iloc[-1]
        else:  # 연속 스트릭 끊김
            new_data['current_streak'] = 1
            new_data['max_streak'] = df['max_streak'].iloc[-1]

        new_data['total_point'] = df['total_point'].iloc[-1] + new_data['point']
        new_data['submit_count'] = df['submit_count'].iloc[-1] + 1
        new_data['review_count'] = df['review_count'].iloc[-1]

    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_data.keys())
        writer.writerow(new_data)

    return new_data

@app.command("/알고조회")
def view_streak(ack, body, client):
    ack()

    user_id = body["user_id"]
    user_name = body["user_name"]
    csv_path = f'streak/{user_name}.csv'

    if not os.path.exists(csv_path):
        client.chat_postEphemeral(
            channel=body["channel_id"],
            user=user_id,
            text="아직 제출한 알고리즘 문제가 없습니다. 첫 문제를 풀어보세요! 💪"
        )
        return

    try:
        # 1. CSV 파일 읽기
        df = pd.read_csv(csv_path)
        if df.empty:
            client.chat_postEphemeral(
                channel=body["channel_id"],
                user=user_id,
                text="아직 제출한 알고리즘 문제가 없습니다. 첫 문제를 풀어보세요! 💪"
            )
            return

        # 2. 날짜 데이터 처리
        df['submit_date'] = pd.to_datetime(df['submit_date']).dt.date  # datetime.date 객체로 변환
        submit_dates = set(df['submit_date'])  # 제출된 날짜들의 집합

        # 3. 이번 주의 날짜 범위 계산 (수정)
        today = datetime.now().date()
        sunday = today - timedelta(days=today.weekday() + 1)  # 이번 주 일요일 계산 (일요일 = 6에서 보정)

        if today.weekday() == 6:  # 오늘이 일요일이면 sunday는 오늘
            sunday = today

        # 4. 이번 주 전체 날짜 생성
        week_dates = [sunday + timedelta(days=i) for i in range(7)]

        # 5. 각 날짜별로 제출 여부 확인하여 스트릭 표시
        streak = []
        for date in week_dates:
            if date in submit_dates:
                streak.append("🟩")  # 제출한 날짜는 초록색
            else:
                streak.append("⬜")  # 미제출 날짜는 흰색

        # 6. 통계 계산
        this_week_submissions = len([d for d in submit_dates if sunday <= d <= today])
        total_submissions = len(df)

        # 7. 연속 제출 계산
        sorted_dates = sorted(list(submit_dates))
        current_streak = 0
        max_streak = 0
        temp_streak = 0

        for i, date in enumerate(sorted_dates):
            if i == 0:
                temp_streak = 1
            else:
                if (date - sorted_dates[i-1]).days == 1:
                    temp_streak += 1
                else:
                    temp_streak = 1

            max_streak = max(max_streak, temp_streak)

            if i == len(sorted_dates) - 1:  # 마지막 제출
                if (today - date).days <= 1:
                    current_streak = temp_streak
                else:
                    current_streak = 0

        # 8. 결과 메시지 생성
        message = f"""*이번 주 스트릭:*
일 월 화 수 목 금 토
{" ".join(streak)}

이번 주 제출: {this_week_submissions}개
총 제출: {total_submissions}개
현재 연속 제출: {current_streak}일
최대 연속 제출: {max_streak}일
"""

        client.chat_postEphemeral(
            channel=body["channel_id"],
            user=user_id,
            text=message
        )

    except Exception as e:
        client.chat_postEphemeral(
            channel=body["channel_id"],
            user=user_id,
            text=f"❌ 조회 중 오류가 발생했습니다: {str(e)}"
        )


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()