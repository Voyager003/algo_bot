import csv
import time
import os
import urllib.parse
from datetime import datetime
from github import Github, GithubIntegration, GithubException
from configs import language_extensions_dict
from dotenv import load_dotenv

def __init__(self):
    load_dotenv()
    self.app_id = int(os.getenv("GITHUB_APP_ID"))
    self.installation_id = int(os.getenv("GITHUB_INSTALLATION_ID"))
    self.private_key_path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")

    if not all([self.app_id, self.installation_id, self.private_key_path]):
        print(f"[DEBUG] APP_ID: {self.app_id}")
        print(f"[DEBUG] INSTALLATION_ID: {self.installation_id}")
        print(f"[DEBUG] PRIVATE_KEY_PATH: {self.private_key_path}")
        raise ValueError("Required environment variables are missing")

    try:
        print(f"[DEBUG] Private Key 파일 경로: {self.private_key_path}")
        with open(self.private_key_path, 'r') as f:
            self.private_key = f.read().strip()  # 앞뒤 공백 제거

        print("[DEBUG] Private Key 읽기 성공:")
        print(f"Private Key 시작: {self.private_key[:50]}")
        print(f"Private Key 끝: {self.private_key[-50:]}")

        # 키가 올바른 형식인지 확인
        if not (self.private_key.startswith('-----BEGIN RSA PRIVATE KEY-----') and
                self.private_key.endswith('-----END RSA PRIVATE KEY-----')):
            raise ValueError("Invalid PEM key format")

        self.integration = GithubIntegration(
            integration_id=self.app_id,
            private_key=self.private_key,
        )

    except Exception as e:
        print(f"[DEBUG] GitHub App 초기화 중 에러 발생: {str(e)}")
        print(f"[DEBUG] Private Key Type: {type(self.private_key)}")
        raise

    def get_github_client(self):
        """GitHub App 클라이언트 생성"""
        try:
            print("[DEBUG] Installation 토큰 생성 시도")
            access_token = self.integration.get_access_token(self.installation_id)
            print("[DEBUG] Installation 토큰 생성 성공")
            return Github(access_token.token)
        except Exception as e:
            print(f"[DEBUG] GitHub App 클라이언트 생성 실패: {str(e)}")
            raise

def get_file_url(file_path, branch_name, needs_review):
    """파일 URL 생성"""
    encoded_path = '/'.join(urllib.parse.quote(component) for component in file_path.split('/'))
    if needs_review:
        return f"github.com/geultto/daily-solvetto/blob/{branch_name}/{encoded_path}"
    else:
        return f"github.com/geultto/daily-solvetto/blob/main/{encoded_path}"

def create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process, submission_comment, code):
    try:
        # 1. 사용자 토큰으로 GitHub 클라이언트 생성
        print("[DEBUG] 사용자 토큰 읽기 시도")
        user_name = body["user"]["username"]
        with open(f'tokens/{user_name}.csv', 'r') as file:
            reader = csv.reader(file)
            _, user_token = next(reader)
        print(f"[DEBUG] 사용자 토큰 읽기 성공: {user_name}")

        g_user = Github(user_token)
        github_user = g_user.get_user()
        github_username = github_user.login
        print(f"[DEBUG] GitHub 사용자 정보 획득: {github_username}")

        # 2. 사용자의 fork된 레포지토리 접근
        user_fork = g_user.get_repo(f"{github_username}/daily-solvetto")
        print(f"[DEBUG] Fork된 레포지토리 접근 성공: {github_username}/daily-solvetto")

        # 3. 새로운 브랜치 생성
        branch_name = f"submit-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        base_branch = user_fork.get_branch("main")
        print(f"[DEBUG] 브랜치 이름 생성: {branch_name}")

        user_fork.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_branch.commit.sha
        )
        print("[DEBUG] 새 브랜치 생성 완료")

        # 4. 파일 생성 및 커밋
        file_path = f"{directory}/{language.lower()}/{problem_name}.{get_file_extension(language)}"
        print(f"[DEBUG] 파일 경로 생성: {file_path}")

        file_result = user_fork.create_file(
            path=file_path,
            message=f"Add solution for {problem_name}",
            content=code,
            branch=branch_name
        )
        print("[DEBUG] 파일 생성 완료")

        try:
            # 5. GitHub App으로 PR 생성
            print("[DEBUG] GitHub App으로 PR 생성 시도")
            github_app = GitHubAppAuth()
            g_app = github_app.get_github_client()
            archive_repo = g_app.get_repo("geultto/daily-solvetto")

            pr = archive_repo.create_pull(
                title=f"[{language}] {problem_name}",
                body=pr_body,
                head=f"{github_username}:{branch_name}",
                base="main"
            )
            print(f"[DEBUG] PR 생성 완료: {pr.html_url}")

            file_url = get_file_url(file_path, branch_name, needs_review)
            pr_result = {
                'pr': pr,
                'file_url': file_url
            }

            # 6. 리뷰 필요 여부에 따른 처리
            if needs_review:
                try:
                    labels = archive_repo.get_labels()
                    label_names = [label.name for label in labels]

                    if "review required" not in label_names:
                        archive_repo.create_label(
                            name="review required",
                            color="d4c5f9",
                            description="리뷰가 필요한 PR"
                        )
                    pr.add_to_labels("review required")
                    print("[DEBUG] 리뷰 라벨 추가 완료")

                except Exception as e:
                    print(f"[DEBUG] Warning: 라벨 처리 중 오류 발생: {str(e)}")
            else:
                try:
                    print("[DEBUG] PR 자동 머지 시도")
                    wait_for_mergeable(pr)
                    pr.merge(
                        commit_title=f"Merge: [{language}] {problem_name}",
                        commit_message="Auto-merged by GitHub App",
                        merge_method="squash"
                    )
                    print("[DEBUG] PR 머지 성공")
                except Exception as e:
                    print(f"[DEBUG] Error: PR 머지 실패: {str(e)}")
                    raise Exception(f"PR 머지 중 오류 발생: {str(e)}")

            return pr_result

        except GithubException as e:
            print(f"[DEBUG] GitHub API 에러:")
            print(f"[DEBUG] Status: {e.status}")
            print(f"[DEBUG] Message: {e.data.get('message')}")
            print(f"[DEBUG] Details: {e.data.get('errors')}")
            raise
        except Exception as e:
            print(f"[DEBUG] Error: PR 생성 실패: {str(e)}")
            raise Exception(f"PR 생성 중 오류 발생: {str(e)}")

    except Exception as e:
        print(f"[DEBUG] Critical Error: {str(e)}")
        raise Exception(f"PR 생성 중 오류 발생: {str(e)}")

def wait_for_mergeable(pr, timeout=30, interval=2):
    """PR이 머지 가능한 상태가 될 때까지 대기"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        pr.update()
        if pr.mergeable:
            return True
        time.sleep(interval)
    raise Exception("PR이 머지 가능한 상태가 되지 않았습니다.")

def get_file_extension(language):
    """언어에 따른 파일 확장자 반환"""
    return language_extensions_dict.get(language.lower(), "txt")