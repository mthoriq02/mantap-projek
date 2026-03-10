import customtkinter as ctk
import pygame
from database import c
import register
import login
import homepage
import payment

c.execute(
    "create table if not exists users_accounts_data (username text unique, password text)"
)

# Inisialisasi pygame mixer (diperlukan untuk MusicPlayer)
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Peringatan: pygame mixer gagal diinisialisasi. Fitur MusicPlayer dinonaktifkan. Error: {e}")

# set tema aplikasi
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

# KELAS UTAMA APLIKASI
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
        self.frame_list = [login.LoginPage, register.RegisterPage]
        
        # buat dan tampilkan semua halaman, tetapi hanya raise yang aktif
        for F in self.frame_list:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
            
        # tampilkan halaman login pertama kali
        self.show_frame(login.LoginPage)

    def show_frame(self, page):
        # tampilkan halaman tertentu dengan tkraise
        frame = self.frames[page]
        frame.tkraise()

    def open_homepage(self, username):
        home = homepage.WeaponShowcaseApp(
            parent=self.container,
            controller=self,
            username=username
        )
        home.grid(row=0, column=0, sticky='nsew')
        home.tkraise()

    def open_window_payment(self, caller, username, cart_items, cart_total, format_price_func, weapons_data):        
        payment_window = payment.PaymentWindow(
            parent=self.container,
            controller=self,
            caller=caller,
            username=username,
            cart_items=cart_items,
            cart_total=cart_total,
            format_price_func=format_price_func,
            weapons_data=weapons_data
        )
        payment_window.grid(row=0, column=0, sticky="nsew")
        payment_window.tkraise()

    
if __name__ == '__main__':
    app = App()
    app.mainloop()