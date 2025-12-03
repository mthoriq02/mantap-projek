from sqlite3 import IntegrityError
from customtkinter import CTk, CTkLabel, CTkButton, CTkEntry, CTkFrame, CTkFont, set_appearance_mode, set_default_color_theme
from database import c, conn
from CTkMessagebox import CTkMessagebox

set_appearance_mode('Dark')
set_default_color_theme('dark-blue')

c.execute(
    "create table if not exists users_accounts_data (username text unique not null, password text not null)" 
)

class RegisterPage(CTkFrame):
    
    def __init__(self, parent, controller):
        super().__init__(parent, width=1000, height=700)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        register_frame = CTkFrame(self,
                                  width=400,
                                  height=500
                                  )
        register_frame.grid(row=0,
                            column=0,
                            padx=(50, 50),
                            pady=(50, 50))
        register_frame.grid_propagate(False)
        register_frame.grid_columnconfigure(0, weight=1)
        
        username_frame = CTkFrame(register_frame,
                                  fg_color='transparent'
                                  )
        username_frame.grid(row=1,
                            column=0,
                            columnspan=2,
                            pady=(0, 20)
                            )
        password_frame = CTkFrame(register_frame,
                                  fg_color='transparent'
                                  )
        password_frame.grid(row=2,
                            column=0,
                            columnspan=2,
                            pady=0
                            )       
        title_label = CTkLabel(register_frame,
                               text="Sign-Up",
                               font=CTkFont(size=26,
                                            weight='bold',
                                            family='Poppins')
                                    )
        title_label.grid(row=0,
                         column=0,
                         columnspan=2,
                         pady=(50, 90),
                         sticky='we'
                         )
        self.username_info_label = CTkLabel(username_frame,
                                            text='*username tidak boleh kosong',
                                            font=CTkFont(size=10,
                                                         weight='normal',
                                                         family='Calibri'),
                                            text_color='#FF0000'
                                            )
        self.username_info_label.grid(row=0,
                                      column=0,
                                      columnspan=2,
                                      pady=0,
                                      sticky='w'
                                      ) 
        self.username_entry = CTkEntry(username_frame,
                                       placeholder_text='Username',
                                       font=CTkFont(size=14,
                                                    family='Poppins'
                                                    ),
                                       width=300,
                                       height=40,
                                       border_color='#000000'
                                       )
        self.username_entry.grid(row=0,
                                 column=0,
                                 columnspan=2,
                                 pady=0
                                 )
        self.username_entry.bind('<FocusOut>', self.username_validate)
        self.password_entry = CTkEntry(password_frame,
                                       placeholder_text='Password',
                                       font=CTkFont(size=14,
                                                    family='Poppins'
                                                    ),
                                       width=300,
                                       height=40,
                                       border_color="#000000"
                                       )
        self.password_entry.grid(row=0,
                                 column=0,
                                 columnspan=2,
                                 pady=2
                                 )
        self.password_info_label = CTkLabel(password_frame,
                                            text='*password setidaknya harus 8 karakter',
                                            font=CTkFont(size=10,
                                                         weight='normal',
                                                         family='Calibri'
                                                         ),
                                            text_color="#8F8383"
                                            )
        self.password_info_label.grid(row=1,
                                      column=0,
                                      columnspan=2,
                                      padx=5,
                                      pady=1,
                                      sticky='w'
                                      )
        self.password_entry.bind('<KeyRelease>', self.password_validate)
        self.password_check = CTkEntry(password_frame,
                                       placeholder_text='Masukkan ulang password',
                                       font=CTkFont(size=14,
                                                    family='Poppins'
                                                    ),
                                       width=300,
                                       height=40,
                                       border_color='#000000'
                                       )    
        self.password_check.grid(row=2,
                                 column=0,
                                 columnspan=2,
                                 pady=2
                                 )
        self.password_check_info_label = CTkLabel(password_frame,
                                                  text='*masukkan ulang password',
                                                  font=CTkFont(size=10,
                                                               weight='normal',
                                                               family='Calibri'
                                                               ),
                                                  text_color='#8F8383'
                                             )
        self.password_check_info_label.grid(row=3,
                                            column=0,
                                            columnspan=2,
                                            pady=0,
                                            sticky='w'
                                            )
        self.password_check.bind('<KeyRelease>', self.password_check_validate)
        self.button_register = CTkButton(register_frame,
                                         text='Sign-Up',
                                         width=300,
                                         height=40,
                                         font=CTkFont(size=16,
                                                      family='Poppins'
                                                      ),
                                         command=self.register_button
                                         )
        self.button_register.grid(row=3,
                                  column=0,
                                  columnspan=2,
                                  pady=40
                                  )
        
    def username_validate(self, event=None):
        username = self.username_entry.get()

        if username == "":
            self.username_entry.configure(border_color='#FF0000')
            self.username_info_label.grid_configure(row=1)
        
        else:
            self.username_entry.configure(border_color='#000000')
    
    def password_validate(self, event=None):
        password = self.password_entry.get()

        if len(password) < 8:
            self.password_info_label.configure(
                text='PASSWORD TERLALU PENDEK',
                text_color='#FF0000'
            )

        elif len(password) >= 8:
            self.password_info_label.configure(
                text='Password sudah cukup',
                text_color='#00FF00'
            )

    def password_check_validate(self, event=None):
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
        username = self.username_entry.get()
        password = self.password_entry.get()
        password_check = self.password_check.get()

        if password != password_check:
            self.password_check_info_label.configure(
                text='Password tidak sesuai',
                text_color='#FF0000'
                )
            return

        if username == "":
            self.username_entry.configure(border_color='#FF0000')
            self.username_info_label.grid_configure(row=1)
            return
        
        if len(password) < 8:
            self.password_info_label.configure(
                text='PASSWORD TERLALU PENDEK',
                text_color='#FF0000'
            )
            return

        try:            
            c.execute(
                "insert into users_accounts_data values (?, ?)",
                (username, password)
            )
            conn.commit()
            CTkMessagebox(title='Sukses',
                          message='Pendaftaran berhasil',
                          icon='check'
                          )

        except IntegrityError:
            CTkMessagebox(title='Error',
                          message='Username sudah terdaftar',
                          icon='warning'
                          )
            
if __name__ == "__main__":
    root = RegisterPage()
    root.mainloop()