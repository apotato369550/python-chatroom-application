import Tkinter as tk
from Tkinter import *
import ttk
import tkMessageBox
from PIL import ImageTk, Image
import threading
import json
import time
from collections import OrderedDict
import os

import config
import client
import server
import activeWindows

def navigate_connect_tab():
    notebook.select(1)

def navigate_host_tab():
    notebook.select(2)

def window_activity_manager():
    while True:
        if not activeWindows.client_window_isactive:
            if connect_button["state"] == "disabled":
                connect_button["state"] = "normal"
        else:
            if connect_button["state"] == "normal":
                connect_button["state"] = "disabled"

        if not activeWindows.server_window_isactive:
            if host_button["state"] == "disabled":
                host_button["state"] = "normal"
        else:
            if host_button["state"] == "normal":
                host_button["state"] = "disabled"

        if not activeWindows.load_config_window:
            if connect_load_configuration["state"] == "disabled":
                connect_load_configuration["state"] = "normal"
            if host_load_configuration["state"] == "disabled":
                host_load_configuration["state"] = "normal"
        else:
            if connect_load_configuration["state"] == "normal":
                connect_load_configuration["state"] = "disabled"
            if host_load_configuration["state"] == "normal":
                host_load_configuration["state"] = "disabled"

        time.sleep(1)

def run_client():
    ip_address = connect_IP_entry.get()
    port = connect_port_entry.get()
    username = connect_username_entry.get()
    password = connect_password_entry.get()

    activeWindows.client_window_isactive = True
    client.client(ip_address, port, username, password)


def run_server():
    port = host_port_entry.get()
    password = host_password_entry.get()
    room_name = host_room_name_entry.get()

    activeWindows.server_window_isactive = True
    server.server(port, password, room_name)

def open_readme():
    os.system("readme.txt")

def test():
    pass


def load_configurations(config_type):

    def load_selected_configuration():
        try:
            config_selected = load_config_listbox.get(load_config_listbox.curselection())
        except:
            tkMessageBox.showerror("Error", "You have not selected a configuration")
            return

        with open("config.json", "r") as f:
            config_dictionary = json.load(f)
            for type in config_dictionary:
                if type == config_type:
                    config_list = config_dictionary.get(type)
                    for config in config_list:
                        if config == config_selected:
                            configuration = config_list.get(config)
                            if config_type == "client":

                                ip = configuration.get("ip")
                                port = configuration.get("port")
                                username = configuration.get("username")
                                password = configuration.get("password")


                                connect_IP_entry.delete(0, END)
                                connect_port_entry.delete(0, END)
                                connect_username_entry.delete(0, END)
                                connect_password_entry.delete(0, END)

                                connect_IP_entry.insert(0, ip)
                                connect_port_entry.insert(0, port)
                                connect_username_entry.insert(0, username)
                                connect_password_entry.insert(0, password)

                            elif config_type == "server":

                                room_name = configuration.get("room_name")
                                port = configuration.get("port")
                                username = configuration.get("username")
                                password = configuration.get("password")

                                host_port_entry.delete(0, END)
                                host_password_entry.delete(0, END)
                                host_room_name_entry.delete(0, END)

                                host_port_entry.insert(0, port)
                                host_password_entry.insert(0, password)
                                host_room_name_entry.insert(0, room_name)
            f.close()
        config_window.quit()
        close_window()

    def display_configurations():
        file = open("config.json", "r")
        with file as f:
            try:
                config_dictionary = json.load(f, object_pairs_hook=OrderedDict)
                for type in config_dictionary:
                    if type == config_type:
                        config_list = config_dictionary.get(config_type)
                        load_config_listbox.delete(0, tk.END)
                        for config in config_list:
                            load_config_listbox.insert(END, config)

            except:
                tkMessageBox.showerror("Error", "Unable to load configurations")



    def close_window():
        activeWindows.load_config_window = False
        config_window.destroy()

    ### Window
    config_window = tk.Toplevel()
    config_window.title("Configurations")
    config_window.geometry("150x300")
    config_window.iconbitmap("images//logo.ico")
    config_window.geometry("275x350")
    config_window.resizable(False, False)

    activeWindows.load_config_window = True

    config_window.protocol("WM_DELETE_WINDOW", close_window)

    ### Widgets
    main_logo = ImageTk.PhotoImage(Image.open("images//logo.png").resize((33, 33)))

    configuration_type = ""

    if config_type == "client":
        configuration_type = "Client"
    elif config_type == "server":
        configuration_type = "Server"

    load_config_title_label = Label(config_window, text="Load " + configuration_type + " Configuration", font=("Helvetica", 14))
    load_config_listbox = Listbox(config_window, width=25, height=13, borderwidth=5, font=("Courier", 10))
    load_config_load_button = Button(config_window, text="Load", command=load_selected_configuration, borderwidth=3, width=10)
    load_config_cancel_button = Button(config_window, text="Cancel", command=close_window, borderwidth=3, width=10)
    load_config_logo_label = Label(config_window, image=main_logo)

    ### Grids
    load_config_title_label.grid(row=0, column=1, pady=5, columnspan=2)
    load_config_listbox.grid(row=1, column=0, columnspan=4, padx=30, pady=5)
    load_config_load_button.grid(row=2, column=1, padx=10)
    load_config_cancel_button.grid(row=2, column=2)
    load_config_logo_label.grid(row=3, column=1, columnspan=2)

    ### Other commands that need to be run
    display_configurations()

    ### Main loop

    config_window.mainloop()

