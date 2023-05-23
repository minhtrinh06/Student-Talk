import sqlite3
import bcrypt
from diffiehellman import DiffieHellman


# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call 
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise

class SQLDatabase():
    '''
        Our SQL Database

    '''

    # Get the database running
    def __init__(self, database_arg=":memory:"):
        self.conn = sqlite3.connect(database_arg)
        self.cur = self.conn.cursor()

    # SQLite 3 does not natively support multiple commands in a single statement
    # Using this handler restores this functionality
    # This only returns the output of the last command
    def execute(self, sql_string):
        out = None
        for string in sql_string.split(";"):
            try:
                out = self.cur.execute(string)
            except:
                pass
        return out

    # Commit changes to the database
    def commit(self):
        self.conn.commit()

    #-----------------------------------------------------------------------------
    
    # Sets up the database
    # Default admin password
    def database_setup(self, admin_password='admin'):

        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Users")
        self.execute("DROP TABLE IF EXISTS Chats")
        self.execute("DROP TABLE IF EXISTS Messages")
        self.execute("DROP TABLE IF EXISTS Guides")
        self.execute("DROP TABLE IF EXISTS Friends")
        self.execute("DROP TABLE IF EXISTS Todos")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Users(
            username TEXT,
            password TEXT,
            admin INTEGER DEFAULT 0
        )""")

        # Create the chats table
        self.execute("""CREATE TABLE Chats(
            user1 TEXT,
            user2 TEXT,
            size INTEGER DEFAULT 0,
            PRIMARY KEY(user1, user2)
        )""")

        # Create the messages table
        self.execute("""CREATE TABLE Messages(
            sender TEXT,
            receiver TEXT,
            message TEXT,
            message_index INTEGER,
            FOREIGN KEY(sender, receiver) REFERENCES Chats(user1, user2),
            PRIMARY KEY(sender, receiver, message, message_index)
        )""")

        # Create course guides table
        self.execute("""CREATE TABLE Guides(
            course_code TEXT,
            course_name TEXT,
            course_description TEXT,
            PRIMARY KEY(course_code)
        )""")

        # Create a friendship table
        self.execute("""CREATE TABLE Friends(
            user1 TEXT,
            user2 TEXT,
            PRIMARY KEY(user1, user2)
        )""")

        # Create a todo list table
        self.execute("""CREATE TABLE Todos(
            username TEXT,
            todo TEXT,
            PRIMARY KEY(username, todo)
        )""")
    
        self.commit()

        # Add our admin user
        self.add_user('admin', admin_password, admin=1)

        # init course guides
        print(self.init_course_guides())

    #-----------------------------------------------------------------------------
    # User handling
    #-----------------------------------------------------------------------------

    # Add a user to the database
    def add_user(self, username, password, admin=0):
        
        data = [username, password, admin]
        self.cur.execute("INSERT INTO Users VALUES(?, ?, ?)", data)
        self.commit()

        return True
    
    def remove_user(self, username):
        self.cur.execute("DELETE FROM Users WHERE username = ?", [username])
        self.cur.execute("DELETE FROM Friends WHERE user1 = ? OR user2 = ?", [username, username])
        self.cur.execute("DELETE FROM Chats WHERE user1 = ? OR user2 = ?", [username, username])
        self.cur.execute("DELETE FROM Todos WHERE username = ?", [username])
        self.commit()
        
        return True
    
    def mute_user(self, username):
        # Remove all friends from user
        print("MUTING USER: ", username)
        self.cur.execute("DELETE FROM Friends WHERE user1 = ? OR user2 = ?", [username, username])
        self.commit()

    #-----------------------------------------------------------------------------

    # Check login credentials
    def check_credentials(self, username, password):
        sql_query = """
                SELECT password
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        res = self.cur.fetchone()
        if res is None:
            return False

        true_pw = res[0]

        if bcrypt.checkpw(password, true_pw):
            return True
        
    def check_username(self, username):
        sql_query = """
                SELECT username 
                FROM Users
                WHERE username = '{username}'
            """
        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        
        res = self.cur.fetchone()

        if res is not None:
            return True
        else:
            return False
        
    # def get_friends(self, username):
    #     sql_query = """
    #             SELECT username 
    #             FROM Users
    #             WHERE NOT username = '{username}'
    #         """
    #     sql_query = sql_query.format(username=username)
    #     self.execute(sql_query)
        
    #     res = self.cur.fetchall()
        
    #     if res is not None:
    #         return res
    #     else:
    #         return False
    
    def chat_exists(self, user1, user2):
        self.cur.execute("SELECT * FROM Chats WHERE user1 = ? AND user2 = ?", [user1, user2])
        res1 = self.cur.fetchone()

        print("CHECKING CHAT EXISTENCE\nRES1: ", res1)
        if res1 is None:
            return False
        else:
            return True
        
        
    def add_chat(self, user1, user2, size=0):
        data = [user1, user2, size]
        self.cur.execute("INSERT INTO Chats VALUES(?, ?, ?)", data)
        self.commit()
        
        return True
    
    def add_message(self, sender, receiver, message):
        data = [sender, receiver] if self.chat_exists(sender, receiver) else [receiver, sender]

        message_index = self.cur.execute("SELECT size FROM Chats WHERE user1 = ? AND user2 = ?", data).fetchone()
        message_index = message_index[0] + 1
        self.cur.execute("UPDATE Chats SET size = ? WHERE user1 = ? AND user2 = ?", [message_index] + data)
        data = [sender, receiver, message, message_index]
        self.cur.execute("INSERT INTO Messages VALUES(?, ?, ?, ?)", data)
        print("ADDED MESSAGE: ", data)
        self.commit()
        
        return True
    
    def get_chat_history(self, user1, user2):
        sql_query = """
                SELECT sender, message
                FROM Messages
                WHERE (sender = '{user1}' AND receiver = '{user2}')
                OR (sender = '{user2}' AND receiver = '{user1}')
                ORDER BY message_index ASC
            """
        sql_query = sql_query.format(user1=user1, user2=user2) if self.chat_exists(user1, user2) else sql_query.format(user1=user2, user2=user1)
        res = self.execute(sql_query)

        if res is not None:
            chat_history = "".join([f'<div class="message"><strong>{message[0]}:</strong> {message[1]}</div>' for message in res.fetchall()])
            return chat_history
        else:
            return None
        
    def get_course_guides(self):
        sql_query = """
                SELECT course_code, course_name, course_description
                FROM Guides
            """
        res = self.execute(sql_query)

        if res is not None:
            course_guides = res.fetchall()
            return course_guides
        else:
            return None
        
    def add_course_guide(self, course_code, course_name, course_description):
        sql_query = """
                INSERT INTO Guides VALUES(?, ?, ?)
            """
        res = self.cur.execute(sql_query, [course_code, course_name, course_description])
        self.commit()

        if res is not None:
            return True
        else:
            return False
        
    def remove_course_guide(self, course_code):
        sql_query = """
                DELETE FROM Guides
                WHERE course_code = '{course_code}'
            """
        sql_query = sql_query.format(course_code=course_code)
        print("REMOVE GUIDE SQL QUERY: ", sql_query)
        res = self.execute(sql_query)
        self.commit()

        if res is not None:
            return True
        else:
            return False
        
    def get_course_guide(self, course_code):
        sql_query = """
                SELECT course_code, course_name, course_description
                FROM Guides
                WHERE course_code = '{course_code}'
            """
        sql_query = sql_query.format(course_code=course_code)
        res = self.execute(sql_query)

        if res is not None:
            course_guide = res.fetchone()
            return course_guide
        else:
            return None
        
    def init_course_guides(self):
        sql_query = """
                INSERT INTO Guides VALUES('INFO1110', 'Intro to Programming', 'This course is an introduction to computer science. It covers the basics of programming in Python.');
                INSERT INTO Guides VALUES('INFO1113', 'Object-Oriented Programming', 'This course is an introduction to computer science. It covers the basics of programming in Java.');
                INSERT INTO Guides VALUES('COMP2123', 'Data Structures and Algorithms', 'This course is an introduction to data structures and algorithms. It covers the basics of data structures and algorithms.');
                INSERT INTO Guides VALUES('COMP2017', 'Systems Programming', 'This course is an introduction to operating systems and machine principles. It covers the basics of operating systems and machine principles.');
            """
        res = self.execute(sql_query)
        self.commit()

        if res is not None:
            return True
        else:
            return False
        
    def are_friends(self, user1, user2):
        sql_query = """
                SELECT *
                FROM Friends
                WHERE user1 = '{user1}' AND user2 = '{user2}'
            """
        sql_query = sql_query.format(user1=user1, user2=user2)
        res = self.execute(sql_query)

        if res is not None:
            return True
        else:
            return False
        
    def add_friend(self, user1, user2):
        sql_query = """
                INSERT INTO Friends VALUES('{user1}', '{user2}')
            """
        sql_query = sql_query.format(user1=user1, user2=user2)
        res = self.execute(sql_query)
        self.commit()

        if res is not None:
            return True
        else:
            return False
        
    def get_friends(self, username):
        sql_query = """
                SELECT user2
                FROM Friends
                WHERE user1 = '{username}'
            """
        sql_query = sql_query.format(username=username)
        res = self.execute(sql_query)

        if res is not None:
            return res.fetchall()
        else:
            return None
        
    def remove_friend(self, user1, user2):
        sql_query = """
                DELETE FROM Friends
                WHERE user1 = '{user1}' AND user2 = '{user2}'
            """
        sql_query = sql_query.format(user1=user1, user2=user2)
        res = self.execute(sql_query)
        self.commit()

        if res is not None:
            return True
        else:
            return False
        
    def add_todo(self, username, todo):
        try:
            sql_query = """
                    INSERT INTO Todos VALUES(?, ?)
                """
            
            #sql_query = sql_query.format(username=username, todo)
            self.cur.execute(sql_query, [username, todo])
            self.commit()

            # if res is not None:
            #     return True
            # else:
            #     return False
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
    
    def get_todos(self, username):
        try:
            sql_query = """
                    SELECT todo
                    FROM Todos
                    WHERE username = '{username}'
                """
            sql_query = sql_query.format(username=username)

            # print(sql_query)
            res = self.execute(sql_query)
            
            if res is not None:
                todos = res.fetchall()
                print(todos)
                return todos
            else:
                print("FAILED TO GET TODOS", res)
                return None
        except sqlite3.Error as error:
            print("Failed to get Todos", error)
        
    def remove_todo(self, username, todo):
        print("TRING TO REMOVE TODO", username, todo)
        sql_query = """
                DELETE FROM Todos
                WHERE username = ? AND todo = ?
            """
        #sql_query = sql_query.format(username=username, todo=todo.replace(" ", "#"))
        res = self.cur.execute(sql_query, [username, todo])
        self.commit()

        if res is not None:
            return True
        else:
            return False