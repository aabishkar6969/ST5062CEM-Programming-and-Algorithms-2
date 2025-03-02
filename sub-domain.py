import tkinter as Tkinter
import tkinter.ttk as ttk
import socket
import threading

IP_ADDRESS = socket.gethostbyname(socket.gethostname())
PORT = 1234

# ========== Socket Programming ================ #

class SocketServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def load(self, ip_address, port, history_text, status_label, client_info_label):
        self.ip_address = ip_address
        self.port = port
        self.history = history_text
        self.status = status_label
        self.client_info = client_info_label

    def bind(self):
        while True:
            try:
                self.socket.bind(("", self.port.get()))
                break
            except:
                pass
        self.socket.listen(1)
        self.connection, addr = self.socket.accept()
        ip, port = addr
        self.status.config(text="Connected", bg="lightgreen")
        self.client_info.config(text="{}:{}".format(ip, self.port.get()))
        threading.Thread(target=self.receive_messages).start()

    def send(self, message: str):
        try:
            self.connection.sendall(message.encode("utf-8"))
        except Exception as e:
            print("[=] Server Not Connected Yet", e)

    def receive_messages(self):
        print(" [+] Receiving messages started")
        while True:
            try:
                data = self.connection.recv(1024)
                if data:
                    message = data.decode("utf-8")
                    formatted_message = "Other: " + message + "\n"
                    self.history.insert("end", formatted_message)
                    start = self.history.index("end") + "-1l"
                    end = self.history.index("end")
                    self.history.tag_add("SENDBYOTHER", start, end)
                    self.history.tag_config("SENDBYOTHER", foreground="green")
            except Exception as e:
                print(e, "[=] Closing Connection [receive_messages]")
                self.connection.close()
                break

    def close(self):
        self.socket.close()

# =============================================

class ServerDialogBox(Tkinter.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ip_address = Tkinter.StringVar()
        self.port = Tkinter.IntVar(value=PORT)
        self.create_interface()
        threading.Thread(target=self.setup_socket).start()

    def setup_socket(self):
        self.socket_server = SocketServer()
        self.socket_server.load(
            self.ip_address, self.port, self.history, self.status, self.client_info
        )
        self.socket_server.bind()

    def create_interface(self):
        self.create_connection_info_panel()
        self.create_chat_history_panel()
        self.create_message_sending_panel()

    def send_text_message(self):
        if self.status.cget("text") == "Connected":
            input_data = self.sending_data.get("1.0", "end").strip()
            if input_data:
                formatted_input = "Me: " + input_data + "\n"
                self.history.insert("end", formatted_input)
                start = self.history.index("end") + "-1l"
                end = self.history.index("end")
                self.history.tag_add("SENDBYME", start, end)
                self.sending_data.delete("1.0", "end")
                self.socket_server.send(input_data)
                self.history.tag_config("SENDBYME", foreground="blue")
            else:
                print("[=] Input Not Provided")
        else:
            print("[+] Not Connected")

    def create_message_sending_panel(self):
        self.sending_data = Tkinter.Text(
            self.sending_panel, font=("Arial", 12, "italic"), width=35, height=5
        )
        self.sending_data.pack(side="left")
        self.send_button = Tkinter.Button(
            self.sending_panel,
            text="Send",
            width=15,
            height=5,
            bg="orange",
            command=self.send_text_message,
            activebackground="lightgreen",
        )
        self.send_button.pack(side="left")

    def create_chat_history_panel(self):
        self.history = Tkinter.Text(
            self.history_frame, font=("Arial", 12, "bold", "italic"), width=50, height=15
        )
        self.history.pack()

    def create_connection_info_panel(self):
        self.connection_info_frame = Tkinter.LabelFrame(
            self, text="Connection Information", fg="green", bg="powderblue"
        )
        self.connection_info_frame.pack(side="top", expand="yes", fill="both")
        self.create_connection_labels()

