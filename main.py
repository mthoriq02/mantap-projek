import customtkinter as ctk
import os
import bcrypt
import tkinter as tk
import pygame
import fnmatch
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
        self.title('Guardian - Etalase Senjata')
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

# kelas login
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
        button_frame = ctk.CTkFrame(login_frame, fg_color='transparent')
        button_frame.grid(row=4,column=0)
        
        # label judul login
        title_label = ctk.CTkLabel(
            login_frame, text='Login',
            font=ctk.CTkFont(size=26, family='Poppins', weight='bold')
            )
        title_label.grid(row=0, column=0, pady=(50, 20), sticky='we')
        
        # sub-judul
        subtitle_label = ctk.CTkLabel(
            login_frame,
            text='Masuk ke akun Anda',
            font=ctk.CTkFont(size=14, family='Arial', weight='normal')
            )
        subtitle_label.grid(row=1, column=0, pady=(0, 80), sticky='ew')

        # label error username kosong
        self.username_error_label = ctk.CTkLabel(
            username_frame,
            text='username harus diisi',
            font=ctk.CTkFont(size=10, family='Poppins'),
            text_color='#FF0000')
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
        self.password_hid.grid(row=1, column=0, columnspan=2, pady=(2, 2), sticky='w')

        # tombol login
        self.login_button = ctk.CTkButton(
            button_frame,
            text='Login',
            width=300, height=40,
            font=ctk.CTkFont(size=14, family='Poppins'),
            command=self.login_button,
            corner_radius=10
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

# kelas register
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
            width=380,
            height=500,
            corner_radius=12
            )
        register_frame.grid(
            row=0,
            column=0,
            padx=(50, 50),
            pady=(80, 10)
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
            show='•',
            corner_radius=8
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
        self.login_link.grid(row=1,column=0,sticky='e')
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

class WeaponShowcaseApp(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.weapons_data = all_data  # Ambil data dari variabel global
        self.cart_items = {} # { 'Nama Senjata': {'quantity': X, 'price_per_unit': Y, 'total_price': Z} }
        self.music_player = MusicPlayer() # Inisialisasi MusicPlayer
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_references = [] # Untuk mencegah garbage collection gambar

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.create_widgets()
        self.load_showcase_items()

    def create_widgets(self):
        # Frame Kontrol Atas
        top_frame = ctk.CTkFrame(self, fg_color="gray10", height=60)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # New Grid Configuration for Top Frame (Logo/Title | Filler | Music | Search | Filter)
        top_frame.grid_columnconfigure(0, weight=0) # Logo & Title
        top_frame.grid_columnconfigure(1, weight=0) # Music Player
        top_frame.grid_columnconfigure(2, weight=1) # Filler Space
        top_frame.grid_columnconfigure(3, weight=0) # Search
        top_frame.grid_columnconfigure(4, weight=0) # Filter
        
        # --- TOP LEFT: Logo and Title ---
        logo_path = os.path.join(self.base_dir, 'logo.png')
        self.logo_image = None
        logo_label = ctk.CTkLabel(top_frame, text="THE GUN ADDICTION ", font=ctk.CTkFont(size=20, weight="bold"))

        if os.path.exists(logo_path):
            try:
                original_image = Image.open(logo_path)
                # Resize logo ke ukuran yang pas
                resized_image = original_image.resize((40, 40), Image.Resampling.LANCZOS)
                self.logo_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(40, 40))
                
                logo_label.configure(image=self.logo_image, text='Guardian', compound="left", padx=10)
                self.image_references.append(self.logo_image) # Simpan referensi
            except Exception as e:
                print(f"Error loading logo: {e}")

        logo_label.grid(row=0, column=0, sticky="w", padx=10)
        
        # Tombol Music Player (Pindahkan ke dekat logo, Kolom 1)
        self.music_state_var = ctk.StringVar(value="▶️ Musik")
        self.music_btn = ctk.CTkButton(top_frame, textvariable=self.music_state_var, command=self.toggle_music, fg_color="#C38D9E", width=100)
        self.music_btn.grid(row=0, column=1, padx=5, pady=10) # Position: Col 1

        # --- TOP RIGHT: Search Bar and Filter ---
        
        # Search Bar (Kolom 3, kiri dari group kanan)
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(top_frame, textvariable=self.search_var, placeholder_text="Cari senjata...", width=200)
        search_entry.grid(row=0, column=3, padx=(10, 5), pady=10, sticky="e")
        self.search_var.trace_add("write", self.filter_showcase)

        # Filter Kategori (Kolom 4, paling kanan)
        categories = ['Semua'] + sorted(list(set(item.get('Kategori', 'Lainnya') for item in self.weapons_data)))
        self.category_var = ctk.StringVar(value=categories[0])
        category_option = ctk.CTkOptionMenu(top_frame, values=categories, command=self.filter_showcase, variable=self.category_var)
        category_option.grid(row=0, column=4, padx=(5, 10), pady=10, sticky="e")


        # Frame Showcase (Scrollable)
        self.showcase_frame = ctk.CTkScrollableFrame(self, fg_color="gray15", label_text="Daftar Produk")
        self.showcase_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.showcase_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Frame Keranjang Bawah (Footer)
        self.cart_frame = ctk.CTkFrame(self, fg_color="gray10", height=60)
        self.cart_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # New Grid Configuration for Bottom Frame (Cart Total Items | Filler | Chatbot | Checkout)
        self.cart_frame.grid_columnconfigure(0, weight=1) # Cart Total Labels
        self.cart_frame.grid_columnconfigure(1, weight=0) # Chatbot Button
        self.cart_frame.grid_columnconfigure(2, weight=0) # Checkout Button

        # Label Total Unit Keranjang (Hanya Jumlah Unit)
        self.cart_total_label = ctk.CTkLabel(self.cart_frame, text="UNIT (0 item)", font=ctk.CTkFont(size=16, weight="bold"))
        self.cart_total_label.grid(row=0, column=0, sticky="w", padx=10)
        
        # Tombol Bantuan/Chatbot
        chatbot_btn = ctk.CTkButton(self.cart_frame, text="💬 GunBot", command=self.open_chatbot, fg_color="#41B3A3")
        chatbot_btn.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # Tombol Checkout
        checkout_button = ctk.CTkButton(self.cart_frame, text="🛒 Pembayaran", command=self.open_payment_window, fg_color="#00FF7F", hover_color="#00B359", text_color="#000000")
        checkout_button.grid(row=0, column=2, sticky="e", padx=10, pady=10)

    def _parse_price(self, price_str):
        """Mengubah string harga (misal 'Rp 10.000.000' atau 10000000) menjadi integer."""
        if isinstance(price_str, (int, float)):
            return int(price_str)
        
        price_str = str(price_str).strip()
        try:
            # Hapus 'Rp', spasi, dan semua pemisah ribuan (titik/komma)
            clean_str = price_str.lower().replace("rp", "").replace(" ", "").replace(".", "").replace(",", "")
            return int(clean_str)
        except:
            return 0
            
    def _format_price(self, price_int):
        """Format integer menjadi format Rupiah (Rp 1.000.000)."""
        # Mengubah integer menjadi format Rupiah Indonesia 
        # Gunakan format {:,} untuk ribuan, lalu ganti separator
        return f"Rp {price_int:,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
        

    def open_chatbot(self):
        """Membuka jendela ChatBot."""
        # Pastikan hanya satu instance ChatBot yang terbuka
        if not hasattr(self, 'chatbot_window') or not self.chatbot_window.winfo_exists():
            self.chatbot_window = ShoppingChatBot(self)
        self.chatbot_window.focus_set()

    def toggle_music(self):
        """Memutar atau menjeda musik latar."""
        if self.music_player.is_playing:
            self.music_player.pause()
            self.music_state_var.set("▶️ Musik")
        else:
            current_track = self.music_player.play()
            if current_track:
                self.music_state_var.set("⏸️ Jeda")
    
    def load_showcase_items(self):
        """Memuat item senjata ke dalam showcase frame."""
        self.filter_showcase()
        
    def filter_showcase(self, *args):
        """Memfilter dan memuat ulang item di showcase."""
        # 1. Kosongkan showcase
        for widget in self.showcase_frame.winfo_children():
            widget.destroy()
        # Perhatian: Jangan clear self.image_references jika logo ada di sana.
        # Clear hanya referensi gambar kartu produk jika perlu, atau pastikan logo tidak ikut ter-destroy.
        
        search_query = self.search_var.get().lower()
        selected_category = self.category_var.get()

        # 2. Filter data
        filtered_data = []
        for item in self.weapons_data:
            name = item.get('Nama Senjata', '').lower()
            category = item.get('Kategori', 'Lainnya')
            
            name_match = search_query in name
            category_match = (selected_category == 'Semua' or category == selected_category)
            
            if name_match and category_match:
                filtered_data.append(item)

        # 3. Tampilkan data yang terfilter
        col = 0
        row = 0
        
        if not filtered_data:
            ctk.CTkLabel(self.showcase_frame, text="Produk tidak ditemukan.", font=ctk.CTkFont(size=16)).grid(row=0, column=0, columnspan=4, pady=50)

        for item in filtered_data:
            self.create_weapon_card(self.showcase_frame, item, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def create_weapon_card(self, parent_frame, weapon_data, row, col):
        """Membuat satu kartu produk senjata."""
        card = ctk.CTkFrame(parent_frame, corner_radius=10, fg_color="gray25")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        
        name = weapon_data.get('Nama Senjata', 'N/A')
        
        # Pastikan harga di-parse ke integer
        raw_price = self._parse_price(weapon_data.get('Harga', 0))
        formatted_price = self._format_price(raw_price)
        
        image_filename = weapon_data.get('Gambar', '')

        # Gambar Produk
        image_path = os.path.join(self.base_dir, 'picture_resource', image_filename)
        
        image_label = ctk.CTkLabel(card, text="[No Image]", font=ctk.CTkFont(size=12))
        image_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        if os.path.exists(image_path):
            try:
                original_image = Image.open(image_path)
                # Resize gambar (Contoh: 150x80)
                resized_image = original_image.resize((150, 80), Image.Resampling.LANCZOS)
                weapon_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(150, 80))
                image_label.configure(image=weapon_image, text="")
                self.image_references.append(weapon_image)
            except Exception as e:
                image_label.configure(text="[Gagal Muat Gambar]")

        # Nama
        name_label = ctk.CTkLabel(card, text=name, font=ctk.CTkFont(size=14, weight="bold"), wraplength=180)
        name_label.grid(row=1, column=0, padx=10, pady=(5, 2), sticky="w")
        
        # Harga
        price_label = ctk.CTkLabel(card, text=formatted_price, font=ctk.CTkFont(size=16, weight="bold"), text_color="#00FF7F")
        price_label.grid(row=2, column=0, padx=10, pady=(2, 5), sticky="w")
        
        # Tombol Detail & Beli
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        detail_btn = ctk.CTkButton(button_frame, text="🔍 Detail", command=lambda data=weapon_data: self.open_detail_window(data), fg_color="gray40")
        detail_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Gunakan raw_price (integer) saat memanggil add_to_cart
        buy_btn = ctk.CTkButton(button_frame, text="➕ Beli", command=lambda n=name, p=raw_price: self.add_to_cart(n, p, 1), fg_color="#E8A87C", hover_color="#D1976F", text_color="#000000")
        buy_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def open_detail_window(self, weapon_data):
        """Membuka jendela detail produk."""
        # Melewatkan fungsi format harga ke DetailWindow
        detail_window = DetailWindow(self, weapon_data, self._format_price)
        detail_window.focus_set()

    def add_to_cart(self, name, price_per_unit, quantity):
        """Menambahkan item ke keranjang belanja."""
        if name in self.cart_items:
            # Update kuantitas dan total
            self.cart_items[name]['quantity'] += quantity
            self.cart_items[name]['total_price'] += (price_per_unit * quantity)
        else:
            # Tambahkan item baru
            self.cart_items[name] = {
                'quantity': quantity,
                'price_per_unit': price_per_unit,
                'total_price': price_per_unit * quantity
            }
        self.update_cart_display()

    def update_cart_display(self):
        """Memperbarui label total item count keranjang (Hanya total item)."""
        total_items = sum(item['quantity'] for item in self.cart_items.values())
        
        # MODIFIKASI: HANYA TAMPILKAN JUMLAH ITEM
        self.cart_total_label.configure(text=f"Keranjang ({total_items} item)")

    def open_payment_window(self):
        """Membuka jendela pembayaran (PaymentWindow)."""
        if not self.cart_items:
            CTkMessagebox(title="Info", message="Keranjang masih kosong. Tambahkan item terlebih dahulu.", icon="info")
            return
            
        # Panggil fungsi di App untuk membuka frame pembayaran
        self.controller.open_window_payment(
            caller=self, 
            cart_items=self.cart_items, 
            cart_total=sum(item['total_price'] for item in self.cart_items.values()), 
            format_price_func=self._format_price, # Melewatkan fungsi format harga
            weapons_data=self.weapons_data
        )

# KELAS DETAIL PRODUK (TOPLEVEL WINDOW)
class DetailWindow(ctk.CTkToplevel):
    def __init__(self, master, weapon_data, format_price_func):
        super().__init__(master)
        self.title(f"Detail Produk: {weapon_data['Nama Senjata']}")
        self.geometry("700x550")
        self.resizable(False, False)
        self.transient(master) # Jendela tetap di atas master

        self.weapon = weapon_data
        self.format_price = format_price_func
        self.master_app = master
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_references = None # Untuk mencegah garbage collection

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # Header (Nama dan Harga)
        header_frame = ctk.CTkFrame(self, fg_color="gray15")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)

        # Nama Senjata
        name_label = ctk.CTkLabel(
            header_frame, 
            text=self.weapon['Nama Senjata'], 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        name_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Harga
        # Ambil harga yang sudah dipastikan integer dari WeaponShowcaseApp
        raw_price = self.master_app._parse_price(self.weapon['Harga'])
        
        price_label = ctk.CTkLabel(
            header_frame, 
            text=self.format_price(raw_price), 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#00FF7F" # Hijau terang
        )
        price_label.grid(row=0, column=1, sticky="e", padx=10, pady=5)

        # Main Content Frame (Gambar & Deskripsi)
        main_frame = ctk.CTkFrame(self, fg_color="gray20")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Bagian Kiri: Gambar
        image_frame = ctk.CTkFrame(main_frame, fg_color="gray15")
        image_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        image_frame.grid_rowconfigure(0, weight=1)
        image_frame.grid_columnconfigure(0, weight=1)

        image_path = os.path.join(self.base_dir, 'picture_resource', self.weapon.get('Gambar', ''))
        
        image_label = ctk.CTkLabel(image_frame, text="[Gambar Tidak Tersedia]", font=ctk.CTkFont(size=14))
        image_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        if os.path.exists(image_path):
            try:
                original_image = Image.open(image_path)
                # Resize gambar agar pas di frame 
                width, height = original_image.size
                ratio = min(350 / width, 300 / height)
                new_size = (int(width * ratio), int(height * ratio))
                
                resized_image = original_image.resize(new_size, Image.Resampling.LANCZOS)
                weapon_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=new_size)
                
                image_label.configure(image=weapon_image, text="")
                self.image_references = weapon_image # Simpan referensi
            except Exception as e:
                print(f"Error memuat gambar: {e}")
                image_label.configure(text="[Gagal Memuat Gambar]")

        # Bagian Kanan: Deskripsi
        desc_frame = ctk.CTkFrame(main_frame, fg_color="gray15")
        desc_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        desc_frame.grid_columnconfigure(0, weight=1)
        desc_frame.grid_rowconfigure(1, weight=1)

        desc_title = ctk.CTkLabel(desc_frame, text="Deskripsi Produk", font=ctk.CTkFont(size=18, weight="bold"))
        desc_title.grid(row=0, column=0, sticky="nw", padx=10, pady=(10, 5))

        # Gunakan CTkTextbox untuk deskripsi panjang
        description_text = self.weapon.get('Deskripsi', 'Deskripsi tidak tersedia.')
        
        desc_box = ctk.CTkTextbox(
            desc_frame, 
            wrap="word", 
            activate_scrollbars=True,
            font=("Arial", 14),
            fg_color="gray15",
            border_width=0
        )
        desc_box.insert("0.0", description_text)
        desc_box.configure(state="disabled") # Jadikan read-only
        desc_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Footer (Tombol)
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        footer_frame.grid_columnconfigure(0, weight=1)
        footer_frame.grid_columnconfigure(1, weight=1)

        # Input Kuantitas
        qty_label = ctk.CTkLabel(footer_frame, text="Kuantitas:", font=ctk.CTkFont(size=14))
        qty_label.grid(row=0, column=0, sticky="w", padx=(10, 5))
        
        self.qty_var = tk.StringVar(value="1")
        self.qty_entry = ctk.CTkEntry(
            footer_frame, 
            width=50, 
            textvariable=self.qty_var,
            font=ctk.CTkFont(size=14)
        )
        self.qty_entry.grid(row=0, column=0, sticky="w", padx=(80, 0))
        self.qty_entry.bind("<KeyRelease>", self.validate_quantity)

        # Tombol Tambah ke Keranjang
        add_to_cart_btn = ctk.CTkButton(
            footer_frame, 
            text="➕ Tambah ke Keranjang", 
            command=self.add_to_cart,
            fg_color="#E8A87C", 
            hover_color="#D1976F",
            text_color="#000000"
        )
        add_to_cart_btn.grid(row=0, column=1, sticky="e", padx=10)

    def validate_quantity(self, event=None):
        """Memastikan input kuantitas adalah angka positif."""
        try:
            qty = int(self.qty_var.get())
            if qty < 1:
                self.qty_var.set("1")
        except ValueError:
            # Hapus karakter non-angka atau set ke 1 jika input kosong
            current_text = self.qty_var.get()
            clean_text = ''.join(filter(str.isdigit, current_text))
            if not clean_text or int(clean_text) == 0:
                self.qty_var.set("1")
            else:
                self.qty_var.set(clean_text)
                
    def add_to_cart(self):
        """Menambahkan item ke keranjang belanja di aplikasi utama."""
        try:
            quantity = int(self.qty_var.get())
        except ValueError:
            CTkMessagebox(title="Error", message="Kuantitas harus berupa angka valid.", icon="warning")
            return

        if quantity < 1:
            CTkMessagebox(title="Error", message="Kuantitas minimal 1.", icon="warning")
            return
            
        weapon_name = self.weapon['Nama Senjata']
        
        # Pastikan harga yang masuk ke keranjang adalah integer yang sudah di-parse
        unit_price = self.master_app._parse_price(self.weapon['Harga'])

        self.master_app.add_to_cart(weapon_name, unit_price, quantity)
        
        CTkMessagebox(
            title="Sukses!",
            message=f"{quantity}x {weapon_name} berhasil ditambahkan ke keranjang!",
            icon="check"
        )
        self.destroy() # Tutup jendela detail setelah menambah ke keranjang

