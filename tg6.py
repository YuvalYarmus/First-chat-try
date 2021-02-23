from css import img_style
from os import mkdir, name
from socket import timeout
import sys
import time
import datetime

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot

from functools import partial
from client2 import My_Client
import concurrent.futures
from threading import Thread
import urllib.request
import os

threads = []

class Chat_ui(QtWidgets.QWidget):
    signal_send = QtCore.pyqtSignal(str)
    switch_window = QtCore.pyqtSignal()
    curr_img = ""
    def __init__(self, name: str = "", phone : str = ""):
        print("in init")
        self.name = name
        QtWidgets.QWidget.__init__(self)
        self.window = QtWidgets.QMainWindow()
        self.window.setObjectName("Window")
        self.window.setWindowTitle("Chat")
        self.window.resize(700,300)
        
        self.main_widget = QtWidgets.QWidget(self.window)
        self.main_widget.setObjectName("main_widget")
        # main vertical layout:
        self.top_layer = QtWidgets.QVBoxLayout(self.main_widget)
        self.top_layer.setObjectName("top_layer")
        # scroll area where messages are shown:
        self.scroll = QtWidgets.QScrollArea(self.main_widget)
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("scroll")
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.scroll_content.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum))
        self.scroll.setWidget(self.scroll_content)
        self.top_layer.addWidget(self.scroll)
        # vertical layout for the msg area:
        self.msgVLayout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.chat_Greet = QtWidgets.QTextEdit()
        font = QtGui.QFont()
        font.setFamily("MS Serif")
        font.setPointSize(14)
        self.chat_Greet.setCurrentFont(font)
        self.chat_Greet.append("Welcome to the server {}!".format(name).title())
        self.chat_Greet.setFocusPolicy(QtCore.Qt.NoFocus)
        self.chat_Greet.setMaximumHeight(int(self.window.size().height() / 12))
        self.chat_Greet.setReadOnly(True)
        self.msgVLayout.addWidget(self.chat_Greet)
        # horizontal layout for input widgets:
        self.inputHLayout = QtWidgets.QHBoxLayout()
        self.inputHLayout.setObjectName("inputHLayout")
        # text msg input:
        
        # self.msgInput = QtWidgets.QTextEdit(self.centralwidget)
        self.msgInput = QtWidgets.QLineEdit(self.main_widget)
        self.msgInput.setObjectName("msgInput")
        self.msgInput.setMaximumHeight(int(self.window.size().height() / 2))
        self.msgInput.returnPressed.connect(self.write_msg)
        self.inputHLayout.addWidget(self.msgInput)
        # send-message button:
        self.sendButton = QtWidgets.QPushButton(self.main_widget)
        self.sendButton.setObjectName("sendButton")
        self.sendButton.setText("Send")
        self.sendButton.clicked.connect(self.write_msg)
        self.sendButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.inputHLayout.addWidget(self.sendButton, 0, QtCore.Qt.AlignBottom)
        
        self.top_layer.addLayout(self.inputHLayout)
        self.window.setCentralWidget(self.main_widget)
        self.main_widget.show()
        self.window.resizeEvent = self.resize_event

        self.style()
        QtCore.QMetaObject.connectSlotsByName(self.window)
        self.window.show()
        
    def write_msg(self): 
        now = datetime.datetime.now().time()
        print("in write msg")
        temp_QTextedit = QtWidgets.QTextEdit(f"[{now}] " + self.msgInput.text())
        # temp_QTextedit.setTextBackgroundColor(QtGui.QColor(0, 255, 0)) 
        from css import write_Qtext 
        temp_QTextedit.setStyleSheet(write_Qtext())
        temp_QTextedit.setReadOnly(True) 
        temp_QTextedit.setMinimumHeight(int(self.window.size().height() / 6))
        temp_QTextedit.setMaximumHeight(int(self.window.size().height() / 4))
        self.msgVLayout.addWidget(temp_QTextedit, 0, QtCore.Qt.AlignRight)
        self.signal_send.emit(self.msgInput.text())
        self.msgInput.clear()
        self.msgInput.setReadOnly(False)

    def add_msg(self, msg : str = ""): 
        if "/help" in msg: 
            print("in add msg /help")
            temp_QTextedit = QtWidgets.QTextEdit(msg)
            from css import help_style
            temp_QTextedit.setHtml(help_style())
            from css import write_Qtext 
            # temp_QTextedit.setStyleSheet("QtWidgets.QTextEdit{border-radius: 15px 50px 30px 5px; }")
            temp_QTextedit.setStyleSheet(write_Qtext())
            temp_QTextedit.setReadOnly(True)
            temp_QTextedit.setMinimumHeight(int(self.window.size().height() / 3))
            temp_QTextedit.setMaximumHeight(int(self.window.size().height()))
            self.msgVLayout.addWidget(temp_QTextedit, 0, QtCore.Qt.AlignLeft)
        # elif msg.startswith("/img"):
        #     # msg should be the link itself here (only with "/img before"), cleaning the str should be before the function
        #     print("in add msg /img")
        #     msg = msg.replace("/msg", "")
        #     temp_QTextedit = QtWidgets.QTextEdit()
        #     from css import img_style
        #     # temp_QTextedit.setHtml(img_style(msg.split(":")[1]).replace(" ", ""))
        #     temp_QTextedit.setStyleSheet(img_style(msg))
        #     temp_QTextedit.setReadOnly(True)
        #     self.msgVLayout.addWidget(temp_QTextedit, 0, QtCore.Qt.AlignCenter)
        elif msg.startswith("/img") or msg.startswith("//serverimg") or ( "[" in msg and "]" in msg and "sends:" in msg and ("//serverimg" in msg or "/img" in msg) ) :
            if msg.startswith("//serverimg"): 
                msg_list = msg.split("---")
                msg_to_be = msg_list[1][1:]
                print(f"\nmsg to be is: {msg_to_be} \n")
            elif msg.startswith("["): 
                sender = msg.split("/img")[0]
                msg = msg.replace(sender, "")
                temp_QTextedit = QtWidgets.QTextEdit(sender)
                temp_QTextedit.setStyleSheet("QtWidgets.QTextEdit{border-radius: 15px 50px 30px 5px; height: 10px;  }")
                self.msgVLayout.addWidget(temp_QTextedit, 0, QtCore.Qt.AlignLeft)
            print("in add msg /img")
            msg = msg.replace("/img", "")
            msg = msg.replace("//serverimg", "")
            print(f"/img url link: {msg}")
            try: 
                self.dl_jpg_url(msg)
                temp = QtWidgets.QLabel()
                pixmap = QtGui.QPixmap(self.curr_img)
                temp.setPixmap(pixmap)
                self.resize(pixmap.width(), pixmap.height())
                self.msgVLayout.addWidget(temp, 0, QtCore.Qt.AlignLeft)
            except: 
                e = sys.exc_info()
                print("exception in uploading img: ", str(e)) 
        else: 
            print("in add msg with: ", msg)
            temp_QTextedit = QtWidgets.QTextEdit(msg)
            temp_QTextedit.setStyleSheet("QtWidgets.QTextEdit{border-radius: 15px 50px 30px 5px; height: 10px;  }")
            # temp_QTextedit.setTextBackgroundColor(QtGui.QColor.fromRgb(0, 255, 0)) 
            # temp_QTextedit.setTextBackgroundColor(QtGui.QColor(0, 255, 0)) 
            temp_QTextedit.setReadOnly(True)
            if msg == "Welcome to the server, pls send us your name": 
                temp_QTextedit.setMaximumHeight(int(self.window.size().height() / 8))    
            self.msgVLayout.addWidget(temp_QTextedit, 0, QtCore.Qt.AlignLeft)
        
    def dl_jpg_url(self, url: str): 
        try: 
            if not os.path.exists("images"):
                os.mkdir("images")
            PATH = "images/img"
            i = 0
            while True: 
                if not os.path.exists("images/img{}.jpg".format(i)): 
                    urllib.request.urlretrieve(url, "images/img{}.jpg".format(i))
                    self.curr_img = "images/img{}.jpg".format(i)
                    break
                i += 1
        except: 
            e = sys.exc_info()
            print("exception in urlretrieve", str(e)) 
                
    def style(self):
        from css import scrollbar_style
        scrollbar_style = scrollbar_style()
        self.main_widget.setStyleSheet(scrollbar_style)
    
    def resize_event(self, event):
        self.msgInput.setMaximumHeight(int(event.size().height() / 2))
        # self.msgInput.adjustHeight()


