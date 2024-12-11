from customtkinter import *
from PIL import Image, ImageTk
import client as cl
import socket
import threading
import clientUI

LENGTH_NUMBER_OF_FILE = 32
LENGTH_NAME = 32
ENCODING = 'utf-8'
LENGTH_SIZE = 32 #16 bytes để truyền kích thước file
LENGTH_MODE = 32  # 8 bytes để đọc mode 
LENGTH_MESS = 32 # 13 bytes tín hiệu phản hồi lại bên gửi
SIZE = 32
PORT_SERVER = 9999
HOST_SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS_SERVER = (HOST_SERVER, PORT_SERVER)
BUFFER = 1024
LENGTH_DIR =  5000 # GỬI DANH SÁCH TỆP
message_notenough = 'NOTENOUGH'
message_enough = 'ENOUGH'
message_success = 'SUCCESS'
message_failure = 'FAILURE'
message_error_notfound = 'ERRORNOTFOUND'
stop_signal = "NOTENOUGH"
message_setup_first_pass_word = 'SETUP_pass_word'
message_setup_first_pin = 'SETUP_PIN'
message_login = "LOGIN"
message_notlogin = "NOTLOGIN"

def enter_password_UI(client, passwrd, label):
    message = client.recv(LENGTH_MESS).decode().strip()
    print(message)
    if message == message_setup_first_pass_word:
        label.configure(text='This is your first login, Let setup your password')
        initpassword = passwrd
        client.send(initpassword.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo mật khẩu có đủ độ dài
        message = client.recv(LENGTH_MESS).decode().strip()
    if message == message_success:
        label.configure(text='Enter your password')
        password = passwrd
        client.send(password.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo mật khẩu có đủ độ dài
    else:
        print('message', message)

def process_login_client_UI(client, passwrd,label):
    # Gọi hàm nhập mật khẩu
    enter_password_UI(client, passwrd, label)

    # Nhận phản hồi từ server
    message = client.recv(LENGTH_MESS).decode().strip()
    if message == message_failure:
        label.configure(text='Wrong password, again')
    else:
        main.destroy()
        clientUI_Window = clientUI.clientUI(client)
        clientUI_Window.mainloop()
        
def init_UI():
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        client.connect(ADDRESS_SERVER)
        client.send(message_login.ljust(LENGTH_MESS).encode(ENCODING))
        # process_login_client_UI(client)
        return client
    except socket.gaierror:
        print("The address server is invalid !")
        return None
    except ConnectionRefusedError:
        print("The server is off !")
        return None

def login_frame(client):
    global main
    main = CTk()
    main.title('Login')
    main.config(bg='white')
    main.configure(fg_color='#E4BD63')
    main.resizable(False, False)
    main.geometry('500x250')
    
    label = CTkLabel(master=main, text='Enter your password', font=('Arial', 23, 'bold'), text_color='brown')
    label.place(x=130, y=20)
    
    entry_password = CTkEntry(main, show='*', width=250, height=30)
    entry_password.place(x=125, y=100)
    
    btn_login = CTkButton(main, text='Login', font=("", 15, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=lambda: process_login_client_UI(client, entry_password.get(), label))
    btn_login.place(x=205, y=180)
    
    return main

if __name__ == '__main__':
    client = init_UI()
    main = login_frame(client)
    main.mainloop()
    
    

