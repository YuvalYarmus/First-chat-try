import sqlite3
from threading import Thread
import socket
import sys
import select
import concurrent.futures
from ClientClass import Client
import time
import datetime

server = socket.socket()
server.bind(('0.0.0.0', 23))
server.listen(5)

threads = []
conns = []
all_clients = [] ### only names and phones with admin status as tuples
all__admins= [] ### a list of all the admins that exists as a tuple of names, phones and admin status
online_clients = [] ### clients from type clients
groups = []
img = ""
getting_img = False

# def get_img(client: Client): 
#     print("in get img function")
#     global img
#     while img[::-1].startswith("//ServerEnd"):
#         data = client.get_conn.recv(1024).decode()
#         img += data


def read_socket(client : Client = None, current_socket : socket = None, address: str = ""): 
    global all_clients, online_clients, all__admins, getting_img, img
    conn  = sqlite3.connect("chatDB1.db")
    cursor = conn.cursor()
    now = datetime.datetime.now().time()
    # now = lambda: datetime.datetime.now().time()
    print("now is: ", now, " getting_img is: ", getting_img)
    if current_socket == None:
        current_socket =  client.get_conn()
    boolean = True
    while boolean: 
        if client and client.get_conn() is server:
            print("\nis server, name: ", str(current_socket.getsockname()))
            print("clients are: ", str(all_clients))
            print("online clients are: ",  str(online_clients))
            (new_socket, address) = server.accept()
            conns.append(new_socket)
            new_socket.send("Welcome to the server, pls send us your name".encode())
            name = new_socket.recv(1024).decode()
            if len(all_clients) < 1: 
                all_clients.append((name, "" ,1))
            else:
                all_clients.append((name, "" ,0))
            c = Client(name, new_socket, address)
            online_clients.append(c)
        elif getting_img:
            print("in getting img elif")
            data = current_socket.recv(1024).decode()
            img += data
            # if data[::-1].startswith("//ServerEnd"):
            if data[::-1].startswith("dnErevreS//"): 
                getting_img = False
                for client2 in online_clients: 
                        if client2.get_conn() is not current_socket: 
                            client2.get_conn().send(img.encode())
                img = ""
                print("done with get image for now")
        else: 
            # print(f"pre data read - client:{client} - current_socket:{current_socket}\n")
            if current_socket == None: data = client.get_conn().recv(1024).decode()                
            else: data = current_socket.recv(1024).decode()   
            if client == None: 
                    for online_client in online_clients: 
                        if online_client.get_conn() == current_socket or online_client.get_conn is current_socket: 
                            client = online_client         
            if data == "": 
                time.sleep(2)
                print("no answer from the client - ")
                for Oclient in online_clients: 
                    if Oclient.get_conn() is current_socket: 
                        Oclient.get_conn.send("You were kicked! ".encode())
                        online_clients.remove(Oclient)
                print("connection closed")
            elif data.startswith("/signup"): 
                param_list = data.split("-")
                exist = False
                for tup in all_clients: 
                    if tup[0] == param_list[1]: 
                        exist = True
                if exist: current_socket.send("That name already exists, pls send us another name".encode())
                if not exist: 
                    c = Client(param_list[1], current_socket, address, param_list[2])
                    client_tup = None
                    if len(all_clients) < 1: client_tup = (param_list[1], param_list[2], 1)
                    else: client_tup = (param_list[1], param_list[2], 0)
                    all_clients.append(client_tup)
                    all__admins.append(client_tup)
                    online_clients.append(c)
                    with conn:
                        cursor.execute("INSERT INTO chatDB VALUES (?, ?, ?)", client_tup)
                    # c.get_conn().send("ok, name was verified for: {}".format(param_list[1]).encode())
                    print(f"/signup trying to send: ok, verified for: {param_list[1]} : {param_list[2]}")
                    c.get_conn().send(f"/signup ok, verified for: {param_list[1]} : {param_list[2]}".encode())
                    print("/signup: name was verified for: {}\n".format(param_list[1]))
            elif data.startswith("/login"): 
                print("entering /login")
                param_list = data.split("-")
                print("/login param_list: ", param_list)
                exist = False
                for tup in all_clients: 
                    if tup[0] == param_list[1]: 
                        exist = True
                if exist: 
                    c = Client(param_list[1], current_socket, address, param_list[2])
                    client_tup = None
                    online_clients.append(c)
                    print(f"/login trying to send: ok, verified for: {param_list[1]} : {param_list[2]}")
                    c.get_conn().send(f"/login ok, name was verified for: {param_list[1]} : {param_list[2]}".encode())
                    print("/login: name was verified for: {}\n".format(param_list[1]))
                else: 
                    print("first exist was false")
                    string = "We cant find a phone number matching that name, or the opposite\nplease try again"
                    current_socket.send(string.encode())
                    print("/login: We cant find a phone number matching that name, or the opposite\nplease try again\n")
                    # continue
            elif data.startswith("/img") or data.startswith("//serverimg"): 
                print("in /img")
                img = ""
                img = data
                # print(f"got: {img}")
                print(f"client is: {client}")
                if data[::-1].startswith("dnErevreS//") or "//ServerEnd" in data:
                    getting_img = False
                    for client2 in online_clients: 
                            if client2.get_conn() is not current_socket: 
                                if client: 
                                    client2.get_conn().send(f"[{now}] {client.get_name()} sends: ".encode())
                                client2.get_conn().send(img.encode())
                    print("done with get image for now")
                else:                     
                    getting_img = True
                    print("starting getting img process, getting img is: ", getting_img)
                # img_thread = Thread(target=get_img, args=(client))
                # img_thread.start()             
            elif data == "/help": 
                commands_string = """ 
                /help - to get the full list of commands the server supports \n
                /private-[name]: [msg] - to send a private msg to one of the other clients who exists in the server \n
                /all_members - get the names of all the members in the server \n
                /online_members - get the names of all the members who are online \n
                /all_admins - get a list of all the admins in the server \n
                /img:[link] - send an img
                """
                if client: client.get_conn().send(commands_string.encode())
                else: current_socket.send(commands_string.encode())
            elif data.startswith("/private"): 
                x = data.find("-") # position where the name starts
                y = data.find(":") # position where the msg starts
                if x == -1 or y == -1: 
                    client.get_conn().send("Error in receiving the msg, pls try again".encode())
                else: 
                    name = data[x + 1: y]
                    msg = data[y + 1: ]
                    found = False
                    for client2 in online_clients:
                        if client2.get_name() == name: 
                            found = True
                            client2.get_conn().send("[{}] {} whispers: {}".format(now, client.get_name(), msg).encode())
                            # client2.get_conn().send("[{}] {} whispers: {}".format(now.strftime("%Y-%m-%d %H:%M:%S"), client.get_name(), msg).encode())
                    if found == False: 
                        client2.get_conn().send("[{}] User: {} not found".format(now, name).encode())
            elif data.startswith("/all_members"):
                clients = ""
                for tup in all_clients: 
                    print("tup: ", tup[0])
                    clients += tup[0] + ", "
                clients = clients[0 : len(clients) - 2]
                client.get_conn().send("[{}] all the members are: {} ".format(now, clients).encode())
                print("/all_members - all_clients is: {}, clients is: {}".format(all_clients, clients))
            elif data.startswith("/online_members"):
                clients = ""
                for client in online_clients: 
                    clients += client.get_name() + ", "
                clients = clients[0 : len(clients) - 2]
                client.get_conn().send("[{}] all the online members are: {} ".format(now, clients).encode())
            elif data.startswith("/all_admins"):
                clients = ""
                for tup in all__admins: 
                    clients += tup[0] + ", "
                clients = clients[0 : len(clients) - 2]
                client.get_conn().send("[{}] all the admins are: {} ".format(now, clients).encode())
            else: 
                if client == None: 
                    for online_client in online_clients: 
                        if online_client.get_conn() == current_socket or online_client.get_conn is current_socket: 
                            client = online_client
                print(f"last else - client:{client} - current_socket:{current_socket}\n")
                print(f"online clients is: {online_clients}\n")
                print(f"last else - {client.get_name()} sends: {data}\n")
                for client2 in online_clients: 
                    if client2.get_conn() is not current_socket: 
                        client2.get_conn().send(f"[{now}] {client.get_name()} sends: {data}".encode())


