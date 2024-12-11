import os
import csv
import time

from datetime import datetime
from github import Github
from configs import language_extensions_dict

def create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process, submission_comment, code):

    user_name = body["user"]["username"]
    with open(f'tokens/{user_name}.csv', 'r') as file:
        reader = csv.reader(file)
        _, user_token = next(reader)

    g_user = Github(user_token)
    github_user = g_user.get_user()
    github_username = github_user.login

    # fork된 레포지토리 작업은 사용자 토큰으로
    user_fork = g_user.get_repo(f"{github_username}/daily-solvetto")
    branch_name = f"submit-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    base_branch = user_fork.get_branch("main")

    user_fork.create_git_ref(
        ref=f"refs/heads/{branch_name}",
        sha=base_branch.commit.sha
    )

    # 파일 경로를 <영문명>/<언어>/<문제이름> 형식으로 수정
    file_path = f"{directory}/{language.lower()}/{problem_name}.{get_file_extension(language)}"

    file_result = user_fork.create_file(
        path=file_path,
        message=f"Add solution for {problem_name}",
        content=code,
        branch=branch_name
    )

    # PR 생성은 Geultto 토큰
    archive_repo = g_user.get_repo("geultto/daily-solvetto")
    pr = archive_repo.create_pull(
        title=f"[{language}] {problem_name}",
        body=pr_body,
        head=f"{github_username}:{branch_name}",
        base="main"
    )

    # 자동 머지 Geultto 토큰
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
    return language_extensions_dict.get(language.lower(), "txt")