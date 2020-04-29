import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import md5hash, registerUser, loginUser, searchBooks, getBookData, postComment, getPostsData


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
    if not 'id' in session or not 'name' in session:
        session['id'] = None
        session['name'] = None
    return render_template("index.html", user = session['name'])

@app.route("/login", methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        if nickname != '' and password != '':
            userId = loginUser(db, nickname, password)
            if userId:
                session['id'] = userId
                session['name'] = nickname
                return redirect(url_for("index"))
            else:
                flash('Nickname or password were wrong!')      
        else:
             flash('No nickname or password!')
        return redirect(url_for('login'))           
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session['id'] = None
    session['name'] = None    
    return redirect(url_for('index'))

@app.route("/registration", methods=['POST', 'GET'])
def registration():

    if request.method == 'POST':
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        password = request.form.get('password')
        if email == '':
            flash('You must fill the email field!')
            return redirect(url_for('registration'))
        if nickname == '':
            flash('You must fill the nick field!')
            return redirect(url_for('registration'))
        if password == '':
            flash('You must fill the password field!')
            return redirect(url_for('registration'))                       
        if email != '' and password != '':
            existUser = db.execute("SELECT email FROM users WHERE (nickname=:nickname)", {"nickname":nickname}).first()
            if existUser != None:
                flash('This nickname is alrady used!')
                return redirect(url_for('registration'))    
            session['id'] = registerUser(db, nickname, email, password)
            session['name'] = nickname
            return redirect(url_for('index'))       
    else:
        return render_template("registration.html")

@app.route('/search' ,methods=['POST','GET'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')
        data = searchBooks(db, query)
        return render_template("search.html", data = data)
    else:
        return render_template("search.html", data = [])

@app.route('/book/<num_isbn>' ,methods=['POST','GET'])
def showBookInfo(num_isbn):
    if request.method == "POST":
        rate = ''
        if request.form.get('bookRate'):
            rate = request.form.get('bookRate')
        if request.form.get('review'):
            text = request.form.get('review')
            userId = session['id']
            postComment(db, text, rate, userId, num_isbn)
        return redirect(url_for('showBookInfo', num_isbn=num_isbn))
    else:
        avgRating = 0
        numOfRatings = 0   
        bookData = getBookData(db, num_isbn)
        posts = []
        key = "d72NGT7cnXqB0hHXJeFfEA"
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": num_isbn})
        if res.status_code == 200:
            res = res.json()
            avgRating = res["books"][0]["average_rating"]
            numOfRatings = res["books"][0]["work_ratings_count"]
        posts = getPostsData(db, num_isbn)
        posted = False
        yourRate = 0
        RMpostsCounter = 0
        RMavgRate = 0
        for post in posts:
            if post.rate:
                RMpostsCounter += 1
                RMavgRate += post.rate
            if post.nickname == session["name"]:
                posted = True
                yourRate = post.rate
        if RMpostsCounter != 0:
            RMavgRate = RMavgRate / RMpostsCounter
        print(posts)
        return render_template('book_info.html', bookData=bookData, posts=posts, avgRating=avgRating, numOfRatings=numOfRatings, posted=posted, yourRate=yourRate, RMavgRate=RMavgRate, RMpostsCounter=RMpostsCounter)
