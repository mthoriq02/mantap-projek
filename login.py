from database import c
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import register
import bcrypt

ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('dark-blue')

c.execute(
    "create table if not exists users_accounts_data (username text unique not null, password text not null)" 
)

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1000, height=700, bg_color='#1e1e1e')
        self.controller = controller

        # konfigurasi layout utama halaman login
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # username yang akan dikirimkan
        self.username = ''

        # frame utama login
        login_frame = ctk.CTkFrame(self, width=380, height=500, corner_radius=12)
        login_frame.grid(row=0, column=0, padx=(50, 50), pady=(80, 10))
        login_frame.grid_propagate(False)
        login_frame.grid_columnconfigure(0, weight=1)

        # frame username dan password
        username_frame = ctk.CTkFrame(login_frame, fg_color='transparent')
        username_frame.grid(row=2, column=0, pady=(0, 20))

        password_frame = ctk.CTkFrame(login_frame, fg_color='transparent')
        password_frame.grid(row=3, column=0, pady=(0, 20))

        # frame tombol
        button_frame = ctk.CTkFrame(login_frame, fg_color='transparent')
        button_frame.grid(row=4, column=0)
        
        # label judul login
        title_label = ctk.CTkLabel(
            login_frame, text='Login',
            font=ctk.CTkFont(size=26, family='Poppins', weight='bold')
            )
        title_label.grid(row=0, column=0, pady=(50, 20), sticky='we')
        
        # sub-judul
        subtitle_label = ctk.CTkLabel(
            login_frame, text='Masuk ke akun Anda',
            font=ctk.CTkFont(size=14, family='Arial', weight='normal')
            )
        subtitle_label.grid(row=1, column=0, pady=(0, 80), sticky='ew')

        # label error username kosong
        self.username_error_label = ctk.CTkLabel(
            username_frame,
            text='username harus diisi',
            font=ctk.CTkFont(size=10, family='Poppins'),
            text_color='#FF0000'
            )
        self.username_error_label.grid(row=0, column=0, columnspan=2, sticky='w')

        # label error login gagal
        self.error_label = ctk.CTkLabel(
            username_frame,
            text='username atau password salah',
            font=ctk.CTkFont(size=10, family='Calibri'),
            text_color='#FF0000'
            )
        self.error_label.grid(row=0, column=0, columnspan=2, sticky='w')

        # input username
        self.username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text='Masukkan Username',
            width=300, height=40, corner_radius=8,
            font=ctk.CTkFont(size=14, family='Poppins')
            )
        self.username_entry.grid(row=0, column=0, columnspan=2)
        
        # validasi username setiap perubahan
        self.username_entry.bind('<FocusOut>', self.username_null)
        self.username_entry.bind('<KeyRelease>', self.username_null)

        # input password
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text='Masukkan Password',
            width=300, height=40, corner_radius=8,
            font=ctk.CTkFont(size=14, family='Poppins'),
            show='•'
            )
        self.password_entry.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        self.hidden_var = ctk.BooleanVar(value=False)
        self.password_hid = ctk.CTkCheckBox(
            password_frame,
            border_width=1, width=1, height=1,
            text='Perlihatkan password',
            font=ctk.CTkFont(size=11, family='Poppins'),
            variable=self.hidden_var,
            onvalue=True, offvalue=False,
            command=self.hidden_password
        )
        self.password_hid.grid(
            row=1, column=0, columnspan=2,
            pady=(2, 2), sticky='w'
            )

        # tombol login
        self.login_button = ctk.CTkButton(
            button_frame, text='Login',
            width=300, height=40,
            font=ctk.CTkFont(size=14, family='Poppins'),
            command=self.login_button, corner_radius=10
            )
        self.login_button.grid(row=0, column=0, columnspan=2)

        # link ke register page
        self.link_register = ctk.CTkLabel(
            button_frame,
            text='Belum punya akun? Daftar',
            font=ctk.CTkFont(size=10, family='Calibri', underline=True),
            text_color='#0D5BC0'
            )
        self.link_register.grid(row=1, column=0, sticky='e')
        self.link_register.bind('<Button-1>', self.register_link)

    def hidden_password(self):
        if self.hidden_var.get():
            self.password_entry.configure(show='')

        else:
            self.password_entry.configure(show='•')

    def register_link(self, event=None):
        # pindah ke halaman register
        self.controller.show_frame(register.RegisterPage)

    def login_button(self):
        # ambil username & password dari input
        self.username = self.username_entry.get()
        password = self.password_entry.get()

        # cek data user dari database
        c.execute(
            "select password from users_accounts_data where username = ?",
            (self.username,)
        )
        result = c.fetchone()

        # jika username tidak kosong
        if self.username != "":
            # jika username dan password benar
            if result:
                hashed_password = result[0]

                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    self.controller.open_homepage(username=self.username)

                # jika salah
                else:
                    self.error_label.grid_configure(row=1)

            else:
                CTkMessagebox(
                    title='Error',
                    message='Akun tidak ditemukan!',
                    icon='warning'
                    )

        # jika tidak diisi
        else:
            self.username_error_label.grid_configure(row=1)

    def username_null(self, event=None):
        # cek jika input username kosong
        username = self.username_entry.get()

        if username == "":
            self.username_error_label.grid_configure(row=1)
        else:
            self.username_error_label.grid_configure(row=0)


if __name__ == "__main__":
    root = LoginPage()
    root.mainloop()