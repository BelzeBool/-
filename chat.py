import sqlite3
from datetime import datetime

db_name = "data.db"


def create_chat_table():
    SQL = """
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            message TEXT,
            at_send TEXT,
            FOREIGN KEY(user_id) REFERENCES user(id)
        )
    """
    con = sqlite3.connect(db_name)
    con.execute(SQL)


class ChatMessage:
    def __init__(self, id, user_id, message, at_send, username=None):
        self.id = id
        self.user_id = user_id
        self.message = message
        self.at_send = at_send
        self.username = username
    
    @staticmethod
    def create(user_id, message):
        SQL = """
            INSERT INTO chat(user_id, message, at_send)
            VALUES (?, ?, ?)
        """
        con = sqlite3.connect(db_name)
        con.execute(SQL, [user_id, message, datetime.now().strftime("%d.%m.%Y %H:%M")])
        con.commit()
    
    @staticmethod
    def get_all():
        SQL = """
            SELECT chat.*, user.username
            FROM chat
            JOIN user ON chat.user_id = user.id
            ORDER BY chat.at_send ASC
        """
        con = sqlite3.connect(db_name)
        q = con.execute(SQL)
        data = q.fetchall()
        return [ChatMessage(*row) for row in data]