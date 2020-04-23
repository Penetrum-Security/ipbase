import sqlite3

import lib.settings


def init_sql():
    """
    initialize the SQL database so that we store to it
    :return:
    """
    cursor = sqlite3.connect(lib.settings.IP_DATABASE_PATH)
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS `ip_rep` ("
        "`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
        "`ip_address` TEXT NOT NULL"
        ")"
    )
    conn = sqlite3.connect(lib.settings.IP_DATABASE_PATH, isolation_level=None, check_same_thread=False)
    return conn.cursor()


def fetch(cursor):
    """
    fetch all the data in the database
    """
    data = cursor.execute("SELECT * FROM ip_rep")
    return data.fetchall()


def insert(data, cursor):
    """
    insert into the database
    """
    is_inserted = False
    try:
        current = fetch(cursor)
        i = len(current) + 1
        for item in current:
            _, cache = item
            if data == cache:
                is_inserted = True
        if not is_inserted:
            cursor.execute("INSERT INTO ip_rep (id, ip_address) VALUES (?, ?)", (i, data))
    except Exception as e:
        print e
        return False
    return True
