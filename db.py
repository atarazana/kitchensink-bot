import os
import sqlite3
import pandas as pd

DB_PATH = f"{os.environ.get('DB_DIR')}/chatbot.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)

    c = conn.cursor()

    # Create table
    c.execute(
        """CREATE TABLE IF NOT EXISTS users
                 (user text PRIMARY KEY, namespace text, app text)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS polls
                 (poll_name text PRIMARY KEY, status text, option_1 text,
                  option_1_count number, option_2 text, option_2_count number, option_3 text, option_3_count number)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS actions
                 (poll_name text PRIMARY KEY, option number, action text)"""
    )

    # Load polls into a Pandas DataFrame
    polls = pd.read_csv(f'{os.environ.get("DATA_DIR")}/polls.csv')
    # Write the data to a sqlite table
    polls.to_sql("polls", conn, if_exists="replace", index=False)

    # Load actions into a Pandas DataFrame
    actions = pd.read_csv(f'{os.environ.get("DATA_DIR")}/actions.csv')
    # Write the data to a sqlite table
    actions.to_sql("actions", conn, if_exists="replace", index=False)

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


def create_poll(poll_name: str, option_1: str, option_2: str, option_3: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(
        """INSERT
           INTO polls
           (poll_name, status, option_1, option_1_count, option_2, option_2_count, option_3, option_3_count)
           VALUES
           (:poll_name, :status, :option_1, :option_1_count, :option_2, :option_2_count, :option_3, :option_3_count)""",
        {
            "poll_name": poll_name,
            "status": "CLOSED",
            "option_1": option_1,
            "option_1_count": 0,
            "option_2": option_2,
            "option_2_count": 0,
            "option_3": option_3,
            "option_3_count": 0,
        },
    )
    conn.commit()
    conn.close()


def close_poll(poll_name: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute("UPDATE polls SET status=:status WHERE poll_name=:poll_name", {"status": "CLOSED", "poll_name": poll_name})
    conn.commit()
    conn.close()


def open_poll(poll_name: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()

    # This is open to SQL injection to some degree, should be
    c.execute("UPDATE polls SET status=:status WHERE poll_name=:poll_name", {"status": "OPEN", "poll_name": poll_name})
    conn.commit()

    c.execute(
        """SELECT poll_name, status, option_1, option_1_count, option_2, option_2_count, option_3, option_3_count
           FROM polls WHERE poll_name=:poll_name""",
        {"poll_name": poll_name},
    )

    poll = c.fetchone()
    print(f"poll = {poll}")

    conn.close()

    return poll


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_poll(poll_name: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(
        """SELECT poll_name, status, option_1, option_1_count, option_2, option_2_count, option_3, option_3_count
           FROM polls WHERE poll_name=:poll_name""",
        {"poll_name": poll_name},
    )

    poll = c.fetchone()
    print(f"poll = {poll}")

    conn.close()

    return poll


def get_action_by_poll_name_and_option(poll_name: str, option: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(
        """SELECT poll_name, option, action
           FROM actions WHERE poll_name=:poll_name and option=:option""",
        {"poll_name": poll_name, "option": option},
    )

    action = c.fetchone()
    print(f"action = {action}")

    conn.close()

    return action


def add_vote_to_poll(poll_name: str, option: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(f"UPDATE polls SET {option}_count={option}_count+1 WHERE poll_name=:poll_name", {"poll_name": poll_name})
    conn.commit()
    conn.close()


def update_app(app, namespace, user):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(
        "REPLACE INTO users(user, namespace, app) VALUES (:user,  :namespace, :app)",
        {
            "user": user,
            "app": app,
            "namespace": namespace,
        },
    )
    conn.commit()
    conn.close()


def select_app(user: str):
    conn = sqlite3.connect(DB_PATH)

    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute("SELECT app, namespace FROM users WHERE user = (:user)", {"user": user})
    result = c.fetchone()
    if result is not None:
        app = result[0]
        namespace = result[1]
        conn.close()
        return app, namespace
    return None
