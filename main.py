import customtkinter as ctk
import os
import bcrypt
import tkinter as tk
from database import c, conn
from sqlite3 import IntegrityError
from CTkMessagebox import CTkMessagebox
from PIL import Image
from tkinter import messagebox
from open_excel import all_data
from datetime import datetime

# buat tabel user jika belum ada
c.execute(
    "create table if not exists users_accounts_data (username text unique not null, password text not null)" 
)

# set tema aplikasi
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # set judul dan ukuran utama aplikasi
        self.title('Guardian')
        self.geometry('1000x700')
        self.iconbitmap('logo.ico')

        # buat container untuk menampung halaman login & register
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill='both', expand=True)

        # konfigurasi grid container
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # dictionary untuk menyimpan halaman
        self.frames = {}
        self.frame_list = [LoginPage, RegisterPage, WeaponShowcaseApp]
        
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

    def open_window_payment(self, caller, cart_items, cart_total, format_price_func, weapons_data):
        payment = PaymentWindow(
            parent=self.container,
            controller=self,
            caller=caller,
            cart_items=cart_items,
            cart_total=cart_total,
            format_price_func=format_price_func,
            weapons_data=weapons_data
        )
        payment.grid(row=0, column=0, sticky="nsew")
        payment.tkraise()

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1000, height=700, bg_color='#1e1e1e')
        self.controller = controller

        # konfigurasi layout utama halaman login
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # frame utama login
        login_frame = ctk.CTkFrame(
            self, width=380,
            height=500,
            corner_radius=12
            )
        login_frame.grid(
            row=0,
            column=0,
            padx=(50, 50),
            pady=(80, 10)
            )
        login_frame.grid_propagate(False)
        login_frame.grid_columnconfigure(0, weight=1)

        # frame username dan password
        username_frame = ctk.CTkFrame(
            login_frame,
            fg_color='transparent'
            )
        username_frame.grid(
            row=2,
            column=0,
            pady=(0, 20)
            )

        password_frame = ctk.CTkFrame(
            login_frame,
            fg_color='transparent'
            )
        password_frame.grid(
            row=3,
            column=0,
            pady=(0, 20)
            )

        # frame tombol
        button_frame = ctk.CTkFrame(
            login_frame,
            fg_color='transparent'
            )
        button_frame.grid(
            row=4,
            column=0
            )
        
        # label judul login
        title_label = ctk.CTkLabel(
            login_frame,
            text='Login',
            font=ctk.CTkFont(size=26, family='Poppins', weight='bold')
        )
        title_label.grid(
            row=0,
            column=0,
            pady=(50, 20),
            sticky='we'
            )
        
        # sub-judul
        subtitle_label = ctk.CTkLabel(
            login_frame,
            text='Masuk ke akun Anda',
            font=ctk.CTkFont(
                size=14,
                family='Arial',
                weight='normal'
            )
        )
        subtitle_label.grid(
            row=1,
            column=0,
            pady=(0, 80),
            sticky='ew'
        )

        # label error username kosong
        self.username_error_label = ctk.CTkLabel(
            username_frame,
            text='username harus diisi',
            font=ctk.CTkFont(size=10, family='Poppins'),
            text_color='#FF0000'
        )
        self.username_error_label.grid(
            row=0,
            column=0, 
            columnspan=2,
            sticky='w'
            )

        # label error login gagal
        self.error_label = ctk.CTkLabel(
            username_frame,
            text='username atau password salah',
            font=ctk.CTkFont(size=10, family='Calibri'),
            text_color='#FF0000'
        )
        self.error_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky='w'
            )

        # input username
        self.username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text='Masukkan Username',
            width=300, height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14, family='Poppins')
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
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text='Masukkan Password',
            width=300,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14, family='Poppins'),
            show='•'
        )
        self.password_entry.grid(
            row=0,
            column=0,
            columnspan=2,
            pady=(0, 5)
            )
        self.hidden_var = ctk.BooleanVar(value=False)
        self.password_hid = ctk.CTkCheckBox(
            password_frame,
            border_width=1,
            width=1,
            height=1,
            text='Perlihatkan password',
            font=ctk.CTkFont(size=11, family='Poppins'),
            variable=self.hidden_var,
            onvalue=True,
            offvalue=False,
            command=self.hidden_password
        )
        self.password_hid.grid(
            row=1,
            column=0,
            columnspan=2,
            pady=(2, 2),
            sticky='w'
        )

        # tombol login
        self.login_button = ctk.CTkButton(
            button_frame,
            text='Login',
            width=300, height=40,
            font=ctk.CTkFont(size=14, family='Poppins'),
            command=self.login_button,
            corner_radius=10
        )
        self.login_button.grid(
            row=0,
            column=0,
            columnspan=2
            )

        # link ke register page
        self.link_register = ctk.CTkLabel(
            button_frame,
            text='Belum punya akun? Daftar',
            font=ctk.CTkFont(size=10, family='Calibri', underline=True),
            text_color='#0D5BC0'
        )
        self.link_register.grid(
            row=1,
            column=0,
            sticky='e'
            )
        self.link_register.bind('<Button-1>', self.register_link)

    def hidden_password(self):
        if self.hidden_var.get():
            self.password_entry.configure(show='')

        else:
            self.password_entry.configure(show='•')

    def register_link(self, event=None):
        # pindah ke halaman register
        self.controller.show_frame(RegisterPage)

    def login_button(self):
        # ambil username & password dari input
        username = self.username_entry.get()
        password = self.password_entry.get()

        # cek data user dari database
        c.execute(
            "select password from users_accounts_data where username = ?",
            (username,)
        )
        result = c.fetchone()

        # jika username tidak kosong
        if username != "":
            # jika username dan password benar
            if result:
                hashed_password = result[0]

                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    self.controller.show_frame(WeaponShowcaseApp)

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

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1000, height=700, bg_color='#1e1e1e')
        self.controller = controller

        # konfigurasi layout utama register
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # frame utama register
        register_frame = ctk.CTkFrame(
            self, 
            width=400,
            height=500,
            corner_radius=12
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
        title_label = ctk.CTkLabel(
            register_frame,
            text="Sign-Up",
            font=ctk.CTkFont(size=26, weight='bold', family='Poppins')
        )
        title_label.grid(
            row=0,
            column=0,
            columnspan=2,
            pady=(50, 20),
            sticky='we'
        )
        subtitle_label = ctk.CTkLabel(
            register_frame,
            text='Silahkan isi data untuk membuat akun',
            font=ctk.CTkFont(
                size=14,
                family='Arial',
                weight='normal'
            )
        )
        subtitle_label.grid(
            row=1,
            column=0,
            pady=(0, 60),
            sticky='ew'
        )

        # frame input username
        username_frame = ctk.CTkFrame(register_frame, fg_color='transparent')
        username_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            pady=(0, 20)
            )

        # frame input password
        password_frame = ctk.CTkFrame(
            register_frame,
            fg_color='transparent'
            )
        password_frame.grid(
            row=3,
            column=0, 
            columnspan=2
            )

        # frame tombol
        button_frame = ctk.CTkFrame(
            register_frame,
            fg_color='transparent'
            )
        button_frame.grid(
            row=4,
            column=0,
            columnspan=2
            )

        # info username kosong
        self.username_info_label = ctk.CTkLabel(
            username_frame,
            text='*username tidak boleh kosong',
            font=ctk.CTkFont(size=10, family='Calibri'),
            text_color='#FF0000'
        )
        self.username_info_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky='w'
            )

        # input username
        self.username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text='Username',
            width=300, height=40,
            font=ctk.CTkFont(size=14, family='Poppins'),
            corner_radius=8
        )
        self.username_entry.grid(
            row=0,
            column=0,
            columnspan=2
            )
        self.username_entry.bind('<FocusOut>', self.username_validate)
        self.username_entry.bind('<KeyRelease>', self.username_validate)

        # input password
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text='Password',
            width=300, height=40,
            font=ctk.CTkFont(size=14, family='Poppins'),
            corner_radius=8
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
        self.password_info_label = ctk.CTkLabel(
            password_frame,
            text='*password setidaknya harus 8 karakter',
            font=ctk.CTkFont(size=10, family='Calibri'),
            text_color="#8F8383"
        )
        self.password_info_label.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky='w'
            )

        # input konfirmasi password
        self.password_check = ctk.CTkEntry(
            password_frame,
            placeholder_text='Masukkan ulang password',
            width=300, height=40,
            font=ctk.CTkFont(size=14, family='Poppins'),
            corner_radius=8
        )
        self.password_check.grid(
            row=2,
            column=0,
            columnspan=2
            )
        self.password_check.bind('<KeyRelease>', self.password_check_validate)
        self.password_check.bind('<FocusOut>', self.password_check_validate)

        # info konfirmasi password
        self.password_check_info_label = ctk.CTkLabel(
            password_frame,
            text='*masukkan ulang password',
            font=ctk.CTkFont(size=10, family='Calibri'),
            text_color='#8F8383'
        )
        self.password_check_info_label.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky='w'
            )

        # tombol daftar
        self.button_register = ctk.CTkButton(
            button_frame,
            text='Sign-Up',
            width=300, height=40,
            font=ctk.CTkFont(size=16, family='Poppins'),
            command=self.register_button,
            corner_radius=10
        )
        self.button_register.grid(row=0, column=0, columnspan=2)

        # link ke login
        self.login_link = ctk.CTkLabel(
            button_frame,
            text='Sudah punya akun? Login',
            text_color='#0D5BC0',
            font=ctk.CTkFont(size=10, family='Calibri', underline=True)
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

class WeaponShowcaseApp(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=1000, height=700)

        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Etalase Scrollable
        self.grid_rowconfigure(2, weight=0) # Footer

        # DATA PRODUK SENJATA
        self.weapons = all_data

        # STATE KERANJANG BELANJA & CHAT
        # PERUBAHAN KRITIS: Menggunakan dictionary untuk melacak kuantitas
        self.cart_items = {} 
        self.cart_total = 0
        self.chat_open = False 

        # --- MEMUAT LOGO BARU DARI FILE ---
        LOGO_PATH = os.path.join(os.getcwd(), "logo.png")
        LOGO_SIZE = (50, 50)

        self.logo_found = False
        try:
            logo_image_pil = Image.open(LOGO_PATH)
            logo_resized = logo_image_pil.resize(LOGO_SIZE, Image.Resampling.LANCZOS)
            self.app_logo = ctk.CTkImage(light_image=logo_resized, dark_image=logo_resized, size=LOGO_SIZE)
            self.logo_found = True
        except FileNotFoundError:
            print(f"Peringatan: File logo '{LOGO_PATH}' tidak ditemukan. Menggunakan teks fallback.")
        except Exception as e:
            print(f"Peringatan: Gagal memuat/mengubah ukuran logo: {e}. Menggunakan teks fallback.")

        # --- HEADER APLIKASI (Judul & Search Bar) - Row 0 ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent") 
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)

        title_logo_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_logo_frame.grid(row=0, column=0, sticky="w")

        title_logo_frame.grid_columnconfigure(0, weight=0)
        title_logo_frame.grid_columnconfigure(1, weight=1)

        if self.logo_found:
            logo_label = ctk.CTkLabel(title_logo_frame, image=self.app_logo, text="")
            logo_label.grid(row=0, column=0, padx=(0, 10), pady=(0, 0), sticky="w")
        
        self.title_label = ctk.CTkLabel(title_logo_frame, 
                                          text=" THE GUN ADDICTION ",
                                          font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=1, pady=(10, 5), sticky="w") 

        self.search_bar = ctk.CTkEntry(self.header_frame,
                                         placeholder_text="🔍 Cari nama senjata...",
                                         width=400,
                                         height=40,
                                         corner_radius=20,
                                         font=ctk.CTkFont(size=16))
        self.search_bar.grid(row=0, column=1, padx=(10, 0), pady=(0, 10), sticky="e") 
        self.search_bar.bind("<KeyRelease>", self.filter_weapons)
        
        # --- KONTEN ETALASE (Scrollable) - Row 1 ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Koleksi Senjata", width=950)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        for i in range(3):
            self.scrollable_frame.grid_columnconfigure(i, weight=1, minsize=300)
            
        # --- FOOTER APLIKASI (WIDGET CHAT & KERANJANG) - Row 2 ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="gray15", height=70, corner_radius=0)
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0) 
        
        self.footer_frame.grid_columnconfigure(0, weight=1) 
        self.footer_frame.grid_columnconfigure(1, weight=0) 
        self.footer_frame.grid_columnconfigure(2, weight=0) 

        # 1. ICON CUSTOMER SERVICE CHAT
        self.chat_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.chat_frame.grid(row=0, column=1, padx=(20, 10), pady=10, sticky="e") 
        
        self.chat_icon = ctk.CTkLabel(self.chat_frame, 
            text="💬", width=50, height=50, corner_radius=10,
            fg_color="gray20", font=ctk.CTkFont(size=30), cursor="hand2") 
        self.chat_icon.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.chat_icon.bind("<Button-1>", self.open_chat_window)
        
        chat_label = ctk.CTkLabel(self.chat_frame, 
                                  text="Layanan\nChat", 
                                  font=ctk.CTkFont(size=12))
        chat_label.grid(row=0, column=1, sticky="w")
        
        # 2. FRAME DETAIL KERANJANG 
        self.cart_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.cart_frame.grid(row=0, column=2, padx=(10, 20), pady=10, sticky="e") 
        self.cart_frame.grid_columnconfigure(1, weight=1) 

        self.cart_interactive_icon = ctk.CTkLabel(self.cart_frame, 
            text="🛒", width=50, height=50, corner_radius=10,
            fg_color="gray20", font=ctk.CTkFont(size=30), cursor="hand2") 
        self.cart_interactive_icon.grid(row=0, column=0, rowspan=1, padx=(0, 10), sticky="nsew")
        self.cart_interactive_icon.bind("<Button-1>", self.open_checkout_window)

        detail_frame = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
        detail_frame.grid(row=0, column=1, padx=0, pady=0, sticky="w") 

        self.cart_count_label = ctk.CTkLabel(detail_frame, 
                                             text="(0 item)", 
                                             font=ctk.CTkFont(size=14, weight="bold"))
        self.cart_count_label.grid(row=0, column=0, sticky="w", pady=(15, 15)) 
        
        self.display_weapons()

    # --- HELPER FUNCTIONS ---
    
    def open_chat_window(self, event=None):
        chat_window = ShoppingChatBot(master=self)
        
    def _parse_price(self, price_str):
        price_str = str(price_str)
        try:
            clean_str = price_str.replace("Rp ", "").replace(".", "")
            return int(clean_str)
        except Exception as e:
            print(f"Error parsing price string: {price_str}. Error: {e}")
            return 0

    def _format_price(self, price_int):
        return f"Rp {price_int:,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
    
    # Fungsi Helper Baru untuk mencari data senjata
    def get_weapon_data_by_name(self, name):
        """Mencari data senjata lengkap berdasarkan Nama Senjata."""
        for weapon in self.weapons:
            if weapon['Nama Senjata'] == name:
                return weapon
        return None

    # PERUBAHAN: Logika update display untuk dictionary
    def update_cart_display(self):
        self.cart_total = 0
        item_count = 0
        
        for item_data in self.cart_items.values():
            self.cart_total += item_data.get('total_price', 0)
            item_count += item_data.get('quantity', 0)
            
        self.cart_count_label.configure(text=f"({item_count} item)")
        
        if item_count > 0:
            self.cart_interactive_icon.configure(fg_color="#006400") # Green when full
        else:
            self.cart_interactive_icon.configure(fg_color="gray20")

    # PERUBAHAN: Logika reset cart untuk dictionary
    def reset_cart(self):
        self.cart_items = {}
        self.cart_total = 0
        self.update_cart_display()

    # PERUBAHAN: Memanggil PaymentWindow dan mengirim data senjata
    def open_checkout_window(self, event=None):
        self.controller.open_window_payment(
            caller=self,
            cart_items=self.cart_items, # Data keranjang
            cart_total=self.cart_total, # Total harga
            format_price_func=self._format_price,
            weapons_data=self.weapons # Mengirim data senjata lengkap
        )

    # PERUBAHAN: Logika buy_weapon untuk dictionary
    def buy_weapon(self, weapon_data):
        weapon_name = weapon_data['Nama Senjata']
        parsed_price = self._parse_price(weapon_data['Harga'])
        
        if weapon_name in self.cart_items:
            self.cart_items[weapon_name]['quantity'] += 1
            self.cart_items[weapon_name]['total_price'] += parsed_price
        else:
            self.cart_items[weapon_name] = {
                'price_per_unit': parsed_price,
                'quantity': 1,
                'total_price': parsed_price
            }
        
        self.update_cart_display()
        print(f"'{weapon_name}' berhasil ditambahkan ke keranjang.")

    # PERUBAHAN: Logika remove_weapon untuk dictionary
    def remove_weapon(self, weapon_data):
        weapon_name = weapon_data['Nama Senjata']
        
        if weapon_name not in self.cart_items:
            messagebox.showinfo("Informasi", f"'{weapon_name}' tidak ada di keranjang.")
            print(f"Gagal mengurangi: '{weapon_name}' tidak ada di keranjang.")
            return

        parsed_price = self.cart_items[weapon_name]['price_per_unit']
        
        if self.cart_items[weapon_name]['quantity'] > 1:
            self.cart_items[weapon_name]['quantity'] -= 1
            self.cart_items[weapon_name]['total_price'] -= parsed_price
            print(f"Satu unit '{weapon_name}' berhasil dikurangi dari keranjang.")
        else:
            # Hapus item jika kuantitasnya menjadi 0
            del self.cart_items[weapon_name]
            print(f"'{weapon_name}' dihapus dari keranjang.")
            
        self.update_cart_display()

    # LOGIKA ETALASE
    def clear_scrollable_frame(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def filter_weapons(self, event=None):
        search_query = self.search_bar.get().lower()
        
        if not search_query:
            self.display_weapons(self.weapons)
            return

        filtered = [
            weapon for weapon in self.weapons 
            if search_query in weapon['Nama Senjata'].lower()
        ]
        
        self.display_weapons(filtered)
        
    def display_weapons(self, weapons_to_display=None):
        self.clear_scrollable_frame() 

        weapons_data = weapons_to_display if weapons_to_display is not None else self.weapons

        if not weapons_data:
            no_results_label = ctk.CTkLabel(self.scrollable_frame,
                                            text="Tidak ada senjata yang cocok dengan kueri pencarian.",
                                            font=ctk.CTkFont(size=18, weight="bold"),
                                            text_color="gray")
            no_results_label.grid(row=0, column=0, columnspan=3, padx=20, pady=50)
            return

        row = 0
        col = 0
        max_cols = 3 

        for weapon in weapons_data:
            self.create_weapon_item(self.scrollable_frame, weapon, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_weapon_item(self, parent_frame, weapon_data, row, col):
        """Membuat widget untuk satu item produk senjata."""

        item_frame = ctk.CTkFrame(parent_frame, corner_radius=10, border_width=2)
        item_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        item_frame.grid_columnconfigure(0, weight=1)

        # Menambahkan Gambar Produk
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, 'picture_resource', weapon_data['Gambar'])
        image_size = (250, 150) 

        try:
            original_image = Image.open(image_path)
            resized_image = original_image.resize(image_size, Image.Resampling.LANCZOS)
            weapon_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=image_size)

            image_label = ctk.CTkLabel(item_frame, image=weapon_image, text="")
            image_label.grid(row=0, column=0, padx=10, pady=(10, 5))
            
        except FileNotFoundError:
            no_image_label = ctk.CTkLabel(item_frame, 
                                          text=f"File gambar: '{weapon_data['Gambar']}'\nTIDAK DITEMUKAN!",
                                          text_color="red",
                                          font=ctk.CTkFont(size=14, slant="italic"))
            no_image_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        except Exception as e:
            error_label = ctk.CTkLabel(item_frame, text=f"Error memuat gambar: {e}", text_color="red")
            error_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")

        # Detail Produk
        name_label = ctk.CTkLabel(item_frame,
                                  text=weapon_data['Nama Senjata'],
                                  font=ctk.CTkFont(size=18, weight="bold"))
        name_label.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="w")

        price_label = ctk.CTkLabel(item_frame,
                                   text=weapon_data['Harga'],
                                   text_color="#00FF7F", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        price_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        desc_label = ctk.CTkLabel(item_frame,
                                  text=weapon_data['Deskripsi'],
                                  wraplength=280,
                                  justify="left")
        desc_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        action_button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        action_button_frame.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="ew")
        action_button_frame.grid_columnconfigure((0, 1), weight=1) 
        
        remove_button = ctk.CTkButton(action_button_frame,
                                      text="➖ Kurangi",
                                      fg_color="red",
                                      hover_color="#8B0000",
                                      command=lambda data=weapon_data: self.remove_weapon(data))
        remove_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        buy_button = ctk.CTkButton(action_button_frame,
                                   text="➕ Tambah",
                                   command=lambda data=weapon_data: self.buy_weapon(data))
        buy_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

class PaymentWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, caller, cart_items, cart_total, format_price_func, weapons_data):
        super().__init__(parent, width=1000, height=700)
        
        self.controller = controller
        self.master_app = caller
        self.cart_total = cart_total
        self.format_price = format_price_func
        self.weapons_data = weapons_data 
        self.selected_payment_method = tk.StringVar(value="") 
        
        # Tambahan: Menyimpan mapping Nama -> Path Gambar/Data
        self.weapon_data_map = {item['Nama Senjata']: item for item in weapons_data}
        self.image_references = {} # Untuk mencegah garbage collection gambar
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # MODIFIKASI: STATE BARU UNTUK SELEKSI ITEM CHECKOUT
        # Menggunakan dictionary untuk melacak status terpilih (tk.BooleanVar) per nama item
        self.selected_items_state = {} 
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Baris utama untuk konten

        self.payment_methods = {
            "Transfer Bank": ["BCA", "Mandiri", "BNI", "BRI"],
            "Kartu Kredit": ["Visa", "MasterCard"],
            "E-Wallet": ["Gopay", "OVO", "ShopeePay", "Dana"],
            "COD": ["Cash on Delivery (Area Terbatas)"]
        }
        
        self.create_widgets()
        self.refresh_display()

    def create_widgets(self):
        # Header
        title_label = ctk.CTkLabel(self,
                                   text="jangan lupa bayar yaa!💳",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")

        # Scrollable Frame untuk Detail Keranjang & Pilihan Pembayaran
        self.main_content_frame = ctk.CTkScrollableFrame(self, 
                                                     label_text="Detail Transaksi", 
                                                     fg_color="gray15")
        self.main_content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew") 
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # Footer Summary
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.summary_frame.grid_columnconfigure(1, weight=1)

        total_label = ctk.CTkLabel(self.summary_frame,
                                   text="TOTAL AKHIR:",
                                   font=ctk.CTkFont(size=20, weight="bold"))
        total_label.grid(row=0, column=0, sticky="w", padx=10)

        self.total_amount_label = ctk.CTkLabel(self.summary_frame,
                                               text="", 
                                               text_color="#00FF7F",
                                               font=ctk.CTkFont(size=24, weight="bold"))
        self.total_amount_label.grid(row=0, column=1, sticky="e", padx=10)
        
        # Action Buttons
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)

        back_button = ctk.CTkButton(action_frame,
                                    text="⬅️ Kembali ke Etalase",
                                    command=lambda: self.controller.show_frame(
                                        WeaponShowcaseApp
                                        ),
                                    fg_color="red")
        back_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        checkout_button = ctk.CTkButton(action_frame,
                                        text="💳 Lakukan Pembayaran",
                                        fg_color="#00FF7F",
                                        hover_color="#00B359",
                                        text_color="#000000",
                                        command=self.process_payment)
        checkout_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def refresh_display(self):
        """Memuat ulang semua konten keranjang dan total harga."""
        
        # PERBAIKAN VITAL: Selalu ambil data keranjang terbaru dari aplikasi utama
        self.cart_items = self.master_app.cart_items

        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        self.create_cart_detail_section(self.main_content_frame)

        separator = ctk.CTkFrame(self.main_content_frame, height=2, fg_color="gray30")
        separator.pack(fill="x", padx=10, pady=15)

        self.create_payment_selection_section(self.main_content_frame)

        # NOTE: self.cart_total diupdate di update_checkout_total, bukan diambil dari master_app.
        # self.cart_total = self.master_app.cart_total # DIHAPUS
        # self.total_amount_label.configure(text=self.format_price(self.cart_total)) # DIHAPUS
        
        if not self.selected_payment_method.get() and self.cart_total > 0:
            self.selected_payment_method.set(self.payment_methods["Transfer Bank"][0])

    # FUNGSI BARU: Menghitung ulang total berdasarkan Checkbox yang dipilih
    def update_checkout_total(self):
        """Menghitung ulang total pembayaran hanya berdasarkan item yang terpilih."""
        
        new_total = 0
        
        # Iterasi melalui state pilihan, bukan hanya self.cart_items
        for item_name, is_selected_var in self.selected_items_state.items():
            # Cek apakah item ini masih ada di keranjang
            if item_name in self.cart_items:
                # Cek apakah checkbox-nya terpilih
                if is_selected_var.get():
                    # Tambahkan total harga item ke new_total
                    new_total += self.cart_items[item_name]['total_price']
        
        # Perbarui tampilan label total
        self.total_amount_label.configure(text=self.format_price(new_total))
        # Simpan total baru ini ke self.cart_total (penting untuk process_payment)
        self.cart_total = new_total

    def create_cart_detail_section(self, parent_frame):
        """Membuat bagian detail keranjang dengan tombol tambah/kurang, gambar, dan CHECKBOX."""
        
        item_container_frame = ctk.CTkFrame(parent_frame, fg_color="gray25", corner_radius=10)
        item_container_frame.pack(fill="x", padx=10, pady=(10, 5))

        header_label = ctk.CTkLabel(item_container_frame, 
                                    # MODIFIKASI TEXT
                                    text="list isi keranjang kamu 😌: (Pilih item untuk Checkout)", 
                                    font=ctk.CTkFont(size=16, weight="bold"))
        header_label.pack(anchor="w", padx=15, pady=(10, 5))

        # Menggunakan self.cart_items yang sudah diperbarui di refresh_display
        if not self.cart_items:
            no_item_label = ctk.CTkLabel(item_container_frame, text="Keranjang kosong. Tidak ada yang bisa di-checkout.", text_color="gray")
            no_item_label.pack(padx=15, pady=20)
            self.update_checkout_total() # Panggil update_checkout_total untuk memastikan total 0
            return

        # Reset references
        self.image_references.clear()
        
        # MODIFIKASI: Inisialisasi/Cleanup state seleksi
        # Buat salinan kunci state saat ini
        items_to_remove_from_state = list(self.selected_items_state.keys()) 
        
        for name in self.cart_items.keys():
            if name not in self.selected_items_state:
                 # Jika ada item baru, inisialisasi sebagai terpilih (True)
                self.selected_items_state[name] = tk.BooleanVar(value=True) 
            # Jika item ditemukan, hapus dari daftar yang akan dihapus
            if name in items_to_remove_from_state:
                items_to_remove_from_state.remove(name)

        # Hapus state untuk item yang tidak ada lagi di cart
        for name in items_to_remove_from_state:
            del self.selected_items_state[name]

        for name, data in self.cart_items.items():
            item_data_frame = ctk.CTkFrame(item_container_frame, fg_color="transparent")
            item_data_frame.pack(fill="x", padx=10, pady=5)
            # MODIFIKASI GRID: Kolom 0 Checkbox, Kolom 1 Gambar, Kolom 2 Nama, Kolom 3 Qty, Kolom 4 Harga
            item_data_frame.grid_columnconfigure(0, weight=0) # Checkbox
            item_data_frame.grid_columnconfigure(1, weight=0) # Gambar
            item_data_frame.grid_columnconfigure(2, weight=2) # Nama
            item_data_frame.grid_columnconfigure(3, weight=1) # Qty Control
            item_data_frame.grid_columnconfigure(4, weight=1) # Harga
            
            # --- 0. CHECKBOX PEMILIHAN ---
            # Menggunakan CTkCheckBox yang di-customize (lingkaran)
            checkbox = ctk.CTkCheckBox(
                item_data_frame, 
                text="", 
                variable=self.selected_items_state[name], 
                command=self.update_checkout_total, # Panggil update total saat diubah
                width=20, height=20, corner_radius=10, 
                fg_color="#00FF7F" 
            )
            checkbox.grid(row=0, column=0, padx=(10, 5), sticky="w")


            # --- 1. MENAMPILKAN GAMBAR (Pindah ke Kolom 1) ---
            weapon_info = self.weapon_data_map.get(name)
            if weapon_info:
                image_path = os.path.join(self.base_dir, 'picture_resource', weapon_info['Gambar'])
                image_size = (50, 30) # Ukuran kecil untuk keranjang

                try:
                    original_image = Image.open(image_path)
                    resized_image = original_image.resize(image_size, Image.Resampling.LANCZOS)
                    weapon_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=image_size)
                    
                    # Simpan referensi
                    self.image_references[name] = weapon_image

                    image_label = ctk.CTkLabel(item_data_frame, image=weapon_image, text="")
                    image_label.grid(row=0, column=1, padx=(5, 5), sticky="w")
                except:
                    # Fallback jika gambar tidak ditemukan
                    image_label = ctk.CTkLabel(item_data_frame, text="🖼️", font=ctk.CTkFont(size=20))
                    image_label.grid(row=0, column=1, padx=(5, 5), sticky="w")
            else:
                 # Fallback jika data tidak ditemukan
                image_label = ctk.CTkLabel(item_data_frame, text="❓", font=ctk.CTkFont(size=20))
                image_label.grid(row=0, column=1, padx=(5, 5), sticky="w")
            
            
            # --- 2. NAMA BARANG (Pindah ke Kolom 2) ---
            name_label = ctk.CTkLabel(item_data_frame,
                                      text=name,
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      justify="left",
                                      wraplength=150)
            name_label.grid(row=0, column=2, padx=10, sticky="w")

            # Kontrol Kuantitas (Frame) - Pindah ke Kolom 3
            qty_control_frame = ctk.CTkFrame(item_data_frame, fg_color="gray20")
            qty_control_frame.grid(row=0, column=3, padx=5, sticky="ew")
            qty_control_frame.grid_columnconfigure((0, 2), weight=1)

            minus_button = ctk.CTkButton(qty_control_frame, 
                                        text="➖", 
                                        width=30,
                                        # MODIFIKASI COMMAND: Memastikan total diupdate setelah kuantitas berubah
                                        command=lambda n=name: [self.update_item_quantity(n, -1)]) 
            minus_button.grid(row=0, column=0, padx=2, pady=5)

            qty_label = ctk.CTkLabel(qty_control_frame, 
                                            text=f"{data['quantity']}", 
                                            font=ctk.CTkFont(size=14, weight="bold"))
            qty_label.grid(row=0, column=1, padx=2, pady=5)

            plus_button = ctk.CTkButton(qty_control_frame, 
                                        text="➕", 
                                        width=30,
                                        # MODIFIKASI COMMAND: Memastikan total diupdate setelah kuantitas berubah
                                        command=lambda n=name: [self.update_item_quantity(n, 1)])
            plus_button.grid(row=0, column=2, padx=2, pady=5)
            
            # Subtotal (Menggunakan data yang sudah diperbarui) - Pindah ke Kolom 4
            price_label = ctk.CTkLabel(item_data_frame,
                                       text=self.format_price(data['total_price']),
                                       text_color="#00FF7F",
                                       font=ctk.CTkFont(size=14, weight="bold"))
            price_label.grid(row=0, column=4, padx=10, sticky="e")
            
        # Blok kode ini dihilangkan/dijadikan komentar untuk menghapus tampilan subtotal barang
        # total_summary_frame = ctk.CTkFrame(item_container_frame, fg_color="transparent")
        # total_summary_frame.pack(fill="x", padx=10, pady=(10, 10))
        # total_summary_frame.grid_columnconfigure(0, weight=1)
        
        # ctk.CTkLabel(total_summary_frame, text="Subtotal Barang:", font=ctk.CTkFont(size=16)).grid(row=0, column=0, sticky="w", padx=10)
        # # Label ini akan di-update oleh update_checkout_total
        # ctk.CTkLabel(total_summary_frame, text=self.format_price(self.master_app.cart_total), font=ctk.CTkFont(size=16, weight="bold"), text_color="#00FF7F").grid(row=0, column=1, sticky="e", padx=10)

        # Panggil perhitungan total setelah semua widget dibuat (penting untuk tampilan awal)
        self.update_checkout_total() 

    def create_payment_selection_section(self, parent_frame):
        """Membuat bagian pemilihan metode pembayaran."""

        payment_label = ctk.CTkLabel(parent_frame, text="Pilih Cara Pembayaran:", 
                                     font=ctk.CTkFont(size=18, weight="bold"))
        payment_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        for category, methods in self.payment_methods.items():
            category_label = ctk.CTkLabel(parent_frame, text=f"**{category}**",
                                          font=ctk.CTkFont(size=15, weight="bold"),
                                          text_color="#A8D0E6") 
            category_label.pack(anchor="w", padx=15, pady=(8, 3))

            for method in methods:
                method_rb = ctk.CTkRadioButton(parent_frame,
                                               text=method,
                                               variable=self.selected_payment_method,
                                               value=method,
                                               font=ctk.CTkFont(size=14))
                method_rb.pack(anchor="w", padx=25, pady=3)
        
    def update_item_quantity(self, item_name, delta):
        """Memperbarui kuantitas item di keranjang utama."""
        
        # Mengambil data dari keranjang utama
        cart_data = self.master_app.cart_items
        
        if item_name not in cart_data:
            return

        unit_price = cart_data[item_name]['price_per_unit']
        current_qty = cart_data[item_name]['quantity']
        new_qty = current_qty + delta

        if new_qty < 0:
            return 

        if new_qty == 0:
            del self.master_app.cart_items[item_name]
            # Hapus state pilihan ketika item dihapus
            if item_name in self.selected_items_state:
                del self.selected_items_state[item_name]
        else:
            self.master_app.cart_items[item_name]['quantity'] = new_qty
            self.master_app.cart_items[item_name]['total_price'] = new_qty * unit_price

        # Memperbarui total dan count di footer aplikasi utama
        self.master_app.update_cart_display() 
        
        # Merefresh tampilan PaymentWindow dengan data terbaru
        # refresh_display akan memanggil create_cart_detail_section, yang akan memanggil update_checkout_total
        self.refresh_display()


    def process_payment(self):
        """Logika simulasi pembayaran."""
        
        # self.cart_total sudah di-update oleh update_checkout_total
        
        # MODIFIKASI: Pesan peringatan disesuaikan dengan logika checkout
        if self.cart_total == 0:
            messagebox.showwarning("Peringatan", "Total pembayaran 0. Silakan pilih item untuk di-checkout atau tambahkan item ke keranjang.")
            return

        selected_method = self.selected_payment_method.get()

        if not selected_method:
            messagebox.showwarning("Peringatan", "Silakan pilih salah satu metode pembayaran.")
            return

        # MODIFIKASI: Logika untuk menghapus HANYA item yang terpilih untuk pembayaran
        items_to_keep = {}
        for item_name, data in self.master_app.cart_items.items():
            is_selected_var = self.selected_items_state.get(item_name)
            
            # Jika item TIDAK terpilih untuk checkout (atau state-nya entah mengapa hilang), maka item tersebut dipertahankan.
            # is_selected_var is None hanya terjadi jika ada bug, tapi jika ada, kita asumsikan TIDAK terpilih.
            if is_selected_var is None or not is_selected_var.get():
                items_to_keep[item_name] = data

        # Simulasi tampilan detail transaksi
        if "Transfer Bank" in selected_method or selected_method in self.payment_methods["Transfer Bank"]:
            detail_msg = f"Silakan transfer ke rekening **{selected_method}** a/n PT GUN INDONESIA. Nomor Rekening akan dikirim via email."
        elif "Kartu Kredit" in selected_method or selected_method in self.payment_methods["Kartu Kredit"]:
            detail_msg = f"Anda akan diarahkan ke laman pembayaran aman untuk memasukkan detail kartu **{selected_method}**."
        elif selected_method in self.payment_methods["E-Wallet"]:
            detail_msg = f"Anda akan menerima notifikasi pembayaran di aplikasi **{selected_method}** Anda."
        elif "COD" in selected_method:
            detail_msg = "Tim kami akan menghubungi Anda untuk konfirmasi alamat dan jadwal pengiriman Cash on Delivery."
        else:
            detail_msg = "Detail transaksi akan dikirimkan ke email terdaftar Anda."


        messagebox.showinfo("Pembayaran Diproses", 
                            f"Transaksi sedang diproses dengan metode:\n**{selected_method}**\n\nTotal: {self.format_price(self.cart_total)}\n\n{detail_msg}\n\nTerima kasih atas pembelian Anda!")
        
        # Setelah sukses, reset keranjang utama hanya dengan item yang tidak di-checkout (items_to_keep)
        self.master_app.cart_items = items_to_keep
        self.master_app.update_cart_display()
        self.destroy()

