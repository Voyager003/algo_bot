from usecases.post_solution.service import handle_submission
from utils.error_handler import print_error
from usecases.post_solution.modals import show_select_review_required_modal, show_post_solution_with_review_modal, show_post_solution_without_review_modal

import time

def init_solution_handlers(app):
    @app.command("/알고풀이")
    def handle_submit_command(ack, body, client):
        ack()

        try:
            show_select_review_required_modal(body, client, callback_id="review_selection")
        except Exception as e:
            print_error(body, client, f"Modal 생성 중 오류가 발생했습니다: {str(e)}")

    @app.view("review_selection")
    def handle_review_selection(ack, body, client):
        ack()
        need_review = body["view"]["state"]["values"]["need_review"]["review_select"]["selected_option"]["value"] == "yes"

        try:
            time.sleep(1.5)

            if need_review:
                show_post_solution_with_review_modal(body, client, callback_id="submission_with_review")
            else:
                show_post_solution_without_review_modal(body, client, callback_id="submission_without_review")
        except Exception as e:
            print_error(body, client, f"Modal 전환 중 오류가 발생했습니다: {str(e)}")

    @app.view("submission_with_review")
    def handle_review_submission(ack, body, view, client):
        ack()
        handle_submission(body, view, client, needs_review=True)

    @app.view("submission_without_review")
    def handle_no_review_submission(ack, body, view, client):
        ack()
        handle_submission(body, view, client, needs_review=False)