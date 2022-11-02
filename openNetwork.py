#imports ...
import webbrowser
from ipaddress import ip_address
import socket
import http.server
import socketserver
import PySimpleGUI as sg 
from notifypy import Notify  
 
#PORT and directory

PORT = 1397

def handler_from(directory):
    def _init(self, *args, **kwargs):
        return http.server.SimpleHTTPRequestHandler.__init__(self, *args, directory=self.directory, **kwargs)
    return type(f'HandlerFrom<{directory}>',
                (http.server.SimpleHTTPRequestHandler,),
                {'__init__': _init, 'directory': directory})

#Ip address

name_pc = socket.gethostname()
ip_address = socket.gethostbyname(name_pc)

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
        with socketserver.TCPServer(('', PORT), handler_from(path)) as httpd:
            notification.title = "Open Lan Network"      #notification when is open
            notification.message = f'Server is open in {ip_address}:{PORT}'
            webbrowser.open(f'http://{ip_address}:{PORT}')
            notification.send()
            httpd.serve_forever() 

window.close

#notifications

#shortcuts to open and close the aplication => modify bash to facility shortcut

