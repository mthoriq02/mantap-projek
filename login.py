from customtkinter import CTk, CTkEntry, CTkButton, CTkFont, CTkFrame, CTkLabel, set_appearance_mode, set_default_color_theme
from register import RegisterPage
from database import c, conn

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


if __name__ == "__main__":
    root = LoginPage()
    root.mainloop()