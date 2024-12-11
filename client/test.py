import tkinter as tk
from tkinter import messagebox

def show_warning():
    messagebox.showwarning("Cảnh báo", "Đây là một cảnh báo!")

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Cảnh báo Dialog")

# Nút để kích hoạt hộp thoại cảnh báo
btn_warning = tk.Button(root, text="Hiển thị Cảnh báo", command=show_warning)
btn_warning.pack(pady=20)

root.mainloop()
