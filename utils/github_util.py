import csv
import time
import os
import base64
import urllib.parse
import subprocess
from datetime import datetime
from configs import language_extensions_dict

def run_gh_command(command, work_dir=None):
    """GitHub CLI 명령어 실행"""
    print(f"[DEBUG] GitHub CLI 명령어 실행: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=work_dir
        )
        print(f"[DEBUG] GitHub CLI 실행 결과: {result.stdout}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[DEBUG] GitHub CLI 실행 실패: {e.stderr}")
        raise Exception(f"GitHub CLI 실행 실패: {e.stderr}")

def get_file_url(file_path, branch_name, username, needs_review):
    encoded_path = '/'.join(urllib.parse.quote(component) for component in file_path.split('/'))

    if needs_review:
        return f"github.com/geultto/daily-solvetto/blob/{username}:{branch_name}/{encoded_path}"
    else:
        return f"github.com/geultto/daily-solvetto/blob/main/{encoded_path}"

def create_and_merge_pr(body, problem_name, language, pr_body, needs_review, directory, solution_process, submission_comment, code):
    try:
        print("[DEBUG] 1. 사용자 토큰 읽기 시도")
        user_name = body["user"]["username"]
        with open(f'tokens/{user_name}.csv', 'r') as file:
            reader = csv.reader(file)
            _, user_token = next(reader)
        print(f"[DEBUG] 2. 사용자 토큰 읽기 성공: {user_name}")

        # 브랜치명 생성
        branch_name = f"submit-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        print(f"[DEBUG] 3. 브랜치명 생성: {branch_name}")

        # main 브랜치의 최신 commit SHA 가져오기
        main_sha = run_gh_command([
            "gh", "api",
            f"/repos/{user_name}/daily-solvetto/git/refs/heads/main",
            "--jq", ".object.sha"
        ])
        print(f"[DEBUG] 4. Main 브랜치 SHA 획득: {main_sha}")

        # 새 브랜치 생성
        run_gh_command([
            "gh", "api",
            f"/repos/{user_name}/daily-solvetto/git/refs",
            "-X", "POST",
            "-f", f"ref=refs/heads/{branch_name}",
            "-f", f"sha={main_sha}"
        ])
        print(f"[DEBUG] 5. 브랜치 생성 완료")

        # 파일 생성
        file_path = f"{directory}/{language.lower()}/{problem_name}.{get_file_extension(language)}"
        file_content = base64.b64encode(code.encode()).decode()

        run_gh_command([
            "gh", "api",
            f"/repos/{user_name}/daily-solvetto/contents/{file_path}",
            "-X", "PUT",
            "-f", f"message=Add solution for {problem_name}",
            "-f", f"content={file_content}",
            "-f", f"branch={branch_name}"
        ])
        print(f"[DEBUG] 6. 파일 생성 완료: {file_path}")

        try:
            # PR 생성
            print("[DEBUG] 7. PR 생성 시도")
            pr_url = run_gh_command([
                "gh", "pr", "create",
                "--repo", "geultto/daily-solvetto",
                "--head", f"{user_name}:{branch_name}",
                "--base", "main",
                "--title", f"[{language}] {problem_name}",
                "--body", pr_body
            ])
            print(f"[DEBUG] 8. PR 생성 완료: {pr_url}")

            if needs_review:
                print("[DEBUG] 9. 리뷰 라벨 추가 시도")
                run_gh_command([
                    "gh", "pr", "edit",
                    pr_url,
                    "--add-label", "review required"
                ])
                print("[DEBUG] 10. 리뷰 라벨 추가 완료")
            else:
                print("[DEBUG] 9. PR 머지 시도")
                run_gh_command([
                    "gh", "pr", "merge",
                    pr_url,
                    "--squash",
                    "--auto",
                    "--delete-branch"
                ])
                print("[DEBUG] 10. PR 머지 완료")

            # PR 객체 Mock 생성 (기존 코드와의 호환성)
            class PullRequestMock:
                def __init__(self, url):
                    self.html_url = url

            pr_mock = PullRequestMock(pr_url)

            return {
                'pr': pr_mock,
                'file_url': get_file_url(file_path, branch_name, user_name, needs_review)
            }

        except Exception as e:
            print(f"[DEBUG] Error: PR 처리 실패: {str(e)}")
            raise

    except Exception as e:
        print(f"[DEBUG] Critical Error: {str(e)}")
        raise Exception(f"PR 생성 중 오류 발생: {str(e)}")

def get_file_extension(language):
    return language_extensions_dict.get(language.lower(), "txt")