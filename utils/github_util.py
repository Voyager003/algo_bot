import csv
import time

from datetime import datetime
from github import Github
from configs import language_extensions_dict

def normalize_path(directory: str, language: str, problem_name: str) -> str:
    try:
        normalized_directory = directory.strip().lower()
        normalized_language = language.strip().lower()
        normalized_problem = problem_name.strip()

        file_path = f"{normalized_directory}/{normalized_language}/{normalized_problem}.{get_file_extension(normalized_language)}"
        print(f"[DEBUG] 경로 정규화: {file_path}")
        return file_path

    except Exception as e:
        raise Exception(f"파일 경로 정규화 실패: {str(e)}")

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

        repo = g_user.get_repo("algotest-org/algobot")
        print(f"[DEBUG] 4. 레포지토리 접근 성공: algotest-org/algobot")

        branch_name = f"feature/algo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        base_branch = repo.get_branch("main")
        print(f"[DEBUG] 5. 브랜치 이름 생성: {branch_name}")

        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_branch.commit.sha
        )
        print("[DEBUG] 6. 새 브랜치 생성 완료")

        # 파일 경로 정규화 적용
        file_path = normalize_path(directory, language, problem_name)
        print(f"[DEBUG] 7. 파일 경로 생성: {file_path}")

        file_result = repo.create_file(
            path=file_path,
            message=f"Add solution for {problem_name}",
            content=code,
            branch=branch_name
        )
        print("[DEBUG] 8. 파일 생성 완료")

        try:
            pr = repo.create_pull(
                title=f"[{language}] {problem_name}",
                body=pr_body,
                head=branch_name,
                base="main"
            )

            # 리뷰 필요 여부에 따라 라벨 추가
            if needs_review:
                try:
                    # 'review required' 라벨 추가
                    review_label = repo.get_label("review required")
                    pr.add_to_labels(review_label)
                    print("[DEBUG] 11. 'review required' 라벨 추가 성공")
                except Exception as e:
                    # 라벨이 없으면 생성
                    try:
                        review_label = repo.create_label(
                            name="review required",
                            color="fbca04",  # 밝은 주황색
                            description="This pull request requires a thorough review"
                        )
                        pr.add_to_labels(review_label)
                        print("[DEBUG] 11a. 'review required' 라벨 생성 및 추가 성공")
                    except Exception as label_error:
                        print(f"[DEBUG] 라벨 추가/생성 실패: {str(label_error)}")

            # 리뷰가 필요하지 않으면 바로 머지
            if not needs_review:
                try:
                    print("[DEBUG] 12. PR 머지 시도")
                    wait_for_mergeable(pr)
                    pr.merge(
                        commit_title=f"Merge: [{language}] {problem_name}",
                        commit_message="Auto-merged by Slack bot",
                        merge_method="squash"
                    )
                    print("[DEBUG] 13. PR 머지 성공")
                except Exception as e:
                    print(f"[DEBUG] Error: PR 머지 실패: {str(e)}")
                    raise Exception(f"PR 머지 중 오류 발생: {str(e)}")

            return pr

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
        pr.update()  # PR 정보 갱신
        if pr.mergeable:
            return True
        time.sleep(interval)

    raise Exception("PR이 머지 가능한 상태가 되지 않았습니다.")

def get_file_extension(language):
    return language_extensions_dict.get(language.lower(), "txt")