import customtkinter as ctk
from PIL import Image
import os 
import tkinter as tk
from tkinter import messagebox 
from datetime import datetime
from open_excel import all_data

# KONFIGURASI UMUM CUSTOMTKINTER
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==============================================================================
# KELAS CHATBOT
# ==============================================================================
class ShoppingChatBot(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.master_app = master
        self.title("Chat Layanan Pelanggan 💬")
        self.geometry("500x500") 
        self.resizable(False, False)
        self.grab_set() 
        self.protocol("WM_DELETE_WINDOW", self.on_close) 

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

    def on_close(self):
        self.master_app.chat_open = False
        self.destroy()

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

# Fitur: Resizable, Pilih Pembayaran, Kontrol Kuantitas Item
class PaymentWindow(ctk.CTkToplevel):
    def __init__(self, master, cart_items, cart_total, format_price_func, weapons_data):
        super().__init__(master)
        self.master_app = master
        self.cart_items = cart_items
        self.cart_total = cart_total
        self.format_price = format_price_func
        self.weapons_data = weapons_data 
        self.selected_payment_method = tk.StringVar(value="") 

        self.title("Proses Pembayaran")
        self.geometry("500x500") 
        # MODIFIKASI: Mengizinkan jendela diperbesar (Resizable)
        self.resizable(True, True) 
        self.grab_set() 
        
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
                                    command=self.destroy,
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
        
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        self.create_cart_detail_section(self.main_content_frame)

        separator = ctk.CTkFrame(self.main_content_frame, height=2, fg_color="gray30")
        separator.pack(fill="x", padx=10, pady=15)

        self.create_payment_selection_section(self.main_content_frame)

        self.cart_total = self.master_app.cart_total 
        self.total_amount_label.configure(text=self.format_price(self.cart_total))
        
        if not self.selected_payment_method.get() and self.cart_total > 0:
            self.selected_payment_method.set(self.payment_methods["Transfer Bank"][0])

    def create_cart_detail_section(self, parent_frame):
        """Membuat bagian detail keranjang dengan tombol tambah/kurang."""
        
        item_container_frame = ctk.CTkFrame(parent_frame, fg_color="gray25", corner_radius=10)
        item_container_frame.pack(fill="x", padx=10, pady=(10, 5))

        header_label = ctk.CTkLabel(item_container_frame, 
                                    text="list isi keranjang kamu \U0001F642:", 
                                    font=ctk.CTkFont(size=16, weight="bold"))
        header_label.pack(anchor="w", padx=15, pady=(10, 5))

        if not self.cart_items:
            no_item_label = ctk.CTkLabel(item_container_frame, text="Keranjang kosong. Tidak ada yang bisa di-checkout.", text_color="gray")
            no_item_label.pack(padx=15, pady=20)
            return

        for name, data in self.cart_items.items():
            item_data_frame = ctk.CTkFrame(item_container_frame, fg_color="transparent")
            item_data_frame.pack(fill="x", padx=10, pady=5)
            item_data_frame.grid_columnconfigure(0, weight=3) 
            item_data_frame.grid_columnconfigure(1, weight=1) 
            item_data_frame.grid_columnconfigure(2, weight=2)

            name_label = ctk.CTkLabel(item_data_frame,
                                      text=name,
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      justify="left")
            name_label.grid(row=0, column=0, padx=10, sticky="w")

            # Kontrol Kuantitas (Frame)
            qty_control_frame = ctk.CTkFrame(item_data_frame, fg_color="gray20")
            qty_control_frame.grid(row=0, column=1, padx=5, sticky="ew")
            qty_control_frame.grid_columnconfigure((0, 2), weight=1)

            minus_button = ctk.CTkButton(qty_control_frame, 
                                        text="➖", 
                                        width=30,
                                        command=lambda n=name: self.update_item_quantity(n, -1))
            minus_button.grid(row=0, column=0, padx=2, pady=5)

            qty_label = ctk.CTkLabel(qty_control_frame, 
                                            text=f"{data['quantity']}", 
                                            font=ctk.CTkFont(size=14, weight="bold"))
            qty_label.grid(row=0, column=1, padx=2, pady=5)

            plus_button = ctk.CTkButton(qty_control_frame, 
                                        text="➕", 
                                        width=30,
                                        command=lambda n=name: self.update_item_quantity(n, 1))
            plus_button.grid(row=0, column=2, padx=2, pady=5)
            
            # Subtotal
            price_label = ctk.CTkLabel(item_data_frame,
                                       text=self.format_price(data['total_price']),
                                       text_color="#00FF7F",
                                       font=ctk.CTkFont(size=14, weight="bold"))
            price_label.grid(row=0, column=2, padx=10, sticky="e")
            
        total_summary_frame = ctk.CTkFrame(item_container_frame, fg_color="transparent")
        total_summary_frame.pack(fill="x", padx=10, pady=(10, 10))
        total_summary_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(total_summary_frame, text="Subtotal Barang:", font=ctk.CTkFont(size=16)).grid(row=0, column=0, sticky="w", padx=10)
        ctk.CTkLabel(total_summary_frame, text=self.format_price(self.cart_total), font=ctk.CTkFont(size=16, weight="bold"), text_color="#00FF7F").grid(row=0, column=1, sticky="e", padx=10)

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
        
        if item_name not in self.cart_items:
            return

        unit_price = self.cart_items[item_name]['price_per_unit']
            
        current_qty = self.cart_items[item_name]['quantity']
        new_qty = current_qty + delta

        if new_qty < 0:
            return 

        if new_qty == 0:
            del self.master_app.cart_items[item_name]
        else:
            self.master_app.cart_items[item_name]['quantity'] = new_qty
            self.master_app.cart_items[item_name]['total_price'] = new_qty * unit_price

        self.master_app.update_cart_display() 
        self.refresh_display()


    def process_payment(self):
        """Logika simulasi pembayaran."""
        
        self.cart_total = self.master_app.cart_total # Ambil total terbaru
        
        if self.cart_total == 0:
            messagebox.showwarning("Peringatan", "Keranjang Anda kosong! Silakan tambahkan item terlebih dahulu.")
            return

        selected_method = self.selected_payment_method.get()

        if not selected_method:
            messagebox.showwarning("Peringatan", "Silakan pilih salah satu metode pembayaran.")
            return

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
        
        self.master_app.reset_cart()
        self.destroy()


# KELAS APLIKASI UTAMA
class WeaponShowcaseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Konfigurasi Jendela
        self.title("Etalase Toko Senjata (Demo)")
        self.geometry("1000x700")

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
        self.checkout_open = False 
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
        if self.chat_open:
            return 
            
        self.chat_open = True
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
        if self.checkout_open:
            return 
            
        self.checkout_open = False
        
        checkout = PaymentWindow(
            master=self,
            cart_items=self.cart_items,
            cart_total=self.cart_total,
            format_price_func=self._format_price,
            weapons_data=self.weapons # Mengirim data senjata lengkap
        )
        
        checkout.protocol("WM_DELETE_WINDOW", self.on_checkout_close) 

    def on_checkout_close(self):
        self.checkout_open = True
        pass

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

# aplikasi dijalankan
if __name__ == "__main__":
    app = WeaponShowcaseApp()
    app.mainloop()