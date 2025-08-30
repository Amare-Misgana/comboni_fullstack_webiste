def get_room_name(username1, username2):
    return f"chat_{'_'.join(sorted([username1, username2]))}"