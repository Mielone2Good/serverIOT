import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("baza.db", check_same_thread=False)

        try:
            self.conn.execute("""CREATE TABLE IF NOT EXISTS Users
            (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Username NVARCHAR(30) UNIQUE,
                Password NVARCHAR(30),
                Admin BOOL DEFAULT FALSE
            );""")

            self.conn.execute("""CREATE TABLE IF NOT EXISTS Messages
            (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Text NVARCHAR(100),
                Author NVARCHAR(30)
            );""")

            self.conn.execute("""CREATE TABLE IF NOT EXISTS Notifications
            (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Author NVARCHAR(30),
                Product NVARCHAR(30),
                Expiration DATE
            )
            """)

            self.add_user("mielony", "cos12", True)
        except:
            print("Jakis blad DB, prawdopodobnie Admin juz istnieje")

    def add_user(self, username, password, admin=False):
        self.conn.execute(f"INSERT INTO Users(Username, Password, Admin) VALUES('{username}', '{password}', {admin});")
        self.conn.commit()

    def add_message(self, text, author):
        self.conn.execute(f"INSERT INTO Messages(Text, Author) VALUES('{text}', '{author}');")
        self.conn.commit()

    def delete_user(self, username):
        self.conn.execute(f"DELETE FROM Users WHERE username = '{username}';")
        self.conn.commit()

    def add_notification(self, author, product, date):
        self.conn.execute(f"INSERT INTO Notifications(Author, Product, Expiration) VALUES('{author}', '{product}', '{date}');")
        self.conn.commit()

    def get_all_message(self):
        cursor = self.conn.execute("SELECT Author || ': ' || Text as Msg FROM Messages;")
        messages = []
        for row in cursor:
            messages.append(row[0])
        return messages

    def get_current_notifications(self):
        cursor = self.conn.execute("SELECT * FROM Notifications WHERE Expiration <= DATE('now');")
        messages = []
        for row in cursor:
            messages.append({
                "id": row[0],
                "author": row[1],
                "product": row[2],
                "date": row[3]
            })
        return messages

    def delete_notification(self, _id):
        self.conn.execute(f"DELETE FROM Notifications WHERE ID = {_id};")
        self.conn.commit()

    def is_correct_username_and_password(self, username, password):
        cursor = self.conn.execute(f"SELECT * FROM Users WHERE Username = '{username}' AND Password = '{password}'")
        for row in cursor:
            return True
        return False

    def username_exist(self, username):
        cursor = self.conn.execute(f"SELECT * FROM Users WHERE Username = '{username}'")
        for row in cursor:
            return True
        return False
