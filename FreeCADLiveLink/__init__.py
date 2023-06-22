import bpy
from bpy.app.handlers import persistent
import socket
import threading
import time

bl_info = {
    "name": "FreeCAD Live Link",
    "description": "Live link for FreeCAD",
    "author": "Salai Vedha Viradhan",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "category": "Import-Export"
}

obj_path = None
import_status = None

def import_obj():
    global obj_path
    bpy.ops.wm.obj_import(filepath=obj_path, forward_axis='Y', up_axis='Z')

    for obj in bpy.data.objects:
        if obj.select_get() == True:
            obj.scale = (0.01, 0.01, 0.01)

    bpy.ops.object.transform_apply(scale=True)

def obj_data_monitor():
    global obj_path
    global import_status

    if obj_path != None:
        try:
            import_obj()
            obj_path = None
            import_status = 'SUCCESS'    
        except Exception as e:
            print(str(e))
            import_status = 'FAILURE'    
    return 1.0

def receive_data():
    global obj_path
    global import_status

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 25000)
    server_socket.bind(server_address)

    while True:
        server_socket.listen(5)
        print("Listening for OBJs...")

        connection, client_address = server_socket.accept()
        print("Connected with FreeCAD instance:", client_address)

        data = connection.recv(1024).decode()

        if data == "Quit Blender!":
            print("FreeCAD Live Link: Shutting down...")
            server_socket.close()
            break

        print(f"OBJ received: {data}")
        import_status = 'IMPORTING'
        obj_path = data

        while import_status != None:
            if import_status == 'SUCCESS':
                connection.sendall("Successfully imported OBJ!".encode())
                break
            elif import_status == 'FAILURE':
                connection.sendall("Failed imported OBJ.".encode())
                break
            else:
                time.sleep(3)
                continue

        import_status = None
        connection.close()

def cleanup_threads():
    threads_cleaned = False
    while not threads_cleaned:
        time.sleep(2)
        for thread in threading.enumerate():
            if thread.getName() == "MainThread" and thread.is_alive() == False:
                cleanup_socket = socket.socket()
                cleanup_socket.connect(('localhost', 25000))
                cleanup_socket.send(b"Quit Blender!")
                cleanup_socket.close()
                threads_cleaned = True
                break

@persistent
def start_live_link(scene):
    threading.Thread(target=receive_data, args=()).start()
    threading.Thread(target=cleanup_threads, args=()).start()
    bpy.app.timers.register(obj_data_monitor)

def register():
    bpy.app.handlers.load_post.append(start_live_link)

def unregister():
    bpy.app.handlers.load_post.remove(start_live_link)