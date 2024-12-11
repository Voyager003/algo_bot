from usecases.input_token.applications import init_token_handlers
from usecases.post_solution.applications import init_solution_handlers
from usecases.view_user_status.application import init_status_handlers

def initialize_handlers(app):
    init_token_handlers(app)
    init_solution_handlers(app)
    init_status_handlers(app)

def initialize_directories():
    import os
    if not os.path.exists('tokens'):
        os.makedirs('tokens')