import os
import re
import subprocess

from slack_bolt import Ack, Respond
from logging import Logger

from slack_sdk import WebClient
from slack_sdk.models.blocks import SectionBlock

from db import get_action_by_poll_name_and_option, get_poll, close_poll, open_poll, create_poll

POLL_OPEN_EXAMPLE_CALL = "/poll open my_poll [Delete Limit,Delete Quota,Delete all]"
POLL_CLOSE_EXAMPLE_CALL = "/poll close my_poll"
POLL_REOPEN_EXAMPLE_CALL = "/poll reopen my_poll"
POLL_GET_EXAMPLE_CALL = "/poll get my_poll"

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))


def poll_command_callback(command, ack: Ack, respond: Respond, logger: Logger):
    try:
        ack()
        logger.info(f" command => {command}")

        verb_pattern = r"(open|close|reopen|get)\s+(.*)"
        verb_match = re.search(verb_pattern, command["text"])

        if verb_match:
            verb = verb_match.group(1)
            subject = verb_match.group(2)
            logger.debug(f" verb => {verb} subject => {subject}")

            match verb.lower():
                case "create":
                    (poll_name, option_1, option_2, option_3) = extract_args_create(subject, logger)
                    respond(f"Creating poll {poll_name}")
                    create_poll(poll_name, option_1, option_2, option_3)
                    respond(
                        f"Poll {poll_name} created but closed:\n- :two: {option_1}\n- :one: {option_2}\n- :three: {option_3}"
                    )
                case "open":
                    (poll_name) = extract_args_open(subject, logger)
                    respond(f"Opening poll {poll_name}")
                    poll = open_poll(poll_name)
                    client.chat_postMessage(
                        channel=command["channel_name"],
                        text=f"Poll {poll['poll_name']} opened for voting:\n- :one: {poll['option_1']}\n- :two: {poll['option_2']}\n- :three: {poll['option_3']}",
                    )
                case "close":
                    poll_name = extract_args_close(subject, logger)
                    respond(f"Closing poll {poll_name}")
                    poll = get_poll(poll_name)
                    if poll is not None:
                        close_poll(poll_name)
                        counts = poll["option_1_count"], poll["option_2_count"], poll["option_3_count"]
                        winner_option = counts.index(max(counts)) + 1
                        client.chat_postMessage(
                            channel=command["channel_name"],
                            text=f"Poll {poll_name} closed, the winner is option {winner_option}",
                        )
                        action = get_action_by_poll_name_and_option(poll_name, winner_option)
                        client.chat_postMessage(
                            channel=command["channel_name"],
                            text=f"Running {action['action']}",
                        )
                        cmd = action["action"]
                        logger.debug(f"Executing {cmd}")
                        (returncode, stdout, stderr) = execute_shell_command(cmd)
                        respond(blocks=blocks_for_cmd_result(returncode, stdout, stderr))
                    else:
                        respond(f"No such a poll named {poll_name}")
                case "get":
                    poll_name = extract_args_get(subject, logger)
                    respond(f"Getting poll {poll_name}")
                    poll = get_poll(poll_name)
                    if poll is not None:
                        respond(
                            f"Poll {poll['poll_name']} is {poll['status']}:\n- :one: {poll['option_1']}\n- :two: {poll['option_2']}\n- :three: {poll['option_3']}"
                        )
                    else:
                        respond(f"No such a poll named {poll_name}")
                case _:
                    client.chat_postMessage(
                        channel=command["channel_name"],
                        text="Poll command not found!",
                    )
        else:
            logger.error("Poll command not found!")
            respond(f"Malformed command: /poll {command['text']}")
    except Exception as e:
        logger.error(e)
        respond(f"Error command: /poll {command['text']} failed with this error: {e}")


def extract_args_create(subject: str, logger: Logger):
    pattern = r"(\w+)\s+\[(.+),(.+),(.+)\]"
    match = re.search(pattern, subject)

    if match:
        poll_name = match.group(1).lstrip().rstrip()
        option_1 = match.group(2).lstrip().rstrip()
        option_2 = match.group(3).lstrip().rstrip()
        option_3 = match.group(4).lstrip().rstrip()
        logger.debug(f"poll_name => {poll_name} option_1 => {option_1} option_2 => {option_2} option_3 => {option_3}")
    else:
        raise Exception(f"Arguments malformed for '/poll open' try this instead: {POLL_OPEN_EXAMPLE_CALL}")

    return (poll_name, option_1, option_2, option_3)


def extract_args_close(subject: str, logger: Logger):
    pattern = r"(\w+)"
    match = re.search(pattern, subject)

    if match:
        poll_name = match.group(1).lstrip().rstrip()
        logger.debug(f"poll_name => {poll_name}")
    else:
        raise Exception(f"Arguments malformed for '/poll close' try this instead: {POLL_CLOSE_EXAMPLE_CALL}")

    return poll_name


def extract_args_open(subject: str, logger: Logger):
    pattern = r"(\w+)"
    match = re.search(pattern, subject)

    if match:
        poll_name = match.group(1).lstrip().rstrip()
        logger.debug(f"poll_name => {poll_name}")
    else:
        raise Exception(f"Arguments malformed for '/poll reopen' try this instead: {POLL_REOPEN_EXAMPLE_CALL}")

    return poll_name


def extract_args_get(subject: str, logger: Logger):
    pattern = r"(\w+)"
    match = re.search(pattern, subject)

    if match:
        poll_name = match.group(1).lstrip().rstrip()
        logger.debug(f"poll_name => {poll_name}")
    else:
        raise Exception(f"Arguments malformed for '/poll get' try this instead: {POLL_GET_EXAMPLE_CALL}")

    return poll_name


def execute_shell_command(command):
    try:
        # Execute the shell command and capture the output and errors
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=2)

        return (result.returncode, result.stdout, result.stderr)
    except subprocess.CalledProcessError as e:
        # An error occurred while executing the command
        print(f"Command execution failed with return code {e.returncode}")
        print(f"Error output: {e.output}")


def blocks_for_cmd_result(returncode, stdout, stderr):
    blocks = [SectionBlock(text=f"*Result* after running latest command with *code({returncode})*:")]
    if stdout:
        blocks.append(SectionBlock(text=f"*Output:* {stdout}"))
    if stderr:
        blocks.append(SectionBlock(text=f"*Error:* {stderr}"))
    return blocks
