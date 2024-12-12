from customtkinter import *
import time
import threading
import client as cl
import tkinter as tk
from tkinter import ttk
import socket
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

choosen_folder = ['']
choosen_file = [[]]
selection = [[]]
wrong_pin = [False]

def download_frame(parent, client):
    frame = CTkFrame(parent, fg_color='#E4BD63', height=500, width=751)
    
    #Label choosen file
    lb_choosen_folder = CTkLabel(master=frame, text='Choose folder to save', font=('Arial', 15, 'bold'), text_color='brown')
    lb_choosen_folder.place(x=300, y=120)
    
    lb_choosen_file = CTkLabel(master=frame, text='Choose file to download', font=('Arial', 15, 'bold'), text_color='brown')
    lb_choosen_file.place(x=300, y=70)
    
    #Progress bar
    progress_bar = CTkProgressBar(frame, width=300, height=20, fg_color='#FFF', progress_color='#EEEE00')
    progress_bar.set(0)
    progress_bar.place(x=300, y=250)
    
    lb_progress = CTkLabel(master=frame, text=' ', font=('Arial', 15, 'bold'), text_color='brown')
    lb_progress.place(x=620, y=250)
    
    lb_speed = CTkLabel(master=frame, text=' ', font=('Arial', 15, 'bold'), text_color='brown')
    lb_speed.place(x=620, y=280)
    
    def enter_pin_window():
        pin_window = CTkToplevel(frame, fg_color='#E4BD63')
        pin_window.geometry('500x250')
        pin_window.transient(frame)
        pin_window.grab_set()
        
        label = CTkLabel(pin_window, text='Enter your pin', font=('Arial', 23, 'bold'), text_color='brown')
        entry = CTkEntry(pin_window, show='*', width=250, height=30)
        btn_enter_pin = CTkButton(pin_window, text='OK', font=("", 20, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=lambda: download_UI(client, choosen_folder[0], choosen_file[0][1], choosen_file[0][0], entry.get(), label))
        
        label.place(x=135, y=20)
        entry.place(x=125, y=100)
        btn_enter_pin.place(x=205, y=180)
        
        def enter_pin_UI(client, Pin, label):
            message = client.recv(LENGTH_MESS).decode().strip()
            if message == message_setup_first_pin:
                label.configure(text='Let setup your pin')
                initpin = Pin
                client.send(initpin.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo pin có đủ độ dài
                message = client.recv(LENGTH_MESS).decode().strip()
            if message == message_success:
                label.configure(text='Enter your pin')
                pin = Pin
                client.send(pin.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo pin có đủ độ dài
            else: 
                print(message)

        def process_login_updownload_UI(client, Pin, label, name_path, name_file): #xử lí đăng nhập
            # Gọi hàm nhập mật khẩu
            enter_pin_UI(client, Pin, label)
            # Nhận phản hồi từ server
            message = client.recv(LENGTH_MESS).decode().strip()
            print('message', message)

            if message == message_failure:
                wrong_pin[0] = True
                label.configure(text='Wrong pin, again')
            else:
                pin_window.destroy()
                name_path_file = ""
                try:
                    #Gửi tên file
                    client.send(name_file.ljust(BUFFER,' ').encode(ENCODING))
                    message = client.recv(LENGTH_MESS).decode().strip()
                    if message == message_success:
                        name_path_file = cl.find_path_to_save_file(name_path,name_file)
                        file_size = int(client.recv(LENGTH_SIZE).decode().strip())
                        #Lấy nội dung
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
                        thread_get_content = threading.Thread(target=cl.get_content_UI, args=(client, name_path_file, file_size, progress_queue))
                        thread_get_content.start()
                        thread_update_progress_bar.start()
                        # cl.get_content(client,name_path_file,file_size)
                    else:
                        print("The file doesn't exit in the server")
                except ConnectionResetError:
                    print("The server suddenly disconnect!")
                    os.remove(name_path_file)
                
        def download_UI(client, name_path, name_file, response_ip, Pin, label):
            if wrong_pin[0] == False:
                client.send(response_ip.ljust(LENGTH_NAME).encode(ENCODING))
                message = client.recv(LENGTH_MESS).decode().strip()
                if message == message_error_notfound:
                    print('Khong tim thay thu muc')
                else: 
                    process_login_updownload_UI(client, Pin, label, name_path, name_file)
            else:
                wrong_pin[0] = False
                process_login_updownload_UI(client, Pin, label, name_path, name_file)
    def dir_dialog():
        dir_path = filedialog.askdirectory(title="Select a file")
        choosen_folder[0] = dir_path
        print("Selected file:", choosen_folder[0])
        lb_choosen_folder.configure(text=choosen_folder[0])
    
    def choose_file():
        mode = 'getlist'
        client.send(mode.ljust(LENGTH_MODE).encode(ENCODING))
        
        window = CTkToplevel(frame, fg_color='#E4BD63', height=200, width=400)
        window.transient(frame)
        window.grab_set()
        window.geometry('400x300')
        
        list_folder = cl.get_list(client)
        tree = ttk.Treeview(window, show='tree', columns=('Type',))
        tree.heading('#0', text='Name', anchor='w')
        tree.column('#0', stretch=True)
        tree.heading('Type', text='Type', anchor='w')
        tree.column('Type', anchor='w', width=100)
        for folder, files in list_folder.items():
            folder_id = tree.insert('', 'end', text=folder, open=True)
            for file in files:
                tree.insert(folder_id, 'end', text=file)
        tree.pack(fill="both", expand=True)
        
        def select_file(event):
            selected_item = tree.selection()
            if selected_item:
                item_id = selected_item[0]
                full_path = []
                while item_id:
                    item_text = tree.item(item_id, 'text')
                    full_path.insert(0, item_text)
                    item_id = tree.parent(item_id)
                if (len(full_path) > 1):
                    selection[0] = full_path
        tree.bind("<<TreeviewSelect>>", select_file)
        
        def selected_file():
            choosen_file[0] = selection[0]
            lb_choosen_file.configure(text=f'{'/'.join(choosen_file[0])}')
            window.destroy()
        btn_ok = CTkButton(window, text='Choose File', font=("", 15, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=selected_file)
        btn_ok.pack(pady=10)
          
    #Button choose file download
    btn_choose_file = CTkButton(frame, text='Choose File', font=("", 15, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=choose_file)
    btn_choose_file.place(x=50, y=50)
    
    #Button choose folder to download
    btn_choose_folder = CTkButton(frame, text='Choose Folder', font=("", 15, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=dir_dialog)
    btn_choose_folder.place(x=50, y=120)
            
    #Button start download file
    def start_progress():
        if len(choosen_file[0]) <= 1:
            messagebox.showwarning("Warning!", "You didn't choose any file to download!")
        elif choosen_folder[0] == '':
            messagebox.showwarning("Warning!", "You didn't choose any folder to save!")
        else:
            mode = 'download'
            client.send(mode.ljust(LENGTH_MODE).encode(ENCODING))
            thread_download = threading.Thread(target=enter_pin_window)
            thread_download.start()
        
    btn_download = CTkButton(frame, text='Start Download', font=("", 15, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=start_progress)
    btn_download.place(x=50, y=250)
    
    return frame