class ShoppingChatBot(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.master_app = master
        self.title("Chat Layanan Pelanggan 💬")
        self.geometry("500x500") 
        self.resizable(True, True)
        self.grab_set() 

        # DATA PRODUK (Untuk keperluan Bot)
        self.products = {
            "Senjata laras panjang": {
                "items": ["Sniper Alpha", "Precision X9", "Long Range Elite"],
                "icon": "🎯"
            },
            "Senjata defender": {
                "items": ["Taktis X-15", "Defender P900", "Taurus Judge Defender", "Shotgun Defender S12"],
                "icon": "🛡️"
            },
            "Senjata serbu": {
                "items": ["Serbu AR-2030", "Assault Pro", "Combat X7"],
                "icon": "⚔️"
            },
            "Senjata melee": {
                "items": ["Karambit Shadow", "Golok Pranjurit", "Combat Knife Pro"],
                "icon": "🔪"
            },
            "Granat & Bom": {
                "items": ["Granat Asap M18", "Flashbang X2", "Tactical Grenade"],
                "icon": "💣"
            },
            "Aksesoris": {
                "items": ["Red Dot Sight", "Tactical Grip", "Extended Magazine", "Silencer Pro"],
                "icon": "🔧"
            }
        }
        
        self.prices = {
            "Sniper Alpha": "Rp 25.000.000",
            "Precision X9": "Rp 28.500.000",
            "Long Range Elite": "Rp 32.000.000",
            "Pistol Taktis X-15": "Rp 5.500.000", # Harga diperbarui sesuai etalase
            "Pistol Defender P900": "Rp 4.200.000", # Harga diperbarui sesuai etalase
            "pistol taurus judge defender": "Rp 6.500.000", # Harga diperbarui sesuai etalase
            "Shotgun Defender S12": "Rp 7.800.000",
            "Senapan Serbu AR-2030": "Rp 18.000.000",
            "Assault Pro": "Rp 21.000.000",
            "Combat X7": "Rp 19.500.000",
            "Pisau Karambit Shadow": "Rp 1.200.000", # Harga diperbarui sesuai etalase
            "Golok Prajurit": "Rp 900.000", # Harga diperbarui sesuai etalase
            "Combat Knife Pro": "Rp 1.500.000",
            "Granat Asap M18": "Rp 750.000",
            "Flashbang X2": "Rp 850.000",
            "Tactical Grenade": "Rp 950.000"
        }
        
        self.quick_questions = [
            "Kategori senjata apa saja?",
            "Tampilkan semua produk!",
            "Harga senjata laras panjang?",
            "Cara pembayaran?",
            "Ada promo saat ini?",
            "Waktu pengiriman?",
            "Bantu saya memilih",
            "Produk legal & berkualitas?"
        ]
        
        self.colors = {
            "primary": "#2E86AB",
            "secondary": "#A8D0E6",
            "accent": "#F76C6C",
            "dark_bg": "#1a1a1a",
            "light_bg": "#2d2d2d",
            "text_light": "#ffffff",
            "text_dark": "#cccccc"
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        self.configure(fg_color=self.colors["dark_bg"])
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self, height=70, fg_color=self.colors["primary"], corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(header_frame, 
            text="💬 Layanan Pelanggan GUNBOT",
            font=("Arial", 18, "bold"),
            text_color="white")
        title_label.pack(expand=True)
        
        self.chat_display_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color=self.colors["dark_bg"],
            border_width=0,
            scrollbar_button_color=self.colors["primary"],
            scrollbar_button_hover_color=self.colors["secondary"]
        )
        self.chat_display_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self.chat_display_frame.grid_columnconfigure(0, weight=1)
        
        questions_frame = ctk.CTkFrame(self, fg_color=self.colors["light_bg"], corner_radius=15)
        questions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        questions_container = ctk.CTkScrollableFrame(
            questions_frame, 
            fg_color="transparent",
            orientation="horizontal",
            height=60
        )
        questions_container.pack(fill="x", padx=10, pady=5)
        
        for question in self.quick_questions:
            btn = ctk.CTkButton(
                questions_container,
                text=question,
                font=("Arial", 11),
                height=35,
                fg_color=self.colors["primary"],
                hover_color=self.colors["secondary"],
                text_color="white",
                corner_radius=20,
                command=lambda q=question: self.send_quick_question(q)
            )
            btn.pack(side="left", padx=3, pady=5)
        
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="💬 Ketik pesan Anda...",
            font=("Arial", 13),
            height=45,
            border_width=1,
            fg_color="#333333",
            text_color="white",
            corner_radius=20
        )
        self.chat_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.chat_entry.bind("<Return>", self.send_message_event)
        
        send_button = ctk.CTkButton(
            input_frame,
            text="Kirim 🚀",
            font=("Arial", 12, "bold"),
            height=45,
            width=100,
            fg_color=self.colors["accent"],
            hover_color="#ff5252",
            text_color="white",
            corner_radius=20,
            command=self.send_message
        )
        send_button.grid(row=0, column=1, sticky="e")
        
        self.chat_entry.focus()
        self.show_welcome_message()
    
    def show_welcome_message(self):
        welcome_text = """🎯 **Halo! Selamat datang di GunBot**

Saya **GunBot**, asisten virtual Anda. Silakan tanyakan tentang kategori produk, harga, pengiriman, atau pilih pertanyaan cepat di bawah!"""
        
        self.add_message("GunBot", welcome_text, is_bot=True)
    
    def add_message(self, sender, message, is_bot=False):
        message_frame = ctk.CTkFrame(self.chat_display_frame, fg_color="transparent")
        message_frame.pack(fill="x", padx=5, pady=3)
        
        bubble_color = self.colors["primary"] if is_bot else self.colors["light_bg"]
        avatar_text = "🤖" if is_bot else "👤"
        sender_name = "GunBot" if is_bot else "Anda"
        text_color = "white" if is_bot else self.colors["text_light"]
        header_text_color = "#ffffff" if is_bot else self.colors["text_dark"]
        
        main_container = ctk.CTkFrame(message_frame, fg_color="transparent")
        
        if is_bot:
            main_container.pack(anchor="w")
            avatar_frame = ctk.CTkFrame(main_container, width=30, height=30, fg_color=bubble_color, corner_radius=15)
            avatar_frame.pack(side="left", padx=(0, 10))
            avatar_label = ctk.CTkLabel(avatar_frame, text=avatar_text, font=("Arial", 14), text_color="white")
            avatar_label.pack(expand=True)
            content_padx = (0, 100)
        else:
            main_container.pack(anchor="e")
            content_padx = (100, 0)
        
        content_frame = ctk.CTkFrame(main_container, corner_radius=15, fg_color=bubble_color)
        
        if is_bot:
            content_frame.pack(side="left", fill="x", expand=True, padx=content_padx)
        else:
            content_frame.pack(side="right", fill="x", expand=True, padx=content_padx)
        
        time_now = datetime.now().strftime("%H:%M")
        header_label = ctk.CTkLabel(
            content_frame,
            text=f"{sender_name} • {time_now}",
            font=("Arial", 10, "bold"),
            text_color=header_text_color
        )
        header_label.pack(anchor="w", padx=10, pady=(8, 3))
        
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=("Arial", 12),
            text_color=text_color,
            justify="left",
            wraplength=450 
        )
        message_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        self.after(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        self.chat_display_frame._parent_canvas.yview_moveto(1.0)
    
    def send_message(self):
        user_input = self.chat_entry.get().strip()
        if not user_input:
            return
            
        self.add_message("Anda", user_input, is_bot=False)
        self.chat_entry.delete(0, tk.END)
        
        self.after(500, lambda: self.process_bot_response(user_input))
    
    def send_quick_question(self, question):
        self.add_message("Anda", question, is_bot=False)
        self.after(500, lambda: self.process_bot_response(question))

    def send_message_event(self, event):
        self.send_message()

    def process_bot_response(self, user_input):
        user_input_lower = user_input.lower()
        response = ""
        
        if any(word in user_input_lower for word in ["kategori", "jenis", "apa saja"]):
            response = self.get_categories_response()
        elif any(word in user_input_lower for word in ["semua", "tampilkan", "semua produk"]):
            response = self.get_all_products_response()
        elif "laras panjang" in user_input_lower:
            response = self.get_category_detail("Senjata laras panjang")
        elif "defender" in user_input_lower:
            response = self.get_category_detail("Senjata defender")
        elif "serbu" in user_input_lower:
            response = self.get_category_detail("Senjata serbu")
        elif "melee" in user_input_lower or "mele" in user_input_lower:
            response = self.get_category_detail("Senjata melee")
        elif "bom" in user_input_lower or "granat" in user_input_lower:
            response = self.get_category_detail("Granat & Bom")
        elif "aksesoris" in user_input_lower:
            response = self.get_category_detail("Aksesoris")
        elif "harga" in user_input_lower:
            response = self.get_price_response(user_input_lower)
        elif any(word in user_input_lower for word in ["pembayaran", "bayar", "metode"]):
            response = self.get_payment_response()
        elif any(word in user_input_lower for word in ["promo", "diskon", "special"]):
            response = self.get_promo_response()
        elif any(word in user_input_lower for word in ["pengiriman", "kirim", "ongkir"]):
            response = self.get_shipping_response()
        elif any(word in user_input_lower for word in ["bantu", "pilih", "rekomendasi"]):
            response = self.get_help_response()
        elif any(word in user_input_lower for word in ["legal", "berkualitas", "aman"]):
            response = self.get_legal_response()
        elif any(word in user_input_lower for word in ["hai", "halo", "hello", "hi"]):
            response = "Halo! 👋 Ada yang bisa saya bantu hari ini? Silakan tanyakan tentang produk senjata kami!"
        else:
            response = self.get_default_response()
        
        self.add_message("GunBot", response, is_bot=True)
    
    def get_categories_response(self):
        categories_text = ""
        for category, info in self.products.items():
            categories_text += f"{info['icon']} **{category}**\n"
        
        return f"""📦 **KATEGORI PRODUK KAMI:**

{categories_text}

💡 *Ketik nama kategori untuk melihat detail produk*"""
    
    def get_all_products_response(self):
        products_text = ""
        for category, info in self.products.items():
            products_text += f"\n{info['icon']} **{category}:**\n"
            for item in info["items"]:
                price = self.prices.get(item, "Hubungi untuk harga")
                products_text += f"   • {item} - {price}\n"
        
        return f"""🛍️ **SEMUA PRODUK:**{products_text}

📞 *Hubungi CS untuk pemesanan dan info detail*"""
    
    def get_category_detail(self, category):
        if category in self.products:
            info = self.products[category]
            products_text = "\n".join([f"• {item} - {self.prices.get(item, 'Hubungi untuk harga')}" 
                                     for item in info["items"]])
            
            return f"""{info['icon']} **{category.upper()}**

{products_text}

💎 *Semua produk berkualitas tinggi dengan garansi resmi*"""
        return "❌ Kategori tidak ditemukan."
    
    def get_price_response(self, user_input):
        for product, price in self.prices.items():
            if product.lower() in user_input:
                return f"""💰 **HARGA {product.upper()}:**

**Harga:** {price}
**Status:** ✅ Tersedia
**Garansi:** 1 Tahun

📞 *Hubungi CS untuk pemesanan dan nego harga*"""
        
        return "❌ Produk tidak ditemukan. Coba sebutkan nama produk seperti: 'Sniper Alpha', 'Karambit Shadow', atau 'Granat Asap'"
    
    def get_payment_response(self):
        return """💳 **METODE PEMBAYARAN:**

• 🏦 Transfer Bank (BCA, Mandiri, BNI, BRI)
• 💳 Kartu Kredit (Visa, MasterCard)
• 📱 E-Wallet (Gopay, OVO, Dana, ShopeePay)
• 💰 COD (Cash on Delivery) - Area Terbatas

🔒 **Pembayaran 100% aman dan terjamin**
📄 Faktur pajak dan dokumentasi lengkap"""
    
    def get_promo_response(self):
        return """🎉 **PROMO SPESIAL BULAN INI!**

🔥 **DISKON 25%** untuk pembelian pertama
🚚 **GRATIS ONGKIR** min. belanja Rp 5.000.000
💳 **CASHBACK 15%** menggunakan e-wallet
🎁 **BUNDLE SPECIAL** senjata + aksesoris

⏰ **Promo berlaku hingga akhir bulan!**
📞 *Hubungi CS untuk klaim promo*"""
    
    def get_shipping_response(self):
        return """🚚 **INFORMASI PENGIRIMAN:**

📍 **Jakarta & Sekitarnya:** 1-2 hari kerja
📍 **Pulau Jawa:** 2-3 hari kerja  
📍 **Luar Jawa:** 3-7 hari kerja
📍 **Same-day delivery** (area tertentu)

🎁 **Gratis ongkir** untuk pembelian di atas Rp 5.000.000!
🔒 **Packaging aman dan discreet**"""
    
    def get_help_response(self):
        return """🤖 **BANTUAN PEMILIHAN PRODUK**

Beri tahu saya kebutuhan Anda:
• 🎯 **Budget** yang tersedia
• 🛡️ **Kategori** produk yang diinginkan
• ⚔️ **Kebutuhan spesifik** (pertahanan, olahraga, koleksi)

**Contoh:** 'Saya cari senjata defender budget 5 juta'
'Butuh senjata laras panjang untuk olahraga'

Atau pilih kategori produk untuk melihat opsi!"""
    
    def get_legal_response(self):
        return """🔒 **LEGALITAS & KUALITAS**

✅ **SEMUA PRODUK LEGAL** berizin resmi
✅ **Dokumentasi lengkap** dan faktur pajak
✅ **Berkualitas tinggi** dengan standar internasional
✅ **Garansi resmi** 1 tahun
✅ **Pelatihan penggunaan** gratis

🏆 **Toko terpercaya sejak 2010**"""
    
    def get_default_response(self):
        return """🤔 **Maaf, saya belum paham pertanyaannya.**

Coba tanyakan tentang:
• 🛍️ Kategori produk senjata
• 💰 Harga produk tertentu  
• 🎁 Info promo dan diskon
• 💳 Metode pembayaran
• 🚚 Waktu pengiriman
• 🔒 Legalitas produk

**Atau gunakan tombol pertanyaan cepat di bawah!**"""
            
app = App()
app.mainloop()