##### Window, Notebook, Toolbar, and Frames

myCenter = 75 # width/4

root = tk.Tk()
root.title("Supr Simpl Chatroom")
root.iconbitmap("images//logo.ico")
root.geometry("300x500")
root.resizable(False, False)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

toolbar = Menu(root)
root.config(menu=toolbar)


file_menu = Menu(toolbar, tearoff=False)
toolbar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Connect to a Chatroom", command=navigate_connect_tab)
file_menu.add_command(label="Create a Chatroom", command=navigate_host_tab)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.destroy)


help_menu = Menu(toolbar, tearoff=False)
toolbar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Open Readme", command=open_readme)

settings_menu = Menu(toolbar, tearoff=False)
toolbar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Manage Configurations", command=config.manage_configurations)


notebook = ttk.Notebook(root)

home_frame = Frame(notebook)
connect_frame = Frame(notebook)
host_frame = Frame(notebook)

notebook.pack(fill="both", expand=True)

home_frame.pack(fill="both", expand=True)
connect_frame.pack(fill="both", expand=True)
host_frame.pack(fill="both", expand=True)

##### Widgets and Images #####

main_logo = ImageTk.PhotoImage(Image.open("images//logo.png").resize((150, 150)))

## Home

# Images
home_logo_label = Label(home_frame, image=main_logo)

# Labels
home_welcome_message = Label(home_frame, text="This is Supr Simpl Chatroom!", font=("Helvetica", 14))
home_below_welcome_message1 = Label(home_frame, text="Create and connect to your local ")
home_below_welcome_message2 = Label(home_frame, text="chatrooms and send messages real time!")
home_get_started_message = Label(home_frame, text="Get started below!")
home_not_sure_message = Label(home_frame, text="Not sure how to get started?")

# Buttons
home_connect_tab_button = Button(home_frame, text="Connect!", width=10, borderwidth=3, command=navigate_connect_tab)
home_host_tab_button = Button(home_frame, text="Host!", width=10, borderwidth=3, command=navigate_host_tab)
home_open_help_button = Button(home_frame, text="Get Help!", width=10, borderwidth=3, command=open_readme)

## Connect:

# Images
connect_logo_label = Label(connect_frame, image=main_logo)

# Labels
connect_title = Label(connect_frame, text="Connect to a chat server!", font=("Helvetica", 15))
connect_how = Label(connect_frame, text="How it works:", font=("Helvetica", 10))
connect_to1 = Label(connect_frame, text="Enter the LAN IP of the machine you wish to connect.")
connect_to2 = Label(connect_frame, text="Add a username you wish to be known as.")
connect_to3 = Label(connect_frame, text="If the chat is private, add a password!")
connect_IP_label = Label(connect_frame, text="LAN IP:")
connect_port_label = Label(connect_frame, text="Port: ")
connect_username_label = Label(connect_frame, text="Username: ")
connect_password_label = Label(connect_frame, text="Password: ")

# Buttons
connect_button = Button(connect_frame, text="Connect!", command=run_client, borderwidth=3)
connect_load_configuration = Button(connect_frame, text="Load Configuration", command=lambda: load_configurations("client"), borderwidth=3)

# Entry
connect_IP_entry = Entry(connect_frame, width=17, borderwidth=5)
connect_port_entry = Entry(connect_frame, width=17, borderwidth=5)
connect_username_entry = Entry(connect_frame, width=17, borderwidth=5)
connect_password_entry = Entry(connect_frame, width=17, borderwidth=5)

## Host:

