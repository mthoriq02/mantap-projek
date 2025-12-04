from customtkinter import CTk, CTkFrame, CTkButton, CTkFont, CTkLabel, CTkEntry, set_appearance_mode, set_default_color_theme
from database import c, conn
from sqlite3 import IntegrityError
from CTkMessagebox import CTkMessagebox

# buat tabel user jika belum ada
c.execute(
    "create table if not exists users_accounts_data (username text unique not null, password text not null)" 
)

# set tema aplikasi
set_appearance_mode('dark')
set_default_color_theme('dark-blue')

class App(CTk):
    def __init__(self):
        super().__init__()

        # set judul dan ukuran utama aplikasi
        self.title('App')
        self.geometry('1000x700')

        # buat container untuk menampung halaman login & register
        self.container = CTkFrame(self)
        self.container.pack(fill='both', expand=True)

        # konfigurasi grid container
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # dictionary untuk menyimpan halaman
        self.frames = {}
        self.frame_list = [LoginPage, RegisterPage]
        
        # buat dan tampilkan semua halaman, tetapi hanya raise yang aktif
        for F in self.frame_list:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
            
        # tampilkan halaman login pertama kali
        self.show_frame(LoginPage)

    def show_frame(self, page):
        # tampilkan halaman tertentu dengan tkraise
        frame = self.frames[page]
        frame.tkraise()

class LoginPage(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1000, height=700)
        self.controller = controller

        # konfigurasi layout utama halaman login
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # frame utama login
        login_frame = CTkFrame(self, width=400, height=500)
        login_frame.grid(
            row=0,
            column=0,
            padx=(50, 50),
            pady=(100, 100)
            )
        login_frame.grid_propagate(False)
        login_frame.grid_columnconfigure(0, weight=1)

        # frame username dan password
        username_frame = CTkFrame(
            login_frame,
            fg_color='transparent'
            )
        username_frame.grid(
            row=1,
            column=0,
            pady=(0, 20)
            )

        password_frame = CTkFrame(
            login_frame,
            fg_color='transparent'
            )
        password_frame.grid(
            row=2,
            column=0,
            pady=(0, 20)
            )

        # frame tombol
        button_frame = CTkFrame(
            login_frame,
            fg_color='transparent'
            )
        button_frame.grid(
            row=3,
            column=0
            )

        # label judul login
        title_label = CTkLabel(
            login_frame,
            text='Login',
            font=CTkFont(size=26, family='Poppins', weight='bold')
        )
        title_label.grid(
            row=0,
            column=0,
            pady=(50, 90),
            sticky='we'
            )

        # label error username kosong
        self.username_error_label = CTkLabel(
            username_frame,
            text='username harus diisi',
            font=CTkFont(size=10, family='Poppins'),
            text_color='#FF0000'
        )
        self.username_error_label.grid(
            row=0,
            column=0, 
            columnspan=2,
            sticky='w'
            )

        # label error login gagal
        self.error_label = CTkLabel(
            username_frame,
            text='username atau password salah',
            font=CTkFont(size=10, family='Calibri'),
            text_color='#FF0000'
        )
        self.error_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky='w'
            )

        # input username
        self.username_entry = CTkEntry(
            username_frame,
            placeholder_text='Masukkan Username',
            width=300, height=40,
            font=CTkFont(size=14, family='Poppins')
        )
        self.username_entry.grid(
            row=0,
            column=0,
            columnspan=2
            )
        
        # validasi username setiap perubahan
        self.username_entry.bind('<FocusOut>', self.username_null)
        self.username_entry.bind('<KeyRelease>', self.username_null)

        # input password
        self.password_entry = CTkEntry(
            password_frame,
            placeholder_text='Masukkan Password',
            width=300, height=40,
            font=CTkFont(size=14, family='Poppins')
        )
        self.password_entry.grid(
            row=0,
            column=0,
            columnspan=2
            )

        # tombol login
        self.login_button = CTkButton(
            button_frame,
            text='Login',
            width=300, height=40,
            font=CTkFont(size=14, family='Poppins'),
            command=self.login_button
        )
        self.login_button.grid(
            row=0,
            column=0,
            columnspan=2
            )

        # link ke register page
        self.link_register = CTkLabel(
            button_frame,
            text='Belum punya akun? Daftar',
            font=CTkFont(size=10, family='Calibri', underline=True),
            text_color='#0D5BC0'
        )
        self.link_register.grid(
            row=1,
            column=0,
            sticky='e'
            )
        self.link_register.bind('<Button-1>', self.register_link)

    def register_link(self, event=None):
        # pindah ke halaman register
        self.controller.show_frame(RegisterPage)

    def login_button(self):
        # ambil username & password dari input
        username = self.username_entry.get()
        password = self.password_entry.get()

        # cek data user dari database
        c.execute(
            "select * from users_accounts_data where username = ? and password = ?",
            (username, password)
        )
        result = c.fetchone()

        # jika username tidak kosong
        if username != "":
            # jika username dan password benar
            if result:
                print('halo')

            # jika salah
            else:
                self.error_label.grid_configure(row=1)

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

