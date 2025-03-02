import sqlite3
import datetime

db_name = "data.db"


def create_post_table():
    SQL = """
        CREATE TABLE IF NOT EXISTS post (
            id INTEGER PRIMARY KEY,
            title TEXT,
            text TEXT,
            at_publish TEXT,
            author_id INTEGER
        )
    """
    con = sqlite3.connect(db_name)
    con.execute(SQL)


class Post:
    def __init__(self, id, title, text, at_publish, author_id, author_name=None):
        self.id = id
        self.title = title
        self.text = text
        self.at_publish = at_publish
        self.author_id = author_id
        self.author_name = author_name
    
    @staticmethod
    def get_all():
        SQL = """
            SELECT post.*, user.username as author_name
            FROM post
            JOIN user ON post.author_id = user.id
        """
        con = sqlite3.connect(db_name)
        q = con.execute(SQL)
        data = q.fetchall()
        return [Post(*row) for row in data]
    
    @staticmethod
    def get_by_author(author_id):
        SQL = """
            SELECT post.*, user.username as author_name
            FROM post
            JOIN user ON post.author_id = user.id
            WHERE author_id = ?
        """
        con = sqlite3.connect(db_name)
        q = con.execute(SQL, [author_id])
        data = q.fetchall()
        return [Post(*row) for row in data]

    @staticmethod
    def create(title, text, author_id):
        SQL = """
            INSERT INTO post(title, text, at_publish, author_id)
            VALUES (?, ?, ?, ?)
        """
        con = sqlite3.connect(db_name)
        con.execute(SQL, [
            title, text, datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), author_id
        ])
        con.commit()