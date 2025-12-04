from customtkinter import CTk, CTkFrame, CTkButton, CTkFont, CTkLabel, CTkEntry, set_appearance_mode, set_default_color_theme
from database import c, conn
from sqlite3 import IntegrityError
from CTkMessagebox import CTkMessagebox

c.execute(
    "create table if not exists users_accounts_data (username text unique not null, password text not null)" 
)

set_appearance_mode('dark')
set_default_color_theme('dark-blue')

class App(CTk):
    def __init__(self):
        super().__init__()

        self.title('App')
        self.geometry('1000x700')

        self.container = CTkFrame(self)
        self.container.pack(fill='both', expand=True)

        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.frames = {}
        self.frame_list = [LoginPage, RegisterPage]
        
        for F in self.frame_list:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0,
                       column=0,
                       sticky='nsew'
                       )
            
        self.show_frame(LoginPage)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

class LoginPage(CTkFrame):
    
    def __init__(self, parent, controller):
        super().__init__(parent, width=1000, height=700)
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        login_frame = CTkFrame(self,
                               width=400,
                               height=500,
                               )
        login_frame.grid(row=0,
                         column=0,
                         padx=(50, 50),
                         pady=(100, 100)
                         )
        login_frame.grid_propagate(False)
        login_frame.grid_columnconfigure(0, weight=1)
        username_frame = CTkFrame(login_frame,
                                  fg_color='transparent'
                                  )
        username_frame.grid(row=1,
                            column=0,
                            pady=(0, 20)
                            )
        password_frame = CTkFrame(login_frame,
                                  fg_color='transparent'
                                  )
        password_frame.grid(row=2,
                            column=0,
                            pady=(0, 20)
                            )
        button_frame = CTkFrame(login_frame,
                                fg_color='transparent'
                                )
        button_frame.grid(row=3,
                          column=0
                          )
        
        title_label = CTkLabel(login_frame,
                               text='Login',
                               font=CTkFont(size=26,
                                            family='Poppins',
                                            weight='bold'
                                            )
                               )
        title_label.grid(row=0,
                         column=0,
                         pady=(50, 90),
                         sticky='we'
                         )
        self.username_error_label = CTkLabel(username_frame,
                                             text='username harus diisi',
                                             font=CTkFont(size=10,
                                                          family='Poppins'),
                                             text_color='#FF0000'
                                             )
        self.username_error_label.grid(row=0,
                                       column=0,
                                       columnspan=2,
                                       pady=0,
                                       sticky='w'
                                       )
        self.error_label = CTkLabel(username_frame,
                                        text='username atau password salah',
                                        font=CTkFont(size=10,
                                                    family='Calibri'),
                                        text_color='#FF0000'
                                        )
        self.error_label.grid(row=0,
                                       column=0,
                                       columnspan=2,
                                       pady=0,
                                       sticky='w'
                                       )
        self.username_entry = CTkEntry(username_frame,
                                  placeholder_text='Masukkan Username',
                                  width=300,
                                  height=40,
                                  font=CTkFont(size=14,
                                               family='Poppins'
                                               )
                                  )
        self.username_entry.grid(row=0,
                            column=0,
                            columnspan=2,
                            pady=0
                            )
        self.username_entry.bind('<FocusOut>', self.username_null)
        self.username_entry.bind('<KeyRelease>', self.username_null)       
        self.password_entry = CTkEntry(password_frame,
                                       placeholder_text='Masukkan Password',
                                       font=CTkFont(size=14,
                                                    family='Poppins'
                                                    ),
                                       width=300,
                                       height=40
                                       )
        self.password_entry.grid(row=0,
                                 column=0,
                                 columnspan=2,
                                 pady=0
                                 )
        self.login_button = CTkButton(button_frame,
                                      text='Login',
                                      font=CTkFont(size=14,
                                                   family='Poppins'
                                                   ),
                                      width=300,
                                      height=40,
                                      command=self.login_button
                                      )
        self.login_button.grid(row=0,
                               column=0,
                               columnspan=2
                               )
        self.link_register = CTkLabel(button_frame,
                                      text='Belum punya akun? Daftar',
                                      font=CTkFont(size=10,
                                                   family='Calibri',
                                                   underline=True
                                                   ),
                                      text_color='#0D5BC0'
                                      )
        self.link_register.grid(row=1,
                                column=0,
                                pady=0,
                                sticky='e'
                                )
        self.link_register.bind('<Button-1>', self.register_link)

    def register_link(self, event=None):
        self.controller.show_frame(RegisterPage)

    def login_button(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        c.execute(
            "select * from users_accounts_data where username = ? and password = ?",
            (username, password)
        )
        result = c.fetchone()

        if username != "":
            if result:
                print('halo')

            else:
                self.error_label.grid_configure(row=1)

        else:
            self.username_error_label.grid_configure(row=1)

    def username_null(self, event=None):
        username = self.username_entry.get()

        if username == "":
            self.username_error_label.grid_configure(row=1)

        else:
            self.username_error_label.grid_configure(row=0)

class RegisterPage(CTkFrame):
    
    def __init__(self, parent, controller):
        super().__init__(parent, width=1000, height=700)
        self.controller = controller

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
        button_frame = CTkFrame(register_frame,
                                fg_color='transparent'
                                )
        button_frame.grid(row=3,
                          column=0,
                          columnspan=2,
                          pady=0
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
                                       height=40
                                       )
        self.username_entry.grid(row=0,
                                 column=0,
                                 columnspan=2,
                                 pady=0
                                 )
        self.username_entry.bind('<FocusOut>', self.username_validate)
        self.username_entry.bind('<KeyRelease>', self.username_validate)
        self.password_entry = CTkEntry(password_frame,
                                       placeholder_text='Password',
                                       font=CTkFont(size=14,
                                                    family='Poppins'
                                                    ),
                                       width=300,
                                       height=40
                                       )
        self.password_entry.grid(row=0,
                                 column=0,
                                 columnspan=2,
                                 pady=2
                                 )
        self.password_entry.bind('<KeyRelease>', self.password_validate)
        self.password_entry.bind('<FocusOut>', self.password_validate)
        self.password_entry.bind('<KeyRelease>', self.password_check_validate)
        self.password_entry.bind('<FocusOut>', self.password_check_validate)
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
        self.password_check = CTkEntry(password_frame,
                                       placeholder_text='Masukkan ulang password',
                                       font=CTkFont(size=14,
                                                    family='Poppins'
                                                    ),
                                       width=300,
                                       height=40
                                       )    
        self.password_check.grid(row=2,
                                 column=0,
                                 columnspan=2,
                                 pady=2
                                 )
        self.password_check.bind('<KeyRelease>', self.password_check_validate)
        self.password_check.bind('<FocusOut>', self.password_check_validate)
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
        self.button_register = CTkButton(button_frame,
                                         text='Sign-Up',
                                         width=300,
                                         height=40,
                                         font=CTkFont(size=16,
                                                      family='Poppins'
                                                      ),
                                         command=self.register_button
                                         )
        self.button_register.grid(row=0,
                                  column=0,
                                  columnspan=2,
                                  pady=0
                                  )
        self.login_link = CTkLabel(button_frame,
                                   text='Sudah punya akun? Login',
                                   text_color='#0D5BC0',
                                   font=CTkFont(size=10,
                                                family='Calibri',
                                                underline=True
                                                )
                                   )
        self.login_link.grid(row=1,
                             column=0,
                             columnspan=2,
                             pady=0,
                             sticky='e'
                             )
        self.login_link.bind('<Button-1>', self.login_open)
        
    def username_validate(self, event=None):
        username = self.username_entry.get()

        if username == "":
            self.username_info_label.grid_configure(row=1)
        
        else:
            self.username_info_label.grid_configure(row=0)
    
    def password_validate(self, event=None):
        password = self.password_entry.get()

        if len(password) < 8:
            self.password_info_label.configure(
                text='Password terlalu pendek',
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

        elif password == password_check:
            self.password_check_info_label.configure(
                text='Password sesuai',
                text_color='#00FF00'
            )
    
    def register_button(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        password_check = self.password_check.get()

        error = False

        if password != password_check:
            self.password_check_info_label.configure(
                text='Password tidak sesuai',
                text_color='#FF0000'
                )
            error = True

        if username == "":
            self.username_info_label.grid_configure(row=1)
            error = True
        
        if len(password) < 8:
            self.password_info_label.configure(
                text='Password terlalu pendek',
                text_color='#FF0000'
            )
            error = True

        if error:
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
            
    def login_open(self, event=None):
        self.controller.show_frame(LoginPage)
            
app = App()
app.mainloop()