#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, session, flash
import model
import re
import dateutil.parser
import calendar


app = Flask(__name__)

app.secret_key = b'#5566778'


@app.route('/', methods=['GET','POST'])
def send_to_dashboard():
    if request.method == 'GET':
        content = model.get_all_tweets()
        content = list(reversed(content))
        content_len = len(content)
        print(content)
        return render_template('dashboard.html', content = content, content_len = content_len)
    else:
        if 'username' not in session:
            flash('You must be logged in to retweet posts')
            return redirect('/login')
        else: 
            retweet_pk = request.form['retweet']
            username = session['username']
            if model.copy_tweet(username, retweet_pk):
                flash('Retweet Successful!')
                return redirect('/message_board')
            else: 
                flash('Something went wrong, try again')
                return redirect('/message_board')

@app.route('/users', methods=['GET','POST'])
def see_all_users():
    if request.method == 'GET':
        content = model.get_all_users()
        content_len = len(content)
        print(content)
        return render_template('users.html', content = content, content_len = content_len)
    else:
        if 'username' not in session:
            flash('You must be logged in to follow users')
            return redirect('/login')
        else: 
            user_to_follow = request.form['follow']
            username = session['username']
            user_to_follow_object = model.set_user_object_from_pk(user_to_follow)
            user_to_follow_username = user_to_follow_object.username
            if user_to_follow_username == username:
                flash(f'You can\'t follow yourself!')
                return redirect('/users')
            elif model.test_followed_object(username, user_to_follow_username):
                flash(f'You are already following that user!')
                return redirect('/users')
            else:
                try: 
                    model.follow_user(username, user_to_follow_username)
                    flash(f'You are now following {user_to_follow_username}!')
                    return redirect('/users')
                except: 
                    flash('Something went wrong, try again')
                    return redirect('/users')
   


# @app.route('/', methods=['GET'])
# def send_to_login():
#         return redirect('/login')


@app.route('/homepage', methods=['GET','POST'])
def homepage_redirect():
    if request.method == 'GET':
        if 'username' in session:
            return redirect('/message_board')
        else:
            flash("you must login before you can view your homepage!")
            return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():    
    if request.method == 'GET':
        print(session)
        if 'username' in session:
            return redirect('/message_board')
        return render_template('login.html')
    else:
        try:
            username = request.form['username']
            password = request.form['password']
            user_object = model.set_user_object(username)
        except:
            flash("Invalid Login")
            return redirect('/login')
        if user_object.check_password(user_object.pass_hash, password):
            session['username'] = username
            flash(f'User {username} successfully logged in!')
            return redirect('/login')
        else:
            flash("Invalid Login")
            return redirect('/login')

@app.route('/create_account', methods=['GET', 'POST'])
def create_new_account():
    if request.method == 'GET':
        if 'username' in session:
            session['username'] = username
            flash(f'User {username} already logged in!')
            return redirect('/login')
        return render_template('create_account.html')
    else:
        username = request.form['username']
        password = request.form['password']
        new_user = model.Account(username=username)
        if new_user.check_set_username():
            flash('User Already Exists')
            return redirect('/create_account')
        if len(password) < 8:
            flash('Please enter a password that is at least 8 characters')
            return redirect('/create_account')
        if re.search('[0-9]',password) is None:
            flash('Please enter a password that has at least one digit')
            return redirect('/create_account')
        if re.search('[A-Z]',password) is None:
            print('pass char')
            flash('Please enter a password that with at least one capital letter')
            return redirect('create_account')
        print('no issues')
        hashed_pw = new_user.calculatehash(password)
        print(hashed_pw)
        new_user.pass_hash = hashed_pw
        new_user.type = "USER"
        new_user.save()
        flash('User Account Successfully Created')
        return redirect('/login')



@app.route('/message_board', methods=['GET', 'POST'])
def message_board():
    if request.method == 'GET':
        if 'username' in session:
            user_id = session['username']
            print(user_id)
            content = model.read_all_tweets(user_id)
            content_len = len(model.read_all_tweets(user_id))
            print(content)
            return render_template('message-board.html', content = content, content_len = content_len)
    if request.method == 'POST':
        if 'username' in session:
            user_id = session['username']
            content = request.form['content']
            try:
                model.create_tweet(user_id,content)
            except:
                ValueError
            flash('Successful Tweet')               
            return redirect('/message_board')
            

@app.route('/logout', methods=['GET'])
def log_out():
    session.clear()
    flash(f'User logged out')
    return redirect('/')




if __name__ == '__main__':
    app.run(debug=True)