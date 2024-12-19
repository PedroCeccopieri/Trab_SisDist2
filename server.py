from services import *

from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client

#  Server Configuration #
serverIp = '127.0.0.1'
serverPort = 5298
server = SimpleXMLRPCServer((serverIp, serverPort), allow_none=True)
print("Chat server waiting connexions...")

# Function Registration #
server.register_function(registerUser, "registerUser")
server.register_function(unregisterUser, "unregisterUser")
server.register_function(getUsers, "getUsers")

server.register_function(createRoom, "createRoom")
server.register_function(joinRoom, "joinRoom")
server.register_function(leaveRoom, "leaveRoom")
server.register_function(getRooms, "getRooms")
server.register_function(getRoomUsers, "getRoomUsers")
server.register_function(sendMessage, "sendMessage")
server.register_function(getMessages, "getMessages")

# Get the binder's IP and port #
with open('servers.txt', 'r') as f:
    binderIp, binderPort = f.read().split(' ')

binder = xmlrpc.client.ServerProxy(f'http://{binderIp}:{binderPort}', allow_none = True)
binder.setService('chat', serverPort)

# Keeps the server running #
server.serve_forever()
