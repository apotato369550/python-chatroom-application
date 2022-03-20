import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import ttk
import tkMessageBox
import json
from collections import OrderedDict

import activeWindows


def manage_configurations():


    def delete_configuration(config_type):
        try:
            if config_type == "client":
                client_config_listbox.get(client_config_listbox.curselection())
            elif config_type == "server":
                server_config_listbox.get(server_config_listbox.curselection())
        except:
            return

        config_selected = ""

        if config_type == "client":
            config_selected = client_config_listbox.get(client_config_listbox.curselection())
        elif config_type == "server":
            config_selected = server_config_listbox.get(server_config_listbox.curselection())

        config_dictionary = {}

        with open("config.json", "r") as f:
            config_dictionary = json.load(f, object_pairs_hook=OrderedDict)
            f.close()

        config_dictionary.get(config_type).pop(config_selected)

        with open("config.json", "w") as f:
            json.dump(config_dictionary, f, indent=1)
            f.close()

        display_configurations()




    def edit_configuration(config_type):

        config_selected = ""

        try:
            if config_type == "client":
                config_selected = client_config_listbox.get(client_config_listbox.curselection())
            elif config_type == "server":
                config_selected = server_config_listbox.get(server_config_listbox.curselection())
        except:
            tkMessageBox.showerror("Error", "You have not selected a configuration")
            return

        with open("config.json") as f:
            config_dictionary = json.load(f)
            config_list = config_dictionary.get(config_type)
            for config in config_list:
                if config == config_selected:
                    if config_type == "client":
                        ip = config_list.get(config).get("ip")
                        port = config_list.get(config).get("port")
                        username = config_list.get(config).get("username")
                        password = config_list.get(config).get("password")

                        client_config_name_entry.delete(0, END)
                        client_config_ip_address_entry.delete(0, END)
                        client_config_port_entry.delete(0, END)
                        client_config_username_entry.delete(0, END)
                        client_config_password_entry.delete(0, END)

                        client_config_name_entry.insert(0, config)
                        client_config_ip_address_entry.insert(0, ip)
                        client_config_port_entry.insert(0, port)
                        client_config_username_entry.insert(0, username)
                        client_config_password_entry.insert(0, password)


                    elif config_type == "server":
                        room_name = config_list.get(config).get("room_name")
                        port = config_list.get(config).get("port")
                        password = config_list.get(config).get("password")

                        server_config_name_entry.delete(0, END)
                        server_config_room_name_entry.delete(0, END)
                        server_config_port_entry.delete(0, END)
                        server_config_password_entry.delete(0, END)

                        server_config_name_entry.insert(0, config)
                        server_config_room_name_entry.insert(0, room_name)
                        server_config_port_entry.insert(0, port)
                        server_config_password_entry.insert(0, password)




    def save_configuration(config_type):
        new_config = {}

        if config_type == "client":
            configuration_name = client_config_name_entry.get()
            ip_address = client_config_ip_address_entry.get()
            port = client_config_port_entry.get()
            username = client_config_username_entry.get()
            password = client_config_password_entry.get()

            if ip_address == "" or port == "" or username == "":
                tkMessageBox.showerror("Error", "Lacking one or more parameters")
                return

            new_config = {
                configuration_name: {
                    "ip": ip_address,
                    "port": port,
                    "username": username,
                    "password": password
                }
            }

        elif config_type == "server":
            configuration_name = server_config_name_entry.get()
            room_name = server_config_room_name_entry.get()
            port = server_config_port_entry.get()
            password = server_config_password_entry.get()

            if room_name == "" or port == "":
                tkMessageBox.showerror("Error", "Lacking one or more parameters")
                return

            new_config = {
                configuration_name: {
                    "room_name": room_name,
                    "port": port,
                    "password": password
                }
            }

        with open("config.json", "r") as f:
            config_dictionary = json.load(f, object_pairs_hook=OrderedDict)
            f.close()

        config_dictionary.get(config_type).update(new_config)

        with open("config.json", "w") as f:
            json.dump(config_dictionary, f, indent=1)
            f.close()

        display_configurations()


    def display_configurations():
        file = open("config.json", "r")
        with file as f:
            try:
                config_dictionary = json.load(f, object_pairs_hook=OrderedDict)
                for config_type in config_dictionary:
                    config_list = config_dictionary.get(config_type)
                    if config_type == "client":
                        client_config_listbox.delete(0, tk.END)
                        for config in config_list:
                            client_config_listbox.insert(END, config)
                    elif config_type == "server":
                        server_config_listbox.delete(0, tk.END)
                        for config in config_list:
                            server_config_listbox.insert(END, config)
            except:
                tkMessageBox.showerror("Error", "Unable to load configurations")


    def close_window():
        activeWindows.edit_config_window_isactive = False
        config_window.destroy()

    ### Window, Notebook, and Frames
    config_window = tk.Toplevel()
    config_window.title("Configurations")
    config_window.iconbitmap("images//logo.ico")
    config_window.geometry("455x400")
    config_window.resizable(False, False)

    notebook = ttk.Notebook(config_window)

    client_config_frame = Frame(notebook)
    server_config_frame = Frame(notebook)

    notebook.pack(fill="both", expand=True)

    client_config_frame.pack(fill="both", expand=True)
    server_config_frame.pack(fill="both", expand=True)

    ##### Widgets and Images #####

    main_logo = ImageTk.PhotoImage(Image.open("images//logo.png").resize((27, 27)))

    ### Client Configurations

    # Images
    client_config_logo_label = Label(client_config_frame, image=main_logo)

    # Labels
    client_config_title_label = Label(client_config_frame, text="Client configurations", font=("Helvetica", 15))
    client_config_name_label = Label(client_config_frame, text="Configuration Name", font=("Helvetica", 10))
    client_config_ip_address_label = Label(client_config_frame, text="LAN IP: ", font=("Helvetica", 10))
    client_config_port_label = Label(client_config_frame, text="Port: ", font=("Helvetica", 10))
    client_config_username_label = Label(client_config_frame, text="Username: ", font=("Helvetica", 10))
    client_config_password_label = Label(client_config_frame, text="Password: ", font=("Helvetica", 10))

    # Entries
    client_config_name_entry = Entry(client_config_frame, width=20, borderwidth=5)
    client_config_ip_address_entry = Entry(client_config_frame, width=20, borderwidth=5)
    client_config_port_entry = Entry(client_config_frame, width=20, borderwidth=5)
    client_config_username_entry = Entry(client_config_frame, width=20, borderwidth=5)
    client_config_password_entry = Entry(client_config_frame, width=20, borderwidth=5)

    # Buttons
    client_config_save_button = Button(client_config_frame, text="Save Configuration", command=lambda: save_configuration("client"), borderwidth=3)
    client_config_delete_button = Button(client_config_frame, text="Delete Configuration", command=lambda: delete_configuration("client"), borderwidth=3)
    client_config_edit_button = Button(client_config_frame, text="Edit Configuration", command=lambda: edit_configuration("client"), borderwidth=3)

    # Listboxes
    client_config_listbox = Listbox(client_config_frame, width=30, height=13, borderwidth=5, font=("Courier", 10))

    ### Server Configurations

    # Images
    server_config_logo_label = Label(server_config_frame, image=main_logo)

    # Labels
    server_config_title_label = Label(server_config_frame, text="Server configurations", font=("Helvetica", 15))
    server_config_name_label = Label(server_config_frame, text="Configuration Name", font=("Helvetica", 10))
    server_config_room_name_label = Label(server_config_frame, text="Room Name: ", font=("Helvetica", 10))
    server_config_port_label = Label(server_config_frame, text="Port: ", font=("Helvetica", 10))
    server_config_password_label = Label(server_config_frame, text="Password: ", font=("Helvetica", 10))

    # Entries
    server_config_name_entry = Entry(server_config_frame, width=20, borderwidth=5)
    server_config_room_name_entry = Entry(server_config_frame, width=20, borderwidth=5)
    server_config_port_entry = Entry(server_config_frame, width=20, borderwidth=5)
    server_config_password_entry = Entry(server_config_frame, width=20, borderwidth=5)

    # Buttons
    server_config_save_button = Button(server_config_frame, text="Save Configuration", command=lambda: save_configuration("server"), borderwidth=3)
    server_config_delete_button = Button(server_config_frame, text="Delete Configuration", command=lambda: delete_configuration("server"), borderwidth=3)
    server_config_edit_button = Button(server_config_frame, text="Edit Configuration", command=lambda: edit_configuration("server"), borderwidth=3)

    # Listboxes
    server_config_listbox = Listbox(server_config_frame, width=30, height=13, borderwidth=5, font=("Courier", 10))

    ##### Grids #####

    ### Client Configurations

    # Images
    client_config_logo_label.grid(row=12, column=1)

    # Labels
    client_config_title_label.grid(row=0, column=0, padx=20, columnspan=3, pady=3)
    client_config_name_label.grid(row=1, column=0, padx=20, pady=3)
    client_config_ip_address_label.grid(row=3, column=0, padx=20, pady=3)
    client_config_port_label.grid(row=5, column=0, padx=20, pady=3)
    client_config_username_label.grid(row=7, column=0, padx=20, pady=3)
    client_config_password_label.grid(row=9, column=0, padx=20, pady=3)

    # Entries
    client_config_name_entry.grid(row=2, column=0, padx=20)
    client_config_ip_address_entry.grid(row=4, column=0, padx=20)
    client_config_port_entry.grid(row=6, column=0, padx=20)
    client_config_username_entry.grid(row=8, column=0, padx=20)
    client_config_password_entry.grid(row=10, column=0, padx=20)

    # Buttons
    client_config_save_button.grid(row=11, column=0, padx=20, pady=10)
    client_config_edit_button.grid(row=1, column=1, padx=20, rowspan=3, pady=3)
    client_config_delete_button.grid(row=1, column=2, padx=20, rowspan=3,pady=3)

    # Listboxes
    client_config_listbox.grid(row=2, column=1, padx=20, rowspan=11, columnspan=2)

    ### Server Configurations

    # Images
    server_config_logo_label.grid(row=12, column=1)

    # Labels
    server_config_title_label.grid(row=0, column=0, columnspan=3, pady=5, padx=20)
    server_config_name_label.grid(row=1, column=0, pady=10, padx=20)
    server_config_room_name_label.grid(row=3, column=0, pady=5, padx=20)
    server_config_port_label.grid(row=5, column=0, pady=10, padx=20)
    server_config_password_label.grid(row=7, column=0, pady=10, padx=20)

    # Entries
    server_config_name_entry.grid(row=2, column=0, padx=20)
    server_config_room_name_entry.grid(row=4, column=0, padx=20)
    server_config_port_entry.grid(row=6, column=0, padx=20)
    server_config_password_entry.grid(row=8, column=0, padx=20)

    # Buttons
    server_config_save_button.grid(row=11, column=0, padx=20, pady=10)
    server_config_edit_button.grid(row=1, column=1, padx=20, rowspan=3, pady=3)
    server_config_delete_button.grid(row=1, column=2, padx=20, rowspan=3, pady=3)

    # Listboxes
    server_config_listbox.grid(row=2, column=1, padx=20,rowspan=11, columnspan=2)



    ### Frames
    notebook.add(client_config_frame, text="Client Configurations")
    notebook.add(server_config_frame, text="Server Configurations")

    ### Commands to be executed before mainloop
    activeWindows.edit_config_window_isactive = True
    config_window.protocol("WM_DELETE_WINDOW", close_window)
    display_configurations()

    ### Mainloop
    config_window.mainloop()







