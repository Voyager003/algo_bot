import csv
import time
import os
from datetime import datetime
from configs import language_extensions_dict
from dotenv import load_dotenv
from github import Github, GithubException, GithubIntegration

class GitHubAppAuth:
    def __init__(self):
        load_dotenv()
        self.app_id = int(os.getenv("GITHUB_APP_ID"))
        self.installation_id = int(os.getenv("GITHUB_INSTALLATION_ID"))
        self.private_key_path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")  # 경로로 변경

        if not all([self.app_id, self.installation_id, self.private_key_path]):
            print(f"[DEBUG] APP_ID: {self.app_id}")
            print(f"[DEBUG] INSTALLATION_ID: {self.installation_id}")
            print(f"[DEBUG] PRIVATE_KEY_PATH: {self.private_key_path}")
            raise ValueError("Required environment variables are missing")

        try:
            # 파일에서 PEM 키 읽기
            print(f"[DEBUG] Private Key 파일 경로: {self.private_key_path}")
            with open(self.private_key_path, 'r') as f:
                self.private_key = f.read()

            print("[DEBUG] Private Key 읽기 성공:")
            print(f"길이: {len(self.private_key)}")
            print(f"시작: {self.private_key[:50]}")

            # GithubIntegration 인스턴스 생성
            self.integration = GithubIntegration(
                integration_id=self.app_id,
                private_key=self.private_key,
            )

        except Exception as e:
            print(f"[DEBUG] 초기화 중 에러 발생: {str(e)}")
            raise

    def get_github_client(self):
        """GitHub 클라이언트 생성"""
        try:
            print("[DEBUG] Installation 토큰 생성 시도")
            access_token = self.integration.get_access_token(self.installation_id)
            print("[DEBUG] Installation 토큰 생성 성공")

            return Github(access_token.token)
        except Exception as e:
            print(f"[DEBUG] GitHub 클라이언트 생성 실패: {str(e)}")
            raise

def get_file_url(repo, file_path, branch_name, needs_review):
    """파일 URL 생성"""
    encoded_path = '/'.join(part.replace(" ", "%20") for part in file_path.split('/'))
    if needs_review:
        return f"github.com/algotest-org/algobot/blob/{branch_name}/{encoded_path}"
    else:
        return f"github.com/algotest-org/algobot/blob/main/{encoded_path}"

def create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process, submission_comment, code):
    try:
        print("[DEBUG] 1. GitHub App 토큰 생성")
        github_auth = GitHubAppAuth()
        g = github_auth.get_github_client()
        print("[DEBUG] 2. App 토큰 생성 완료")

        # PR 생성 과정 시작
        print(f"[DEBUG] PR 생성 과정 시작")

        # 1. algotest-org/algobot 저장소 접근
        org_repo = g.get_repo("algotest-org/algobot")
        print(f"[DEBUG] 대상 저장소: {org_repo.full_name}")

        # 2. main 브랜치의 최신 커밋 가져오기
        main_branch = org_repo.get_branch("main")
        source_commit = main_branch.commit

        # 3. 새 브랜치 생성 및 GitHub에 푸시
        branch_name = f"feature/algo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        print(f"[DEBUG] 브랜치 생성: {branch_name}")
        org_repo.create_git_ref(f"refs/heads/{branch_name}", source_commit.sha)

        # 4. 파일 생성 및 커밋 (Co-authored-by 추가)
        file_path = f"{directory}/{language.lower()}/{problem_name}.{get_file_extension(language)}"
        commit_message = f"""Add solution for {problem_name}

Co-authored-by: {body["user"]["username"]} <{body["user"]["username"]}@users.noreply.github.com>"""

        org_repo.create_file(
            path=file_path,
            message=commit_message,
            content=code,
            branch=branch_name
        )
        print("[DEBUG] 파일 생성 완료")

        # 5. PR 생성
        pr = org_repo.create_pull(
            title=f"[{language}] {problem_name}",
            body=pr_body,
            head=branch_name,
            base="main"
        )
        print(f"[DEBUG] PR 생성 성공: {pr.html_url}")

        # 6. 라벨 추가 또는 머지
        if needs_review:
            pr.add_to_labels("review required")
            print("[DEBUG] 리뷰 라벨 추가 완료")
        else:
            pr.merge(merge_method="squash")
            print("[DEBUG] PR 머지 완료")

        return {
            'pr': pr,
            'file_url': get_file_url("algotest-org/algobot", file_path, branch_name, needs_review)
        }

    except GithubException as e:
        print(f"[DEBUG] GitHub API 에러:")
        print(f"[DEBUG] Status: {e.status}")
        print(f"[DEBUG] Message: {e.data.get('message')}")
        print(f"[DEBUG] Details: {e.data.get('errors')}")
        raise

    except Exception as e:
        print(f"[DEBUG] 일반 에러: {str(e)}")
        raise

def get_file_extension(language):
    """언어에 따른 파일 확장자 반환"""
    return language_extensions_dict.get(language.lower(), "txt")