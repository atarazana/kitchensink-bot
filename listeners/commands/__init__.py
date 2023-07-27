from slack_bolt import App

from .sample_command import sample_command_callback
from .help_command import help_command_callback
from .poll_command import poll_command_callback


def register(app: App):
    app.command("/sample")(sample_command_callback)
    app.command("/help")(help_command_callback)
    app.command("/poll")(poll_command_callback)