class Login(QtWidgets.QWidget):
    switch_sign_up = QtCore.pyqtSignal()
    switch_window_main = QtCore.pyqtSignal(str, str)
    start_socket = QtCore.pyqtSignal(str, str, str)
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.start_socket = self.start_socket
        self.window = QtWidgets.QMainWindow()
        self.window.setObjectName("Window")
        self.window.setWindowTitle("Login")
        # self.window.resize(400,200)

        self.main_widget = QtWidgets.QWidget(self.window)
        self.main_widget.setObjectName("main_widget")

        self.top_layer = QtWidgets.QVBoxLayout(self.main_widget)
        self.top_layer.setObjectName("top_layer")
        
        self.Ylayout = QtWidgets.QVBoxLayout()
        self.top_layer.addLayout(self.Ylayout)
        self.Xlayout = QtWidgets.QHBoxLayout()
        self.Xlayout2 = QtWidgets.QHBoxLayout()

        self.label = QtWidgets.QLabel("Enter your name: ")
        font = QtGui.QFont()
        font.setFamily("MS Serif")
        font.setPointSize(16)
        self.label.setFont(font)
        self.Xlayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit()
        # self.lineEdit.returnPressed.connect(self.start_socket_connection)
        self.lineEdit.returnPressed.connect(self.switch_and_start)
        self.Xlayout.addWidget(self.lineEdit)
        self.Ylayout.addLayout(self.Xlayout)
        

        self.label2 = QtWidgets.QLabel("Enter your phone number: ")
        font = QtGui.QFont()
        font.setFamily("MS Serif")
        font.setPointSize(16)
        self.label2.setFont(font)
        self.Xlayout2.addWidget(self.label2)
        self.lineEdit2 = QtWidgets.QLineEdit()
        self.lineEdit2.returnPressed.connect(self.switch_and_start)
        self.Xlayout2.addWidget(self.lineEdit2)
        self.Ylayout.addLayout(self.Xlayout2)

        self.pushButton = QtWidgets.QPushButton("Confirm name")
        # self.pushButton.clicked.connect(self.start_socket_connection)
        self.pushButton.clicked.connect(self.switch_and_start)
        self.Ylayout.addWidget(self.pushButton)


        self.pushButton2 = QtWidgets.QPushButton("Sign Up")
        # self.pushButton.clicked.connect(self.start_socket_connection)
        self.pushButton2.clicked.connect(self.switch_to_sign_up)
        self.Ylayout.addWidget(self.pushButton2)


        self.window.setCentralWidget(self.main_widget)
        self.main_widget.show()
        QtCore.QMetaObject.connectSlotsByName(self.window)
        # self.setLayout(self.Ylayout)
    
    def switch_to_sign_up(self):
        self.switch_sign_up.emit()
    
    def switch_main(self): 
        self.switch_window_main.emit(self.lineEdit.text(), self.lineEdit2.text())

    def switch_and_start(self): 
        # self.switch_window_main.emit(self.lineEdit.text(), self.lineEdit2.text())
        self.start_socket.emit(self.lineEdit.text(), self.lineEdit2.text(), "/login")
        self.close()

