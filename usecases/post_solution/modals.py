from utils.slack_util import show_modal
from configs import language_extensions_dict

def show_select_review_required_modal(body ,client, callback_id):
    show_modal(
        body=body,
        client=client,
        callback_id=callback_id,
        title="알고리즘 풀이 제출",
        submit_title="다음",
        blocks=[
            {
                "type": "input",
                "block_id": "need_review",
                "element": {
                    "type": "radio_buttons",
                    "action_id": "review_select",
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "예! 리뷰가 필요해요"},
                            "value": "yes"
                        },
                        {
                            "text": {"type": "plain_text", "text": "아니요~ 괜찮아요"},
                            "value": "no"
                        }
                    ]
                },
                "label": {"type": "plain_text", "text": "코드 리뷰가 필요하신가요?"}
            }
        ],
    )

def show_post_solution_with_review_modal(body ,client, callback_id):
    show_modal(
        body=body,
        client=client,
        callback_id=callback_id,
        title="알고리즘 풀이 제출",
        submit_title="제출",
        blocks=[
            {
                "type": "input",
                "block_id": "directory_name",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "directory_input",
                    "placeholder": {"type": "plain_text", "text": "영문이름을 입력해주세요."}
                },
                "label": {"type": "plain_text", "text": "영문이름"}
            },
            {
                "type": "input",
                "block_id": "problem_name",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "problem_input",
                    "placeholder": {"type": "plain_text", "text": "문제 이름을 입력하세요"}
                },
                "label": {"type": "plain_text", "text": "문제"}
            },
            {
                "type": "input",
                "block_id": "problem_link",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "link_input",
                    "placeholder": {"type": "plain_text", "text": "문제 링크를 입력하세요"}
                },
                "label": {"type": "plain_text", "text": "문제 링크"}
            },
            {
                "type": "input",
                "block_id": "language",
                "element": {
                    "type": "static_select",
                    "action_id": "language_select",
                    "placeholder": {"type": "plain_text", "text": "언어를 선택하세요"},
                    "options": [
                        {"text": {"type": "plain_text", "text": lang}, "value": lang.lower()}
                        for lang in language_extensions_dict.keys()
                    ]
                },
                "label": {"type": "plain_text", "text": "언어"}
            },
            {
                "type": "input",
                "block_id": "code",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "code_input",
                    "multiline": True,
                    "placeholder": {"type": "plain_text", "text": "코드를 입력하세요"}
                },
                "label": {"type": "plain_text", "text": "코드"}
            },
            {
                "type": "input",
                "block_id": "solution_process",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "process_input",
                    "multiline": True,
                    "placeholder": {"type": "plain_text", "text": "문제 풀이 과정을 설명해주세요"}
                },
                "label": {"type": "plain_text", "text": "풀이 과정"}
            },
            {
                "type": "input",
                "block_id": "review_request",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "request_input",
                    "multiline": True,
                    "placeholder": {"type": "plain_text", "text": "중점적으로 리뷰받고 싶은 부분을 적어주세요."}
                },
                "label": {"type": "plain_text", "text": "리뷰 요청 사항"}
            },
            {
                "type": "input",
                "block_id": "submission_comment",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "comment_input",
                    "multiline": True,
                    "placeholder": {"type": "plain_text", "text": "제출 코멘트를 입력해주세요"}
                },
                "label": {"type": "plain_text", "text": "제출 코멘트"}
            }
        ],
    )

def show_post_solution_without_review_modal(body ,client, callback_id):
    show_modal(
        body=body,
        client=client,
        callback_id=callback_id,
        title="알고리즘 풀이 제출",
        submit_title="제출",
        blocks=[
                {
                    "type": "input",
                    "block_id": "directory_name",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "directory_input",
                        "placeholder": {"type": "plain_text", "text": "영문이름을 입력해주세요."}
                    },
                    "label": {"type": "plain_text", "text": "영문이름"}
                },
                {
                    "type": "input",
                    "block_id": "problem_name",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "problem_input",
                        "placeholder": {"type": "plain_text", "text": "문제 이름을 입력하세요"}
                    },
                    "label": {"type": "plain_text", "text": "문제"}
                },
                {
                    "type": "input",
                    "block_id": "problem_link",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "link_input",
                        "placeholder": {"type": "plain_text", "text": "문제 링크를 입력하세요"}
                    },
                    "label": {"type": "plain_text", "text": "문제 링크"}
                },
                {
                    "type": "input",
                    "block_id": "language",
                    "element": {
                        "type": "static_select",
                        "action_id": "language_select",
                        "placeholder": {"type": "plain_text", "text": "언어를 선택하세요"},
                        "options": [
                            {"text": {"type": "plain_text", "text": lang}, "value": lang.lower()}
                            for lang in language_extensions_dict.keys()
                        ]
                    },
                    "label": {"type": "plain_text", "text": "언어"}
                },
                {
                    "type": "input",
                    "block_id": "code",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "code_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "코드를 입력하세요"}
                    },
                    "label": {"type": "plain_text", "text": "코드"}
                },
                {
                    "type": "input",
                    "block_id": "solution_process",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "process_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "문제 풀이 과정을 설명해주세요"}
                    },
                    "label": {"type": "plain_text", "text": "풀이 과정"}
                },
                {
                    "type": "input",
                    "block_id": "submission_comment",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "comment_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "제출 코멘트를 입력해주세요"}
                    },
                    "label": {"type": "plain_text", "text": "제출 코멘트"}
                }
            ],
    )

