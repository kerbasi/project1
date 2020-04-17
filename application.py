import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import md5hash, registerUser, loginUser


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index(): 
    if 'user' in session:
        print(session['user'])
    else:
        session['user'] = None   
    return render_template("index.html", user = session['user'])

@app.route("/login", methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email != '' and password != '':
            if loginUser(db, email, password):
                session['user'] = email
                return redirect(url_for("index"))
            else:
                error = '1'       
        else:
             error = '2'
        return render_template('error.html', error = error)           
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session['user'] = None
    return redirect(url_for('index'))

@app.route("/registration", methods=['POST', 'GET'])
def registration():
    error = None
    if request.method == 'GET':
        return render_template("registration.html")
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        if email != '' and password != '':
            existUser = db.execute("SELECT email FROM users WHERE (email=:email)", {"email":email}).first()
            if existUser != None:
                    error = 'This email is already used!'
                    return render_template('error.html', error=error)
            registerUser(db, email, password)       
            session['user'] = email
            return redirect(url_for('index'))
        else:
            error = 'You must promt valid email and password'
            return render_template('error.html', error=error)
        return "done"