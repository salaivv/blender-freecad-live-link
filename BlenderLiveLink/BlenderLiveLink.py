import os
import socket
import importOBJ
import FreeCAD as App
import FreeCADGui as Gui
from PySide2 import QtWidgets
from tempfile import TemporaryDirectory


def export_obj():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 25000)
    client_socket.connect(server_address)
    
    if App.ActiveDocument:
        temp_dir = TemporaryDirectory()
        obj_path = os.path.join(temp_dir.name, f"{App.ActiveDocument.Name}.obj")
        importOBJ.export(App.ActiveDocument.Objects, obj_path)

        client_socket.sendall(obj_path.encode())

        status_message = client_socket.recv(1024).decode()
        print("Blender:", status_message)

        temp_dir.cleanup()
    else:
        print('No model found to export. Please open a model file.')

    client_socket.close()
    

def create_menu():
    menu = QtWidgets.QMenu("Blender")

    action = QtWidgets.QAction("Export to Blender", menu)
    action.triggered.connect(export_obj)

    menu.addAction(action)

    main_menu = Gui.getMainWindow().menuBar()
    main_menu.addMenu(menu)