'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
import view
import random
import sql
import bcrypt
from diffiehellman import DiffieHellman


# Initialise our views, all arguments are defaults for the template
page_view = view.View()

# Initialize the database
db = sql.SQLDatabase("project.db")

# Uncomment to reset the database
# hashed_admin_pw = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
# db.database_setup(hashed_admin_pw)

chats = {}

#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def index():
    '''
        index
        Returns the view for the index
    '''
    return page_view("index")

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view("login")

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    user_exists = db.check_username(username)
    subject = "Login failed"
    if not user_exists:
        return page_view("invalid", subject=subject, reason="Username does not exist")
    
    #hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    pw_to_check = password.encode('utf-8')

    login = db.check_credentials(username, pw_to_check)
    
    if login: 
        return view_friend_list(username)
    else:
        return page_view("invalid", subject=subject, reason="Incorrect password")

#-----------------------------------------------------------------------------
# Register
#-----------------------------------------------------------------------------

def register_form():
    '''
        register
        Returns the view for the register page
    '''
    return page_view("register")

#-----------------------------------------------------------------------------

def register_check(username, password, confirm):
    '''
        register_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password
        :: confirm  :: The password confirmation

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    user_exists = db.check_username(username)
    invalid_subject = "Registration failed."
    if user_exists:
        return page_view("invalid", subject=invalid_subject, reason="User already exists")
    
    if password != confirm:
        return page_view("invalid", subject=invalid_subject, reason="Passwords do not match")
    
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    register = db.add_user(username, hashed_pw)

    if register:
        return page_view("welcome", name=username)
    else:
        return page_view("invalid", subject=invalid_subject, reason="Unknown error")
    

#-----------------------------------------------------------------------------
# Friends
#-----------------------------------------------------------------------------
def view_friend_list(username):
    '''
        friend_list
        Returns the view for the friend list page

        :: name :: The name of the user
    '''
    guides = db.get_course_guides()
    guides_str = ""
    for guide in guides:
        guide_str = """
            <li>
            <h4>{course_code}: {course_name}</h4>
            <p>{des}</p>
            </li>
        """.format(course_code=guide[0], course_name=guide[1], des=guide[2])
        guides_str += guide_str

    todos = db.get_todos(username)
    # if len(todos) != 0:
    #     todos = [" ".join(todo[0].split("#")) for todo in todos]

    todos_str = ""
    for todo in todos:
        todo_str = """
            <li>
                <form class="input-form" action="/remove_todo" method="post">
                    <input type="hidden" name="user" value={user}> 
                    <input type="hidden" name="todo" value="{todo}">
                    <h4 class="todo-task">{todo}</h4>
                    <input type="submit" class="delete-todo-button" value="Finish"/>
                </form>
            </li>
        """.format(user=username, todo=todo[0])
        todos_str += todo_str

    friends = db.get_friends(username)
    friends_str = ""
    for friend in friends:
        friend_str = """
            <li>
                <form class="input-form" action="/chat" method="post">
                    <input type="hidden" name="sender" value={sender}> 
                    <input type="hidden" name="receiver" value={receiver}>
                    <span>{receiver}</span>
                    <input type="submit" class="chat-button" value="Chat"/>
                </form>
            </li>
        """.format(sender=username, receiver=friend[0])
        friends_str += friend_str
    if username == "admin":
        return page_view("friend_list", header="admin_header", sender=username, friends=friends_str, user=username, guides=guides_str, todos=todos_str)
    return page_view("friend_list", header="user_header", sender=username, friends=friends_str, user=username, guides=guides_str, todos=todos_str)

def add_friends(user1, user2):
    db.add_friend(user1, user2)
    view_friend_list(user1)

def remove_friends(user1, user2):
    db.remove_friend(user1, user2)
    view_friend_list(user1)

def add_todo_item(username, todo):
    db.add_todo(username, todo)
    view_friend_list(username)

def delete_todo_item(username, todo):
    print("FROM MODEL, REMOVING TODO: " + todo + " FOR USER: " + username)
    db.remove_todo(username, todo)
    view_friend_list(username)

#-----------------------------------------------------------------------------
# Chat
#-----------------------------------------------------------------------------

def view_chat(username, friend_name):
    '''
        chat
        Returns the view for the chat page

        :: name :: The name of the user
    '''
    if username is None or friend_name is None:
        if username == "admin":
            return page_view("invalid", header="admin_header", reason="No username or friend name provided",  user=username)
        return page_view("invalid", header="user_header", reason="No username or friend name provided",  user=username)
    
    if not db.chat_exists(username, friend_name) and not db.chat_exists(friend_name, username):
        db.add_chat(username, friend_name)
        chat_history = ""
        print("ADDED CHAT", username, friend_name)
    else:
        print("LOADING CHAT" , username, friend_name)
        chat_history = db.get_chat_history(username, friend_name)

    print("CHAT HISTORY", chat_history)
    if username == "admin":
        return page_view("chat", header="admin_header", message_history=chat_history, sender=username, receiver=friend_name, user=username)
    return page_view("chat", header="user_header", message_history=chat_history, sender=username, receiver=friend_name, user=username)

def send_message(message, sender, receiver):
    '''
        send_message
        Returns the view for the chat page

        :: message :: The message to send
    '''
    # curr_chat = chats[(sender, receiver)] if (sender, receiver) in chats.keys() else chats[(receiver, sender)]
    # curr_chat.add_message(sender, message)
    db.add_message(sender, receiver, message)
    chat_history = db.get_chat_history(sender, receiver)
    
    print("CHAT HISTORY", chat_history)
    if sender == "admin":
        return page_view("chat", header="admin_header", message_history=chat_history, sender=sender, receiver=receiver,  user=sender)
    return page_view("chat", header="user_header", message_history=chat_history, sender=sender, receiver=receiver,  user=sender)


#-----------------------------------------------------------------------------
# Admin
#-----------------------------------------------------------------------------
def admin():
    '''
        admin
        Returns the view for the admin page
    '''
    return page_view("admin", header="admin_header", user="admin")

def add_guide(course_code, course_name, description):
    '''
        add_guide
        Returns the view for the admin page
    '''
    db.add_course_guide(course_code, course_name, description)
    return page_view("admin", header="admin_header", user="admin")

def remove_guide(course_code):
    '''
        remove_guide
        Returns the view for the admin page
    '''
    db.remove_course_guide(course_code)
    return page_view("admin", header="admin_header", user="admin")

def remove_user(username):
    '''
        remove_user
        Returns the view for the admin page
    '''
    db.remove_user(username)
    return page_view("admin", header="admin_header", user="admin")

def mute_user(username):
    '''
        mute_user
        Returns the view for the admin page
    '''
    db.mute_user(username)
    return page_view("admin", header="admin_header", user="admin")
#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("about")

def contact():
    '''
        contact
        Returns the view for the contact page
    '''
    return page_view("contact")

#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)
