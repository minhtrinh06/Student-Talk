'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, static_file, response, template

import model

#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------
@route('/static/:filename#.*#')
def send_static(filename):
    return static_file(filename, root='./static/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to login
@get('/')
@get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''
    return model.index()

#-----------------------------------------------------------------------------

# Display the login page
@get('/login')
def get_login_controller():
    '''
        get_login
        
        Serves the login page
    '''
    return model.login_form()

#-----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    response.set_cookie("sender", username)

    # Call the appropriate method
    return model.login_check(username, password)

#-----------------------------------------------------------------------------

# Display the register page
@get('/register')
def get_register():
    '''
        get_register
        
        Serves the register page
    '''
    return model.register_form()

#-----------------------------------------------------------------------------

# Register a new user
@post('/register')
def post_register():
    '''
        post_register
        
        Handles registration attempts
        Expects a form containing 'username', 'password' and 'confirm' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    confirm = request.forms.get('confirm')
    
    # Call the appropriate method
    return model.register_check(username, password, confirm)

#-----------------------------------------------------------------------------
# Friend page
@get('/friend_list')
def friend_list():
    username = request.forms.get('user')
    if username is not None:
        return model.view_friend_list(username)
    else:
        raise ValueError("No username provided")

@post('/friend_list')
def friend_list():
    user = request.forms.get('user')

    if user is not None:
        return model.view_friend_list(user)
    else:
        raise ValueError("No username provided")
    

@get('/add_friends')
def add_friends():
    username = request.forms.get('user')
    if username is not None:
        return model.view_friend_list(username)
    else:
        raise ValueError("No username provided")

@post('/add_friends')
def add_friends():
    sender = request.forms.get('sender')
    friend = request.forms.get('friend')

    model.add_friends(sender, friend)

    return model.view_friend_list(sender)

@get('/remove_friends')
def remove_friends():
    sender = request.forms.get('sender')
    friend = request.forms.get('friend')

    model.remove_friends(sender, friend)

    return model.view_friend_list(sender)

@post('/remove_friends')
def remove_friends():
    sender = request.forms.get('sender')
    friend = request.forms.get('friend')

    model.remove_friends(sender, friend)

    return model.view_friend_list(sender)

@post('/todo')
def todo():
    user = request.forms.get('sender')
    todo = request.forms.get('todo')

    print("user: ", user)
    print("todo: ", todo)

    model.add_todo_item(user, todo)
    return model.view_friend_list(user)

@post('/remove_todo')
def remove_todo():
    print("FROM CONTROLLER REMOVE TODO: ", request.forms.get('todo'))
    user = request.forms.get('user')
    todo = request.forms.get('todo')
    model.delete_todo_item(user, todo)
    return model.view_friend_list(user)

@get('/todo')
def todo():
    user = request.forms.get('sender')
    todo = request.forms.get('todo')
    model.add_todo_item(user, todo)
    return model.view_friend_list(user)

@get('/remove_todo')
def remove_todo():
    user = request.forms.get('user')
    todo = request.forms.get('todo')
    model.delete_todo_item(user, todo)
    return model.view_friend_list(user)

#-----------------------------------------------------------------------------
# Chat page
@get('/chat')
def get_chat():
    '''
        get_chat
        
        Serves the chat page
    '''
    username = request.forms.get('user')
    friend = request.forms.get('friend')
    return model.view_chat(username, friend)

@post('/chat')
def post_chat():
    '''
        post_chat
        
        Handles chat messages
        Expects a form containing 'text' field
    '''
    message = request.forms.get('message')
    sender = request.forms.get('sender')
    receiver = request.forms.get('receiver')
    public_key = request.forms.get('public_key')
    
    print("sender: ", sender)
    print("receiver: ", receiver)
    if message == None:
        return model.view_chat(sender, receiver)
    return model.send_message(message, sender, receiver)

@get('/admin')
def get_admin():
    '''
        get_admin
        
        Serves the admin page
    '''
    return model.admin()

@post('/add_guide')
def add_guide():
    '''
        add_guide
        
        Handles adding a guide
        Expects a form containing 'course code', 'course name' and 'description' fields
    '''
    code = request.forms.get('course_code')
    name = request.forms.get('course_name')
    description = request.forms.get('description')

    return model.add_guide(code, name, description)

@post('/remove_guide')
def remove_guide():
    '''
        remove_guide
        
        Handles removing a guide
        Expects a form containing 'course code' field
    '''
    code = request.forms.get('course_code')
    return model.remove_guide(code)

@post('/remove_user')
def remove_user():
    '''
        remove_user
        
        Handles removing a user
        Expects a form containing 'username' field
    '''
    username = request.forms.get('username')
    return model.remove_user(username)

@post('/mute_user')
def mute_user():
    '''
        mute_user
        
        Handles muting a user
        Expects a form containing 'username' field
    '''
    username = request.forms.get('username')
    return model.mute_user(username)

#-----------------------------------------------------------------------------

# Display the about page
@get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    return model.about()

# Display the contact page
@get('/contact')
def get_contact():
    '''
        get_contact
        
        Serves the contact page
    '''
    return model.contact()

#-----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    return model.handle_errors(error)
