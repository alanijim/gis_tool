import psycopg2
from PyQt4.QtGui import QMessageBox

def get_default_path(canvas):
    ip = "localhost"
    for layer in canvas.layers():
        if layer.providerType() == 'postgres':
            uri = layer.source()
            conn_info = uri.split(' ')
            conn_params = {}
            for param in conn_info:
                key, value = param.split('=')
                conn_params[key] = value.strip("'")
            ip = conn_params.get('host', 'localhost')
            break

    QMessageBox.information(None, "Slaac Gathering Tool", ip)
    return f"http://{ip}:9080/slaac"