# KELAS PAYMENTWINDOW (CHECKOUT FRAME)
class PaymentWindow(ctk.CTkFrame):
    """Jendela/Frame Checkout yang menggantikan tampilan utama."""
    def __init__(self, parent, caller, controller, cart_items, cart_total, format_price_func, weapons_data):
        super().__init__(parent)
        self.controller = controller
        self.master_app = caller
        self.cart_items = cart_items
        self.initial_cart_total = cart_total
        # Fungsi format_price diambil dari WeaponShowcaseApp
        self.format_price = format_price_func 
        self.weapons_data = weapons_data
        
        # State
        self.cart_total = 0
        self.selected_items_state = {} 
        self.selected_payment_method = ctk.StringVar(value="")
        self.image_references = []
        
        # Helper map untuk cepat mencari info senjata
        self.weapon_data_map = {item['Nama Senjata']: item for item in weapons_data if 'Nama Senjata' in item}
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.payment_methods = {
            "Transfer Bank": ["BCA", "Mandiri", "BNI", "BRI"],
            "E-Wallet": ["Gopay", "OVO", "Dana", "ShopeePay"],
            "Kartu Kredit": ["Visa", "MasterCard"]
        }
        
        self.create_widgets()
        self.refresh_display()

    def create_widgets(self):
        # Header
        title_label = ctk.CTkLabel(self, text="jangan lupa bayar yaa!💳", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")

        # Scrollable Frame untuk Detail Keranjang & Pilihan Pembayaran
        self.main_content_frame = ctk.CTkScrollableFrame(self, label_text="Detail Transaksi", fg_color="gray15")
        self.main_content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # Footer Summary
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.summary_frame.grid_columnconfigure(1, weight=1)
        
        total_label = ctk.CTkLabel(self.summary_frame, text="TOTAL AKHIR:", font=ctk.CTkFont(size=20, weight="bold"))
        total_label.grid(row=0, column=0, sticky="w", padx=10)
        
        self.total_amount_label = ctk.CTkLabel(self.summary_frame, text=self.format_price(0), text_color="#00FF7F", font=ctk.CTkFont(size=24, weight="bold"))
        self.total_amount_label.grid(row=0, column=1, sticky="e", padx=10)

        # Action Buttons
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        back_button = ctk.CTkButton(action_frame, text="⬅️ Kembali ke Etalase", command=lambda: self.controller.show_frame(WeaponShowcaseApp), fg_color="red")
        back_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        checkout_button = ctk.CTkButton(action_frame, text="💳 Lakukan Pembayaran", fg_color="#00FF7F", hover_color="#00B359", text_color="#000000", command=self.process_payment)
        checkout_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def refresh_display(self):
        """Memuat ulang semua konten keranjang dan total harga."""
        
        # PERBAIKAN VITAL: Selalu ambil data keranjang terbaru dari aplikasi utama
        self.cart_items = self.master_app.cart_items 
        
        # Kosongkan frame
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()
        self.image_references.clear()

        # MODIFIKASI: Inisialisasi/Cleanup state seleksi
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
        
        # Buat detail keranjang
        self.create_cart_detail_section(self.main_content_frame)
        
        separator = ctk.CTkFrame(self.main_content_frame, height=2, fg_color="gray30")
        separator.pack(fill="x", padx=10, pady=15)
        
        # Buat bagian pilihan pembayaran
        self.create_payment_selection_section(self.main_content_frame)
        
        self.update_checkout_total() # Hitung ulang total

    def create_cart_detail_section(self, parent_frame):
        """Membuat bagian detail item keranjang."""
        
        if not self.cart_items:
            ctk.CTkLabel(parent_frame, text="Keranjang Kosong. Silakan kembali ke etalase.", font=ctk.CTkFont(size=16)).pack(pady=20)
            return

        item_container_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        item_container_frame.pack(fill="x", padx=0, pady=5)

        # Header Kolom
        header_frame = ctk.CTkFrame(item_container_frame, fg_color="gray25", height=40, corner_radius=0)
        header_frame.pack(fill="x", padx=10, pady=5)
        header_frame.grid_columnconfigure(0, weight=0) # Checkbox
        header_frame.grid_columnconfigure(1, weight=0) # Gambar
        header_frame.grid_columnconfigure(2, weight=2) # Nama
        header_frame.grid_columnconfigure(3, weight=1) # Qty Control
        header_frame.grid_columnconfigure(4, weight=1) # Harga
        
        ctk.CTkLabel(header_frame, text="", width=20).grid(row=0, column=0, padx=5)
        ctk.CTkLabel(header_frame, text="Produk", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, sticky="w")
        ctk.CTkLabel(header_frame, text="Kuantitas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3)
        ctk.CTkLabel(header_frame, text="Harga Total", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, sticky="e", padx=10)

        for name, data in self.cart_items.items():
            item_data_frame = ctk.CTkFrame(item_container_frame, fg_color="transparent")
            item_data_frame.pack(fill="x", padx=10, pady=5)
            item_data_frame.grid_columnconfigure(0, weight=0) # Checkbox
            item_data_frame.grid_columnconfigure(1, weight=0) # Gambar
            item_data_frame.grid_columnconfigure(2, weight=2) # Nama
            item_data_frame.grid_columnconfigure(3, weight=1) # Qty Control
            item_data_frame.grid_columnconfigure(4, weight=1) # Harga
            
            # --- 0. CHECKBOX PEMILIHAN ---
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
            image_label = ctk.CTkLabel(item_data_frame, text="[No Image]", font=ctk.CTkFont(size=10))
            image_label.grid(row=0, column=1, padx=5, sticky="w")

            if weapon_info:
                # Menggunakan folder 'picture_resource'
                image_path = os.path.join(self.base_dir, 'picture_resource', weapon_info.get('Gambar', ''))
                image_size = (50, 30) # Ukuran kecil untuk keranjang
                try:
                    original_image = Image.open(image_path)
                    resized_image = original_image.resize(image_size, Image.Resampling.LANCZOS)
                    weapon_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=image_size)
                    image_label.configure(image=weapon_image, text="")
                    self.image_references.append(weapon_image)
                except:
                    image_label.configure(text="[Gagal Muat Gambar]")

            # --- 2. NAMA PRODUK (Kolom 2) ---
            name_label = ctk.CTkLabel(item_data_frame, text=name, font=ctk.CTkFont(size=14, weight="bold"), justify="left")
            name_label.grid(row=0, column=2, padx=10, sticky="w")

            # --- 3. KONTROL KUANTITAS (Kolom 3) ---
            qty_control_frame = ctk.CTkFrame(item_data_frame, fg_color="transparent")
            qty_control_frame.grid(row=0, column=3, sticky="nsew", padx=10)
            
            # Tombol Minus
            minus_btn = ctk.CTkButton(qty_control_frame, text="–", width=30, height=30, command=lambda n=name: self.update_item_quantity(n, -1), fg_color="red")
            minus_btn.pack(side="left", padx=(0, 5))
            
            # Kuantitas
            qty_label = ctk.CTkLabel(qty_control_frame, text=str(data['quantity']), width=30, font=ctk.CTkFont(size=14))
            qty_label.pack(side="left")

            # Tombol Plus
            plus_btn = ctk.CTkButton(qty_control_frame, text="+", width=30, height=30, command=lambda n=name: self.update_item_quantity(n, 1))
            plus_btn.pack(side="left", padx=(5, 0))

            # --- 4. HARGA TOTAL (Kolom 4) ---
            price_label = ctk.CTkLabel(item_data_frame, text=self.format_price(data['total_price']), text_color="#00FF7F", font=ctk.CTkFont(size=14, weight="bold"))
            price_label.grid(row=0, column=4, padx=10, sticky="e")
    
    def update_item_quantity(self, item_name, delta):
        """Memperbarui kuantitas item di keranjang utama dan memuat ulang tampilan."""
        # Mengambil data dari keranjang utama
        cart_data = self.master_app.cart_items
        if item_name not in cart_data:
            self.refresh_display()
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
        
        # Panggil update pada etalase utama
        self.master_app.update_cart_display() 
        self.refresh_display()

    def create_payment_selection_section(self, parent_frame):
        """Membuat bagian untuk memilih metode pembayaran."""
        payment_label = ctk.CTkLabel(parent_frame, text="Pilih Cara Pembayaran:", font=ctk.CTkFont(size=18, weight="bold"))
        payment_label.pack(anchor="w", padx=10, pady=(10, 5))

        for category, methods in self.payment_methods.items():
            category_label = ctk.CTkLabel(parent_frame, text=f"**{category}**", font=ctk.CTkFont(size=15, weight="bold"), text_color="#A8D0E6")
            category_label.pack(anchor="w", padx=15, pady=(8, 3))
            for method in methods:
                method_rb = ctk.CTkRadioButton(parent_frame, text=method, variable=self.selected_payment_method, value=method, font=ctk.CTkFont(size=14))
                method_rb.pack(anchor="w", padx=25, pady=3)

    def update_checkout_total(self):
        """Menghitung total hanya dari item yang terpilih (checked)."""
        self.cart_total = 0
        
        # Iterasi melalui item di keranjang utama
        for name, data in self.master_app.cart_items.items():
            # Cek apakah item ini terpilih di PaymentWindow
            if name in self.selected_items_state and self.selected_items_state[name].get():
                self.cart_total += data['total_price']
        
        # Update label total
        self.total_amount_label.configure(text=self.format_price(self.cart_total))

    # --- FUNGSI BARU UNTUK GENERATE STRUK KOMPLEKS ---
    def _generate_complex_receipt(self, checked_out_items, total_paid, payment_method):
        """Menghasilkan teks struk pembayaran yang lebih kompleks dan terperinci."""
        
        # Contoh ID Transaksi acak
        transaction_id = datetime.now().strftime("%Y%m%d%H%M%S") 
        now = datetime.now().strftime("%d %B %Y %H:%M:%S")

        # --- HEADER ---
        receipt = "========================================\n"
        receipt += "       STRUK PEMBAYARAN - GUN ADDICTION\n"
        receipt += "========================================\n"
        receipt += f"Tanggal/Waktu: {now}\n"
        receipt += f"ID Transaksi: #{transaction_id}\n"
        receipt += "----------------------------------------\n"
        
        # --- DETAIL ITEM ---
        receipt += "ITEM YANG DIBELI:\n"
        subtotal_items = 0
        
        for name, data in checked_out_items.items():
            price_unit = data['price_per_unit']
            price_total = data['total_price']
            qty = data['quantity']
            
            # Format prices menggunakan fungsi format_price yang dilewatkan
            price_unit_formatted = self.format_price(price_unit)
            price_total_formatted = self.format_price(price_total)
            
            subtotal_items += price_total
            
            # Format: Nama (Qty x @ Harga Satuan) = Subtotal
            receipt += f"{name}\n"
            receipt += f"   - Qty: {qty} x {price_unit_formatted} = {price_total_formatted}\n"
            
        receipt += "----------------------------------------\n"

        # --- RINGKASAN HARGA (Hypothetical Diskon) ---
        
        # Logika Diskon sederhana (0% untuk contoh)
        DISCOUNT_RATE = 0.0 
        discount = int(subtotal_items * DISCOUNT_RATE)
        final_total = subtotal_items - discount
        
        final_total_formatted = self.format_price(final_total)
        total_paid_formatted = self.format_price(total_paid) 

        receipt += "RINGKASAN HARGA:\n"
        receipt += f"Subtotal Item: {self.format_price(subtotal_items)}\n"
        receipt += f"Diskon ({int(DISCOUNT_RATE*100)}%): {self.format_price(discount)}\n"
        receipt += "----------------------------------------\n"
        receipt += f"TOTAL AKHIR: {final_total_formatted}\n"
        receipt += "----------------------------------------\n"
        
        # --- DETAIL PEMBAYARAN ---
        receipt += "DETAIL PEMBAYARAN:\n"
        receipt += f"Metode Pembayaran: **{payment_method}**\n"
        receipt += "Status: LUNAS\n"
        receipt += f"Dibayar: {total_paid_formatted}\n"
        receipt += "\n========================================\n"
        receipt += "          TERIMA KASIH ATAS KUNJUNGANNYA\n"
        receipt += "========================================\n"

        return receipt
    # --- AKHIR FUNGSI BARU ---


    def process_payment(self):
        selected_method = self.selected_payment_method.get()
        
        # 1. Validasi
        if not self.cart_total or self.cart_total <= 0:
            CTkMessagebox(title="Pembayaran Gagal", message="Tidak ada item yang dipilih untuk dibayar.", icon="warning")
            return
            
        if not selected_method:
            CTkMessagebox(title="Pembayaran Gagal", message="Pilih salah satu metode pembayaran.", icon="warning")
            return

        # 2. Proses Checkout
        checked_out_items = {}
        items_to_keep = {}

        for name, data in self.master_app.cart_items.items():
            if name in self.selected_items_state and self.selected_items_state[name].get():
                checked_out_items[name] = data
            else:
                items_to_keep[name] = data
        
        # --- PENGGANTIAN UTAMA: GENERATE STRUK ---
        receipt_text = self._generate_complex_receipt(
            checked_out_items, 
            self.cart_total, 
            selected_method
        )
        # --- AKHIR PENGGANTIAN ---


        # 3. Tampilkan Pesan Sukses MENGGUNAKAN JENDELA KUSTOM
        ReceiptWindow(self.master_app.controller, receipt_text) # Panggil jendela kustom yang baru
        
        # 4. Update State
        # Setelah sukses, reset keranjang utama hanya dengan item yang tidak di-checkout (items_to_keep)
        self.master_app.cart_items = items_to_keep
        self.master_app.update_cart_display()
        
        # Kembali ke etalase
        self.controller.show_frame(WeaponShowcaseApp)
        # self.destroy() # Hapus frame pembayaran

# kelas struk
class ReceiptWindow(ctk.CTkToplevel):
    """Jendela kustom untuk menampilkan struk pembayaran dengan ukuran yang lebih kecil."""
    def __init__(self, master, receipt_text):
        super().__init__(master)
        self.title("Struk Pembayaran")
        # --- MODIFIKASI UKURAN GEOMETRY DI SINI ---
        self.geometry("450x650") # Ukuran kustom yang lebih kecil dari standar 
        self.resizable(False, False)
        self.transient(master) # Jendela tetap di atas master
        self.grab_set() # Fokuskan pada jendela ini

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Scrollable Textbox untuk menampilkan struk
        self.receipt_textbox = ctk.CTkTextbox(
            self,
            wrap="word",
            font=("Courier New", 12), # Font monospace agar format struk rapi
            fg_color="gray15",
            text_color="#00FF7F" # Warna teks hijau neon untuk kesan terminal/struk
        )
        self.receipt_textbox.insert("0.0", receipt_text)
        self.receipt_textbox.configure(state="disabled") # Jadikan read-only
        self.receipt_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Tombol Tutup
        close_btn = ctk.CTkButton(self, text="Tutup", command=self.destroy)
        close_btn.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

# KELAS MUSICPLAYER (UTILITAS)

class MusicPlayer:
    def __init__(self, music_dir="music_resource", supported_formats=None):
        if supported_formats is None:
            self.supported_formats = ['*.mp3', '*.ogg', '*.wav'] 
        else:
            self.supported_formats = supported_formats
            
        self.music_dir = os.path.join(os.getcwd(), music_dir)
        self.music_files = []
        self._load_default_files()
        
        self.current_index = 0
        self.current_music = self.music_files[0] if self.music_files else None
        self.is_playing = False
        self.volume = 0.5 
        
        if self.current_music and pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.volume)

    def _load_default_files(self):
        """Memuat file musik dari direktori default."""
        if not os.path.exists(self.music_dir):
            print(f"Direktori musik '{self.music_dir}' tidak ditemukan.")
            return

        self.music_files = []
        for root, _, files in os.walk(self.music_dir):
            for pattern in self.supported_formats:
                for filename in fnmatch.filter(files, pattern):
                    self.music_files.append(os.path.join(root, filename))
        
        if not self.music_files:
            print("Tidak ada file musik default ditemukan.")

    def add_music_file(self, file_path):
        """Menambahkan file musik ke playlist"""
        if file_path and os.path.exists(file_path):
            if file_path not in self.music_files:
                self.music_files.append(file_path)
                if self.current_music is None:
                    self.current_music = file_path
                    self.current_index = len(self.music_files) - 1
                return True
        return False

    def play(self):
        """Memulai atau melanjutkan musik"""
        if not pygame.mixer.get_init():
            return None # Jangan jalankan jika mixer gagal
            
        if not self.music_files:
            messagebox.showinfo("Info", "Tidak ada file musik. Silakan tambahkan file musik terlebih dahulu.")
            return None
        
        if not self.is_playing:
            try:
                if self.current_music is None:
                    self.current_music = self.music_files[0]
                    self.current_index = 0

                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(self.current_music)
                    pygame.mixer.music.set_volume(self.volume)
                    pygame.mixer.music.play(-1) # -1 untuk loop tak terbatas
                else:
                    pygame.mixer.music.unpause()
                
                self.is_playing = True
                return self.current_music
            except Exception as e:
                print(f"Error memutar musik: {e}")
                messagebox.showerror("Error", f"Gagal memutar musik: {str(e)}")
                return None
        return self.current_music

    def pause(self):
        """Menjeda musik"""
        if pygame.mixer.get_init() and self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False

    def stop(self):
        """Menghentikan musik"""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.is_playing = False
        self.current_music = None

    def set_volume(self, volume):
        """Mengatur volume"""
        self.volume = max(0.0, min(1.0, volume))
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.volume)

    def next_track(self):
        """Pindah ke lagu berikutnya"""
        if not self.music_files:
            return None
        self.stop()
        self.current_index = (self.current_index + 1) % len(self.music_files)
        self.current_music = self.music_files[self.current_index]
        return self.play()

    def previous_track(self):
        """Pindah ke lagu sebelumnya"""
        if not self.music_files:
            return None
        self.stop()
        self.current_index = (self.current_index - 1 + len(self.music_files)) % len(self.music_files)
        self.current_music = self.music_files[self.current_index]
        return self.play()
    
