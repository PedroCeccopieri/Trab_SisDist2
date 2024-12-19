import xmlrpc.client
import tkinter as tk
import datetime
import math

userLogged = None
roomLooged = None

width = 700
height = 750

root = tk.Tk()
root.title("client")
root.geometry(f'{width}x{height}+100+0')
root.bind_all("<Button-1>", lambda event: event.widget.focus())

# Clear all widgets in the frame #
def clear(f):
    
    for widget in f.winfo_children():
        widget.destroy()

# Setup the conexions with the server and binder #
def setup():
    global server

    with open('servers.txt', 'r') as f:
        ip, port = f.read().split(' ')

    binder = xmlrpc.client.ServerProxy(f'http://{ip}:{port}', allow_none = True)
    serverPort = binder.getService('chat')

    if serverPort is None:
        print("Service not found.")
        exit(1)

    server = xmlrpc.client.ServerProxy(f'http://{ip}:{serverPort}', allow_none = True)

# Login Screen #
def login():

    # Submit the user registration to the server
    def submit():
        global userLogged

        # Remove the error labels
        lbErr1.pack_forget()
        lbErr2.pack_forget()
        
        # Gettin the string in the entry
        nick = name_var.get()

        # Verify if the string is alpha numeric
        if not (nick.isalnum()):
            lbErr1.pack()
            return
        
        # Register user in the server
        r = server.registerUser(nick)
        
        # Verify if the name is duplicated
        if not (r):
            lbErr2.pack()
            return
        
        # Store the username in the client
        userLogged = nick

        # Setting the new screen
        clear(root)
        roomsLobby()

    # Error labels to be shown
    lbErr1 = tk.Label(root, text = "The nickname has to be alphanumeric")
    lbErr2 = tk.Label(root, text = "This nickname was already taken")

    # Binding the return key to subit the nickname
    root.bind('<Return>', lambda _: submit())

    # Varibel to store the entry
    name_var = tk.StringVar()

    # Main Frame
    frame1 = tk.LabelFrame(root, text = "Login")
    frame1.pack()

    # Nickname Label
    lb1 = tk.Label(frame1, text = "Nickname:")
    lb1.grid(row=0, column=0)

    # Nickname Entry
    txtbox1 = tk.Entry(frame1, textvariable = name_var)
    txtbox1.grid(row=0, column=1, padx=5, pady=5)

    # Submit Button
    subBut  = tk.Button(root, width = 15, text = 'Submit', command = submit)
    subBut.pack(pady=5)

