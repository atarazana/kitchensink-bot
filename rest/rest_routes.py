from rest import rest

from db import add_vote_to_poll, is_poll_open

OPTIONS = ['option_1', 'option_2', 'option_3']

@rest.route('/hello', methods=['GET'])
def hello():
    return 'Hello from Flask!'

@rest.route('/vote/<poll_name>/<option>', methods=['GET'])
def vote(poll_name: str, option: str):
    if poll_name and option in OPTIONS:
        try:
            if is_poll_open(poll_name):
                add_vote_to_poll(poll_name,option)
                return f"Voted option: {option} for poll: {poll_name}"
            return f"Poll: {poll_name} is not OPEN or doesn't exist yet"
        except Exception as e:
          print(f"Error {e}")
          return f"Error {e}"

    return "You have to provide a valid poll_name [poll_1, poll_2, ...] and option [option_1, option_2, option_3] like /vote/poll_1/option_3"