# KELAS MUSICPLAYER (UTILITAS)

class MusicPlayer:
    def __init__(self, music_dir="music_resource", supported_formats=None):
        if supported_formats is None:
            self.supported_formats = ['*.mp3', '*.ogg', '*.wav'] 
        else:
            self.supported_formats = supported_formats
            
        self.music_dir = os.path.join(os.getcwd(), music_dir)
        self.music_files = []
        self._load_default_files()
        
        self.current_index = 0
        self.current_music = self.music_files[0] if self.music_files else None
        self.is_playing = False
        self.volume = 0.5 
        
        if self.current_music and pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.volume)

    def _load_default_files(self):
        """Memuat file musik dari direktori default."""
        if not os.path.exists(self.music_dir):
            print(f"Direktori musik '{self.music_dir}' tidak ditemukan.")
            return

        self.music_files = []
        for root, _, files in os.walk(self.music_dir):
            for pattern in self.supported_formats:
                for filename in fnmatch.filter(files, pattern):
                    self.music_files.append(os.path.join(root, filename))
        
        if not self.music_files:
            print("Tidak ada file musik default ditemukan.")

    def add_music_file(self, file_path):
        """Menambahkan file musik ke playlist"""
        if file_path and os.path.exists(file_path):
            if file_path not in self.music_files:
                self.music_files.append(file_path)
                if self.current_music is None:
                    self.current_music = file_path
                    self.current_index = len(self.music_files) - 1
                return True
        return False

    def play(self):
        """Memulai atau melanjutkan musik"""
        if not pygame.mixer.get_init():
            return None # Jangan jalankan jika mixer gagal
            
        if not self.music_files:
            messagebox.showinfo("Info", "Tidak ada file musik. Silakan tambahkan file musik terlebih dahulu.")
            return None
        
        if not self.is_playing:
            try:
                if self.current_music is None:
                    self.current_music = self.music_files[0]
                    self.current_index = 0

                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(self.current_music)
                    pygame.mixer.music.set_volume(self.volume)
                    pygame.mixer.music.play(-1) # -1 untuk loop tak terbatas
                else:
                    pygame.mixer.music.unpause()
                
                self.is_playing = True
                return self.current_music
            except Exception as e:
                print(f"Error memutar musik: {e}")
                messagebox.showerror("Error", f"Gagal memutar musik: {str(e)}")
                return None
        return self.current_music

    def pause(self):
        """Menjeda musik"""
        if pygame.mixer.get_init() and self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False

    def stop(self):
        """Menghentikan musik"""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.is_playing = False
        self.current_music = None

    def set_volume(self, volume):
        """Mengatur volume"""
        self.volume = max(0.0, min(1.0, volume))
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.volume)

    def next_track(self):
        """Pindah ke lagu berikutnya"""
        if not self.music_files:
            return None
        self.stop()
        self.current_index = (self.current_index + 1) % len(self.music_files)
        self.current_music = self.music_files[self.current_index]
        return self.play()

    def previous_track(self):
        """Pindah ke lagu sebelumnya"""
        if not self.music_files:
            return None
        self.stop()
        self.current_index = (self.current_index - 1 + len(self.music_files)) % len(self.music_files)
        self.current_music = self.music_files[self.current_index]
        return self.play()
    
    # kelas chatbot
    # KELAS SHOPPING CHATBOT (TOPLEVEL WINDOW)
