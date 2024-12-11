from customtkinter import *
import threading
import os
import time

PATH_LOG = 'C:/database/server_log.txt'

def update_log(path, log_text_box):
    while True:
        log_text_box.configure(state='normal')
        with open(path, mode='r', encoding='utf-8') as f:
            content = log_text_box.get('1.0', 'end-1c')
            size = len(content.encode('utf-8'))
            f.seek(size, 0)
            lines = f.readlines()
            if lines is None:
                continue
            for line in lines:
                log_text_box.insert('end', line)
        log_text_box.configure(state='disable')
        log_text_box.see('end')
        time.sleep(0.5)

def log_frame(parent):
    frame = CTkFrame(parent, fg_color='#E4BD63', height=500, width=751)
    
    #Log
    scroll_bar = CTkScrollbar(frame, orientation='vertical', fg_color="blue") 
    scroll_bar.pack(side="right", fill="y")
    
    log_text_box = CTkTextbox(frame, height=500, width=751, fg_color='#E4BD63', text_color='brown', font=('Arial', 16, 'bold'), state='normal')
    log_text_box.pack(side="left", fill="both", expand=True)
    
    log_text_box.configure(yscrollcommand=scroll_bar.set)
    
    with open(PATH_LOG, mode='r') as f:
        lines = f.readlines()
        for line in lines:
            log_text_box.insert('end', line)
    log_text_box.configure(state='disabled')
    log_text_box.see('end')
    
    thread_update_log = threading.Thread(target=update_log, args=(PATH_LOG, log_text_box))
    thread_update_log.start()
    
    return frame
    