class Sign_up(QtWidgets.QWidget): 
    switch_Log_in = QtCore.pyqtSignal()
    switch_window_main = QtCore.pyqtSignal(str, str)
    start_socket = QtCore.pyqtSignal(str, str, str)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.window = QtWidgets.QMainWindow()
        self.window.setObjectName("Window")
        self.window.setWindowTitle("SignUp")

        self.main_widget = QtWidgets.QWidget(self.window)
        self.main_widget.setObjectName("main_widget")

        self.top_layer = QtWidgets.QVBoxLayout(self.main_widget)
        self.top_layer.setObjectName("top_layer")

        self.Ylayout = QtWidgets.QVBoxLayout()
        self.top_layer.addLayout(self.Ylayout)
        self.Xlayout = QtWidgets.QHBoxLayout() 
        self.Xlayout2 = QtWidgets.QHBoxLayout()

        self.label = QtWidgets.QLabel("Enter your name: ")
        font = QtGui.QFont()
        font.setFamily("MS Serif")
        font.setPointSize(16)
        self.label.setFont(font)
        self.Xlayout.addWidget(self.label)

        self.lineEdit = QtWidgets.QLineEdit()
        self.Xlayout.addWidget(self.lineEdit)

        self.label2 = QtWidgets.QLabel("Enter your phone number: ")
        font = QtGui.QFont()
        font.setFamily("MS Serif")
        font.setPointSize(16)
        self.label2.setFont(font)
        self.Xlayout2.addWidget(self.label2)

        self.lineEdit2 = QtWidgets.QLineEdit()
        self.lineEdit2.returnPressed.connect(self.switch_and_start)
        self.Xlayout2.addWidget(self.lineEdit2)

        self.Ylayout.addLayout(self.Xlayout)
        self.Ylayout.addLayout(self.Xlayout2)

        self.pushButton = QtWidgets.QPushButton("Confirm")
        self.pushButton.clicked.connect(self.switch_and_start)
        self.Ylayout.addWidget(self.pushButton)

        self.pushButton2 = QtWidgets.QPushButton("Log in")
        # self.pushButton.clicked.connect(self.start_socket_connection)
        self.pushButton2.clicked.connect(self.switch_Log_in)
        self.Ylayout.addWidget(self.pushButton2)

        # self.setLayout(self.Ylayout)
        self.window.setCentralWidget(self.main_widget)
        self.main_widget.show()
        QtCore.QMetaObject.connectSlotsByName(self.window)

    def switch_to_login(self):
        self.switch_Log_in.emit()

    def switch_and_start(self): 
        self.start_socket.emit(self.lineEdit.text(), self.lineEdit2.text(), "/signup")
        # self.switch_window_main.emit(self.lineEdit.text(), self.lineEdit2.text())        
        # self.close()

