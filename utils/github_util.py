import csv
import time
import os
import urllib.parse

from datetime import datetime
from github import Github
from configs import language_extensions_dict

def get_file_url(archive_repo, file_path, branch_name, needs_review):
    encoded_path = '/'.join(urllib.parse.quote(component) for component in file_path.split('/'))

    if needs_review:
        return f"github.com/geultto/daily-solvetto/blob/{branch_name}/{encoded_path}"
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

        g_user = Github(user_token)
        github_user = g_user.get_user()
        github_username = github_user.login
        print(f"[DEBUG] 3. GitHub 사용자 정보 획득: {github_username}")

        # 사용자의 fork된 레포지토리 접근
        user_fork = g_user.get_repo(f"{github_username}/daily-solvetto")
        print(f"[DEBUG] 4. Fork된 레포지토리 접근: {github_username}/daily-solvetto")

        # 새 브랜치 생성
        branch_name = f"feature/algo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        base_branch = user_fork.get_branch("main")
        user_fork.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_branch.commit.sha
        )
        print(f"[DEBUG] 5. 새 브랜치 생성: {branch_name}")

        # 파일 생성
        file_path = f"{directory}/{language.lower()}/{problem_name}.{get_file_extension(language)}"
        print(f"[DEBUG] 6. 파일 경로 생성: {file_path}")

        user_fork.create_file(
            path=file_path,
            message=f"Add solution for {problem_name}",
            content=code,
            branch=branch_name
        )
        print("[DEBUG] 7. 파일 생성 완료")

        # GitHub UI를 통한 PR 생성 URL 생성
        encoded_title = urllib.parse.quote(f"[{language}] {problem_name}")
        encoded_body = urllib.parse.quote(pr_body)
        compare_url = (
            f"https://github.com/geultto/daily-solvetto/compare/main..."
            f"{github_username}:{branch_name}?quick_pull=1"
            f"&title={encoded_title}&body={encoded_body}"
        )
        print(f"[DEBUG] 8. PR 생성 URL 생성: {compare_url}")

        file_url = f"github.com/{github_username}/daily-solvetto/blob/{branch_name}/{file_path}"

        return {
            'pr_url': compare_url,
            'file_url': file_url,
            'branch_name': branch_name
        }

    except Exception as e:
        print(f"[DEBUG] Critical Error: {str(e)}")
        raise Exception(f"PR 생성 중 오류 발생: {str(e)}")

def _handle_review_labels(repo, pr):
    """리뷰 라벨 처리"""
    try:
        print("[DEBUG] 리뷰 라벨 처리 - 라벨 확인")
        try:
            review_label = repo.get_label("review required")
            print("[DEBUG] 기존 'review required' 라벨 찾음")
        except:
            review_label = repo.create_label(
                name="review required",
                color="d4c5f9",
                description="리뷰가 필요한 PR"
            )
            print("[DEBUG] 새 'review required' 라벨 생성")

        pr.add_to_labels(review_label)
        print("[DEBUG] 'review required' 라벨 추가 완료")
    except Exception as e:
        print(f"[DEBUG] Warning: 라벨 처리 중 오류 발생: {str(e)}")

def _handle_pr_merge(pr, language, problem_name):
    """PR 머지 처리"""
    try:
        print("[DEBUG] 머지 가능 상태 확인 시작")
        if wait_for_mergeable(pr):
            print("[DEBUG] 머지 가능 상태 확인됨, 머지 시도")
            pr.merge(
                commit_title=f"Merge: [{language}] {problem_name}",
                commit_message="Auto-merged by Slack bot",
                merge_method="squash"
            )
            print("[DEBUG] 머지 완료")
        else:
            print("[DEBUG] Error: PR이 머지 가능한 상태가 아님")
            raise Exception("PR이 머지 가능한 상태가 아닙니다")
    except Exception as e:
        print(f"[DEBUG] Error: PR 머지 실패: {str(e)}")
        raise Exception(f"PR 머지 실패: {str(e)}")

def wait_for_mergeable(pr, timeout=30, interval=2):
    """PR이 머지 가능한 상태가 될 때까지 대기"""
    print(f"[DEBUG] 머지 가능 상태 대기 시작 (최대 {timeout}초)")
    start_time = time.time()
    while time.time() - start_time < timeout:
        pr.update()
        print(f"[DEBUG] PR 상태 확인: mergeable={pr.mergeable}")
        if pr.mergeable:
            return True
        time.sleep(interval)
    print("[DEBUG] 머지 가능 상태 대기 시간 초과")
    return False

def get_file_extension(language):
    """언어에 따른 파일 확장자 반환"""
    return language_extensions_dict.get(language.lower(), "txt")