# Lobby of the rooms #
def roomsLobby():

    displayedRooms = []

    # Update the rooms #
    def update():

        get()
        frame1.after(1000, update)
    
    # Get the rooms avalible #
    def get():
        nonlocal lstbox

        rooms = server.getRooms()

        # Check if a room was deleted. If so, it clears all the rooms in the listbox
        if (len(displayedRooms) > len(rooms)):
            displayedRooms.clear()
            lstbox.delete(0, tk.END)

        # Insert the rooms in the listbox if it was not added yet
        for r in rooms:
            if (r not in displayedRooms):
                displayedRooms.append(r)
                lstbox.insert(tk.END, f"{r} - Users: {len(server.getRoomUsers(r))}")

        # Update the users count in the listbox
        for idx, item in enumerate(lstbox.get(0, tk.END)):
            n = item[0:item.find(" -")]
            u = int(item[item.find(":") + 2::])

            ru = len(server.getRoomUsers(n))

            if (u != ru):
                lstbox.insert(idx, f"{n} - Users: {ru}")
                lstbox.delete(idx+1)

    # User join routine #
    def join():
        global roomLooged

        # Remove Error labels
        lbJoinErr.pack_forget()

        # Get the name of the room
        name = lstbox.get(lstbox.curselection()[0])
        name = name[0:name.find(" -")]

        # Check if the operation is valid
        if (server.joinRoom(userLogged, name)):

            # Register the room name in the client
            roomLooged = name
            
            # Setting the new screen
            clear(root)
            inChat()

        else:

            # Shows Error label
            lbJoinErr.pack()

    # Create room routine #
    def create():

        # Submit the room creation to the server
        def submit():

            # Remove the error labels
            lbErr1.pack_forget()
            lbErr2.pack_forget()
            
            # Gettin the string in the entry
            name = name_var.get()

            # Verify if the string is alpha numeric
            if not (name.isalnum()):
                lbErr1.pack()
                return
            
            # Register room in the server
            r = server.createRoom(name)

            # Verify if the name is duplicated
            if not (r):
                lbErr2.pack()
                return
            
            # Destroy the window and update the listbox
            crLvl.destroy()
            get()

        # New toplevel screen
        crLvl = tk.Toplevel()

        # Error labels to be shown
        lbErr1 = tk.Label(crLvl, text = "The room name has to be alphanumeric")
        lbErr2 = tk.Label(crLvl, text = "This room already exist")

        # Varibel to store the entry
        name_var = tk.StringVar()

        # Main frame
        frame1 = tk.LabelFrame(crLvl, text = "Create Room")
        frame1.pack()

        # Room name Label
        lb1 = tk.Label(frame1, text = "Room name:")
        lb1.grid(row=0, column=0)

        # Room name Entry
        txtbox1 = tk.Entry(frame1, textvariable = name_var)
        txtbox1.grid(row=0, column=1, padx=5, pady=5)

        # Submit Button
        subBut  = tk.Button(crLvl, width = 15, text = 'Create', command = submit)
        subBut.pack(pady=5)

    # Error labels to be shown
    lbJoinErr = tk.Label(root, text = "Couldn't join the room")

    # Main Frame
    frame1 = tk.LabelFrame(root, text = "Lobby")
    frame1.pack()

    # Rooms Listbox
    lstbox = tk.Listbox(frame1, width = 25, height = 15)
    lstbox.pack(pady = 5, padx = 5)

    # Buttons Frame
    frame12 = tk.Frame(frame1)
    frame12.pack()

    # Create Room Button
    createBut = tk.Button(frame12, width = 10, text = 'Create', command = create)
    createBut.grid(row = 0, column = 0, pady = 5, padx = 5)

    # Join Room Button
    joinBut = tk.Button(frame12, width = 10, text = 'Join', command = join)
    joinBut.grid(row = 0, column = 1, pady = 5, padx = 5)
    
    update()

