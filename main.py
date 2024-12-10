import os
import csv
import base64
import pandas as pd
import time

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
                "callback_id": "review_selection",
                "title": {"type": "plain_text", "text": "알고리즘 풀이 제출"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "need_review",
                        "element": {
                            "type": "radio_buttons",
                            "action_id": "review_select",
                            "options": [
                                {
                                    "text": {"type": "plain_text", "text": "예! 리뷰가 필요해요"},
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
                ],
                "submit": {"type": "plain_text", "text": "다음"},
            }
        )
    except Exception as e:
        client.chat_postEphemeral(
            channel=body['channel_id'],
            user=body['user_id'],
            text=f"Modal 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.view("review_selection")
def handle_review_selection(ack, body, client):
    ack()
    need_review = body["view"]["state"]["values"]["need_review"]["review_select"]["selected_option"]["value"] == "yes"

    if need_review:
        show_review_modal(body, client)
    else:
        show_no_review_modal(body, client)

def show_review_modal(body, client):
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "submission_with_review",
            "title": {"type": "plain_text", "text": "알고리즘 풀이 제출"},
            "submit": {"type": "plain_text", "text": "제출"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "directory_name",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "directory_input",
                        "placeholder": {"type": "plain_text", "text": "예: ChoYoonUn/javascript"}
                    },
                    "label": {"type": "plain_text", "text": "디렉토리 경로"}
                },
                {
                    "type": "input",
                    "block_id": "problem_name",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "problem_input",
                        "placeholder": {"type": "plain_text", "text": "문제 이름을 입력하세요"}
                    },
                    "label": {"type": "plain_text", "text": "문제"}
                },
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
                    "label": {"type": "plain_text", "text": "언어"}
                },
                {
                    "type": "input",
                    "block_id": "solution_process",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "process_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "문제 풀이 과정을 설명해주세요"}
                    },
                    "label": {"type": "plain_text", "text": "풀이 과정"}
                },
                {
                    "type": "input",
                    "block_id": "review_request",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "request_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "리뷰 받고 싶은 부분을 작성해주세요"}
                    },
                    "label": {"type": "plain_text", "text": "리뷰 요청 사항"}
                }
            ]
        }
    )

def show_no_review_modal(body, client):
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "submission_without_review",
            "title": {"type": "plain_text", "text": "알고리즘 풀이 제출"},
            "submit": {"type": "plain_text", "text": "제출"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "directory_name",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "directory_input",
                        "placeholder": {"type": "plain_text", "text": "예: ChoYoonUn/javascript"}
                    },
                    "label": {"type": "plain_text", "text": "디렉토리 경로"}
                },
                {
                    "type": "input",
                    "block_id": "problem_name",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "problem_input",
                        "placeholder": {"type": "plain_text", "text": "문제 이름을 입력하세요"}
                    },
                    "label": {"type": "plain_text", "text": "문제"}
                },
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
                    "label": {"type": "plain_text", "text": "언어"}
                },
                {
                    "type": "input",
                    "block_id": "solution_process",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "process_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "문제 풀이 과정을 설명해주세요"}
                    },
                    "label": {"type": "plain_text", "text": "풀이 과정"}
                }
            ]
        }
    )

def handle_submission(body, view, client, needs_review):

    channel_id = body["user"]["id"]
    user_name = body["user"]["username"]

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

    try:
        # 입력값 추출
        values = view["state"]["values"]
        directory = values["directory_name"]["directory_input"]["value"]
        problem_name = values["problem_name"]["problem_input"]["value"]
        problem_link = values["problem_link"]["link_input"]["value"]
        language = values["language"]["language_select"]["selected_option"]["value"]
        solution_process = values["solution_process"]["process_input"]["value"]
        review_request = values.get("review_request", {}).get("request_input", {}).get("value", "")

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
        # PR 생성 및 처리
        pr = create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process)

        # PR 처리 후 메시지 전송
        if needs_review:
            # 채널에 PR 생성 메시지 전송
            client.chat_postMessage(
                channel=os.environ.get("SLACK_CHANNEL_ID"),
                text=f"✨ 새로운 PR이 생성되었습니다!\n*<{pr.html_url}|[{language}] {problem_name}>*"
            )
        else:
            # PR 자동 머지 후 채널에 메시지 전송
            client.chat_postMessage(
                channel=os.environ.get("SLACK_CHANNEL_ID"),
                text=f"✅ [{problem_name}] 문제가 제출되었습니다!"
            )

            # 스트릭 정보를 DM으로 전송
            view_streak_message(body["user"]["id"], client)

    except Exception as e:
        client.chat_postMessage(
            channel=body["user"]["id"],
            text=f"❌ 오류가 발생했습니다: {str(e)}"
        )

