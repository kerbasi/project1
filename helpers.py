import hashlib

from random import randint

def md5hash(salt, raw_data):
    constSalt = "13dfef"
    return hashlib.sha224((str(salt)+str(constSalt)+raw_data).encode('utf-8')).hexdigest()

def registerUser(db, email, password):
    salt = randint(0, 9999)
    pass_hash = md5hash(salt, password)
    db.execute("INSERT INTO users (email, salt, pass_hash) VALUES (:email, :salt, :pass_hash)", {"email":email, "salt":salt, "pass_hash":pass_hash})
    db.commit()  

def loginUser(db, email, password):
    data = db.execute("SELECT salt, pass_hash FROM users WHERE email=:email", {"email":email}).fetchone()
    if data == None:
        return False
    elif data.pass_hash == md5hash(data.salt, password):
        return True
    else:
        return False
    print(data.salt, data.pass_hash)
    return False
