#imports ...
import os
import webbrowser
import cgi
#from ipaddress import ip_address
import threading
import socket
import http.server
import socketserver
import PySimpleGUI as sg 
from notifypy import Notify  
 
#PORT and directory

PORT = 1397
chosen_path = None

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    
    def translate_path(self, path):
        global chosen_path
        return os.path.join(chosen_path, self.path[1:])
    
    def do_GET(self):
        if self.path == '/upload':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Upload File</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            text-align: center;
                            background-color: #f3f4f6;
                        }
                        .upload-container {
                            background-color: #fff;
                            border: 1px solid #e5e7eb;
                            padding: 20px;
                            margin: 50px auto;
                            width: 60%;
                            border-radius: 5px;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        }
                        .upload-btn-wrapper {
                            position: relative;
                            overflow: hidden;
                            display: inline-block;
                        }
                        .btn {
                            border: 2px solid #D1D5DB;
                            color: #4B5563;
                            background-color: white;
                            padding: 8px 20px;
                            border-radius: 8px;
                            font-size: 15px;
                            font-weight: bold;
                        }
                        .upload-btn-wrapper input[type=file] {
                            font-size: 100px;
                            position: absolute;
                            left: 0;
                            top: 0;
                            opacity: 0;
                        }
                        #upload-btn {
                            display: none;
                            margin-top: 10px;
                        }
                        .loader {
                            border: 8px solid #f3f3f3;
                            border-top: 8px solid #3498db;
                            border-radius: 50%;
                            width: 40px;
                            height: 40px;
                            animation: spin 1s linear infinite;
                            display: none;
                        }
                        @keyframes spin {
                            0% { transform: rotate(0deg); }
                            100% { transform: rotate(360deg); }
                        }
                    </style>
                </head>
                <body>
                    <div class="upload-container">
                        <form action="/upload" method="post" enctype="multipart/form-data" onsubmit="showLoader()">
                            <div class="upload-btn-wrapper">
                                <button class="btn">Select a file</button>
                                <input type="file" name="file" onchange="handleFileSelected(this)"/>
                            </div>
                            <div id="file-name"></div>
                            <input type="submit" class="btn" value="Upload" id="upload-btn"/>
                            <div id="loader" class="loader"></div>
                        </form>
                    </div>
                    <script>
                        function handleFileSelected(input) {
                            document.getElementById('file-name').innerHTML = input.files[0].name;
                            document.getElementById('upload-btn').style.display = 'block';
                        }
                        function showLoader() {
                            document.getElementById('loader').style.display = 'block';
                        }
                    </script>
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


#RUN SERVER

def run_server():
    ip_address = get_private_ip()
    notification = Notify()
    notification.title = "Open Lan Network"
    notification.message = f'Server is open in {ip_address}:{PORT}/upload'
    notification.send()
    webbrowser.open(f'http://{ip_address}:{PORT}')

    with socketserver.TCPServer((ip_address, PORT), CustomHandler) as httpd:
        httpd.serve_forever()


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
            "Start", enable_events=True, size=(5,1), target=(1,0),
            key="-Start Server-"
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

server_thread = None

while True:
    event, values = window.read()
    
    if event == "-Exit-" or event == sg.WIN_CLOSED:   # if press Ok or close the window end program
        if server_thread:
            server_thread.join
        break
    
    if event =="-Start Server-":
        chosen_path = values['-FOLDER-']
        print({chosen_path})
        if chosen_path:
            if server_thread is None:
                server_thread = threading.Thread(target=run_server)
                server_thread.daemon = True
                server_thread.start()
            else:
                sg.popup("Sevidor sigue en ejecucion")
        else:
            sg.popup("Escoje un directorio primero!!!!!")

window.close

#notifications

#shortcuts to open and close the aplication => modify bash to facility shortcut

