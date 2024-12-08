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
    """사용자의 스트릭 데이터를 CSV에 저장"""
    init_streak_directory()
    today = datetime.now().date()
    csv_path = f'streak/{user_name}.csv'

    # 새로운 제출 데이터
    new_data = {
        'user_id': user_id,
        'user_name': user_name,
        'submit_date': today.strftime('%Y-%m-%d'),
        'problem_link': problem_link,
        'point': 10,  # 기본 포인트
        'total_point': 0,
        'submit_count': 1,  # 총 제출 수
        'current_streak': 1,  # 현재 연속 제출
        'max_streak': 1,     # 최대 연속 제출
        'review_count': 0    # 리뷰 수
    }

    # 파일이 존재하지 않으면 새로 생성
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=new_data.keys())
            writer.writeheader()
            writer.writerow(new_data)
        return new_data

    # 기존 파일이 있다면 마지막 데이터를 읽어서 업데이트
    df = pd.read_csv(csv_path)
    if not df.empty:
        last_row = df.iloc[-1]
        last_submit = datetime.strptime(last_row['submit_date'], '%Y-%m-%d').date()
        days_diff = (today - last_submit).days

        # 스트릭 및 카운트 업데이트
        if days_diff == 1:  # 연속 제출
            new_data['current_streak'] = last_row['current_streak'] + 1
        else:
            new_data['current_streak'] = 1  # 스트릭 리셋

        new_data['max_streak'] = max(new_data['current_streak'], last_row['max_streak'])
        new_data['total_point'] = last_row['total_point'] + new_data['point']
        new_data['submit_count'] = last_row['submit_count'] + 1
        new_data['review_count'] = last_row['review_count']  # 리뷰 수는 유지

    # 새로운 데이터 추가
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
        df = pd.read_csv(csv_path)
        if df.empty:
            client.chat_postEphemeral(
                channel=body["channel_id"],
                user=user_id,
                text="아직 제출한 알고리즘 문제가 없습니다. 첫 문제를 풀어보세요! 💪"
            )
            return

        # 날짜 데이터 변환 및 정렬
        df['submit_date'] = pd.to_datetime(df['submit_date'])
        df = df.sort_values('submit_date')
        submission_dates = set(df['submit_date'].dt.date)

        # 현재 날짜와 월 정보
        today = datetime.now().date()
        month_start = today.replace(day=1)
        _, last_day = calendar.monthrange(today.year, today.month)
        month_end = today.replace(day=last_day)

        # 이전 달과 다음 달 정보
        if month_start.month == 1:
            prev_month = month_start.replace(year=month_start.year-1, month=12)
        else:
            prev_month = month_start.replace(month=month_start.month-1)

        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year+1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month+1)

        # 달력의 시작일과 종료일 계산
        calendar_start = month_start - timedelta(days=(month_start.weekday() + 1) % 7)
        calendar_end = month_end + timedelta(days=(6 - month_end.weekday()))

        # 달력 날짜 생성
        dates = []
        current_date = calendar_start
        while current_date <= calendar_end:
            dates.append(current_date)
            current_date += timedelta(days=1)

        # 달력 생성
        calendar_days = []
        for date in dates:
            if date.month != month_start.month:
                calendar_days.append("　")  # 다른 달의 날짜
            elif date > today:
                calendar_days.append("⬜")  # 미래 날짜
            elif date in submission_dates:  # 여기서 비교가 제대로 되는지 확인
                print(f"Found submission for date: {date}")  # 디버깅용
                calendar_days.append("🟩")  # 제출한 날짜
            else:
                calendar_days.append("⬜")

        # 주 단위로 나누기
        weeks = [calendar_days[i:i+7] for i in range(0, len(calendar_days), 7)]
        calendar_text = ""
        for week in weeks:
            calendar_text += " ".join(week) + "\n"

        # 전체 기간의 스트릭 계산
        all_submission_dates = sorted(list(submission_dates))
        current_streak = 0
        max_streak = 0
        temp_streak = 0

        for i in range(len(all_submission_dates)):
            if i == 0:
                temp_streak = 1
            else:
                diff = (all_submission_dates[i] - all_submission_dates[i-1]).days
                if diff == 1:  # 연속된 날짜
                    temp_streak += 1
                else:
                    temp_streak = 1

            max_streak = max(max_streak, temp_streak)

            # 오늘 또는 어제 제출했다면 current_streak 갱신
            if i == len(all_submission_dates) - 1:
                days_since_last = (today - all_submission_dates[i]).days
                if days_since_last <= 1:
                    current_streak = temp_streak
                else:
                    current_streak = 0

        # 이번 달 제출 횟수
        monthly_submissions = len(df[
                                      (df['submit_date'].dt.year == today.year) &
                                      (df['submit_date'].dt.month == today.month)
                                      ])

        # 총 제출 횟수
        total_submissions = len(df)

        message = f"""*{today.year}년 {today.month}월 스트릭:*
일 월 화 수 목 금 토
{calendar_text}
이번 달 제출: {monthly_submissions}개
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
        print(f"Error: {e}")  # 디버깅용
        client.chat_postEphemeral(
            channel=body["channel_id"],
            user=user_id,
            text=f"❌ 조회 중 오류가 발생했습니다: {str(e)}"
        )


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()