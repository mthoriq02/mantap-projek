import customtkinter as ctk
import tkinter as tk
import os
import homepage
from PIL import Image
from CTkMessagebox import CTkMessagebox
from datetime import datetime


class PaymentWindow(ctk.CTkFrame):
    """Jendela/Frame Checkout yang menggantikan tampilan utama."""
    def __init__(self, parent, controller, caller, username, cart_items, cart_total, format_price_func, weapons_data):
        super().__init__(parent)
        self.controller = controller
        self.master_app = caller
        self.username = username
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
        
        back_button = ctk.CTkButton(action_frame, text="⬅️ Kembali ke Etalase", command=lambda: self.controller.show_frame(homepage.WeaponShowcaseApp), fg_color="red")
        back_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        checkout_button = ctk.CTkButton(action_frame, text="💳 Lakukan Pembayaran", fg_color="#00FF7F", hover_color="#00B359", text_color="#000000", command=self.process_payment)
        checkout_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def refresh_display(self):
        """Memuat ulang semua konten keranjang dan total harga."""

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
        #memanggil nama user menggunakan username
        receipt += f"nama pembeli: {self.username}\n"
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

        # 3. Tampilkan Pesan Sukses MENGGUNAKAN JENDELA KUSTOM
        ReceiptWindow(self.master_app.controller, receipt_text)
        
        # 4. Update State
        self.master_app.cart_items = items_to_keep
        self.master_app.update_cart_display()
        
        # Kembali ke etalase
        self.controller.open_homepage(username=self.username)

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

if __name__ == "__main__":
    root = PaymentWindow(None, None, None, "testuser", {}, 0, lambda x: f"Rp {x:,}", [])
    root.mainloop()