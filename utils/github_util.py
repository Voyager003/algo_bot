import os
import csv
import time
import urllib.parse
from datetime import datetime
from configs import language_extensions_dict
from github import Github, GithubException, GithubIntegration
from dotenv import load_dotenv

load_dotenv()

class GitHubAppAuth:
    def __init__(self):
        self.app_id = int(os.getenv("GITHUB_APP_ID"))
        self.installation_id = int(os.getenv("GITHUB_APP_INSTALLATION_ID"))
        self.private_key_path = os.path.join("key", "geultto-algobot.2024-12-30.private-key.pem")

        if not all([self.app_id, self.installation_id, self.private_key_path]):
            raise ValueError("Required environment variables are missing")

        try:
            with open(self.private_key_path, 'r') as f:
                self.private_key = f.read()
            # GithubIntegration 인스턴스 생성
            self.integration = GithubIntegration(
                integration_id=self.app_id,
                private_key=self.private_key,
            )

        except Exception as e:
            print(f"[DEBUG] 초기화 중 에러 발생: {str(e)}")
            raise

    def get_github_client(self):
        try:
            access_token = self.integration.get_access_token(self.installation_id)
            return Github(access_token.token)
        except Exception as e:
            print(f"[DEBUG] GitHub 클라이언트 생성 실패: {str(e)}")
            raise

def get_file_url(archive_repo, file_path, branch_name, needs_review):
    encoded_path = '/'.join(urllib.parse.quote(component) for component in file_path.split('/'))
    if needs_review:
        return f"github.com/geultto/daily-solvetto/blob/{branch_name}/{encoded_path}"
    else:
        return f"github.com/geultto/daily-solvetto/blob/main/{encoded_path}"

def create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process, submission_comment, code):
    try:
        # 1. 사용자 토큰으로 fork된 레포지토리에 push
        print("[DEBUG] 사용자 토큰 읽기 시도")
        user_name = body["user"]["username"]
        with open(f'tokens/{user_name}.csv', 'r') as file:
            _, user_token = next(csv.reader(file))
        print(f"[DEBUG] 사용자 토큰 읽기 성공: {user_name}")

        g_user = Github(user_token)
        github_user = g_user.get_user()
        github_username = github_user.login
        print(f"[DEBUG] GitHub 사용자 정보 획득: {github_username}")

        # github email 가져오기
        github_email = github_user.email  # GitHub 사용자의 이메일 가져오기
        if github_email is None:  # 이메일이 비공개인 경우
            github_email = f"{github_username}@users.noreply.github.com"

        # fork된 레포지토리에 접근
        user_fork = g_user.get_repo(f"{github_username}/daily-solvetto")
        print(f"[DEBUG] Fork된 레포지토리 접근 성공: {github_username}/daily-solvetto")

        # 브랜치 생성
        branch_name = f"submit-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        base_branch = user_fork.get_branch("main")
        print(f"[DEBUG] 브랜치 이름 생성: {branch_name}")

        user_fork.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_branch.commit.sha
        )
        print("[DEBUG] 새 브랜치 생성 완료")

        # PR 커밋 메시지에 co-author 정보 추가
        commit_message = f"Add solution for {problem_name}\n\nCo-authored-by: {github_username} <{github_email}>"

        # 파일 생성 및 push
        file_path = f"{directory}/{language.lower()}/{problem_name}.{get_file_extension(language)}"
        user_fork.create_file(
            path=file_path,
            message=commit_message,
            content=code,
            branch=branch_name
        )
        print("[DEBUG] 파일 생성 및 push 완료")

        # GitHub에서 브랜치 인식을 위한 대기
        time.sleep(5)

        # 2. Github App으로 PR 생성 및 관리
        print("[DEBUG] GitHub App 인증 시작")
        github_app = GitHubAppAuth()
        g_app = github_app.get_github_client()
        app_repo = g_app.get_repo("geultto/daily-solvetto")

        # PR 생성
        print(f"[DEBUG] PR 생성 시도 - head: {github_username}:{branch_name}, base: main")
        pr = app_repo.create_pull(
            title=f"[{language}] {problem_name}",
            body=pr_body,
            head=f"{github_username}:{branch_name}",
            base="main",
            maintainer_can_modify=False
        )
        print(f"[DEBUG] PR 생성 완료: {pr.html_url}")

        file_url = get_file_url(app_repo, file_path, f"{github_username}:{branch_name}", needs_review)
        pr_result = {'pr': pr, 'file_url': file_url}

        # 리뷰 필요 여부에 따른 처리
        if needs_review:
            if "review required" not in [l.name for l in app_repo.get_labels()]:
                app_repo.create_label(
                    name="review required",
                    color="d4c5f9",
                    description="리뷰가 필요한 PR"
                )
            pr.add_to_labels("review required")
            print("[DEBUG] 리뷰 라벨 추가 완료")
        else:
            wait_for_mergeable(pr)
            pr.merge(
                commit_title=f"Merge: [{language}] {problem_name}",
                commit_message=f"Auto-merged by GitHub App\n\nCo-authored-by: {github_username} <{github_email}>",
                merge_method="squash"
            )
            print("[DEBUG] PR 자동 머지 완료")

        return pr_result

    except GithubException as e:
        print(f"[DEBUG] GitHub API 에러:")
        print(f"[DEBUG] Status: {e.status}")
        print(f"[DEBUG] Message: {e.data.get('message')}")
        print(f"[DEBUG] Details: {e.data.get('errors')}")
        raise

    except Exception as e:
        print(f"[DEBUG] 일반 에러: {str(e)}")
        raise

def wait_for_mergeable(pr, timeout=30, interval=2):
    start_time = time.time()
    while time.time() - start_time < timeout:
        pr.update()
        if pr.mergeable:
            return True
        time.sleep(interval)

    raise Exception("PR이 머지 가능한 상태가 되지 않았습니다.")

def get_file_extension(language):
    return language_extensions_dict.get(language.lower(), "txt")