class RegisterPage(CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1000, height=700)
        self.controller = controller

        # konfigurasi layout utama register
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # frame utama register
        register_frame = CTkFrame(
            self, 
            width=400,
            height=500
            )
        register_frame.grid(
            row=0,
            column=0,
            padx=50,
            pady=50
            )
        register_frame.grid_propagate(False)
        register_frame.grid_columnconfigure(0, weight=1)
        
        # judul register
        title_label = CTkLabel(
            register_frame,
            text="Sign-Up",
            font=CTkFont(size=26, weight='bold', family='Poppins')
        )
        title_label.grid(
            row=0,
            column=0,
            columnspan=2,
            pady=(50, 90),
            sticky='we'
            )

        # frame input username
        username_frame = CTkFrame(register_frame, fg_color='transparent')
        username_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            pady=(0, 20)
            )

        # frame input password
        password_frame = CTkFrame(
            register_frame,
            fg_color='transparent'
            )
        password_frame.grid(
            row=2,
            column=0, 
            columnspan=2
            )

        # frame tombol
        button_frame = CTkFrame(
            register_frame,
            fg_color='transparent'
            )
        button_frame.grid(
            row=3,
            column=0,
            columnspan=2
            )

        # info username kosong
        self.username_info_label = CTkLabel(
            username_frame,
            text='*username tidak boleh kosong',
            font=CTkFont(size=10, family='Calibri'),
            text_color='#FF0000'
        )
        self.username_info_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky='w'
            )

        # input username
        self.username_entry = CTkEntry(
            username_frame,
            placeholder_text='Username',
            width=300, height=40,
            font=CTkFont(size=14, family='Poppins')
        )
        self.username_entry.grid(
            row=0,
            column=0,
            columnspan=2
            )
        self.username_entry.bind('<FocusOut>', self.username_validate)
        self.username_entry.bind('<KeyRelease>', self.username_validate)

        # input password
        self.password_entry = CTkEntry(
            password_frame,
            placeholder_text='Password',
            width=300, height=40,
            font=CTkFont(size=14, family='Poppins')
        )
        self.password_entry.grid(
            row=0,
            column=0,
            columnspan=2
            )
        self.password_entry.bind('<KeyRelease>', self.password_validate)
        self.password_entry.bind('<FocusOut>', self.password_validate)
        self.password_entry.bind('<KeyRelease>', self.password_check_validate)
        self.password_entry.bind('<FocusOut>', self.password_check_validate)

        # info validasi password
        self.password_info_label = CTkLabel(
            password_frame,
            text='*password setidaknya harus 8 karakter',
            font=CTkFont(size=10, family='Calibri'),
            text_color="#8F8383"
        )
        self.password_info_label.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky='w'
            )

        # input konfirmasi password
        self.password_check = CTkEntry(
            password_frame,
            placeholder_text='Masukkan ulang password',
            width=300, height=40,
            font=CTkFont(size=14, family='Poppins')
        )
        self.password_check.grid(
            row=2,
            column=0,
            columnspan=2
            )
        self.password_check.bind('<KeyRelease>', self.password_check_validate)
        self.password_check.bind('<FocusOut>', self.password_check_validate)

        # info konfirmasi password
        self.password_check_info_label = CTkLabel(
            password_frame,
            text='*masukkan ulang password',
            font=CTkFont(size=10, family='Calibri'),
            text_color='#8F8383'
        )
        self.password_check_info_label.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky='w'
            )

        # tombol daftar
        self.button_register = CTkButton(
            button_frame,
            text='Sign-Up',
            width=300, height=40,
            font=CTkFont(size=16, family='Poppins'),
            command=self.register_button
        )
        self.button_register.grid(row=0, column=0, columnspan=2)

        # link ke login
        self.login_link = CTkLabel(
            button_frame,
            text='Sudah punya akun? Login',
            text_color='#0D5BC0',
            font=CTkFont(size=10, family='Calibri', underline=True)
        )
        self.login_link.grid(
            row=1,
            column=0,
            sticky='e'
            )
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
            # simpan user baru ke database
            c.execute(
                "insert into users_accounts_data values (?, ?)",
                (username, password)
            )
            conn.commit()

            # tampilkan pesan sukses
            CTkMessagebox(
                title='Sukses',
                message='Pendaftaran berhasil',
                icon='check'
            )

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
            
app = App()
app.mainloop()
