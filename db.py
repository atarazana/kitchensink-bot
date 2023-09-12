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

    c.execute(
        """CREATE TABLE IF NOT EXISTS votes
                 (poll_name text, uuid text, option text, PRIMARY KEY (poll_name, uuid))"""
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

    c.execute("UPDATE polls SET status=:status WHERE poll_name=:poll_name", {"status": "CLOSED", "poll_name": poll_name})
    conn.commit()
    conn.close()


def close_polls():
    open_polls = get_polls_by_status("OPEN")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("UPDATE polls SET status=:status", {"status": "CLOSED"})
    conn.commit()
    conn.close()

    return open_polls


def open_poll(poll_name: str):
    open_polls = get_polls_by_status("OPEN")
    if len(open_polls) >= 1:
        poll_names = map(lambda poll: poll["poll_name"], open_polls)
        return None, f"Close {list(poll_names)} before trying to open {poll_name}"

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()

    c.execute(
        """UPDATE polls
            SET status=:status,
                option_1_count=:option_1_count, option_2_count=:option_2_count, option_3_count=:option_3_count
            WHERE poll_name=:poll_name""",
        {"status": "OPEN", "poll_name": poll_name, "option_1_count": 0, "option_2_count": 0, "option_3_count": 0},
    )
    c.execute(
        """DELETE FROM votes
           WHERE poll_name=:poll_name""",
        {"poll_name": poll_name},
    )
    conn.commit()
    conn.close()

    poll = get_poll(poll_name)

    return poll, None


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def count_open_polls():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(
        """SELECT count(*)
           FROM polls WHERE status='OPEN'"""
    )

    count = c.fetchone()[0]
    print(f"open polls = {count}")

    conn.close()

    return count


def is_poll_open(poll_name: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(
        """SELECT poll_name, status
           FROM polls WHERE poll_name=:poll_name""",
        {"poll_name": poll_name},
    )

    poll = c.fetchone()
    print(f"poll = {poll}")

    conn.close()

    if poll is not None:
        return poll["status"] == "OPEN"
    return False


def get_poll(poll_name: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(
        """SELECT poll_name, title, comments, status,
           option_1, option_1_count, option_2, option_2_count, option_3, option_3_count
           FROM polls WHERE poll_name=:poll_name""",
        {"poll_name": poll_name},
    )

    poll = c.fetchone()
    print(f"poll = {poll}")

    conn.close()

    return poll


def get_votes(poll_name: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(
        """SELECT poll_name, uuid, option
           FROM votes WHERE poll_name=:poll_name""",
        {"poll_name": poll_name},
    )

    votes = c.fetchall()
    # print(f"votes = {votes}")

    conn.close()

    return votes


def get_all_polls():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(
        """SELECT poll_name, title, comments, status,
           option_1, option_1_count, option_2, option_2_count, option_3, option_3_count
           FROM polls"""
    )

    polls = c.fetchall()
    # print(f"polls = {polls}")

    conn.close()

    return polls


def get_polls_by_status(status: str):
    if status is None:
        return None

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(
        """SELECT poll_name, title, comments, status,
           option_1, option_1_count, option_2, option_2_count, option_3, option_3_count
           FROM polls WHERE status=:status""",
        {"status": status.upper()},
    )

    polls = c.fetchall()
    # print(f"polls = {polls}")

    conn.close()

    return polls


def get_action_by_poll_name_and_option(poll_name: str, option: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(
        """SELECT poll_name, option, command, txt, image_url
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


def add_vote_to_poll_unique(poll_name: str, uuid: str, option: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # This is open to SQL injection to some degree, should be
    c.execute(f"UPDATE polls SET {option}_count={option}_count+1 WHERE poll_name=:poll_name", {"poll_name": poll_name})
    c.execute(
        "INSERT OR REPLACE INTO votes (poll_name,uuid,option) VALUES (:poll_name,:uuid,:option)",
        {"poll_name": poll_name, "uuid": uuid, "option": option},
    )
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
