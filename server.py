import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import messagebox
import socket
import time
import threading

import activeWindows
import client

def server(port, password, room_name):

    def test():
        return

    def server_thread():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind(("", int(port)))

        clients_list = {}
        mute_list = []
        deaf_list = []
        messages = []


        server.listen(5)

        def validate_client(connection):
            print("Validating client... ")
            try:
                client_password = connection.recv(2000)
                print(client_password)
                print("password: " + client_password.decode("utf-8"))
                if client_password.decode("utf-8") == password:
                    connection.send(bytes("1", "utf-8"))
                else:
                    connection.send(bytes("0", "utf-8"))
                    return False
            except Exception as e:
                print("server 1: " + e)
                connection.send(bytes("0", "utf-8"))
                connection.close()
                return False

            try:
                client_username = connection.recv(2000)
                if client_username.decode("utf-8") not in clients_list:
                    connection.send(bytes("1", "utf-8"))
                else:
                    connection.send(bytes("0", "utf-8"))

                return True
            except:
                connection.send(bytes("0", "utf-8"))
                connection.close()
                return False


        def client_thread(client, username):

            print("Running client_thread")

            client.send(bytes(room_name, "utf-8"))

            for message in messages:
                print(message)
                client.send(bytes(message, "utf-8"))

            print("Type of username: " + str(type(username)))
            broadcast_message("", username.decode("utf-8") + " has entered the chat \n")

            while True:
                try:
                    message = client.recv(2000).decode("utf-8")
                    print(message)
                    print("message received")
                    if message:
                        if message[0: 3] == "***":
                            print("command received")
                            action_handler(message[3:])
                        elif username not in mute_list:
                            print("broadcasting message")
                            broadcast_message(username.decode("utf-8"), message)
                        else:
                            print("poo poo")
                    else:
                        print("Client closed:(")
                        client.close()
                        remove(username)

                except:
                    continue

        def action_handler(action):
            action_split = action.split(" ", 1)

            for action in action_split:
                print(action)

            command = action_split[0]
            parameter = action_split[1]

            if command == "d":
                disconnect(parameter)


        def broadcast_message(sender, message):
            for client in clients_list:
                if client not in deaf_list:
                    if sender != "":
                        full_message = sender + ":   " + message + "\n"
                    else:
                        full_message = message
                    clients_list[client].send(bytes(full_message, "utf-8"))
                    messages.append(full_message)
