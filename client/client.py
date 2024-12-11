import socket
from alive_progress import alive_bar
import time
import os
import math
import concurrent.futures
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
import json
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

def enter_password(client):
    message = client.recv(LENGTH_MESS).decode().strip()
    print(message)
    while True:
        if message == message_setup_first_pass_word:
            initpassword = input('Khoi tao password: ')
            client.send(initpassword.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo mật khẩu có đủ độ dài
            message = client.recv(LENGTH_MESS).decode().strip()
        if message == message_success:
            password = input('Nhap vao pass word: ')
            client.send(password.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo mật khẩu có đủ độ dài
            break
        else:
            print('message', message)


def enter_pin(client):
    message = client.recv(LENGTH_MESS).decode().strip()
    while True:
        if message == message_setup_first_pin:
            initpin = input('Khoi tao pin: ')
            client.send(initpin.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo pin có đủ độ dài
            message = client.recv(LENGTH_MESS).decode().strip()
        if message == message_success:
            pin = input('Nhap vao pin: ')
            client.send(pin.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo pin có đủ độ dài
            break
        else: 
            print(message)


def process_login_updownload(client): #xử lí đăng nhập
    # Gọi hàm nhập mật khẩu
    enter_pin(client)

    # Nhận phản hồi từ server
    message = client.recv(LENGTH_MESS).decode().strip()
    print('message', message)

    while message == message_failure:
        print('SAI PIN')
        enter_pin(client)
        message = client.recv(LENGTH_MESS).decode().strip()


def process_login_client(client): #xử lí đăng nhập
    # Gọi hàm nhập mật khẩu
    enter_password(client)

    # Nhận phản hồi từ server
    message = client.recv(LENGTH_MESS).decode().strip()

    while message == message_failure:
        print('SAI PASS WORD')
        enter_password(client)
        message = client.recv(LENGTH_MESS).decode().strip()               
        # return None

#Khởi tạo kết nối server
def init(message):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        client.connect(ADDRESS_SERVER)
        ###
        client.send(message.ljust(LENGTH_MESS).encode(ENCODING))
        if message == message_login:
            process_login_client(client)
        
        return client
    except socket.gaierror:
        print("The address server is invalid !")
        return None
    except ConnectionRefusedError:
        print("The server is off !")
        return None

#Nhập tên file
def input_name_file():
    name_file = input("Input name file: ")
    while True:
        if not os.path.isfile(name_file) or not os.path.exists(name_file):
            print("The name file is not exist!")
            name_file = input("Input the new name file: ")
        else:
            return name_file


#Nhập tên folder
def input_name_folder():
    name_file = input("Input name folder: ")
    while True:
        if os.path.exists(name_file):
            return name_file
        else:
            print("The name folder is not exist!")
            name_file = input("Input the new name folder: ")


#xử lí tên đường dẫn để lấy tên file
def cut_name_in_path(name_file):
    positive_last_slash = 0
    for i in range(len(name_file) - 1,-1,-1):
        if name_file[i] == '/' or name_file[i] == "\\":
            positive_last_slash = i
            break
    
    if positive_last_slash == 0:
        return name_file
    name_result = name_file[positive_last_slash+1:len(name_file)]
    return name_result


#xử lý lấy tổng dung lượng file và gửi dung lượng file
def send_header_to_server(client, name_file,file):
    file_size = os.path.getsize(name_file)
    file_size_string = str(file_size)
    name_file_nopath = cut_name_in_path(name_file)
    client.send(name_file_nopath.ljust(LENGTH_NAME,' ').encode(ENCODING))
    client.send(file_size_string.ljust(LENGTH_SIZE,' ').encode(ENCODING))
    return file_size

#Gửi các dữ liệu qua server
def send_data_to_upload(name_file,client):
    file = open(name_file,"rb")
    file_size = send_header_to_server(client, name_file,file)
    name_file_no_path = cut_name_in_path(name_file)
    while True:
        #đếm số lần lập
        number_of_repeat =math.ceil(file_size/ BUFFER)
        #Tạo thanh bar kết hợp gửi file
        with alive_bar(number_of_repeat, title=f"Upload {name_file_no_path}") as bar:
            for _ in range(number_of_repeat):
                chunk = file.read(BUFFER)  
                if not chunk:
                    break  
                client.send(chunk)
                time.sleep(0.0000000005) 
                bar()
            break
    file.close()
    message = client.recv(LENGTH_MESS).decode().strip()
    if message == message_notenough:
        print('Send fail')


#Upload file
def upload(client):
    process_login_updownload(client)
    name_file = input_name_file()
    if os.path.exists(name_file):
        try:
            send_data_to_upload(name_file,client)
        except ConnectionResetError:
            print("The server suddenly disconnect!")
    else:
        print("File is not exist")
        
def upload_UI(client, name_file):
    # process_login_updownload(client)
    if os.path.exists(name_file):
        try:
            send_data_to_upload(name_file,client)
        except ConnectionResetError:
            print("The server suddenly disconnect!")
    else:
        print("File is not exist")

#tìm đường dẫn để lưu file
def find_path_to_save_file(name_path,name_file):
    name_path_and_file = name_path
    if name_path_and_file[len(name_path_and_file)-1] == '/':
        name_path_and_file += name_file
    else:
        name_path_and_file =name_path_and_file+ "/" +name_file
    #Nếu file đã tồn tại thì xóa
    if os.path.exists(name_path_and_file) == True:
        os.remove(name_path_and_file)
    file = open(name_path_and_file,"x")
    file.close()
    return name_path_and_file


#Lấy nội dung từ client
def get_content(client,name_file_and_path,file_size):
    received_size = 0
    with open(name_file_and_path,"ab") as file:
        #tính số làn lập
        number_of_repeat= math.ceil(file_size/ BUFFER)
        with alive_bar(number_of_repeat, title="Downloading") as bar:
            for _ in range(number_of_repeat):
                #nhận file
                data = client.recv(BUFFER)
                bytes_to_write = min(len(data), file_size - received_size)
                file.write(data[:bytes_to_write])
                received_size += bytes_to_write
                time.sleep(0.0000000005) 
                bar()
                if not data:
                    if received_size < file_size:
                        client.send(message_notenough.ljust(LENGTH_MESS,' ').encode(ENCODING))
                        os.remove(name_file_and_path)
                        print("Error: The data is insufficient")
                        break
                if received_size == file_size:
                    break
        if received_size == file_size: 
            client.send(message_enough.ljust(LENGTH_MESS,' ').encode(ENCODING))
            
def get_content_UI(client,name_file_and_path,file_size, queue):
    received_size = 0
    start_time = time.time()
    with open(name_file_and_path,"ab") as file:
        #tính số làn lập
        number_of_repeat= math.ceil(file_size/ BUFFER)
        for _ in range(number_of_repeat):
            #nhận file
            data = client.recv(BUFFER)
            bytes_to_write = min(len(data), file_size - received_size)
            file.write(data[:bytes_to_write])
            received_size += bytes_to_write
            time.sleep(0.0000000005) 
            queue.put((received_size / file_size, bytes_to_write / (time.time() - start_time) / 1024))
            start_time = time.time()
            if not data:
                if received_size < file_size:
                    client.send(message_notenough.ljust(LENGTH_MESS,' ').encode(ENCODING))
                    os.remove(name_file_and_path)
                    print("Error: The data is insufficient")
                    break
            if received_size == file_size:
                break
        if received_size == file_size: 
            client.send(message_enough.ljust(LENGTH_MESS,' ').encode(ENCODING))


#Hàm chính download
def download(client, name_path, name_file, response_ip):
    client.send(response_ip.ljust(LENGTH_NAME).encode(ENCODING))
    message = client.recv(LENGTH_MESS).decode().strip()
    if message == message_error_notfound:
        print('Khong tim thay thu muc')
    else: 
        process_login_updownload(client)
        name_path_file = ""
        try:
            #Gửi tên file
            client.send(name_file.ljust(BUFFER,' ').encode(ENCODING))
            message = client.recv(LENGTH_MESS).decode().strip()
            if message == message_success:
                name_path_file = find_path_to_save_file(name_path,name_file)
                file_size = int(client.recv(LENGTH_SIZE).decode().strip())
                #Lấy nội dung
                get_content(client,name_path_file,file_size)
            else:
                print("The file doesn't exit in the server")
        except ConnectionResetError:
            print("The server suddenly disconnect!")
            os.remove(name_path_file)
            

###
#Gửi dữ liệu không có thanh tiến trình
def send_data_multithreading(name_file):
    #khởi tạo theo mode không cần đăng nhập
    client = init(message_notlogin)
    mode = "upload multithread1" 
    try:
        #gửi dữ liệu
        client.send(mode.ljust(LENGTH_MODE).encode(ENCODING))
        file = open(name_file,"rb")
        send_header_to_server(client, name_file,file)
        while True:
            chunk = file.read(BUFFER)  
            if not chunk:
                break  
            client.send(chunk)
        file.close()
        #Gửi xác nhận thành công
        print(name_file + " successful download.")
        message = client.recv(LENGTH_MESS).decode().strip()
        if message == message_enough:
            pass
        else:
            print("The file error! Please upload file again")
        client.send('exit'.ljust(LENGTH_MODE).encode(ENCODING))
        client.close()
    except ConnectionResetError:
        print("The server suddenly disconnect!")
        print(f"{name_file} is not successful")
        client.close()


#Hàm đếm số luồng đã hoàn thành
def count_thread_success(threads):
    count = 0 
    for thread in threads:
        if not thread.is_alive():
            count = count + 1
    return count

#Gửi dữ liệu đa luồng của folder
def upload_multithreaded():
    try: 
        # nhập vào folder cần tải
        name_folder = input_name_folder()
        if os.path.exists:
            list_file = os.listdir(name_folder)
            threads = []
            #tạo ra các luồng ứng với từng file
            for file in list_file:
                name_file_path = name_folder + "\\" + file
                thread = threading.Thread(target = send_data_multithreading,args = (name_file_path,))
                thread.start()
                threads.append(thread)
            #Hiện thị thanh bar theo số luồng đã hoàn thành xong
            count_thread = 0
            count_thread_current = 0
            with alive_bar(len(list_file), title=f"Upload ") as bar:
                while True:
                    count_thread = count_thread_success(threads)
                    if count_thread_current != count_thread:
                        bar(count_thread - count_thread_current)
                        count_thread_current = count_thread
                    time.sleep(0.000000000000000005) 
                    if count_thread == len(list_file):
                        break
            for thread in threads:
                thread.join()
        else:
            print("Folder is not exist")
    except ConnectionResetError:
        print("The server suddenly disconnect!")
        
def upload_multithreaded_UI(name_folder):
    try: 
        if os.path.exists:
            list_file = os.listdir(name_folder)
            threads = []
            #tạo ra các luồng ứng với từng file
            for file in list_file:
                name_file_path = name_folder + "\\" + file
                thread = threading.Thread(target = send_data_multithreading,args = (name_file_path,))
                thread.start()
                threads.append(thread)
            #Hiện thị thanh bar theo số luồng đã hoàn thành xong
            count_thread = 0
            count_thread_current = 0
            with alive_bar(len(list_file), title=f"Upload ") as bar:
                while True:
                    count_thread = count_thread_success(threads)
                    if count_thread_current != count_thread:
                        bar(count_thread - count_thread_current)
                        count_thread_current = count_thread
                    time.sleep(0.000000000000000005) 
                    if count_thread == len(list_file):
                        break
            for thread in threads:
                thread.join()
        else:
            print("Folder is not exist")
    except ConnectionResetError:
        print("The server suddenly disconnect!")

#Lấy danh sách file và in ra
def get_list(client):
    #nhận danh sách folder từ server
    list_folder = client.recv(LENGTH_DIR).decode().strip()
    list_folder = json.loads(list_folder)
    #in danh sách
    for name_folder in list_folder.keys():
        print(name_folder,end = ": ")
        no = 0
        for name_file in list_folder[name_folder]:
            if no == len(list_folder[name_folder]) - 1:
                print(name_file,end = " ")
            else:
                print(name_file,end=" , ")
            no = no + 1
        print("\n")
    return list_folder

def menu():
    client = init(message_login)
    #cHƯA
    if client:
        while(True):
            try:
                print("Menu mode: ")
                print("1.upload")
                print("2.download")
                print("3.upload multithread")
                print("4.getlist")
                print("5.exit")
                mode = input("Input:")
                client.send(mode.ljust(LENGTH_MODE).encode(ENCODING))
                if mode == "upload":
                    upload(client)
                if mode == "download":
                    filename = input('chon file')
                    ip = input('thu muc')
                    path = input('noi luu')
                    download(client,path,filename,ip)
                if mode == "upload multithread":
                    process_login_updownload(client)
                    upload_multithreaded()
                if mode == "getlist":
                    # process_login_updownload(client)
                    get_list(client)
                if mode == "exit":
                    client.close()
                    break
            except:
                print('SERVER unexpected disconnect')
                break

def main():
    menu()
if __name__ == '__main__':
    main()