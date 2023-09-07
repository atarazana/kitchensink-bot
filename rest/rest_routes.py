from rest import rest

from db import add_vote_to_poll, is_poll_open, get_polls_by_status

OPTIONS = ["option_1", "option_2", "option_3"]


@rest.route("/hello", methods=["GET"])
def hello():
    return {"message": "Hello from Flask!"}


@rest.route("/poll/<status>", methods=["GET"])
def polls(status: str):
    return get_polls_by_status(status)


@rest.route("/vote/<poll_name>/<option>", methods=["GET"])
def vote(poll_name: str, option: str):
    print(f"Vote received: {poll_name}/{option}")
    if poll_name and option in OPTIONS:
        try:
            if is_poll_open(poll_name):
                add_vote_to_poll(poll_name, option)
                return {"message": f"Voted option: {option} for poll: {poll_name}"}
            return {"error": f"Poll: {poll_name} is not OPEN or doesn't exist yet"}
        except Exception as e:
            print(f"Error {e}")
            return {"error": f"Error {e}"}

    return {
        "error": "You have to provide a valid poll_name [poll_1, poll_2, ...] "
        "and option [option_1, option_2, option_3] like /vote/poll_1/option_3"
    }
