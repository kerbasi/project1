import hashlib

from random import randint

def md5hash(salt, raw_data):
    constSalt = "13dfef"
    return hashlib.sha224((str(salt)+str(constSalt)+raw_data).encode('utf-8')).hexdigest()

def registerUser(db, nickname, email, password):
    salt = randint(0, 9999)
    pass_hash = md5hash(salt, password)
    db.execute("INSERT INTO users (nickname, email, salt, pass_hash) VALUES (:nickname, :email, :salt, :pass_hash)", 
                {"nickname":nickname, "email":email, "salt":salt, "pass_hash":pass_hash})
    db.commit()
    return db.execute("SELECT id FROM users WHERE nickname=:nickname",{"nickname":nickname}).fetchone().id

def loginUser(db, nickname, password):
    data = db.execute("SELECT salt, pass_hash, id FROM users WHERE nickname=:nickname", {"nickname":nickname}).fetchone()
    if data == None:
        return None
    elif data.pass_hash == md5hash(data.salt, password):
        return data.id
    else:
        return None

def searchBooks(db, query):
    return db.execute('SELECT num_isbn, title, author, pub_year FROM books WHERE \
                            num_isbn ILIKE :query0 OR num_isbn ILIKE :query1 OR num_isbn ILIKE :query2 OR num_isbn ILIKE :query3 OR \
                            title ILIKE :query0 OR title ILIKE :query1 OR title ILIKE :query2 OR title ILIKE :query3', 
                            {"query0":query, "query1":'%' + query, "query2":query + '%', "query3":'%' + query + '%'}).fetchall()

def getBookData(db, num_isbn):
    return db.execute('SELECT num_isbn, title, author, pub_year FROM books WHERE num_isbn=:num_isbn', 
                            {"num_isbn":num_isbn}).fetchone()

def postComment(db, text, rate, userId, num_isbn):
    if rate == '':
        rate = None
    book_id = db.execute('SELECT id FROM books WHERE num_isbn = :num_isbn', {"num_isbn":num_isbn}).fetchone()
    db.execute('INSERT INTO reviews (book_id, author_id, text, rate, time) VALUES (:book_id, :author_id, :text, :rate, current_timestamp)',
                {"book_id":book_id.id, "author_id":userId, "text":text, "rate":rate})
    db.commit()
    return 1

def getPostsData(db, num_isbn):
    book_id = db.execute('SELECT id FROM books WHERE num_isbn = :num_isbn', {"num_isbn":num_isbn}).fetchone()
    return db.execute('SELECT reviews.text, users.nickname, reviews.rate, reviews.time FROM reviews INNER JOIN users ON reviews.author_id=users.id WHERE book_id=:book_id',
                        {"book_id":book_id.id}).fetchall()