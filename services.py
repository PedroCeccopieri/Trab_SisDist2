import time

from threading import Thread
from room import Room

users = []
rooms = {}

def getRoom(name):

    for n, r in rooms.items():
        if (n == name):
            return r
        
    return None

def checkUser(name):

    return users.count(name) == 1

## SERVICES ##

def registerUser(name):

    if (users.count(name) == 0):
        users.append(name)
        print(f"### User {name} was registered ###")
        return True
    else:
        print(f"### The user '{name}' already exist ###")
        return False
    
def unregisterUser(name):

    try:
        users.remove(name)
        print(f"### User {name} was unregistered ###")
        return True
    except ValueError:
        print(f"### Fail to unregister {name} ###")
        return False
    
def getUsers():

    print(f"### Users were got ###")
    return users

def createRoom(name):

    if (getRoom(name)):
        print(f"### The room '{name}' already exist ###")
        return False
    
    rooms[name] = Room(name)
    print(f"### The room {name} was created ###")
    return True

def deleteRoom(name):
    
    if not (getRoom(name)):
        print(f"### The room '{name}' can not be deleted. This room doesn't exist ###")
        return False
    
    if (len(getRoomUsers(name)) != 0):
        print(f"### The room '{name}' can not be deleted. There is someone in the room ###")
        return False
    
    del rooms[name]
    return True

def joinRoom(user, room):

    if not (checkUser(user)):
        print(f"### There is no user {user} to join room {room} ###")
        return None

    r = getRoom(room)

    if not (r):
        print(f"### User {user} tried to join room {room} but this room doesn't exist ###")
        return False

    if (r.isLogged(user)):
        print(f"### The user {user} is already logged in room {room} ###")
        return False

    print(f"### User {user} joined room {room} ###")
    r.join(user)
    return True

def leaveRoom(user, room):

    if not (checkUser(user)):
        print(f"### There is no user {user} to leave room {room} ###")
        return None

    r = getRoom(room)

    if not (r):
        print(f"### User {user} tried to leave room {room} but this room doesn't exist ###")
        return False
    
    if not (r.isLogged(user)):
        print(f"### The user {user} is not logged in room {room} ###")
        return False
    
    print(f"### User {user} left room {room} ###")
    r.leave(user)
    return True

def getRooms():

    print(f"### Rooms were got ###")
    return [n for n, _ in rooms.items()]

def getRoomUsers(room):

    r = getRoom(room)

    if (r):
        print(f"### User from room {room} were got ###")
        return r.users
    else:
        print(f"### Can't get users from room '{room}'. The room '{room}' doesn't exist ###")
        return None

def sendMessage(user, room, message, to = None):

    if not (checkUser(user)):
        print(f"### There is no user {user} to send a message to room {room} ###")
        return None

    r = getRoom(room)
    
    if not (r):
        print(f"### Can't send a message from user {user} to room '{room}'. The room '{room}' doesn't exist ###")
        return False
    
    if (user == to):
        print(f"### The user {user} tried to send a message to yourself in room {room} ###")
        return False
    
    if (to is not None and getRoomUsers(room).count(to) == 0):
        print(f"### The user {user} tried to send a message to {to} in room {room} but {to} is not in the room ###")
        return False
    
    if not (r.isLogged(user)):
        print(f"### The user {user} tried to send a message to room {room} from outside the room ###")
        return False

    r.sendMsg(user, (message, time.time()), to)
    print(f"### User {user} send a message to room {room} ###")
    return True

def getMessages(user, room):

    if not (checkUser(user)):
        print(f"### There is no user {user} to get messages from room {room} ###")
        return None

    r = getRoom(room)

    if not (r):
        print(f"### Can't get the messages to user {user} from room '{room}'. The room '{room}' doesn't exist ###")
        return None
    
    if not (r.isLogged(user)):
        print(f"### The user {user} tried to get messages from room {room} from outside the room ###")
        return False
    
    print(f"### User {user} got the messages from room {room} ###")
    return r.getMsg(user)

## THREADS ##

def checkEmptyRooms():
    while (True):
        for n, r in rooms.items():
            t = round(time.time() - r.lastUpdate)

            if (t > 10 and r.empty):
                deleteRoom(n)
                break

        time.sleep(1)

t = Thread(target = checkEmptyRooms)
t.start()