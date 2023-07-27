from slack_bolt import App

from .show_round_1_action import show_round_1_action_callback
from .sample_action import sample_action_callback


def register(app: App):
    app.action("sample_action_id")(sample_action_callback)
    app.action("show_round_1_action_id")(show_round_1_action_callback)
