import base64
import io
import os
import threading
from socket import socket, AF_INET, SOCK_STREAM

# === УСТАНОВІТЬ webcolors ЧЕРЕЗ pip install webcolors
import webcolors


from datetime import datetime

from customtkinter import *
from tkinter import filedialog
from PIL import Image

HOST = "127.0.0.1"   
PORT = 80


class ChatApp(CTk):

    def __init__(self):
        super().__init__()

        self.geometry("800x800")
        self.title("Online Chat")
        self.config(bg="#281c52")

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.username = None
        self.images_cache = []

        self.r = 0
        self.g = 0
        self.b = 0
        self.color = "#601bff"

        self.globalcolor = "#c7c2f8"

        self.font = ('Helvetica', 17, 'italic')

        self.show_auth_screen()


    # ================= AUTH =================

    def show_auth_screen(self):
        self.auth_frame = CTkFrame(self,bg_color="#281c52", fg_color=self.globalcolor, corner_radius=10)
        self.auth_frame.pack(expand=True)

        CTkLabel(self.auth_frame, text="Авторизація",
                 font=self.font).pack(pady=20)

        self.login_entry = CTkEntry(self.auth_frame, placeholder_text="Логін")
        self.login_entry.pack(pady=10)

        self.pass_entry = CTkEntry(self.auth_frame,
                                   placeholder_text="Пароль",
                                   show="*")
        self.pass_entry.pack(pady=10)

        CTkButton(self.auth_frame, text="Увійти",
                  command=self.login).pack(pady=10)

        CTkButton(self.auth_frame, text="Реєстрація",
                  command=self.register).pack(pady=10)

        self.status_label = CTkLabel(self.auth_frame, text="")
        self.status_label.pack(pady=10)

    def login(self):
        username = self.login_entry.get()
        password = self.pass_entry.get()
        try:
            self.sock.send(f"LOGIN@{username}@{password}".encode())
            response = self.sock.recv(1024).decode().strip()

            if response == "LOGIN_OK":
                self.username = username
                self.password = password
                self.auth_frame.destroy()
                self.build_customizer()
                threading.Thread(target=self.receive_loop,
                             daemon=True).start()
                

                self.getcolor()
                
            
            else:
                self.status_label.configure(text="❌ Невірні дані",
                                        text_color="red")
        except ConnectionResetError:
            print("ЗАКРИТО")

    def register(self):
        username = self.login_entry.get()
        password = self.pass_entry.get()

        self.sock.send(f"REGISTER@{username}@{password}@{self.color}".encode())
        response = self.sock.recv(1024).decode().strip()

        if response == "REGISTER_OK":
            self.status_label.configure(text="✅ Зареєстровано!",
                                        text_color="green")
        else:
            self.status_label.configure(text="❌ Користувач існує",
                                        text_color="red")

    # =================== CUSTOMIZER ==================

    # slider functions
    def Color_red(self, value):
        
        print(self.r)

        self.r = int(value)  

        self.change_colors(True)
 

    def Color_green(self, value):

        self.g = int(value)

        self.change_colors(True)

    def Color_blue(self, value):

        self.b = int(value)
        print(self.username,self.password)
        self.change_colors(True)
    
    # === build customizer ===

    def build_customizer(self):
        
        if not hasattr(self, "custframe"):
            self.custframe = CTkFrame(self, corner_radius=10, bg_color="#281c52")
            self.custframe.pack(expand=True)

            self.text_color = CTkLabel(self.custframe, text="Customize", font=self.font, bg_color="#281c52")
            self.text_color.pack(fill='x')

            self.rslider = CTkSlider(self.custframe, width=200, button_color="#ff3030", from_ = 0, to = 255, 
                                     command=self.Color_red, bg_color=self.globalcolor, corner_radius=4)
            self.gslider = CTkSlider(self.custframe, width=200, button_color="#2bb132", from_ = 0, to = 255, 
                                     command=self.Color_green, bg_color=self.globalcolor)
            self.bslider = CTkSlider(self.custframe, width=200, button_color="#2251d3", from_ = 0, to = 255, 
                                     command=self.Color_blue, bg_color=self.globalcolor)

            self.rslider.pack(side='top', fill='x')
            self.gslider.pack(side='top', fill='x')
            self.bslider.pack(side='top', fill='x')


            self.button_finish = CTkButton(self.custframe, command=self.build_chat, text="Finish", bg_color=self.globalcolor, corner_radius=10)
            self.button_finish.pack(side='bottom', fill='x')

            self.button_save = CTkButton(self.custframe, command=self.savecust,text="Save", bg_color=self.globalcolor)
            self.button_save.pack(side='bottom', fill='x')

    #def destroycust(self):
       # self.custframe.destroy()

    def change_colors(self, convert):

        
        print(webcolors.rgb_to_hex((self.r,self.g,self.b)))

        # convert RGB to hex 
        if convert:
            self.color = webcolors.rgb_to_hex((self.r,self.g,self.b))
        
        if hasattr(self, "text_color"):
            self.text_color.configure(text_color=self.color)

        if hasattr(self, "button_finish"):
            self.button_finish.configure(fg_color=self.color)

        if hasattr(self, "button_save"):
            self.button_save.configure(fg_color=self.color)

        if hasattr(self, "custframe"):
            self.custframe.configure(bg_color=self.color)


        

    def savecust(self):

        self.sock.send(f"COLOR@{self.username}@{self.password}@{self.color}".encode())
        print(self.color)

    
    def getcolor(self):
        self.sock.send(f"COLOR_GET@{self.username}@{self.password}".encode())
 


    # ================= CHAT =================


    def build_chat(self):

        if hasattr(self, "custframe"):
            self.custframe.destroy()

        self.chat_frame = CTkScrollableFrame(self, corner_radius=10, bg_color="#281c52", border_width=4)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

        bottom = CTkFrame(self, bg_color="#281c52", corner_radius=20)
        bottom.pack(fill="x", padx=10, pady=10)

        CTkButton(bottom, text="Font", width=50,
                  command=self.build_customizer, fg_color=self.color, bg_color="#281c52").pack(side="left")

        self.entry = CTkEntry(bottom, placeholder_text="Enter Text:")
        self.entry.pack(side="left", fill="x", expand=True, padx=5)

        CTkButton(bottom, text="📷", width=50,
                  command=self.send_image, fg_color=self.color, bg_color="#281c52").pack(side="right", padx=5)

        CTkButton(bottom, text=">", width=50,
                  command=self.send_message, fg_color=self.color).pack(side="right")
        

    def add_message(self, text, author=None, image=None):
        if hasattr(self, "chat_frame"):
            print(author)
            bubble = CTkFrame(self.chat_frame,
                          fg_color=self.color if author == self.username else "#2b2b2b",
                          corner_radius=15)

            bubble.pack(anchor="e" if author == self.username else "w",
                    pady=5, padx=5)

            if image:
                self.images_cache.append(image)
                CTkLabel(bubble, text=text,
                     image=image,
                     compound="top",
                     wraplength=450,
                     text_color="white", bg_color=self.color).pack(padx=10, pady=5)
            else:


                CTkLabel(bubble, text=text if author == self.username else f"{author}: {text}",
                     wraplength=450,
                     text_color="white",
                     justify="left").pack(padx=10, pady=5)
                
                current_time = datetime.now().strftime("%H:%M:%S")
                current_date = datetime.now().date()
                CTkLabel(self.chat_frame, text=f"Прислано в : {current_date}, {current_time}",
                     wraplength=450,
                     text_color="gray",
                     fg_color="transparent",
                     height=10,
                     justify="left").pack(anchor="e" if author == self.username else "w",
                    pady=5, padx=5)

    # ================= SEND =================

    def send_message(self):
        msg = self.entry.get().strip()
        if not msg:
            return

        self.sock.send(f"TEXT@{msg}".encode())
        self.add_message(msg, self.username)
        self.entry.delete(0, END)

    def send_image(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return

        with open(file_name, "rb") as f:
            raw = f.read()

        b64_data = base64.b64encode(raw).decode()
        short_name = os.path.basename(file_name)

        self.sock.send(f"IMAGE@{short_name}@{b64_data}".encode())

        pil_img = Image.open(file_name)
        img = CTkImage(light_image=pil_img, size=(300, 300))
        self.add_message(short_name, self.username, img)

    # ================= RECEIVE =================

    def receive_loop(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    print("BREAK")
                    break

                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())

            except:
                break

    def handle_line(self, line):
        parts = line.split("@", 3)
        print("HANDLE")
        print(parts)
        if parts[0] == "TEXT":
            self.after(0, self.add_message,
                       parts[2], parts[1])

        elif parts[0] == "SYSTEM":
            self.after(0, self.add_message,
                       f"🔔 {parts[1]}")

        elif parts[0] == "IMAGE":
            author = parts[1]
            filename = parts[2]
            img_data = base64.b64decode(parts[3])
            pil_img = Image.open(io.BytesIO(img_data))
            img = CTkImage(light_image=pil_img, size=(300, 300))

            self.after(0, self.add_message,
                       filename, author, img)
        # change color
        elif parts[0] == "COLOR_GET":
            
            print("SAVECOLOR")
            self.color = parts[1]
            print(self.color)
            r,g,b = webcolors.hex_to_rgb(self.color)
            self.r = r
            self.g = g
            self.b = b

            self.rslider.set(self.r)
            self.gslider.set(self.g)
            self.bslider.set(self.b)

            self.after(0, lambda: self.change_colors(False))


if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