def create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process):
    # GitHub 토큰 읽기
    user_name = body["user"]["username"]
    with open(f'tokens/{user_name}.csv', 'r') as file:
        reader = csv.reader(file)
        _, token = next(reader)

    # GitHub 연동
    g = Github(token)
    github_user = g.get_user()
    github_username = github_user.login

    # fork된 레포지토리 가져오기
    user_fork = g.get_repo(f"{github_username}/daily-solvetto")

    # 브랜치 이름 생성
    branch_name = f"feature/algo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # base 브랜치의 최신 커밋 SHA 가져오기
    base_branch = user_fork.get_branch("main")

    # 새 브랜치 생성
    user_fork.create_git_ref(
        ref=f"refs/heads/{branch_name}",
        sha=base_branch.commit.sha
    )

    # 파일 경로 생성
    file_path = f"{directory}/{problem_name}.{get_file_extension(language)}"

    # 파일 내용 base64 인코딩
    content = base64.b64encode(solution_process.encode('utf-8')).decode('utf-8')

    # fork된 레포지토리에 파일 생성
    file_result = user_fork.create_file(
        path=file_path,
        message=f"Add solution for {problem_name}",
        content=content,
        branch=branch_name
    )

    # PR 생성
    geultto_token = os.environ.get("GEULTTO_GITHUB_TOKEN")
    g_geultto = Github(geultto_token)
    archive_repo = g_geultto.get_repo("geultto/daily-solvetto")

    pr = archive_repo.create_pull(
        title=f"[{language}] {problem_name}",
        body=pr_body,
        head=f"{github_username}:{branch_name}",
        base="main"
    )

    if not needs_review:
        try:
            wait_for_mergeable(pr)
            pr.merge(
                commit_title=f"Merge: [{language}] {problem_name}",
                commit_message="Auto-merged by Slack bot",
                merge_method="squash"
            )
        except Exception as e:
            raise Exception(f"PR 머지 중 오류 발생: {str(e)}")

    return pr

def wait_for_mergeable(pr, timeout=30, interval=2):
    """PR이 머지 가능한 상태가 될 때까지 대기"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        pr.update()  # PR 정보 갱신
        if pr.mergeable:
            return True
        time.sleep(interval)

    raise Exception("PR이 머지 가능한 상태가 되지 않았습니다.")

def get_file_extension(language):
    """언어별 파일 확장자 반환"""
    extensions = {
        "java": "java",
        "javascript": "js",
        "python": "py",
        "swift": "swift",
        "kotlin": "kt",
        "rust": "rs"
    }
    return extensions.get(language.lower(), "txt")

def view_streak_message(user_id, client):
    """스트릭 정보를 DM으로 전송"""
    try:
        df = pd.read_csv(f'streak/{user_id}.csv')
        if df.empty:
            return "아직 제출 기록이 없습니다."

        df['submit_date'] = pd.to_datetime(df['submit_date']).dt.date
        last_row = df.iloc[-1]

        message = f"""*스트릭 현황:*
현재 연속 제출: {last_row['current_streak']}일
최대 연속 제출: {last_row['max_streak']}일
이번 제출 포인트: {last_row['total_points']}점 (기본: {last_row['base_points']}점 + 보너스: {last_row['bonus_points']}점)
누적 포인트: {last_row['accumulated_points']}점
"""
        client.chat_postMessage(
            channel=user_id,
            text=message
        )
    except Exception as e:
        print(f"스트릭 메시지 전송 중 오류: {str(e)}")

def init_streak_directory():
    """스트릭 데이터 저장을 위한 디렉토리 생성"""
    if not os.path.exists('streak'):
        os.makedirs('streak')

def calculate_points(df, today):
    """포인트 계산 함수"""
    base_points = 10  # 기본 점수
    bonus_points = 0

    if not df.empty:
        # 연속 제출 보너스 계산
        current_streak = df['current_streak'].iloc[-1]
        if current_streak >= 30:
            bonus_points += 20
        elif current_streak >= 14:
            bonus_points += 15
        elif current_streak >= 7:
            bonus_points += 10
        elif current_streak >= 3:
            bonus_points += 5

    total_points = base_points + bonus_points
    return total_points, base_points, bonus_points


@app.view("submission_with_review")
def handle_review_submission(ack, body, view, client):
    ack()
    handle_submission(body, view, client, needs_review=True)

@app.view("submission_without_review")
def handle_no_review_submission(ack, body, view, client):
    ack()
    handle_submission(body, view, client, needs_review=False)


def save_streak_data(user_id, user_name, problem_link, code):
    init_streak_directory()
    today = datetime.now().date()
    submit_date = datetime.now()
    weekday = submit_date.strftime('%A')
    csv_path = f'streak/{user_name}.csv'

    # 초기 데이터 구조
    new_data = {
        'user_id': user_id,
        'user_name': user_name,
        'submit_date': submit_date.strftime('%Y-%m-%d'),
        'weekday': weekday,
        'problem_link': problem_link,
        'base_points': 10,
        'bonus_points': 0,
        'total_points': 10,
        'accumulated_points': 10,
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

        # 스트릭 계산
        if days_diff == 1:  # 연속 제출
            new_data['current_streak'] = df['current_streak'].iloc[-1] + 1
            new_data['max_streak'] = max(new_data['current_streak'], df['max_streak'].iloc[-1])
        elif days_diff == 0:  # 같은 날 제출
            new_data['current_streak'] = df['current_streak'].iloc[-1]
            new_data['max_streak'] = df['max_streak'].iloc[-1]
        else:  # 연속 스트릭 끊김
            new_data['current_streak'] = 1
            new_data['max_streak'] = df['max_streak'].iloc[-1]

        # 포인트 계산
        total_points, base_points, bonus_points = calculate_points(df, today)
        new_data['base_points'] = base_points
        new_data['bonus_points'] = bonus_points
        new_data['total_points'] = total_points
        new_data['accumulated_points'] = df['accumulated_points'].iloc[-1] + total_points

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
        message = f"""*이번 주의 스트릭:*
{" ".join(streak)}

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