# Images
host_logo_label = Label(host_frame, image=main_logo)

# Labels
host_title = Label(host_frame, text="Host a chat server!", font=("Helvetica", 15))
host_how = Label(host_frame, text="How it works:", font=("Helvetica", 10))
host_to1 = Label(host_frame, text="Add a port where your server will receive connections from.")
host_to2 = Label(host_frame, text="Add a username you wish to be known as.")
host_to3 = Label(host_frame, text="Add room name and a password to make it private.")
host_port_label = Label(host_frame, text="Port: ")
host_password_label = Label(host_frame, text="Password: ")
host_room_name_label = Label(host_frame, text="Room Name: ")

# Buttons
host_button = Button(host_frame, text="Host!", command=run_server, borderwidth=3)
host_load_configuration = Button(host_frame, text="Load Configuration",
                                 command=lambda: load_configurations("server"), borderwidth=3)

# Entries
host_port_entry = Entry(host_frame, width=17, borderwidth=5)
host_password_entry = Entry(host_frame, width=17, borderwidth=5)
host_room_name_entry = Entry(host_frame, width=17, borderwidth=5)

### Photo references


##### Grids #####

## Home

# Images
home_logo_label.grid(row=0, column=1, columnspan=2, padx=myCenter)

# Labels
home_welcome_message.grid(row=1, column=1, columnspan=2, pady=10)
home_below_welcome_message1.grid(row=2, column=1, columnspan=2)
home_below_welcome_message2.grid(row=3, column=1, columnspan=2)
home_get_started_message.grid(row=4, column=1, columnspan=2, pady=10)
home_not_sure_message.grid(row=6, column=1, columnspan=2, pady=20)

# Buttons
home_connect_tab_button.grid(row=5, column=0, columnspan=2)
home_host_tab_button.grid(row=5, column=2, columnspan=2)
home_open_help_button.grid(row=7, column=1, columnspan=2)


## Connect

# Images
connect_logo_label.grid(row=14, column=1, columnspan=2, padx=myCenter)

# Labels
connect_title.grid(row=0, column=1, columnspan=2, pady=10)
connect_how.grid(row=1, column=1, columnspan=2)
connect_to1.grid(row=2, column=1, columnspan=2)
connect_to2.grid(row=3, column=1, columnspan=2)
connect_to3.grid(row=4, column=1, columnspan=2)
connect_IP_label.grid(row=6, column=0, columnspan=2)
connect_port_label.grid(row=8, column=0, columnspan=2)
connect_username_label.grid(row=10, column=0, columnspan=2)
connect_password_label.grid(row=12, column=0, columnspan=2)

# Buttons
connect_load_configuration.grid(row=8, column=2, columnspan=2)
connect_button.grid(row=11, column=2, columnspan=2)

# Entries
connect_IP_entry.grid(row=7, column=0, columnspan=2)
connect_port_entry.grid(row=9, column=0, columnspan=2)
connect_username_entry.grid(row=11, column=0, columnspan=2)
connect_password_entry.grid(row=13, column=0, columnspan=2)

## Host

# Images
host_logo_label.grid(row=14, column=1, columnspan=2, padx=myCenter)

# Labels
host_title.grid(row=0, column=1, columnspan=2, pady=10)
host_how.grid(row=1, column=1, columnspan=2)
host_to1.grid(row=2, column=1, columnspan=2)
host_to2.grid(row=3, column=1, columnspan=2)
host_to3.grid(row=4, column=1, columnspan=2)
host_port_label.grid(row=6, column=0, columnspan=2)
host_password_label.grid(row=8, column=0, columnspan=2)
host_room_name_label.grid(row=10, column=0, columnspan=2)

# Buttons
host_load_configuration.grid(row=8, column=2, columnspan=2)
host_button.grid(row=11, column=2, columnspan=2)

# Entries
host_port_entry.grid(row=7, column=0, columnspan=2)
host_password_entry.grid(row=9, column=0, columnspan=2)
host_room_name_entry.grid(row=11, column=0, columnspan=2)

### Frames
notebook.add(home_frame, text="Home")
notebook.add(connect_frame, text="Connect")
notebook.add(host_frame, text="Host")

# Threads
window_manager_thread = threading.Thread(target=window_activity_manager)
window_manager_thread.daemon = True
window_manager_thread.start()

if not os.path.exists("config.json"):
    print("file does not exist")
    config_file = open("config.json", "w+")
    with config_file as f:
        config_template = {
            "client": {},
            "server": {}
        }
        json.dump(config_template, f, indent=1)

root.mainloop()