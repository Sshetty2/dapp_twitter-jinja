#!/usr/bin/env python3

import sqlite3
import time
import hashlib
import uuid
import os.path
from datetime import datetime
from pytz import timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "./datastores/master.db")

fmt = '%I:%M:%S %m-%d-%Y'
eastern = timezone('US/Eastern')
naive_dt = datetime.now()
loc_dt = datetime.now(eastern)
date_now = naive_dt.strftime(fmt)

CONFIG = {
    'DBNAME': db_path,
    'SALT': "!$33gl3d33g"
}

DBNAME = "master.db"

## ---- REST API ENDPOINT FUNCTION CALLS --- ##

def validate_pw(userid, password):
    
    try: 
        user_object = set_user_object(userid)
    except:
        return "username error"
    pass_hash = user_object.pass_hash
    if user_object.check_password(pass_hash, password):
        return "success"
    return "password error"

def create_new_user(userid, password, user_type):
    try:
        user_object = Account(username=userid)
    except:
        return "username error"
    if user_object.check_set_username():
        return "userid already exists"
    hashed_pw = user_object.calculatehash(password)
    user_object.pass_hash = hashed_pw
    user_object.type = user_type
    user_object.save()

def create_new_user_query(userid, password, user_type):
    try:
        user_object = Account(username=userid)
    except:
        return "username error"
    if user_object.check_set_username():
        return "userid already exists"
    hashed_pw = user_object.calculatehash(password)
    user_object.pass_hash = hashed_pw
    user_object.type = user_type
    user_object.save()

    


def set_user_object(username):
    user_object = Account(username=username)
    user_object = user_object.set_from_username()
    return user_object

def set_user_object_from_pk(pk):
    user_object = Account(pk=pk)
    user_object = user_object.set_from_pk()
    return user_object


##TODO:
def create_tweet(username, tweet):
    user_object = Account(username=username)
    user_object = user_object.set_from_username()
    comment_obj= Tweet(pk=None, users_pk=user_object.pk, username=username, content=tweet, time=None)
    comment_obj.save()
    return True

##TODO:
def get_all_tweets():
    user_object = Account()
    all_tweets = user_object.getalltweets_array()
    return all_tweets

def read_all_tweets(username):
    user_object = Account(username=username)
    user_object = user_object.set_from_username()
    all_tweets = user_object.gettweets_array()
    return all_tweets

def copy_tweet(username, retweet_pk):
    tweet = read_tweet(retweet_pk)
    create_tweet(username, tweet)
    return True

## unreasonably long code because of a lack of a followed class)

def follow_user(username, user_to_follow_pk):
    user_to_follow_object = set_user_object(user_to_follow_pk)
    username_object = set_user_object(username)
    users_pk = username_object.pk
    username = username_object.username
    followed_pk = user_to_follow_object.pk
    followed_username = user_to_follow_object.username
    try:
        with OpenCursor() as cur:
            SQL = """
            INSERT INTO users_followed(users_pk, username, followed_pk, followed_username)
            VALUES(?, ?, ?, ?);
            """
            cur.execute(SQL, (users_pk, username, followed_pk, followed_username))
            pk = cur.lastrowid
        return True
    except:
        return False

def test_followed_object(username, user_to_follow):
    try:
        user_to_follow_object = set_user_object(user_to_follow)
        username_object = set_user_object(username)
        username_pk = username_object.pk
        user_to_follow_pk = user_to_follow_object.pk
        with OpenCursor() as cur:
            SQL = """
            SELECT * FROM users_followed WHERE users_pk = ? AND followed_pk = ?;
            """
            cur.execute(SQL, (username_pk, user_to_follow_pk))
            row=cur.fetchone()
        if row:
            return True
        return False
    except:
        return False
        

def read_tweet(retweet_pk):
    tweet_object = Tweet(pk=retweet_pk)
    tweet_object = tweet_object.set_from_pk()
    return tweet_object.content


def get_all_users():
    user_object = Account()
    all_tweets = user_object.getallusers_array()
    return all_tweets



class OpenCursor:
    def __init__(self, *args, **kwargs):
        # update:
        if 'dbname' in kwargs:
            self.dbname = kwargs['dbname']
            del(kwargs['dbname'])
        else:
            self.dbname = CONFIG['DBNAME']

        self.conn = sqlite3.connect(self.dbname, *args, **kwargs)
        self.conn.row_factory = sqlite3.Row  # access fetch results by col name
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, extype, exvalue, extraceback):
        if not extype:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()


