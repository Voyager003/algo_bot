# Algo Bot 🤖

알고리즘 스터디를 위한 Slack Bot입니다. GitHub PR 생성, 코드 리뷰 요청, 스트릭 관리 등 알고리즘 스터디에 필요한 기능을 제공합니다.

## Features 🌟

### GitHub 토큰 등록 `/알고토큰`
- GitHub 토큰 등록 및 관리
- 사용자별 토큰 보안 저장
- PR 생성을 위한 인증 관리

### 알고리즘 풀이 제출 `/알고풀이`
- 문제 풀이 코드 제출
- 코드 리뷰 요청 옵션
- 자동 GitHub PR 생성 및 병합
- 다양한 프로그래밍 언어 지원

### 스트릭 조회 `/알고조회`
- 주간 알고리즘 풀이 현황 확인
- 연속 제출 스트릭 관리
- 포인트 시스템
- 통계 데이터 제공

## Project Structure 📁

```
algo_bot/
├── key/                  # GitHub App private-key
├── streak/               # 스트릭 데이터
├── tokens/               # 사용자 GitHub 토큰
├── usecases/            # 비즈니스 로직
│   ├── input_token/     # 토큰 입력 관련
│   ├── post_solution/   # 풀이 제출 관련
│   └── view_user_status/ # 사용자 상태 조회
└── utils/               # 유틸리티 함수
```

## Prerequisites 🔧

- Python 3.8+
- Slack Bot Token
- Slack App Token
- GitHub App 설정
    - Private Key
    - App ID
    - Installation ID

## Installation 🚀

1. 저장소 클론

```bash
git clone https://github.com/Voyager003/algo_bot.git
cd algo_bot
```

2. 가상환경 설정

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
cp .env.sample .env 
```

## Usage 💻

### 1. GitHub 토큰 등록
```
/알고토큰
```
- GitHub Personal Access Token 입력
- Repository 접근 권한 필요

### 2. 알고리즘 풀이 제출
```
/알고풀이
```
1. 코드 리뷰 필요 여부 선택
2. 사용자 정보 입력
3. 문제 정보 및 코드 입력
4. 풀이 과정 및 코멘트 작성

### 3. 스트릭 조회
```
/알고조회
```
- 주간 풀이 현황 확인
- 스트릭 및 포인트 확인

## Development 🛠

### Core Features

1. **토큰 관리**
    - `input_token/` : GitHub 토큰 입력 및 관리
    - CSV 파일 기반 토큰 저장

2. **풀이 제출**
    - `post_solution/` : 알고리즘 풀이 제출 프로세스
    - GitHub PR 자동화
    - 리뷰 요청 관리

3. **사용자 상태**
    - `view_user_status/` : 스트릭 및 통계 관리
    - CSV 기반 데이터 저장

### Utilities

- `directory_util.py` : 디렉토리 관리
- `error_handler.py` : 에러 처리
- `github_util.py` : GitHub API 연동
- `slack_util.py` : Slack API 연동
- `status_util.py` : 상태 관리

## Contributing 🤝

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License 📝

[MIT License](LICENSE)