class Pop_Up1(QtWidgets.QWidget):
    signal_send = QtCore.pyqtSignal()
    signal_end = QtCore.pyqtSignal()

    def __init__(self, name : str, boolean : bool, mode : str = "", phone : str = ""):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Prompt')

        layout = QtWidgets.QGridLayout()
        if boolean: 
            self.label = QtWidgets.QLabel("hello {} pls send if you want to send a message, if not just the close the window".format(name))
            layout.addWidget(self.label)
        else: 
            if mode == "/signup": 
                self.label = QtWidgets.QLabel("we are sorry, {} the name is alerady taken. \nPlease choose another".format(name))
            elif mode == "/login": 
                self.label = QtWidgets.QLabel(f"we are sorry, {name},We cant find a phone number matching that name, or the opposite")
            else: self.label = QtWidgets.QLabel("we are sorry, {name}, we have some unresolved error, please try again")
            layout.addWidget(self.label)
        
        if boolean and mode != "restart": 
            self.button = QtWidgets.QPushButton('Send and Close')
            self.button.clicked.connect(self.doube_emit)
            layout.addWidget(self.button)

        self.button2 = QtWidgets.QPushButton('Close')
        self.button2.clicked.connect(self.signal_end.emit)
        layout.addWidget(self.button2)

        self.setLayout(layout)
    def doube_emit(self) -> None: 
        self.signal_send.emit()
        self.signal_end.emit()

class MyThread(QtCore.QThread): 
    def __init__(self, func = None, parent = None) -> None:
        super(MyThread, self).__init__(parent)
        self.func = func
    def run(self) -> None: 
        self.func()

