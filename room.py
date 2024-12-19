import time

class Room:

    def __init__(self, name):
        
        self.name = name

        self.users = []
        self.msgs = []

        self.lastUpdate = time.time()
        self.empty = True

    def join(self, user):

        self.users.append(user)
        self.empty = False

    def leave(self, user):

        self.users.remove(user)

        if (len(self.users) == 0):
            self.empty = True
            self.lastUpdate = time.time()

    def sendMsg(self, user, msg, to):

        self.msgs.append((user, msg, to))

    def getMsg(self, user):

        return [i for i in self.msgs if (i[2] == None or i[2] == user or i[0] == user)]
    
    def isLogged(self, user):
        return self.users.count(user) == 1
