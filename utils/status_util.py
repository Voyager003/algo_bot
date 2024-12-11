import os
import csv
from datetime import datetime, timedelta
import pandas as pd

def get_streak_message(df):
    df['submit_date'] = pd.to_datetime(df['submit_date']).dt.date
    submit_dates = set(df['submit_date'])

    today = datetime.now().date()
    sunday = today - timedelta(days=today.weekday() + 1)

    if today.weekday() == 6:
        sunday = today

    week_dates = [sunday + timedelta(days=i) for i in range(7)]

    streak = []
    for date in week_dates:
        if date in submit_dates:
            streak.append("🟩")
        else:
            streak.append("⬜")

    this_week_submissions = len([d for d in submit_dates if sunday <= d <= today])
    total_submissions = len(df)

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

        if i == len(sorted_dates) - 1:
            if (today - date).days <= 1:
                current_streak = temp_streak
            else:
                current_streak = 0

    return (
f"""*이번 주의 스트릭이에요!:*
{" ".join(streak)}

총 제출한 코드는 {total_submissions}개이며
지금 진행되고 있는 연속 제출일은 {current_streak}일
최대로 이어진 연속 제출은 {max_streak}일 입니다!
"""
    )

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