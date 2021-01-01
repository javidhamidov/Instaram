from flask import Flask, render_template, url_for, request, redirect, make_response
from hashlib import sha256
import json
from uuid import uuid4
from werkzeug.utils import secure_filename
import os
import time
import random

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#Max 16 mb
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

mail = 'unknown'
current = 'unknown'
password = 0

def get_unique_filename(filename):
    #Split the filename to get the extension
    split_filename = filename.split('.')
    #Get the last part as extension
    extension = split_filename[len(split_filename) - 1]
    #Get a new uuid 
    unique_name = uuid4().__str__()
    return "{}.{}".format(unique_name, extension)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/profile', defaults={'username': current})
@app.route('/profile/<username>')
def profile(username):
    if password == 0:
        return redirect(url_for('login'))
    else:
        with open("posts.json") as file:
            data = json.load(file)
        only_user = []
        for post in data:
            if post['username'] == current:
                only_user.append(post)
        return render_template("profile.html", username=current, mail=mail, data=reversed(only_user))

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']
        with open('account_info.json') as file:
            data = json.load(file)
        all_users = []
        n = 0
        for account in data:
            all_users.append(account['email'])
        if email not in all_users:
            return render_template('login.html', message="THIS ACCAUNT DOES NOT EXIST!")
        else:
            n = all_users.index(email)
            hashed = sha256(pwd.encode("utf-8")).hexdigest()
            if hashed == data[n]['password']:
                global current, password, mail
                mail=data[n]['email']
                current=data[n]['username']
                password=data[n]['password']
                return redirect(url_for('profile', username=current))
            else:
                return render_template('login.html', message="INCORRECT PASSWORD!")
    else:
        return render_template('login.html')

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        pwd = request.form['password']
        with open('account_info.json') as file:
            data = json.load(file)
        all_users = []
        print(data)
        for account in data:
            all_users.append(account['email'])
        if email in all_users:
            return render_template('register.html', message="THE ACCOUNT WITH THIS EMAIL ALREADY EXISTS!")
        else:
            hashed = sha256(pwd.encode("utf-8")).hexdigest()
            new_account={
                "username" : username,
                "email" : email,
                "password" : hashed
            }
            data.append(new_account)
            with open("account_info.json", "w") as file:
                json.dump(data, file, indent=4)
            global current, password, mail
            mail = 'unknown'
            current = 'unknown'
            password = 0
            return redirect(url_for('login'))
    else:
        return render_template("register.html")

@app.route('/logout')
def logout():
    global current, password, mail
    mail = 'unknown'
    current = 'unknown'
    password = 0
    return redirect(url_for('home'))

@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    if current == 'unknown' or password == 0:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            f = request.files['image']
            filename = secure_filename(f.filename)
            filename = get_unique_filename(filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            title = request.form['title']
            seconds = time.time()
            date = time.ctime(seconds)
            with open('posts.json') as file:
                data = json.load(file)
            lis = []
            for item in data:
                lis.append(item['id'])
            while True:
                id = random.randrange(10000000, 100000000)
                if id not in lis:
                    break
            new_file = '/static/uploads/' + filename
            new_post={
                "id": id,
                "title": title,
                "filename": new_file,
                "username": current,
                "date": date
            }
            data.append(new_post)
            with open('posts.json', 'w') as file:
                json.dump(data, file, indent=4) 
            return redirect(url_for('profile'))
        else:
            return render_template("upload.html")

@app.route('/feed')
def feed():
    if password == 0:
        return redirect(url_for('login'))
    else:
        with open("posts.json") as file:
            data = json.load(file)
        return render_template('feed.html', data=reversed(data))
@app.route('/view_profile/<username>')
def view(username):
    with open("posts.json") as file:
            data = json.load(file)
    only_user = []
    for post in data:
        if post['username'] == username:
            only_user.append(post)
    return render_template("view_profile.html", username=username, data=reversed(only_user))

if __name__ == '__main__':
    app.run(debug=True)