# In chat screen #
def inChat():

    inchatMsgs = []
    inchatUsers = []

    # Update the messages and users in the room #
    def update():

        getUsers()
        getMsg()
        frame.after(1000, update)

    # Parse the messages to display #
    def parse(line):

        # Number of characteres in each line and number of lines
        n = 60 
        lines = math.ceil(len(line) / n)

        words = []

        for w in line.split(" "):

            # Pre-parse of long words
            if (len(w) > n):
                # Lines occupied by the long word
                q = math.ceil(len(w) / n)
    
                for j in range(q):

                    # Break the long word in chunks of n characters
                    if (j < q - 1):
                        words.append(w[j * n : (j+1) * n])
                    else:
                        words.append(w[j * n ::])
            else:
                # Pre-parse of short words
                words.append(w)

        # Result String
        result = ""

        i, j = 0, 0
        
        # Iterate through all the parsed words to create lines of length n
        # math.ceil((len(line) % n) / n) = 1 if len(line) % n != 0 for the last line that len(line) < n
        for _ in range(lines + math.ceil((len(line) % n) / n)):

            parsedLine = " ".join(words[i:j])
            
            # Get words until the parsed line surpasses n characters
            while (len(parsedLine) <= n and j <= len(words)):
                j += 1
                parsedLine = " ".join(words[i:j])

            # Get the previous word to make len(parsed line) < n
            if (j > 1):
                j -= 1

            parsedLine = " ".join(words[i:j])

            # Add to the result if the parsed line is not empty
            if (parsedLine):
                result += parsedLine + "\n"

            # Go to next line
            i = j

        # Returns the parsed text and the number of lines
        return (result[0:-1], result.count("\n"))

    # Send message to the server #
    def sendMsg(key):

        # Remove Error labels
        errLabel.pack_forget()

        # Gettin the string in the entry
        msg = msgbox.get()

        # Do nothing if the message is empty
        if not (msg):
            return
        
        # Checking if the message is private
        if (msg[0] == "/"):
            m = msg.split(" ")
            to = m[0][1::] # Get the recipient username
            msg = " ".join(m[1::]) # Get the message

            # Try to send the message
            if not (server.sendMessage(userLogged, roomLooged, msg, to)):

                # Show error if the user doesn't exist
                errLabel.pack(side = "left")
            
        else:

            # Send the message
            server.sendMessage(userLogged, roomLooged, msg)

        # Clear the Entry
        msgbox.delete(0, tk.END)

        getMsg()

    # Get the messages from the server #
    def getMsg():

        msgs = []

        # Get the last 50 messages in the server
        for i in server.getMessages(userLogged, roomLooged)[-50::]:
            if (i not in inchatMsgs):
                inchatMsgs.append(i)
                msgs.append(i)

        # Display all the messages that are not yet displayed
        for i in msgs:

            # Get data
            day = datetime.datetime.fromtimestamp(i[1][1]).strftime("%d/%m/%Y %H:%M:%S")
            sender = i[0]
            msg = i[1][0]
            recever = i[2]

            # Check if it's private
            if (sender == userLogged):
                f = tk.LabelFrame(scrollableFrame, text = f"{sender}", labelanchor = "ne")
            else:
                f = tk.LabelFrame(scrollableFrame, text = f"{sender}", labelanchor = "nw")
                
            # Build the container
            f.pack()

            timestamp = tk.Label(f, text = day)
            timestamp.pack()

            if (recever):
                tk.Label(f, text = "* PRIVATE MESSAGE *").pack()
            
            m, l = parse(msg)
            t = tk.Text(f, width = 60, height = l)
            t.insert(tk.END, m)
            t.config(state = tk.DISABLED)
            t.pack(padx = 5)

        # Scroll down if there is new messages and the bar is already down
        if (scrollbar.get()[1] > 0.9):
            canvas.update_idletasks()
            canvas.yview_moveto("1.0")

    # Get users logged in the room #
    def getUsers():

        users = server.getRoomUsers(roomLooged)
        
        # Allow to write in the textbox
        usersBox.config(state = tk.NORMAL)

        # Clear the textbox if some user leave the room
        if (usersBox.get("1.0", tk.END).count("\n") > len(users)):
            inchatUsers.clear()
            usersBox.delete("1.0", tk.END)
        
        # Display all the users that are not yet displayed
        for i in users:
            if (i not in inchatUsers):
                inchatUsers.append(i)

                # Adds a \n for all the users names in the textbox but the first
                if (i != inchatUsers[0]):
                    usersBox.insert(tk.END, "\n")

                usersBox.insert(tk.END, i)

        # Disallow to write in the textbox
        usersBox.config(state = tk.DISABLED)

    # Leave routine #
    def leave():
        global roomLooged
        
        if (server.leaveRoom(userLogged, roomLooged)):
            roomLooged = None
            clear(root)
            roomsLobby()

    # Bind the return key to send the messages
    root.bind('<Return>', sendMsg)

    frame = tk.Frame(root)
    frame.pack()

    # Build Scrollable Frame
    frame1 = tk.Frame(frame)
    frame1.grid(row = 0, column = 0)

    canvas = tk.Canvas(frame1, width = 500, height = 500)
    canvas.pack(side = "left", fill = "both", expand = True, anchor='center')

    scrollbar = tk.Scrollbar(frame1, orient = "vertical", command = canvas.yview)
    scrollbar.pack(side = "right", fill = "y", anchor='center')

    scrollableFrame = tk.Frame(canvas)
    scrollableFrame.bind("<Configure>", lambda _: canvas.configure(scrollregion = canvas.bbox("all")))

    canvas.create_window((0, 0), window = scrollableFrame, anchor="nw")

    canvas.configure(yscrollcommand = scrollbar.set)

    # Build User Box
    usersBox = tk.Text(frame, width = 15, height = 25)
    usersBox.config(state = tk.DISABLED)
    usersBox.grid(row = 0, column = 1)

    # Messages Entry Frame
    frame2 = tk.Frame(root)
    frame2.pack(pady = 10)

    msg_var = tk.StringVar()
    
    msgbox = tk.Entry(frame2, textvariable = msg_var, width = 100)
    msgbox.pack(side = "left", fill = "x", expand = True)

    sendBut = tk.Button(frame2, text = "Send", command = lambda: sendMsg(None))
    sendBut.pack(side = "left")

    # Leave Button
    leaveButt = tk.Button(root, text = "Leave Room", command = leave)
    leaveButt.pack()

    # Error label to be shown
    errLabel = tk.Label(frame2, text = "The message coundn't be sent")

    update()

# Start of the program #
setup()
login()

root.mainloop()

# Logoff when the window closes #
server.leaveRoom(userLogged, roomLooged)
server.unregisterUser(userLogged)