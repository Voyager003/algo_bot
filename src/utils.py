def get_motivational_message(streak):
    if streak == 0:
        return "오늘부터 다시 시작해볼까요? 화이팅!"
    elif streak <= 3:
        return "조금씩 습관을 만들어가고 있어요. 계속 달려보세요!"
    elif streak <= 7:
        return "멋져요! 꾸준함이 쌓여가고 있네요. 그 열정 멈추지 마세요!"
    elif streak <= 14:
        return "와우! 정말 대단해요. 알고리즘 마스터를 향해 가고 있어요!"
    else:
        return "믿을 수 없네요! 여러분은 진정한 알고리즘 전사입니다!"

def calculate_streak(submissions):
    if not submissions:
        return 0, 0

    streak = 0
    max_streak = 0
    prev_date = submissions[0]

    for submission_date in submissions:
        if (prev_date - submission_date).days == 1:
            streak += 1
            max_streak = max(max_streak, streak)
        elif (prev_date - submission_date).days == 0:
            continue
        else:
            streak = 0
        prev_date = submission_date

    return streak, max_streak