import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import socket
import threading
import activeWindows
import tkMessageBox


def client(ip_address, port, username, password):

    def validate_client():
        # print("attempting to validate client...")

        IP = ip_address
        PORT = int(port)
        PASSWORD = password
        USERNAME = username

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server.connect((IP, PORT))
            server.send("0")
            confirmed = server.recv(2000)
            if bool(int(confirmed)):
                pass
            else:
                tkMessageBox.showwarning("Warning", "Unable to connect to server")
                return False
        except:
            return False

        try:
            server.send(PASSWORD)
            validated = server.recv(2000)
            if bool(int(validated)):
                pass
            else:
                tkMessageBox.showwarning("Warning", "Wrong password")
                return False

        except:
            return False

        try:
            server.send(USERNAME)
            validated = server.recv(2000)
            if bool(int(validated)):
                pass
            else:
                tkMessageBox.showwarning("Warning", "Username is already in use. Please select another one")
                return False
        except:
            return False

        server.close()
        return True

    def client_thread():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server.connect((ip_address, int(port)))
            server.send("1")
            server.recv(2000)
            server.send(username)
            server.recv(2000)
        except:
            exit()

        room_name = server.recv(2000)

        client_title_label.config(text=room_name)

        def send_message(event):
            message = client_chat_bar.get()
            if not message == "":
                try:
                    server.send(message)
                except:
                    pass
                client_chat_bar.delete(0, END)

        def action_handler(action):
            if " " in action:
                action_split = action.split(" ", 1)

                command = action_split[0]
                parameter = action_split[1]

                if command == "rnc":
                    client_title_label.config(text=parameter)
            else:
                command = action

                if command == "k":
                    client_chat_window.config(state=NORMAL)
                    client_chat_window.insert(END, "You have been kicked from the chatroom")
                    client_chat_window.config(state=DISABLED)
                    server.close()
                elif command == "d":
                    client_chat_window.config(state=NORMAL)
                    client_chat_window.insert(END, "You have disconnected from the chatroom")
                    client_chat_window.config(state=DISABLED)
                    server.close()
                elif command == "sd":
                    client_chat_window.config(state=NORMAL)
                    client_chat_window.insert(END, "The server has been shut down")
                    client_chat_window.config(state=DISABLED)
                    server.close()
                elif command == "m":
                    client_chat_window.config(state=NORMAL)
                    client_chat_window.insert(END, "You have been muted. Messages you send will no longer be processed \n")
                    client_chat_window.config(state=DISABLED)
                elif command == "um":
                    client_chat_window.config(state=NORMAL)
                    client_chat_window.insert(END, "You have been unmuted. Messages you send will now be seen \n")
                    client_chat_window.config(state=DISABLED)
                elif command == "df":
                    client_chat_window.config(state=NORMAL)
                    client_chat_window.insert(END, "You have been deafened. You will no longer receive messages \n")
                    client_chat_window.config(state=DISABLED)
                elif command == "udf":
                    client_chat_window.config(state=NORMAL)
                    client_chat_window.insert(END, "You have been undeafened. You can now receive messeges \n")
                    client_chat_window.config(state=DISABLED)
                else:
                    pass


        def disconnect():
            try:
                server.send("***d " + username)
            except:
                pass
            activeWindows.client_window_isactive = False
            client_window.destroy()



        client_send_button.bind("<Button-1>", send_message)
        client_window.bind("<Return>", send_message)

        client_window.protocol("WM_DELETE_WINDOW", disconnect)

        while True:
            try:
                message = server.recv(2000)
                if message[0: 3] == "***":
                    action_handler(message[3:])
                    if message == "***k" or message == "***d" or message == "***sd":
                        break
                else:
                    client_chat_window.config(state=NORMAL)
                    client_chat_window.insert(END, message)
                    client_chat_window.config(state=DISABLED)
            except:
                continue


    if port == "" or username == "" or ip_address == "":
        tkMessageBox.showerror("Error", "One or more your fields are blank. Please fill them.")
        activeWindows.client_window_isactive = False
        return

    try:
        socket.inet_aton(ip_address)
    except:
        tkMessageBox.showerror("Error", "Invalid IP address")
        activeWindows.client_window_isactive = False
        return

    try:
        int(port)
    except:
        tkMessageBox.showerror("Error", "Your port number is invalid")
        activeWindows.client_window_isactive = False
        return



    if not validate_client():
        tkMessageBox.showerror("Error", "Unable to validate client")
        activeWindows.client_window_isactive = False
        return

    ### Window and Toolbar

    client_window = tk.Toplevel()
    client_window.iconbitmap("images//logo.ico")
    client_window.geometry("300x500")
    client_window.geometry("300x500")
    client_window.resizable(False, False)

    toolbar = Menu(client_window)
    client_window.config(menu=toolbar)

    toolbar.add_command(label="Exit")
    toolbar.add_command(label="Help")

    main_logo = ImageTk.PhotoImage(Image.open("images//logo.png").resize((100, 100)))

    client_title_label = Label(client_window, text="Sample Chatroom!", font=("Helvetica", 15))
    client_chat_window = Text(client_window, width=40, height=17, borderwidth=5, wrap=WORD)
    client_chat_bar = Entry(client_window, width=33, borderwidth=5)
    client_send_button = Button(client_window, text="Send", width=10, borderwidth=3)
    client_logo_label = Label(client_window, image=main_logo)

    client_chat_window.config(state=DISABLED)

    ##### Grids #####

    client_title_label.grid(row=0, column=0, pady=3)
    client_chat_window.grid(row=1, column=0, columnspan=2, pady=3)
    client_chat_bar.grid(row=2, column=0, pady=3)
    client_send_button.grid(row=2, column=1, pady=3)
    client_logo_label.grid(row=4, pady=5, columnspan=2)

    ### starting client thread
    ct = threading.Thread(target=client_thread)
    ct.daemon = True
    ct.start()


    client_window.mainloop()


