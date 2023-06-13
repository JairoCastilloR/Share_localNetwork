#imports ...
import os
import webbrowser
import cgi
#from ipaddress import ip_address
import socket
import http.server
import socketserver
import PySimpleGUI as sg 
from notifypy import Notify  
 
#PORT and directory

PORT = 1397


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/upload':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <form action="/upload" method="post" enctype="multipart/form-data">
                        <input type="file" name="file">
                        <input type="submit" value="Upload">
                    </form>
                </body>
                </html>
            """)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/upload':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']}
            )
            uploaded_file = form['file']
            file_name = os.path.basename(uploaded_file.filename)
            file_path = os.path.join(self.directory, file_name)

            with open(file_path, 'wb') as f:
                f.write(uploaded_file.file.read())

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'File uploaded successfully')
        else:
            self.send_response(403)
            self.wfile.write(b'Access denied')
#Ip address

#name_pc = socket.gethostname()
#ip_address = socket.gethostbyname(name_pc)

def get_private_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

ip_address =get_private_ip()
print(f"Serving on {ip_address}")
#Notifications

notification = Notify()

#interface

sg.theme('Dark grey 13')

list_path=[
    [
    sg.Text("Path para compartir"),
    sg.In(size=(25,1), enable_events=True, key="-FOLDER-"),
    sg.FolderBrowse(),
    ],
    [
        sg.Button(
            "Confirm", enable_events=True, size=(5,1), target=(1,0),
            key="-CONFIRM-"
        ),
        sg.Button(
            "Exit", enable_events=True, size=(3,1), target=(-1,0),
            key="-Exit-"
        )
    ]
]

# --- full layout ---

layout= [
    [
        sg.Column(list_path)
    ]
]

#create window

window = sg.Window("App_Jairo", layout)

#create event

while True:
    event, values = window.read()
    if event =="-Exit-" or event == sg.WIN_CLOSED:   # if press Ok or close the window end program
        break
    if event =="-CONFIRM-":
        path = values['-FOLDER-']
        with socketserver.TCPServer((ip_address, PORT), CustomHandler) as httpd:
            notification.title = "Open Lan Network"      #notification when is open
            notification.message = f'Server is open in {ip_address}:{PORT}'
            webbrowser.open(f'http://{ip_address}:{PORT}')
            notification.send()
            httpd.serve_forever() 

window.close

#notifications

#shortcuts to open and close the aplication => modify bash to facility shortcut

