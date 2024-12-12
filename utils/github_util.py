import csv
import time
import os

from datetime import datetime
from github import Github
from configs import language_extensions_dict

def create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process, submission_comment, code):
    try:
        print("[DEBUG] 1. 사용자 토큰 읽기 시도")
        # 사용자의 GitHub 토큰으로 fork된 레포지토리 작업
        user_name = body["user"]["username"]
        with open(f'tokens/{user_name}.csv', 'r') as file:
            reader = csv.reader(file)
            _, user_token = next(reader)
        print(f"[DEBUG] 2. 사용자 토큰 읽기 성공: {user_name}")

        g_user = Github(user_token)
        github_user = g_user.get_user()
        github_username = github_user.login
        print(f"[DEBUG] 3. GitHub 사용자 정보 획득: {github_username}")

        # fork된 레포지토리 작업은 사용자 토큰으로
        user_fork = g_user.get_repo(f"{github_username}/daily-solvetto")
        print(f"[DEBUG] 4. Fork된 레포지토리 접근 성공: {github_username}/daily-solvetto")

        branch_name = f"feature/algo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        base_branch = user_fork.get_branch("main")
        print(f"[DEBUG] 5. 브랜치 이름 생성: {branch_name}")

        user_fork.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_branch.commit.sha
        )
        print("[DEBUG] 6. 새 브랜치 생성 완료")

        file_path = f"{directory}/{language.lower()}/{problem_name}.{get_file_extension(language)}"
        print(f"[DEBUG] 7. 파일 경로 생성: {file_path}")

        file_result = user_fork.create_file(
            path=file_path,
            message=f"Add solution for {problem_name}",
            content=code,
            branch=branch_name
        )
        print("[DEBUG] 8. 파일 생성 완료")

        # 사용자 토큰으로 merge 시도
        try:
            print("[DEBUG] 9. 사용자 토큰으로 PR 생성 시도")
            archive_repo_user = g_user.get_repo("geultto/daily-solvetto")
            pr = archive_repo_user.create_pull(
                title=f"[{language}] {problem_name}",
                body=pr_body,
                head=f"{github_username}:{branch_name}",
                base="main"
            )
            print("[DEBUG] 10. 사용자 토큰으로 PR 생성 성공")
        except Exception as e:
            print(f"[DEBUG] Error: 사용자 토큰으로 PR 생성 실패: {str(e)}")
            print("[DEBUG] 11. Geultto 토큰으로 PR 생성 시도")
            # PR 생성은 GEULTTO_GITHUB_TOKEN으로
            geultto_token = os.environ.get("GEULTTO_GITHUB_TOKEN")
            g_geultto = Github(geultto_token)
            archive_repo = g_geultto.get_repo("geultto/daily-solvetto")
            pr = archive_repo.create_pull(
                title=f"[{language}] {problem_name}",
                body=pr_body,
                head=f"{github_username}:{branch_name}",
                base="main"
            )
            print("[DEBUG] 12. Geultto 토큰으로 PR 생성 성공")

        if not needs_review:
            try:
                print("[DEBUG] 13. PR 머지 시도")
                wait_for_mergeable(pr)
                pr.merge(
                    commit_title=f"Merge: [{language}] {problem_name}",
                    commit_message="Auto-merged by Slack bot",
                    merge_method="squash"
                )
                print("[DEBUG] 14. PR 머지 성공")
            except Exception as e:
                print(f"[DEBUG] Error: PR 머지 실패: {str(e)}")
                raise Exception(f"PR 머지 중 오류 발생: {str(e)}")

        return pr

    except Exception as e:
        print(f"[DEBUG] Critical Error: {str(e)}")
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