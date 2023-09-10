from rest import rest

from db import add_vote_to_poll_unique, is_poll_open, get_polls_by_status

OPTIONS = ["option_1", "option_2", "option_3"]


@rest.route("/hello", methods=["GET"])
def hello():
    return {"message": "Hello from Flask!"}


@rest.route("/poll/<status>", methods=["GET"])
def polls(status: str):
    return get_polls_by_status(status)


@rest.route("/vote/<poll_name>/<uuid>/<option>", methods=["GET"])
def vote(poll_name: str, uuid: str, option: str):
    print(f"Vote received: {poll_name}/{uuid}/{option}")
    if poll_name and uuid and option in OPTIONS:
        try:
            if is_poll_open(poll_name):
                add_vote_to_poll_unique(poll_name, uuid, option)
                return {"message": f"Voted uuid: {uuid} with option: {option} for poll: {poll_name}"}
            return {"error": f"Poll: {poll_name} is not OPEN or doesn't exist yet"}
        except Exception as e:
            print(f"Error {e}")
            return {"error": f"Error {e}"}

    return {
        "error": "You have to provide a valid poll_name [poll_1, poll_2, ...] "
        "a uuid and option in [option_1, option_2, option_3] like /vote/poll_1/YOUOJJG9/option_3"
    }
