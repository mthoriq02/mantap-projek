from sqlite3 import IntegrityError
from database import c, conn
from CTkMessagebox import CTkMessagebox
from login import LoginPage
import customtkinter as ctk
import tkinter as tk
import bcrypt

ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('dark-blue')

c.execute(
    "create table if not exists users_accounts_data (username text unique not null, password text not null)" 
)

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1000, height=700, bg_color='#1e1e1e')
        self.controller = controller

        # konfigurasi layout utama register
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # frame utama register
        register_frame = ctk.CTkFrame(self, width=380, height=500, corner_radius=12)
        register_frame.grid(row=0, column=0, padx=(50, 50), pady=(80, 10))
        register_frame.grid_propagate(False)
        register_frame.grid_columnconfigure(0, weight=1)
        
        # judul register
        title_label = ctk.CTkLabel(
            register_frame,text="Sign-Up",
            font=ctk.CTkFont(size=26, weight='bold', family='Poppins')
            )
        title_label.grid(
            row=0, column=0, columnspan=2,
            pady=(50, 20), sticky='we'
            )
        subtitle_label = ctk.CTkLabel(
            register_frame,
            text='Silahkan isi data untuk membuat akun',
            font=ctk.CTkFont(size=14, family='Arial', weight='normal')
            )
        subtitle_label.grid(row=1,column=0,pady=(0, 60),sticky='ew')

        # frame input username
        username_frame = ctk.CTkFrame(register_frame, fg_color='transparent')
        username_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20))

        # frame input password
        password_frame = ctk.CTkFrame(register_frame, fg_color='transparent')
        password_frame.grid(row=3, column=0, columnspan=2)

        # frame tombol
        button_frame = ctk.CTkFrame(register_frame, fg_color='transparent')
        button_frame.grid(row=4, column=0, columnspan=2)

        # info username kosong
        self.username_info_label = ctk.CTkLabel(
            username_frame,
            text='*username tidak boleh kosong',
            font=ctk.CTkFont(size=10, family='Calibri'),
            text_color='#FF0000'
            )
        self.username_info_label.grid(row=0, column=0, columnspan=2, sticky='w')

        # input username
        self.username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text='Username',
            width=300, height=40,
            font=ctk.CTkFont(size=14, family='Poppins'),
            corner_radius=8
            )
        self.username_entry.grid(row=0, column=0, columnspan=2)
        self.username_entry.bind('<FocusOut>', self.username_validate)
        self.username_entry.bind('<KeyRelease>', self.username_validate)

        # input password
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text='Password',
            width=300, height=40,
            font=ctk.CTkFont(size=14, family='Poppins'),
            show= '•',
            corner_radius=8
            )
        self.password_entry.grid(row=0, column=0, columnspan=2)
        self.password_entry.bind('<KeyRelease>', self.password_validate)
        self.password_entry.bind('<FocusOut>', self.password_validate)
        self.password_entry.bind('<KeyRelease>', self.password_check_validate)
        self.password_entry.bind('<FocusOut>', self.password_check_validate)
        
        # checkbox tampilkan password
        self.hidden_var_1 = ctk.BooleanVar(value=False)
        self.password_hid = ctk.CTkCheckBox(
            password_frame,
            border_width=1, width=1, height=1,
            text='Perlihatkan password',
            font=ctk.CTkFont(size=11, family='Poppins'),
            variable=self.hidden_var_1,
            onvalue=True, offvalue=False,
            command=self.show_password
            )
        self.password_hid.grid(row=1, column=0, pady=5, sticky='w')

        # info validasi password
        self.password_info_label = ctk.CTkLabel(
            password_frame,
            text='*password setidaknya harus 8 karakter',
            font=ctk.CTkFont(size=10, family='Calibri'),
            text_color="#8F8383"
            )
        self.password_info_label.grid(row=1, column=1, sticky='e')

        # input konfirmasi password
        self.password_check = ctk.CTkEntry(
            password_frame,
            placeholder_text='Masukkan ulang password',
            width=300, height=40,
            font=ctk.CTkFont(size=14, family='Poppins'),
            show='•', corner_radius=8
            )
        self.password_check.grid(row=2, column=0, columnspan=2)
        self.password_check.bind('<KeyRelease>', self.password_check_validate)
        self.password_check.bind('<FocusOut>', self.password_check_validate)
        
        #checkbox tampilkan konfirmasi password
        self.hidden_var_2 = ctk.BooleanVar(value=False)
        self.password_check_hid = ctk.CTkCheckBox(
            password_frame,
            border_width=1, width=1, height=1,
            text='Perlihatkan password',
            font=ctk.CTkFont(size=11, family='Poppins'),
            variable=self.hidden_var_2,
            onvalue=True, offvalue=False,
            command=self.show_password_check
            )
        self.password_check_hid.grid(row=3, column=0, pady=5, sticky='w')
        
        # info konfirmasi password
        self.password_check_info_label = ctk.CTkLabel(
            password_frame,
            text='*masukkan ulang password',
            font=ctk.CTkFont(size=10, family='Calibri'),
            text_color='#8F8383'
            )
        self.password_check_info_label.grid(row=3, column=1, sticky='e')

        # tombol daftar
        self.button_register = ctk.CTkButton(
            button_frame,
            text='Sign-Up', width=300, height=40,
            font=ctk.CTkFont(size=16, family='Poppins'),
            command=self.register_button, corner_radius=10
            )
        self.button_register.grid(row=0, column=0, columnspan=2)

        # link ke login
        self.login_link = ctk.CTkLabel(
            button_frame,
            text='Sudah punya akun? Login',
            text_color='#0D5BC0',
            font=ctk.CTkFont(size=10, family='Calibri', underline=True)
            )
        self.login_link.grid(row=1, column=0, sticky='e')
        self.login_link.bind('<Button-1>', self.login_open)
        
    def username_validate(self, event=None):
        # tampilkan pesan jika username kosong
        username = self.username_entry.get()
        if username == "":
            self.username_info_label.grid_configure(row=1)
        else:
            self.username_info_label.grid_configure(row=0)
    
    def password_validate(self, event=None):
        # validasi panjang password
        password = self.password_entry.get()

        if len(password) < 8:
            self.password_info_label.configure(
                text='Password terlalu pendek',
                text_color='#FF0000'
                )
        else:
            self.password_info_label.configure(
                text='Password sudah cukup',
                text_color='#00FF00'
                )

    def password_check_validate(self, event=None):
        # cek apakah password match dengan konfirmasi
        password = self.password_entry.get()
        password_check = self.password_check.get()

        if password != password_check:
            self.password_check_info_label.configure(
                text='Password tidak sesuai',
                text_color='#FF0000'
                )
        else:
            self.password_check_info_label.configure(
                text='Password sesuai',
                text_color='#00FF00'
                )

    def show_password(self):
        if self.hidden_var_1.get():
            self.password_entry.configure(show='')

        else:
            self.password_entry.configure(show='•')

    def show_password_check(self):
        if self.hidden_var_2.get():
            self.password_check.configure(show='')

        else:
            self.password_check.configure(show='•')

    def register_button(self):
        # ambil semua input
        username = self.username_entry.get()
        password = self.password_entry.get()
        password_check = self.password_check.get()

        error = False

        # validasi kecocokan password
        if password != password_check:
            self.password_check_info_label.configure(
                text='Password tidak sesuai',
                text_color='#FF0000'
                )
            error = True

        # validasi username kosong
        if username == "":
            self.username_info_label.grid_configure(row=1)
            error = True
        
        # validasi panjang password
        if len(password) < 8:
            self.password_info_label.configure(
                text='Password terlalu pendek',
                text_color='#FF0000'
                )
            error = True

        # hentikan jika error ditemukan
        if error:
            return

        try:
            # hashing password untuk keamanan user
            byte_password = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(byte_password, bcrypt.gensalt())
            
            # simpan user baru ke database
            c.execute(
                "insert into users_accounts_data values (?, ?)",
                (username, hashed_password)
            )
            conn.commit()

            # tampilkan pesan sukses
            CTkMessagebox(
                title='Sukses',
                message='Pendaftaran berhasil',
                icon='check'
                )
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.password_check.delete(0, tk.END)
            self.controller.show_frame(LoginPage)

        except IntegrityError:
            # username sudah terdaftar
            CTkMessagebox(
                title='Error',
                message='Username sudah terdaftar',
                icon='warning'
                )
            
    def login_open(self, event=None):
        # pindah ke halaman login
        self.controller.show_frame(LoginPage)

if __name__ == "__main__":
    root = RegisterPage()
    root.mainloop()