class ShoppingChatBot(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("GunBot - Layanan Pelanggan")
        self.geometry("400x500")
        self.resizable(False, False)
        self.transient(master) # Jendela tetap di atas master
        self.master_app = master
        
        self.colors = {
            "primary": "#41B3A3", "secondary": "#C38D9E", "accent": "#E8A87C", 
            "error": "#F76C6C", "dark_bg": "#1a1a1a", "light_bg": "#2d2d2d", 
            "text_light": "#ffffff", "text_dark": "#cccccc"
        }
        
        # Mapping untuk Bot Response (Menggunakan data senjata yang dimuat)
        product_categories = {}
        for item in all_data:
            category = item.get('Kategori', 'Lainnya') # Asumsi ada kolom Kategori di Excel
            name = item.get('Nama Senjata')
            if category not in product_categories:
                product_categories[category] = {"items": [], "icon": "❓"}
            if name:
                product_categories[category]["items"].append(name)
        
        # Tambahkan ikon default jika Kategori tidak ada/kosong
        for cat in product_categories:
             if 'Pistol' in cat: product_categories[cat]['icon'] = '🛡️'
             elif 'Sniper' in cat: product_categories[cat]['icon'] = '🎯'
             elif 'Shotgun' in cat: product_categories[cat]['icon'] = '💣'
             elif 'Serbu' in cat: product_categories[cat]['icon'] = '⚔️'
             elif 'Melee' in cat: product_categories[cat]['icon'] = '🔪'
             
        self.categories = product_categories

        self.setup_ui()
        
    def setup_ui(self):
        self.configure(fg_color=self.colors["dark_bg"])
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, height=70, fg_color=self.colors["primary"], corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.pack_propagate(False)
        title_label = ctk.CTkLabel(header_frame, text="💬 Layanan Pelanggan GUNBOT", font=("Arial", 18, "bold"), text_color="white")
        title_label.pack(expand=True)

        # Chat Display
        self.chat_display_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color=self.colors["dark_bg"], 
            border_width=0, 
            scrollbar_button_color=self.colors["primary"], 
            scrollbar_button_hover_color=self.colors["accent"]
        )
        self.chat_display_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.chat_display_frame.grid_columnconfigure(0, weight=1)
        self.chat_row_counter = 0

        # Input Area
        input_frame = ctk.CTkFrame(self, fg_color=self.colors["light_bg"])
        input_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_entry = ctk.CTkEntry(
            input_frame, 
            placeholder_text="Ketik pesan Anda...",
            font=("Arial", 14), 
            height=45, 
            fg_color=self.colors["dark_bg"], 
            text_color=self.colors["text_light"],
            corner_radius=20
        )
        self.chat_entry.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=10)
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
        send_button.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=10)

        qr_frame = ctk.CTkFrame(self, fg_color=self.colors["light_bg"], corner_radius=15)
        qr_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        qr_frame.grid_columnconfigure(0, weight=1)


        quick_replies = [
            ("Kategori Produk", "kategori"), 
            ("Metode Pembayaran", "pembayaran"),
            ("Info Pengiriman", "pengiriman"),
            ("Promo Bulan Ini", "promo"),
            ("Legalitas produk", "Legalitas")
        ]

        
        
        questions_container = ctk.CTkScrollableFrame(
            qr_frame, 
            fg_color="transparent",
            orientation="horizontal",
            height=60
        )

        questions_container.pack(fill="x", padx=10, pady=5)
        for i, (text, command) in enumerate(quick_replies):
            btn = ctk.CTkButton(
                questions_container,
                text=text,
                font=("Arial", 11),
                height=35,
                width=140,
                fg_color=self.colors["primary"],
                hover_color=self.colors["secondary"],
                text_color="white",
                corner_radius=15,
                command=lambda cmd=command, txt=text: self.handle_quick_reply(cmd, txt)
            )
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        self.chat_entry.focus()
        self.show_welcome_message()

    def show_welcome_message(self):
        welcome_text = """🎯 
            **Halo! Selamat datang di GunBot**
            Saya **GunBot**, asisten virtual Anda.
            Silakan tanyakan tentang kategori 
            produk, harga, pengiriman, atau pilih 
            pertanyaan cepat di bawah!"""
        self.add_message("GunBot", welcome_text, is_bot=True)
        return welcome_text  # Kembalikan teks agar bisa digunakan di process_command


    def add_message(self, sender, message, is_bot=False):
        message_frame = ctk.CTkFrame(self.chat_display_frame, fg_color="transparent")
    
    # Tentukan posisi berdasarkan pengirim
        if is_bot:
            message_frame.grid(row=self.chat_row_counter, column=0, sticky="w", pady=5, padx=5)
            bubble_color = self.colors["light_bg"]
            text_color = self.colors["text_light"]
            avatar_text = "🤖"
            sender_name = "GunBot"
            sticky_position = "w"
            header_text_color = self.colors["text_light"]
        else:
            message_frame.grid(row=self.chat_row_counter, column=0, sticky="e", pady=5, padx=5)
            bubble_color = self.colors["primary"]
            text_color = "black"
            avatar_text = "👤"
            sender_name = "Anda"
            sticky_position = "e"
            header_text_color = "black"
        
        message_frame.grid_columnconfigure(0, weight=1)
        main_container = ctk.CTkFrame(message_frame, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky=sticky_position)
        main_container.grid_columnconfigure(0, weight=0)  # Untuk avatar (jika ada)
        main_container.grid_columnconfigure(1, weight=1)

        if is_bot:
            # Avatar untuk bot di kolom 0
            avatar_frame = ctk.CTkFrame(main_container, width=30, height=30, fg_color=bubble_color, corner_radius=15)
            avatar_frame.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
            avatar_label = ctk.CTkLabel(avatar_frame, text=avatar_text, font=("Arial", 14), text_color=text_color)
            avatar_label.grid(row=0, column=0, padx=5, pady=5)
        
            # Bubble pesan di kolom 1
            content_frame_column = 1
        else:
             content_frame_column = 0
        # Untuk user, tidak ada avatar, langsung content frame di kolom 1

        # Bubble pesan
        content_frame = ctk.CTkFrame(main_container, corner_radius=15, fg_color=bubble_color)
        content_frame.grid(row=0, column=content_frame_column, sticky=sticky_position)
        content_frame.grid_columnconfigure(0, weight=1)

        time_now = datetime.now().strftime("%H:%M")
        header_label = ctk.CTkLabel(
            content_frame,
            text=f"{time_now}",
            font=("Arial", 10, "bold"),
            text_color=header_text_color
        )   
        header_label.grid(row=0, column=1, padx=5, pady=5) 
   
        # Header dengan nama pengirim
        header_label = ctk.CTkLabel(
            content_frame,
            text=sender_name,
            font=("Arial", 10, "bold"),
            text_color=text_color
        )
        header_label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 3))
    
    # Isi pesan
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=("Arial", 12),
            text_color=text_color,
            justify="left",
            wraplength=300
        )
        message_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))
    
        self.chat_row_counter += 1
        self.chat_display_frame._parent_canvas.yview_moveto(1.0) # Auto-scroll
        
    def handle_quick_reply(self, command, text):
        self.add_message("Anda", text, is_bot=False)
        self.process_command(command)

    def send_message_event(self, event):
        self.send_message()

    def send_message(self):
        user_input = self.chat_entry.get().strip()
        self.chat_entry.delete(0, 'end')

        if not user_input:
            return

        self.add_message("Anda", user_input, is_bot=False)
        self.process_command(user_input.lower())

    def process_command(self, command):
        
        if any(keyword in command for keyword in ["kategori", "jenis", "produk", "senjata"]):
            response = self.get_category_response()
        elif any(keyword in command for keyword in ["pembayaran", "metode", "bayar"]):
            response = self.get_payment_response()
        elif any(keyword in command for keyword in ["promo", "diskon", "cashback"]):
            response = self.get_promo_response()
        elif any(keyword in command for keyword in ["kirim", "pengiriman", "kurir"]):
            response = self.get_shipping_response()
        elif any(keyword in command for keyword in ["legalitas","Legalitas","apakah produk ini legal"]):
            response = self.get_legalitas_response()
        elif any(keyword in command for keyword in ["halo", "hai", "selamat datang", "mulai"]):
            response = self.show_welcome_message() # Restart welcome message
            return
        else:
            response = self.get_default_response()


        self.add_message("GunBot", response, is_bot=True)
        
        
    # --- BOT RESPONSES ---

    def get_category_response(self):
        if not self.categories:
            return "Maaf, data produk sedang tidak tersedia. Silakan cek kembali nanti."
            
        res = "🛡️ **KATEGORI PRODUK KAMI:**\n"
        for cat, data in self.categories.items():
            # Batasi 3 contoh item saja
            items = ", ".join(data['items'][:3])
            if len(data['items']) > 3:
                 items += ", dan lain-lain..."
                 
            res += f"\n**{data['icon']} {cat.upper()}**\n"
            res += f"   - Contoh: {items}"
        return res

    def get_payment_response(self):
        return """
           **METODE PEMBAYARAN:**
        • 🏦 Transfer Bank (BCA, BNI, BRI)
        • 💳 Kartu Kredit (Visa, MasterCard)
        • 📱 E-Wallet (Gopay, Dana, ShopeePay)
        • 💰 COD (Cash on Delivery)"""

    def get_legalitas_response(self):
        return """
            Produk telah menerima izin dari kepolisian 
            dalam penjualan produk. Semua senjata yang 
            dijual sudah melalui proses legal dan 
            memiliki dokumen yang diperlukan.Kami 
            menjamin keaslian dan legalitas setiap
            produk yang dijual."""

    def get_promo_response(self):
        return """
            🎉 **PROMO SPESIAL BULAN INI!**
            🔥 **DISKON 25%** untuk pembelian pertama
            🚚 **GRATIS ONGKIR** min. belanja 
                Rp 5.000.000
            💳 **CASHBACK 15%** menggunakan e-wallet
            🎁 **BUNDLE SPECIAL** 
                senjata + aksesoris
            ⏰ **Promo berlaku hingga akhir bulan!**
            📞 *Hubungi CS untuk klaim promo*"""

    def get_shipping_response(self):
        return """
            🚚 **INFORMASI PENGIRIMAN:**
            📍 **Jakarta & Sekitarnya:**
                 1-2 hari kerja
            📍 **Pulau Jawa:** 2-3 hari kerja
            📍 **Luar Jawa:** 3-7 hari kerja
            📍 **Same-day delivery** 
                (area tertentu)
            🔒 **Packaging aman dan discreet**"""

    def get_default_response(self):
        return """
            Maaf, saya hanya bisa menjawab 
            pertanyaan seputar kategori produk,
            pembayaran, promo, dan pengiriman.
            Coba ketik salah satu: **kategori**,
            **pembayaran**, **promo**, 
            **legalitas**, atau **pengiriman**.""" 
            
app = App()
app.mainloop()