def main():
    global all_clients, online_clients, all__admins, threads
    try:
        conn  = sqlite3.connect("chatDB1.db")
        cursor = conn.cursor()
        with conn:
            cursor.execute("CREATE TABLE IF NOT EXISTS chatDB (name TEXT PRIMARY KEY, phone TEXT, admin INTEGER)")
        with conn:
            cursor.execute("SELECT * FROM chatDB WHERE name != ''")
            all_clients =  cursor.fetchall()
            for db_tuple in all_clients: 
                print("db_tuple: ", db_tuple)
                if db_tuple[2] == 1: 
                    all__admins.append(db_tuple)
        print("after initializing - all_admins: {}, all_clients: {}".format(all__admins, all_clients))
        while True:
            with concurrent.futures.ThreadPoolExecutor(10) as executor:
                new_socket, address = executor.submit(server.accept).result()
                if new_socket not in conns:
                    conns.append(new_socket)
                    new_socket.send("Welcome to the server, pls send us your name".encode())
                    thread = Thread(target=read_socket, args=(None, new_socket, address))
                    threads.append(thread)
                    thread.start()

                    threads = []
                    for client in online_clients: 
                        thread = Thread(target=read_socket, args=(client,))
                        threads.append(thread)
                        thread.start()


    except RecursionError as e:
        print("last main block RecursionError: ", e)
    except: 
        e = sys.exc_info()
        print("exception", str(e)) 


if __name__ == "__main__": 
    main()
