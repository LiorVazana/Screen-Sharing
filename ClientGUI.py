import threading
import tkinter
import customtkinter
from ClientStreaming import ClientStreaming
from ClientWatching import ClientWatching


class ScreenShareApp:
    def __init__(self, ip_address='192.168.7.17', port=45795):
        self.ip_address = ip_address
        self.port = port

        self.app_title = "Screen-Share app by 'VAZANA'"
        self.app = customtkinter.CTk()
        self.app.geometry("600x440")
        self.app.title(self.app_title)

        customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
        customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue")

        self.main_frame = customtkinter.CTkFrame(master=self.app, )
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        self.app_title_label = customtkinter.CTkLabel(master=self.main_frame, justify=customtkinter.LEFT,
                                                      text=self.app_title, font=('', 25))
        self.app_title_label.pack(pady=25, padx=10, anchor=tkinter.CENTER)

        self.buttons_frame = customtkinter.CTkFrame(master=self.main_frame, fg_color='transparent')
        self.buttons_frame.pack(pady=10, padx=10)

        self.start_streaming_button = customtkinter.CTkButton(master=self.buttons_frame, command=self.start_streaming,
                                                              text='Start Streaming',
                                                              height=35, width=140, font=('', 14))
        self.start_streaming_button.pack(pady=10, padx=10, anchor=tkinter.CENTER)

        self.join_frame = customtkinter.CTkFrame(master=self.buttons_frame, fg_color='transparent')
        self.join_frame.pack()

        self.session_id_entry = customtkinter.CTkEntry(master=self.join_frame, placeholder_text="Session ID", width=90)
        self.session_id_entry.grid(row=0, column=0, padx=5, pady=5)

        self.join_button = customtkinter.CTkButton(master=self.join_frame, command=self.join_stream, text='Join',
                                                   height=35, width=10,
                                                   font=('', 14))
        self.join_button.grid(row=0, column=1, padx=5, pady=5)

        self.error_label = customtkinter.CTkLabel(master=self.buttons_frame, justify=customtkinter.LEFT, text='',
                                                  text_color='red')
        self.error_label.pack(pady=5, padx=10, anchor=tkinter.CENTER)

        self.app.mainloop()

    def disable_buttons(self):
        self.join_button.configure(state='disabled')
        self.start_streaming_button.configure(state='disabled')
        self.session_id_entry.configure(state='disabled')

    def start_streaming(self):
        self.error_label.configure(text='')

        streaming_client = ClientStreaming(self.ip_address, self.port)

        try:
            stream_id = streaming_client.get_id()
        except:
            self.error_label.configure(text='Server not running')
            return

        self.app_title_label.configure(text=f'Your session ID is: {stream_id}')

        self.disable_buttons()

        streaming_thread = threading.Thread(target=streaming_client.stream, daemon=True)
        streaming_thread.start()

    def join_stream(self):
        self.error_label.configure(text='')

        stream_id = self.session_id_entry.get()

        if not stream_id.isnumeric():
            self.error_label.configure(text='ID must be int!')
            return

        client_watching = ClientWatching(self.ip_address, self.port)

        self.disable_buttons()

        watching_thread = threading.Thread(target=client_watching.show_stream, args=(stream_id,), daemon=True)
        watching_thread.start()


def main():
    app = ScreenShareApp()


if __name__ == '__main__':
    main()
