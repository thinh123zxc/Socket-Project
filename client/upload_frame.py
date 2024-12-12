from customtkinter import *
import time
import threading
import client as cl
import socket
import time
import os
import tkinter as tk
from tkinter import messagebox
import queue

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

check = [False]
choosen_obj = ['']
mode_upload = ['']

def upload_frame(parent, client):
    frame = CTkFrame(parent, fg_color='#E4BD63', height=500, width=751)
    
    #Label choosen file
    lb_choosen_obj = CTkLabel(master=frame, text='Choose file to upload', font=('Arial', 15, 'bold'), text_color='brown')
    lb_choosen_obj.place(x=300, y=50)
     
    def file_dialog():
        file_path = filedialog.askopenfilename(title="Select your file", filetypes=[("All Files", "*.*"),])
        choosen_obj[0] = file_path
        print(f"file selected: {choosen_obj[0]}")
        lb_choosen_obj.configure(text=choosen_obj[0])
        mode_upload[0] = 'upload'
        
    def folder_dialog():
        folder_path = filedialog.askdirectory(title='Select your folder')
        choosen_obj[0] = folder_path
        print(f"folder selected: {choosen_obj[0]}")
        lb_choosen_obj.configure(text=choosen_obj[0])
        mode_upload[0] = 'upload multithread'
        
    def enter_pin_window():
        pin_window = CTkToplevel(frame, fg_color='#E4BD63')
        pin_window.geometry('500x250')
        pin_window.transient(frame)
        pin_window.grab_set()
        
        label = CTkLabel(pin_window, text='Enter your pin', font=('Arial', 23, 'bold'), text_color='brown')
        entry = CTkEntry(pin_window, show='*', width=250, height=30)
        btn_enter_pin = CTkButton(pin_window, text='OK', font=("", 20, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=lambda: process_login_updownload_UI(client, entry.get(), label))
        
        label.place(x=135, y=20)
        entry.place(x=125, y=100)
        btn_enter_pin.place(x=205, y=180)
        
        def enter_pin_UI(client, PIN, label):
            message = client.recv(LENGTH_MESS).decode().strip()
            if message == message_setup_first_pin:
                label.configure(text='Let setup your pin')
                initpin = PIN
                client.send(initpin.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo pin có đủ độ dài
                message = client.recv(LENGTH_MESS).decode().strip()
            if message == message_success:
                label.configure(text='Enter your pin')
                pin = PIN
                client.send(pin.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo pin có đủ độ dài
            else: 
                print(message)

        def process_login_updownload_UI(client, PIN, label): #xử lí đăng nhập
            # Gọi hàm nhập mật khẩu
            enter_pin_UI(client, PIN, label)

            # Nhận phản hồi từ server
            message = client.recv(LENGTH_MESS).decode().strip()
            print('message', message)

            if message == message_failure:
                label.configure(text='Wrong pin, again')
            else:
                pin_window.destroy()
                if os.path.isfile(choosen_obj[0]):
                    progress_queue = queue.Queue()
                    def update_progress_bar():
                        progress_bar.set(0)
                        while True:
                            if progress_queue.empty():
                                continue
                            progress, speed = progress_queue.get_nowait()
                            lb_progress.configure(text=f'{int(progress * 100)}%')
                            lb_speed.configure(text=f'{speed:.2f} kb/s')
                            progress_bar.set(progress)
                            time.sleep(0.0001)
                            if progress >= 1:
                                break
                    thread_update_progress_bar = threading.Thread(target=update_progress_bar)
                    thread_upload = threading.Thread(target=cl.upload_UI, args=(client, choosen_obj[0], progress_queue))
                    thread_upload.start()
                    thread_update_progress_bar.start()
                    
                elif os.path.isdir(choosen_obj[0]):
                    progress_queue = queue.Queue()
                    def update_progress_bar():
                        progress_bar.set(0)
                        lb_speed.configure(text=' ')
                        while True:
                            if progress_queue.empty():
                                continue
                            current_success, total_file = progress_queue.get_nowait()
                            lb_progress.configure(text=f'{current_success}/{total_file}')
                            progress_bar.set(current_success / total_file)
                            time.sleep(0.00000001)
                            if current_success == total_file:
                                break
                    thread_update_progress_bar = threading.Thread(target=update_progress_bar)
                    thread_upload = threading.Thread(target=cl.upload_multithreaded_UI, args=(choosen_obj[0], progress_queue))
                    thread_update_progress_bar.start()
                    thread_upload.start()
        
    #Button choose file
    btn_choose_file = CTkButton(frame, text='Choose File', font=("", 15, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=file_dialog)
    btn_choose_file.place(x=50, y=50)
    
    #Button choose folder
    btn_choose_folder = CTkButton(frame, text='Choose Folder', font=("", 15, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=folder_dialog)
    btn_choose_folder.place(x=50, y=120)
        
    #Progress bar
    progress_bar = CTkProgressBar(frame, width=300, height=20, fg_color='#FFF', progress_color='#EEEE00')
    progress_bar.set(0)
    progress_bar.place(x=300, y=250)
    
    #Nhan hien thi tien do va toc do upload
    lb_progress = CTkLabel(master=frame, text=' ', font=('Arial', 15, 'bold'), text_color='brown')
    lb_progress.place(x=620, y=250)
    
    lb_speed = CTkLabel(master=frame, text=' ', font=('Arial', 15, 'bold'), text_color='brown')
    lb_speed.place(x=620, y=280)
            
    #Button start upload file
    def start_progress():
        if choosen_obj[0] == '':
            messagebox.showwarning("Warning!", "You didn't choose any file!")
        else:
            client.send(mode_upload[0].ljust(LENGTH_MODE).encode(ENCODING))
            thread_upload = threading.Thread(target=enter_pin_window)
            thread_upload.start()
        
    btn_upload = CTkButton(frame, text='Start Upload', font=("", 15, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=start_progress)
    btn_upload.place(x=50, y=250)
    
    return frame