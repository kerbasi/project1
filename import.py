import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open('books.csv')
    reader = csv.reader(f)
    next(reader, None)
    for numISBN, title, author, pubYear in reader:
        db.execute('INSERT INTO books (num_isbn, title, author, pub_year) VALUES (:numISBN, :title, :author, :pubYear)', 
                    {"numISBN":numISBN, "title":title, "author":author, "pubYear":pubYear})
    db.commit()
        

if __name__ == '__main__':
    main()