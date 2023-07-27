import re

from slack_bolt import App
from .sample_message import sample_message_callback
from .wildcard_message import wildcard_message_callback


# To receive messages from a channel or dm your app must be a member!
def register(app: App):
    app.message(re.compile(r"logs\s.*"))(wildcard_message_callback)
    app.message(re.compile(r"(hi|hello|hey)"))(sample_message_callback)