class Account:
    def __init__(self, pk=None, username=None, pass_hash=None, user_type= None):
        self.pk = pk
        self.username = username
        self.pass_hash = pass_hash
        self.type = user_type

    def __str__(self):
        display =f"PK = {self.pk}, username = {self.username}, pass hash = {self.pass_hash}, user type = {self.type}"
        return display
    
    def __repr__(self):
        display =f"PK = {self.pk}, username = {self.username}, pass hash = {self.pass_hash}, user type = {self.type}"
        return display

    #def getposition(self, pk):

    def save(self):
        with OpenCursor() as cur:
            if not self.pk:
                SQL = """
                INSERT INTO users(username, pass_hash, type)
                VALUES(?, ?, ?);
                """
                cur.execute(SQL, (self.username, self.pass_hash, self.type))
                self.pk = cur.lastrowid

            else:
                SQL = """
                UPDATE users SET username=?, pass_hash=?, type=? WHERE
                pk=?;
                """
                cur.execute(SQL, (self.username, self.pass_hash, self.type))

    def calculatehash(self, password):
        hashobject = hashlib.sha256()
        salt = CONFIG['SALT']
        saltedstring = password.encode() + salt.encode()
        hashobject.update(saltedstring)
        return hashobject.hexdigest()

    def check_password(self, hashed_password, user_password):
        hashobject = hashlib.sha256()
        salt = CONFIG['SALT']
        new_salted_string = user_password.encode() + salt.encode()
        hashobject.update(new_salted_string)
        new_hashed_pw = hashobject.hexdigest()
        if hashed_password == new_hashed_pw:
            return True
        return False

    def set_from_row(self, row):
        self.pk = row["pk"]
        self.username = row["username"]
        self.pass_hash = row["pass_hash"]
        self.type = row["type"]
        return self
    
    def check_set_username(self):
        try:
            with OpenCursor() as cur: 
                SQL = """
                SELECT * FROM users WHERE username = ?;
                """
                cur.execute(SQL, (self.username, ))
                row=cur.fetchone()   
            if not row:
                return False
            self.set_from_row(row)
            # if the username is found, the attributes are set 
            return True
        except:
            return False
    
    def set_from_username(self):
        with OpenCursor() as cur: 
            SQL = """
            SELECT * FROM users WHERE username = ?;
            """
            cur.execute(SQL, (self.username, ))
            row=cur.fetchone()  
        self.set_from_row(row)
        return self
    
    def set_from_pk(self):
        with OpenCursor() as cur: 
            SQL = """
            SELECT * FROM users WHERE pk = ?;
            """
            cur.execute(SQL, (self.pk, ))
            row=cur.fetchone()  
        self.set_from_row(row)
        return self

    def create_tweet(self, username, tweet):
        with OpenCursor() as cur:
            SQL = """
            SELECT * FROM tweets WHERE users_pk = ?;
            """

    # def get_all_tweets(self):
    #     with OpenCursor() as cur:
    #         SQL = """
    #         SELECT * FROM tweets WHERE users_pk = ?;
    #         """
    #         cur.execute(SQL, (self.pk, ))
    #         rows = cur.fetchall()
    #         results = []
    #         for row in rows: 
    #             acc = Tweet()
    #             acc.set_from_row(row)
    #             results.append(acc)
    #         return results

    def gettweets_array(self):
        with OpenCursor() as cur:
            SQL = """
            SELECT DISTINCT tweets.pk, tweets.users_pk, tweets.username, tweets.content, tweets.time
            FROM tweets
            JOIN users_followed
            ON users_followed.followed_pk =  tweets.users_pk
            WHERE users_followed.users_pk = ?
            UNION ALL
            SELECT * FROM tweets WHERE users_pk = ?
            ORDER BY time DESC;
            """
            cur.execute(SQL, (self.pk, self.pk))
            rows = cur.fetchall()
            results = []
            for row in rows:
                row_place = []
                row_place.append(row["pk"]) 
                row_place.append(row["users_pk"])
                row_place.append(row["username"])
                row_place.append(row["content"])  
                row_place.append(row["time"]) 
                results.append(row_place)
            return results

    def getalltweets_array(self):
        with OpenCursor() as cur:
            SQL = """
            SELECT * FROM tweets;
            """
            cur.execute(SQL)
            rows = cur.fetchall()
            results = []
            for row in rows:
                row_place = []
                row_place.append(row["pk"]) 
                row_place.append(row["users_pk"])
                row_place.append(row["username"])
                row_place.append(row["content"])  
                row_place.append(row["time"]) 
                results.append(row_place)
            return results

    def getallusers_array(self):
        with OpenCursor() as cur:
            SQL = """
            SELECT * FROM users;
            """
            cur.execute(SQL)
            rows = cur.fetchall()
            results = []
            for row in rows:
                row_place = []
                row_place.append(row["pk"]) 
                row_place.append(row["username"])
                row_place.append(row["pass_hash"])
                row_place.append(row["type"])   
                results.append(row_place)
            return results

class Tweet:
    def __init__(self, users_pk=None, username = None, pk=None, content=None, time=None):
        self.pk = pk
        self.users_pk = users_pk
        self.username = username
        self.content = content
        self.time = time

    #def getposition(self, pk):

    def save(self):
        if self.time is None:
            self.time = date_now
        with OpenCursor() as cur:
            if not self.pk:
                SQL = """
                INSERT INTO tweets(users_pk, username, content, time)
                VALUES(?, ?, ?, ?);
                """
                cur.execute(SQL, (self.users_pk, self.username, self.content, self.time))
                self.pk = cur.lastrowid

            else:
                SQL = """
                UPDATE tweets SET users_pk=?, username=?, content=?, time=? WHERE
                pk=?;
                """
                cur.execute(SQL, (self.users_pk, self.username, self.content, self.time))
    
    def __repr__(self):
        display =f"PK = {self.pk}, users pk = {self.users_pk}, username = {self.username}, content = {self.content}, time = {self.time}"
        return display
    
    def __str__(self):
        display =f"PK = {self.pk}, user name = {self.username}, content = {self.content}, time = {self.time}"
        return display
    
    def set_from_pk(self):
        with OpenCursor() as cur: 
            SQL = """
            SELECT * FROM tweets WHERE pk = ?;
            """
            cur.execute(SQL, (self.pk, ))
            row=cur.fetchone()  
        self.set_from_row(row)
        return self

    def set_from_row(self, row):
        self.pk = row["pk"]
        self.users_pk = row["users_pk"]
        self.username = row["username"]
        self.content = row["content"]
        self.time = row["time"]
        return self



    