# message received


        def remove(connection):
            if connection in clients_list:
                clients_list.pop(connection, None)
                details_clients = list(details_server_connections_listbox.get(0, END))
                action_clients = list(actions_server_connections_listbox.get(0, END))

                for client in details_clients:
                    if client == connection:
                        details_clients.remove(client)

                for client in action_clients:
                    if client == connection:
                        action_clients.remove(client)

                details_server_connections_listbox.delete(0, END)
                actions_server_connections_listbox.delete(0, END)

                for client in details_clients:
                    details_server_connections_listbox.insert(END, client)

                for client in action_clients:
                    actions_server_connections_listbox.insert(END, client)


        def change_room_name():
            new_room_name = actions_edit_room_name_entry.get()
            if new_room_name == "":
                return
            actions_edit_room_name_entry.delete(0, END)
            details_chatroom_name_label.config(text=new_room_name)
            broadcast_message("", "***rnc " + new_room_name)
            log_action("Successfully changed room name to " + new_room_name)



        def shutdown():
            try:
                for client in clients_list:
                    clients_list[client].send("***sd")
                log_action("Shutting down server...")

                time.sleep(1)
                clients_list.clear()
                server.close()
            except:
                pass
            activeWindows.server_window_isactive = False
            server_window.destroy()

        def disconnect(user):
            try:
                clients_list[user].send("***d")
                remove(user)
                broadcast_message("", user + " has disconnected \n")
                log_action(user + "has disconnected")
            except:
                pass



        def kick():
            try:
                user = actions_server_connections_listbox.get(actions_server_connections_listbox.curselection())
                clients_list[user].send("***k")
                remove(user)
                broadcast_message("", user + " has been kicked from the chat \n")
                log_action(user + "has been kicked from the chat")
            except:
                pass


        def mute():
            try:
                user = actions_server_connections_listbox.get(actions_server_connections_listbox.curselection())
                if user in mute_list:
                    clients_list[user].send("***um")
                    broadcast_message("", user + " has been unmuted \n")
                    log_action(user + "has been unmuted")
                    mute_list.remove(user)
                else:
                    clients_list[user].send("***m")
                    broadcast_message("", user + " has been muted \n")
                    log_action(user + "has been muted")
                    mute_list.append(user)
            except:
                pass

        def deafen():
            try:
                user = actions_server_connections_listbox.get(actions_server_connections_listbox.curselection())
                if user not in deaf_list:
                    clients_list[user].send("***df")
                    broadcast_message("", user + " has been deafened \n")
                    log_action(user + "has been deafened")
                    deaf_list.append(user)
                else:
                    clients_list[user].send("***udf")
                    broadcast_message("", user + " has been undeafened \n")
                    log_action(user + "has been undeafened")
                    deaf_list.remove(user)
            except:
                pass


        actions_edit_room_name_button.config(command=change_room_name)
        actions_mute_user_button.config(command=mute)
        actions_deafen_user_button.config(command=deafen)
        actions_kick_user_button.config(command=kick)
        actions_shutdown_server_button.config(command=shutdown)

        server_window.protocol("WM_DELETE_WINDOW", shutdown)

        # print("Button has been bound")

        while True:
            clientsocket, address = server.accept()

            try:
                validated = clientsocket.recv(2000)
                clientsocket.send(bytes("1", "utf-8"))
                if bool(int(validated)):
                    print("validated:D")
                    client_username = clientsocket.recv(2000)
                    clients_list[client_username] = clientsocket
                    details_server_connections_listbox.insert(END, client_username)
                    actions_server_connections_listbox.insert(END, client_username)
                    clientsocket.send(bytes("1", "utf-8"))
                    ct = threading.Thread(target=client_thread, args=(clientsocket, client_username))
                    ct.daemon = True
                    ct.start()
                    log_action(client_username.decode("utf-8") + " [" + address[0] + "] has entered the chat")
                elif not validate_client(clientsocket):
                    print("Not validated:(")
                    clientsocket.close()
            except Exception as e:
                print("server 2: " + str(e))
                break

    def log_action(action):
        try:
            log_window.config(state=NORMAL)
            log_window.insert(END, "///" + action + "/// \n")
            log_window.config(state=DISABLED)
        except:
            pass

    def timer():
        timer_counter = [0, 0, 0]
        timer_pattern = '{0:02d}:{1:02d}:{2:02d}'

        while True:
            timer_counter[2] += 1
            if timer_counter[2] >= 60:
                timer_counter[2] = 0
                timer_counter[1] += 1

            if timer_counter[1] >= 60:
                timer_counter[1] = 0
                timer_counter[0] += 1

            time_string = timer_pattern.format(timer_counter[0], timer_counter[1], timer_counter[2])
            try:
                details_server_time_running.config(text=time_string)
            except:
                pass
            time.sleep(1)



    def display_server_details():
        details_server_ip_address.config(text=socket.gethostbyname(socket.gethostname()))
        details_server_port.config(text=str(port))
        details_server_password.config(text=password)


    if port == "" or room_name == "":
        messagebox.showerror("Error", "One or more of your fields are blank. Please fill them.")
        activeWindows.server_window_isactive = False
        return

    try:
        int(port)
    except:
        messagebox.showerror("Error", "Please Enter a valid port number.")
        activeWindows.server_window_isactive = False
        return





    ### Window, Notebook, Toolbar, and Frames

    server_window = tk.Toplevel()
    server_window.title(room_name)
    server_window.geometry("350x500")
    server_window.iconbitmap("images//logo.ico")
    server_window.resizable(False, False)

    toolbar = Menu(server_window)
    server_window.config(menu=toolbar)

    toolbar.add_command(label="Exit", command=test)
    toolbar.add_command(label="Help", command=test)
    toolbar.add_command(label="Test", command=test)

    notebook = ttk.Notebook(server_window)

    details_frame = Frame(notebook)
    action_frame = Frame(notebook)
    logs_frame = Frame(notebook)

    notebook.pack(fill="both", expand=True)

    details_frame.pack(fill="both", expand=True)
    action_frame.pack(fill="both", expand=True)
    logs_frame.pack(fill="both", expand=True)

    ##### Widgets and Images #####

    details_main_logo = ImageTk.PhotoImage(Image.open("images//logo.png").resize((30, 30)))
    actions_main_logo = ImageTk.PhotoImage(Image.open("images//logo.png").resize((75, 75)))
    log_main_logo = ImageTk.PhotoImage(Image.open("images//logo.png").resize((50, 50)))

    ### Details

    # Labels
    details_chatroom_name_label = Label(details_frame, text=room_name, font=("Helvetica", 15))
    details_title_label = Label(details_frame, text="Server Details:", font=("Helvetica", 14))
    details_server_room_name_label = Label(details_frame, text="Room Name: ", font=("Helvetica", 10))
    details_server_time_running_label = Label(details_frame, text="Time Active: ", font=("Helvetica", 10))
    details_server_ip_address_label = Label(details_frame, text="Server IPV4 Address: ", font=("Helvetica", 10))
    details_server_port_label = Label(details_frame, text="Server Port: ", font=("Helvetica", 10))
    details_server_password_label = Label(details_frame, text="Server Password: ", font=("Helvetica", 10))
    details_server_connections_label = Label(details_frame, text="Connected Clients: ", font=("Helvetica", 10))

    details_server_room_name = Label(details_frame, text=room_name)
    details_server_time_running = Label(details_frame, text="00:00")
    details_server_ip_address = Label(details_frame, text="XXX.XXX.X.XXX")
    details_server_port = Label(details_frame, text="1234")
    details_server_password = Label(details_frame, text="abcdefg123")

    details_logo_label = Label(details_frame, image=details_main_logo)

    # Listboxes
    details_server_connections_listbox = Listbox(details_frame, width=33, height=8, borderwidth=5, font=("Courier", 13))

    ### Actions

    # Labels
    actions_title_label = Label(action_frame, text="Server Actions", font=("Helvetica", 15))
    actions_logo_label = Label(action_frame, image=actions_main_logo)

    # Buttons
    actions_edit_room_name_button = Button(action_frame, text="Change Room Name", borderwidth=3)
    actions_kick_user_button = Button(action_frame, text="Kick User", borderwidth=3)
    actions_mute_user_button = Button(action_frame, text="Mute/Unmute User", borderwidth=3)
    actions_deafen_user_button = Button(action_frame, text="Deafen/Undeafen User", borderwidth=3)
    actions_shutdown_server_button = Button(action_frame, text="Shut down Server", borderwidth=3)

    # Entries
    actions_edit_room_name_entry = Entry(action_frame, borderwidth=5)

    # Listboxes
    actions_server_connections_listbox = Listbox(action_frame, width=33, height=8, borderwidth=5, font=("Courier", 13))

    ### Logs

    # Labels
    log_title_label = Label(logs_frame, text="Logged Actions and Events: ", font=("Helvetica", 15))
    log_logo_label = Label(logs_frame, image=log_main_logo)

    # Listboxes
    log_window = Text(logs_frame, width=40, height=17, borderwidth=5, font=("Courier", 10), wrap=WORD)

    log_window.config(state=DISABLED)



    ##### Grids #####

    ### Details

    # Labels
    details_chatroom_name_label.grid(row=0, column=0, pady=3, columnspan=2)
    details_title_label.grid(row=1, column=0, pady=1, columnspan=2)
    details_server_room_name_label.grid(row=2, column=0, pady=1)
    details_server_time_running_label.grid(row=3, column=0, pady=1)
    details_server_ip_address_label.grid(row=4, column=0, pady=1)
    details_server_port_label.grid(row=5, column=0, pady=1)
    details_server_password_label.grid(row=6, column=0, pady=1)
    details_server_connections_label.grid(row=7, column=0, pady=1)

    details_server_room_name.grid(row=2, column=1, pady=1)
    details_server_time_running.grid(row=3, column=1)
    details_server_ip_address.grid(row=4, column=1)
    details_server_port.grid(row=5, column=1)
    details_server_password.grid(row=6, column=1)

    details_logo_label.grid(row=9, column=0, columnspan=2)

    # Listboxes
    details_server_connections_listbox.grid(row=8, column=0, columnspan=2, pady=7)

    ### Actions

    # Labels
    actions_title_label.grid(row=0, column=0, columnspan=2, pady=5)
    actions_logo_label.grid(row=6, column=0, columnspan=2)

    # Buttons
    actions_edit_room_name_button.grid(row=1, column=0, pady=5)
    actions_mute_user_button.grid(row=2, column=1, pady=5)
    actions_deafen_user_button.grid(row=2, column=0, pady=5)
    actions_kick_user_button.grid(row=4, column=0, pady=5, columnspan=2)
    actions_shutdown_server_button.grid(row=5, column=0, pady=5, columnspan=2)

    # Entries
    actions_edit_room_name_entry.grid(row=1, column=1, pady=5)

    # Listboxes
    actions_server_connections_listbox.grid(row=3, column=0, columnspan=2, pady=5)

    ### Logs

    # Labels
    log_title_label.grid(row=0, column=0, columnspan=2, pady=7)

    log_logo_label.grid(row=2, column=0, columnspan=2)

    # Listboxes
    log_window.grid(row=1, column=0, columnspan=2, pady=5)


    ### Frames
    notebook.add(details_frame, text="Details")
    notebook.add(action_frame, text="Actions")
    notebook.add(logs_frame, text="Log")

    ### Commands to be run
    display_server_details()

    st = threading.Thread(target=server_thread)
    st.daemon = True
    st.start()

    tt = threading.Thread(target=timer)
    tt.daemon = True
    tt.start()

    log_action("Started chatroom [" + room_name +"]")

    ### Mainloop
    server_window.mainloop()




