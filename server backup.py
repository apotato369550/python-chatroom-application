import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import ttk
import tkMessageBox
import socket
import time
import threading

import activeWindows

def server(port, host_username, password, room_name):

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

        print("server_thread is running")

        server.listen(5)

        def validate_client(connection):

            try:
                client_password = connection.recv(2000)
                print(client_password)
                if client_password == password:
                    # print("passwords match")
                    connection.send("1")
                else:
                    # print("passwords do not match")
                    connection.send("0")
                    return False
            except:
                # print("Unable to validate password")
                connection.send("0")
                connection.close()
                return False

            try:
                client_username = connection.recv(2000)
                # print(client_username)
                # print("username validated")
                if client_username not in clients_list:
                    connection.send("1")
                else:
                    connection.send("0")

                return True
            except:
                # print("unable to validate username")
                connection.send("0")
                connection.close()
                return False


        def client_thread(client, username):

            print("Running client_thread")

            client.send(room_name)

            for message in messages:
                print(message)
                client.send(message)

            broadcast_message("", username + " has entered the chat \n")

            while True:
                try:
                    message = client.recv(2000)
                    print("message received")
                    if message:
                        if message[0: 3] == "***":
                            print("command received")
                            action_handler(message[3:])
                        elif username not in mute_list:
                            broadcast_message(username, message)
                    else:
                        client.close()
                        remove(username)

                except:
                    continue

        def action_handler(action):
            # print("running action handler")
            # print(action + " - action")
            # print("printing sdfasdfsd")
            action_split = action.split(" ", 1)

            for action in action_split:
                print(action)

            command = action_split[0]
            parameter = action_split[1]

            # print(command)
            # print(parameter)

            if command == "d":
                disconnect(parameter)


        def broadcast_message(sender, message):
            for client in clients_list:
                if client not in deaf_list:
                    if sender != "":
                        full_message = sender + ":   " + message + "\n"
                    else:
                        full_message = message
                    clients_list[client].send(full_message)
                    messages.append(full_message)
            print("Message broadcasted")
            # print(message)

        def remove(connection):
            # print(connection)
            if connection in clients_list:
                clients_list.pop(connection, None)
                # print(clients_list)
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

                print("Connection removed")

        def change_room_name():
            new_room_name = actions_edit_room_name_entry.get()

            actions_edit_room_name_entry.delete(0, END)

            details_chatroom_name_label.config(text=new_room_name)

            broadcast_message("", "***rnc " + new_room_name)


        def shutdown():
            try:
                print("shutting down")
                for client in clients_list:
                    clients_list[client].send("***sd")

                time.sleep(1)
                clients_list.clear()
                server.close()
            except:
                print("unable to shut down")
            activeWindows.server_window_isactive = False
            server_window.destroy()

        def disconnect(user):
            try:
                clients_list[user].send("***d")
                remove(user)
                print("user has disconnected")
                broadcast_message("", user + " has disconnected \n")
            except:
                print("unable to disconnect user")



        def kick():
            try:
                print("getting selected user")
                user = actions_server_connections_listbox.get(actions_server_connections_listbox.curselection())
                clients_list[user].send("***k")
                remove(user)
                print("user has been kicked")
                broadcast_message("", user + " has been kicked from the chat \n")
            except:
                print("unable to get selected user")


        def mute():
            try:
                user = actions_server_connections_listbox.get(actions_server_connections_listbox.curselection())
                if user in mute_list:
                    clients_list[user].send("***um")
                    broadcast_message("", user + " has been unmuted \n")
                    mute_list.remove(user)
                else:
                    clients_list[user].send("***m")
                    broadcast_message("", user + " has been muted \n")
                    mute_list.append(user)
                print("user has been muted/unmuted")
            except:
                print("unable to get selected user")

        def deafen():
            print("printing user about to be deafened")
            try:
                user = actions_server_connections_listbox.get(actions_server_connections_listbox.curselection())
                if user not in deaf_list:
                    clients_list[user].send("***df")
                    broadcast_message("", user + " has been deafened \n")
                    deaf_list.append(user)
                else:
                    clients_list[user].send("***udf")
                    broadcast_message("", user + " has been undeafened \n")
                    deaf_list.remove(user)
                print("user has been deafened/undeafened")
                print(str(deaf_list))
            except:
                print("unable to get selected user for deafening")


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
                print("validated: " + validated)
                clientsocket.send("1")
                if bool(int(validated)):
                    client_username = clientsocket.recv(2000)
                    clients_list[client_username] = clientsocket
                    details_server_connections_listbox.insert(END, client_username)
                    actions_server_connections_listbox.insert(END, client_username)
                    clientsocket.send("1")
                    ct = threading.Thread(target=client_thread, args=(clientsocket, client_username))
                    ct.daemon = True
                    ct.start()
                elif not validate_client(clientsocket):
                    clientsocket.close()
            except:
                break
        print("broke out of loop")


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

    def alert_popup(title, reason, description):
        popup = tk.Toplevel()
        popup.title(title)

        title = Label(popup, text=title + ":")
        description = Label(popup, text=reason + ": " + description)
        ok_button = Button(popup, text="OK", command=popup.destroy)

        title.pack()
        description.pack()
        ok_button.pack()

        popup.mainloop()

    if port == "" or host_username == "" or room_name == "":
        alert_popup("Error", "Parameter Error", "One or more of your parameters are either invalid or blank.")
        exit()

    try:
        int(port)
    except:
        alert_popup("Error", "Parameter Error", "Your port number is invalid.")
        exit()


    ### Window, Notebook, Toolbar, and Frames

    server_window = tk.Toplevel()
    server_window.title(room_name)
    server_window.geometry("350x500")
    server_window.iconbitmap("images//logo.ico")
    server_window.resizable(False, False)

    toolbar = Menu(server_window)
    server_window.config(menu=toolbar)

    toolbar.add_command(label="Exit", command=server_window.destroy)
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
    chat_main_logo = ImageTk.PhotoImage(Image.open("images//logo.png").resize((100, 100)))

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

    ### Logs

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

    ### Mainloop
    server_window.mainloop()




