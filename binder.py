from xmlrpc.server import SimpleXMLRPCServer

# Dictionary to store the services and its port #
services = {}

# Register a service in the binder #
def setService(name, port):
    services[name] = port
    print(f"Serviço {name} registrado na porta {port}")
    return True

# Get a service in the binder #
def getService(name):
    return services.get(name, None)

# Get the binder's IP and port #
with open('servers.txt', 'r') as f:
    ip, port = f.read().split(' ')

# Create XML-RPC server for the binder #
binder_server = SimpleXMLRPCServer((ip, int(port)), allow_none=True)
print("Binder pronto e aguardando registros...")

# Function Registration #
binder_server.register_function(setService, "setService")
binder_server.register_function(getService, "getService")

# Keeps the server running #
binder_server.serve_forever()