class Controller(QtWidgets.QWidget):

    signal_add_msg = QtCore.pyqtSignal(str)
    move_main = QtCore.pyqtSignal(str, str)
    new_popup = QtCore.pyqtSignal(bool, str, str, str)
    restart = QtCore.pyqtSignal()
    login_close = QtCore.pyqtSignal()
    signup_close = QtCore.pyqtSignal()
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.client = My_Client()
        self.show_login()
        self.img = ""
        self.taking_img = False
        self.move_main.connect(self.show_main)
        self.new_popup.connect(self.show_PopUp1)
        # self.restart.connect(self.__init__)
        self.restart.connect(self.show_login)
        self.login_close.connect(self.close_login)
        self.signup_close.connect(self.close_signup)

    def close_login(self): 
        self.login.window.close()
    def close_signup(self): 
        try:
            print("trying to close signup ") 
            self.sign_up.window.close()
        except: 
            e = sys.exc_info()
            print("exception close_signup", str(e))
    def restart_F(self): 
        self.new_popup.emit(False, "restart", "", "")
        self.client.close()
        self.restart.emit()

    def restart2(self): 
        self.restart.emit()
        self.new_popup.emit(False, "restart", "", "")

    def show_login(self):
        self.login = Login()
        try: 
            self.login.start_socket.connect(self.start_socket1)
            self.login.switch_window_main.connect(self.show_main)
            self.login.switch_sign_up.connect(lambda : [self.show_sign_up(), self.login.window.close()])
            print("trying to show")
            self.login.window.show()
            print("should show login")
        except: 
            e = sys.exc_info()
            print("exception in login", str(e))
        
        
    def show_sign_up(self): 
        self.sign_up = Sign_up()
        self.sign_up.switch_Log_in.connect(lambda : [self.show_login(), self.sign_up.window.close()])
        # self.sign_up.switch_window_main.connect(lambda : [self.show_main(), self.sign_up.close()])
        self.sign_up.switch_window_main.connect(self.sign_up.window.close)
        self.sign_up.start_socket.connect(self.start_socket1)

        self.sign_up.window.show()

    def show_main(self, name : str = "", phone : str = ""):
        if name == "" or phone == "": 
            print("show main: one of the params (or more) did not arrive")
        print("in show_main")
        try: 
            self.main = Chat_ui(name, phone)
            print("managed to make main")           
            self.signal_add_msg.connect(self.main.add_msg)
            self.main.signal_send.connect(self.send_Socket)
            self.main.window.show()
            print("should show main")
        except: 
            e = sys.exc_info()
            print("exception in show_main", str(e))

    def show_PopUp1(self, boolean: bool, mode : str = "", name : str = "", phone : str = "") -> None: 
        self.pop_up = Pop_Up1(name, boolean, mode, phone)
        self.pop_up.signal_send.connect(lambda: self.send_Socket(name, phone, mode))
        close = lambda  : self.pop_up.close()
        self.pop_up.signal_end.connect(close)
        self.pop_up.show()

    def start_socket1(self, name : str = "", phone : str = "", mode :str = "") -> None: 
        if name == "" or phone == "" or mode == "": 
            print("start_socket: one of the params (or more) did not arrive")
        # self.read_from_socket = Thread(target=self.socket_Read, args=())
        # self.read_from_socket.start()
        global threads
        for thread in threads: 
            try: 
                thread.terminate()
            except: 
                e = sys.exc_info()
                print("exception thread termintaion", str(e))
        threads = []
        self.read_thread = MyThread(self.socket_Read)
        threads.append(self.read_thread)
        self.read_thread.start()
        print("start_socket: started threading to read socket")
        self.show_PopUp1(True, mode, name, phone)

     
    def socket_Read(self):
        try: 
            self.data = ""
            self.data = self.client.current_socket.recv(1024).decode()            
            if self.data != "" and len(self.data) >= 1: 
                print("read successfully: ", self.data)
                # if not self.taking_img:
                if self.taking_img != None and self.taking_img == False: 
                    if self.data.startswith("/img") or "//serverimg" in self.data: 
                        print("starting to read img")
                        if self.data[::-1].startswith("//ServerEnd") or "//ServerEnd" in self.data or self.data[::-1].startswith("dnErevreS//"): 
                            self.data = self.data.replace("//ServerEnd", "")
                            data101 = self.data.split("---")[0].split("//")[0] + "/img" + self.data.split("---")[1][1:]
                            print(f"data 101: {data101}")
                            # self.data = self.data.split("---")[1][1:]                            
                            # self.data = "/img" + self.data
                            # self.img=self.data
                            print("emiting img: ", data101)
                            self.signal_add_msg.emit(data101)
                            self.img = ""
                        else: 
                            self.img+= self.img
                            self.taking_img = True
                    elif self.data.startswith("/login ok, name was verified for:"): 
                        param_list = self.data.split(":")
                        print(f"1trying to pass to main: {param_list[1]}, {param_list[2]}")
                        try: 
                            self.move_main.emit(param_list[1], param_list[2]) 
                            print("emitted to open main")
                            self.login_close.emit() 
                            print("closed login window")
                        except: 
                            e = sys.exc_info()
                            print("exception in .login verified", str(e))
                    elif self.data.startswith("/signup ok, verified for:"):
                        param_list = self.data.split(":")
                        print(f"2trying to pass to main: {param_list[1]}, {param_list[2]}")
                        try: 
                            self.move_main.emit(param_list[1], param_list[2])
                            self.signup_close.emit()
                            print("closed /signup window")  
                        except: 
                            e = sys.exc_info()
                            print("exception in /signup verified", str(e))
                    elif self.data.startswith("That name already exists, pls send us another name"): 
                        # self.show_PopUp1(False, "", name)
                        # self.show_login()
                        try: 
                            self.login = None
                            self.restart.emit()
                            self.new_popup.emit(False, "restart", "", "")
                            print("tried to reopen all")
                        except: 
                            e = sys.exc_info()
                            print("exception in restart", str(e))
                    elif self.data.startswith("We cant find a phone number matching that name, or the opposite\nplease try again"): 
                        print("trying to restart")
                        try: 
                            self.login = None
                            self.restart.emit()
                            self.new_popup.emit(False, "restart", "", "")
                            print("tried to reopen all")
                        except: 
                            e = sys.exc_info()
                            print("exception in restart", str(e))
                    else:
                        self.signal_add_msg.emit(self.data)
                        print("signaled to to add msg")
                else: 
                    # if self.data[::-1].startswith("//ServerEnd"): 
                    if self.data[::-1].startswith("//ServerEnd") or "//ServerEnd" in self.data or self.data[::-1].startswith("dnErevreS//"):
                        print(f"got img when taking img was true. got: {self.data}")
                        self.img+=self.data.replace("//ServerEnd", "")
                        self.signal_add_msg.emit(self.img)
                        self.img = ""
                        self.taking_img = False
                    else: 
                        self.taking_img = True
                        self.img+= self.img

            time.sleep(0.2)
            self.socket_Read()
        except timeout as e: 
            # print("Got timed out?: {}".format(e))
            self.socket_Read()
            time.sleep(0.2)
        except RecursionError as e: 
            print("Got RecursionError: {}".format(e))
        except: 
            e = sys.exc_info()
            print("exception", str(e)) 


    def send_Socket(self, param : str, phone : str = "", mode : str = ""): 
        try: 
            # if mode and phone != "": 
            if mode and phone != "": 
                print(f"in mode send: {mode}-{param}-{phone}")
                self.client.current_socket.send(f"{mode}-{param}-{phone}".encode())
            else: 
                if param.startswith("/img"): 
                    param += "//ServerEnd"
                    param = param.replace("/img", "//serverimg{}---".format( len(param) + len("//serverimg---") + len(str(len(param) + len("//serverimg---")))   )  )
                    self.client.current_socket.send(param.encode()) 
                    print("sending image:  {}".format(param))
                else: 
                    print("in send, param is {}".format(param))
                    self.client.current_socket.send(str(param).encode()) 
        except: 
            e = sys.exc_info()
            print("exception in send_Socket: ", str(e))



def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()