from customtkinter import *
import log_frame as lf
import repository_frame as rf
import server as sv
import threading
    
def init_server():
    server_socket = sv.init_server()
    sv.listening(server_socket)

def serverUI():
    # Main
    thread = threading.Thread(target=init_server)
    thread.start()
    
    main = CTk()
    main.title('Server')
    main.config(bg='white')
    main.resizable(False, False)
    main.geometry('850x500')
    
    #Log frame
    log_frame = lf.log_frame(main)
    
    #Repository frame
    # repo_frame = rf.repository_frame(main)

    # Frame 1
    frame1 = CTkFrame(main, fg_color='#B4CDF2', height=500, width=100)
    frame1.grid(row=0, column=0, sticky="ns")

    # Repository button
    # def btn_show_repo():
    #     log_frame.grid_forget()
    #     repo_frame.grid(row=0, column=1, sticky="nsew")
        
    # repo_btn = CTkButton(frame1, text='Repository', font=("", 15, 'bold'), height=40, width=60, fg_color='#0085FF', cursor='hand2', corner_radius=20, command=btn_show_repo)
    # repo_btn.grid(row=0, column=0, sticky='new', pady=10, padx=5)

    # Log button
    def btn_show_log():
        # repo_frame.grid_forget()
        log_frame.grid(row=0, column=1, sticky="nsew")
    log_btn = CTkButton(frame1, text='Log', font=("", 15, 'bold'), height=40, width=90, fg_color='#0085FF', cursor='hand2', corner_radius=20, command=btn_show_log)
    log_btn.grid(row=1, column=0, sticky='new', pady=8, padx=5)

    # Start/Stop server button
    # server_on = [False]
    # status_btn = CTkButton(frame1, image=status_off, text='', corner_radius=50, width=50, height=64, fg_color='#B4CDF2', command=lambda:control_server(server_on, status_btn))
    # status_btn.grid(row=2, column=0, sticky='s', pady=10)
    # frame1.grid_rowconfigure(2, weight=1)

    # Frame 2
    log_frame.grid(row=0, column=1, sticky="nsew")
    return main

if __name__ == '__main__':
    main = serverUI()
    main.mainloop()
