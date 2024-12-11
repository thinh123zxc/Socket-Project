from customtkinter import *
import upload_frame as ul
import download_frame as dl
import client as cl
import socket

def clientUI(client):
    # Main
    main = CTk()
    main.title(f'Client - IP: {socket.gethostbyname(socket.gethostname())}')
    main.config(bg='white')
    main.resizable(False, False)
    main.geometry('850x500')
    
    #Upload frame
    upload_frame = ul.upload_frame(main, client)
    
    #Download frame
    download_frame = dl.download_frame(main, client)

    # Frame 1
    frame1 = CTkFrame(main, fg_color='#B4CDF2', height=500, width=100)
    frame1.grid(row=0, column=0, sticky="ns")

    # Upload button
    def btn_show_upload():
        download_frame.grid_forget()
        upload_frame.grid(row=0, column=1, sticky="nsew")
        
    upload_btn = CTkButton(frame1, text='Upload', font=("", 15, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=btn_show_upload)
    upload_btn.grid(row=0, column=0, sticky='new', pady=10, padx=5)

    # Download button
    def btn_show_download():
        upload_frame.grid_forget()
        download_frame.grid(row=0, column=1, sticky="nsew")
        
    download_btn = CTkButton(frame1, text='Download', font=("", 15, 'bold'), height=40, width=60, fg_color="#0085FF", cursor='hand2', corner_radius=20, command=btn_show_download)
    download_btn.grid(row=1, column=0, sticky='new', pady=8, padx=5)

    # User button
    # user_icon = Image.open("user3.png")
    # user_icon = ImageTk.PhotoImage(user_icon)
    # user_btn = CTkButton(frame1, image=user_icon, text='', corner_radius=50, width=50, height=64, fg_color='#B4CDF2')
    # user_btn.grid(row=2, column=0, sticky='s', pady=10)
    # frame1.grid_rowconfigure(2, weight=1)

    # Frame 2
    upload_frame.grid(row=0, column=1, sticky="nsew")
    return main

if __name__ == '__main__':
    main = clientUI('adsad')
    main.mainloop()
