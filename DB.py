import sqlite3
from sqlite3 import Error


# Establish Database Connection
def connect(db_file):
    print('Connecting to Eternal Database...')
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        print('Connection Established.')
    except Error as e:
        print(e)
    return connection


# Initialize the database to ensure that it has the tables that are needed
def initialize(db_con):
    sql_create_user_history_table = """ CREATE TABLE IF NOT EXISTS user_history (
                                        id integer PRIMARY KEY,
                                        discord_name text NOT NULL,
                                        server_name text NOT NULL,
                                        event text NOT NULL,
                                        user_name text NOT NULL,
                                        timestamp text NOT NULL
                                    ); """

    sql_create_user_characters_table = """ CREATE TABLE IF NOT EXISTS user_characters (
                                        id integer PRIMARY KEY,
                                        discord_name text NOT NULL,
                                        character text NOT NULL UNIQUE,
                                        timestamp text NOT NULL
                                    ); """
    try:
        c = db_con.cursor()
        c.execute(sql_create_user_history_table)
        c.execute(sql_create_user_characters_table)
    except Error as e:
        print(e)


# Insert a user into the user_history table
def insert_user_history(db_con, discord_name, server, event, user_name, date):
    # Cast all of the parameters to string, in case they were ints or something else.
    discord_name = str(discord_name)
    server = str(server)
    event = str(event)
    user_name = str(user_name)
    date = str(date)

    sql = ''' INSERT INTO user_history(discord_name, server_name, event, user_name, timestamp)
              VALUES(?,?,?,?,?) '''
    cur = db_con.cursor()
    cur.execute(sql, (discord_name, server, event, user_name, date))
    db_con.commit()


# Insert a user a user's alt into the user_characters table
def insert_user_character(db_con, discord_name, character, date):
    # Cast all of the parameters to string, in case they were ints or something else.
    discord_name = str(discord_name)
    character = str(character)
    date = str(date)

    sql = ''' INSERT INTO user_characters(discord_name, character, timestamp)
              VALUES(?,?,?) '''
    cur = db_con.cursor()
    try:
        cur.execute(sql, (discord_name, character, date))
        db_con.commit()
        return False
    except Error as e:
        return True


def search_user_character(db_conn, character):
    results = []
    cur = db_conn.cursor()
    cur.execute("SELECT * FROM user_characters WHERE character=?", (character,))

    rows = cur.fetchall()

    for row in rows:
        results.append(row)
    return results


def search_characters_for_user(db_conn, user):
    results = []
    cur = db_conn.cursor()
    cur.execute("SELECT * FROM user_characters WHERE discord_name=?", (user,))

    rows = cur.fetchall()

    for row in rows:
        results.append(row)
    return results


def count_events_for_user(db_conn, user, event):
    cur = db_conn.cursor()
    cur.execute("SELECT * FROM user_history WHERE discord_name=? AND event=?", (user, event))

    rows = cur.fetchall()
    return str(len(rows))


def get_previous_nicks(db_conn, user, event):
    results = []
    cur = db_conn.cursor()
    cur.execute("SELECT * FROM user_history WHERE discord_name=? AND event=?", (user, event))

    rows = cur.fetchall()
    for row in rows:
        results.append(row[4])
    return ", ".join(results)

