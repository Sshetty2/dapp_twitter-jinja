#!/usr/bin/env python3

import sqlite3
import time
import hashlib
import uuid
from datetime import datetime
from pytz import timezone

fmt = '%I:%M:%S %m-%d-%Y'
eastern = timezone('US/Eastern')
naive_dt = datetime.now()
loc_dt = datetime.now(eastern)
date_now = naive_dt.strftime(fmt)




CON = None
CUR = None


def calculatehash(password):
    hashobject = hashlib.sha256()
    salt = "!$33gl3d33g"
    saltedstring = password.encode() + salt.encode()
    hashobject.update(saltedstring)
    return hashobject.hexdigest()


def setup(dbname="master.db"):
    global CON
    global CUR
    CON = sqlite3.connect(dbname)
    CUR = CON.cursor()





def run():
    SQL = "DELETE FROM users;"
    CUR.execute(SQL)

    SQL = "DELETE FROM sqlite_sequence WHERE name = 'users';"
    CUR.execute(SQL)

    SQL = """INSERT INTO users(username, pass_hash, type)
    VALUES(?, ?, ?);"""
    pw_hash = calculatehash("password")
    CUR.execute(SQL, ("sshetty", pw_hash, 'USER'))
    CUR.execute(SQL, ("admin", pw_hash,'ADMIN'))
   
    SQL = "DELETE FROM tweets;"
    CUR.execute(SQL)

    SQL = "DELETE FROM sqlite_sequence WHERE name = 'tweets';"
    CUR.execute(SQL)

    SQL = """INSERT INTO tweets(users_pk, username, content, time) 
    VALUES(?, ?, ?, ?);"""
    CUR.execute(SQL, (1, "sshetty", "Hello, This is the first tweet", date_now))
    CUR.execute(SQL, (1, "sshetty", "This is the second tweet", date_now))


    CON.commit()
    CUR.close()
    CON.close()


if __name__ == "__main__":
    setup()
    run()
