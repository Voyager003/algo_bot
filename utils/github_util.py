import os
import csv
import time

from datetime import datetime
from github import Github
from configs import language_extensions_dict

def create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process, code):
    # 1. 사용자의 GitHub 토큰으로 fork된 레포지토리 작업
    user_name = body["user"]["username"]
    try:
        with open(f'tokens/{user_name}.csv', 'r') as file:
            reader = csv.reader(file)
            _, user_token = next(reader)
    except:
        raise Exception("GitHub 토큰이 등록되어 있지 않습니다. /알고토큰 명령어로 먼저 등록해주세요.")

    # 사용자 토큰으로 GitHub 연동
    g_user = Github(user_token)
    github_user = g_user.get_user()
    github_username = github_user.login

    try:
        user_fork = g_user.get_repo(f"{github_username}/daily-solvetto")

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

        # fork된 레포지토리에 파일 생성
        file_result = user_fork.create_file(
            path=file_path,
            message=f"Add solution for {problem_name}",
            content=code,
            branch=branch_name
        )

        # 2. GEULTTO_GITHUB_TOKEN으로 PR 생성 및 머지
        geultto_token = os.environ.get("GEULTTO_GITHUB_TOKEN")
        g_geultto = Github(geultto_token)
        archive_repo = g_geultto.get_repo("geultto/daily-solvetto")

        # PR 생성
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

    except Exception as e:
        raise Exception(f"PR 생성 중 오류 발생: {str(e)}")

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