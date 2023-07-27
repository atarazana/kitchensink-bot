from slack_bolt import App
from .sample_shortcut import sample_shortcut_callback
from .round_1_shortcut import round_1_shortcut_callback


def register(app: App):
    app.shortcut("round_1")(round_1_shortcut_callback)
    app.shortcut("sample_shortcut_id")(sample_shortcut_callback)
