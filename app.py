from flask import Flask, request
from datetime import datetime
import requests

app = Flask(__name__)

visitas = []

def obtener_pais(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        return res.get("country", "Desconocido")
    except:
        return "Desconocido"

@app.route("/")
def inicio():
    ip = request.remote_addr
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pais = obtener_pais(ip)

    visitas.append({
        "ip": ip,
        "fecha": fecha,
        "pais": pais
    })

    return f"""
    <h1>Bienvenido</h1>
    <p>Tu IP es: {ip}</p>
    <p>País: {pais}</p>
    """

@app.route("/admin")
def admin():
    tabla = ""
    for v in visitas:
        tabla += f"<tr><td>{v['ip']}</td><td>{v['fecha']}</td><td>{v['pais']}</td></tr>"

    return f"""
    <h1>Panel de Visitas</h1>
    <table border="1">
        <tr>
            <th>IP</th>
            <th>Fecha</th>
            <th>País</th>
        </tr>
        {tabla}
    </table>
    """

import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
