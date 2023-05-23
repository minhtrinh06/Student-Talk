class User:
    def __init__(self, username):
        self.username = username
        self.friends = []

    def add_friend(self, friend_username):
        if friend_username not in self.friends:
            self.friends.append(friend_username)
        else:
            print(f"{friend_username} is already a friend.")

    def remove_friend(self, friend_username):
        if friend_username in self.friends:
            self.friends.remove(friend_username)
        else:
            print(f"{friend_username} is not a friend.")

    def __repr__(self):
        return f"<User username={self.username}, friends={self.friends}>"
