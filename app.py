from flask import Flask, request
from datetime import datetime
import requests
import os

app = Flask(__name__)

visitas = []

def obtener_info_ip(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        return {
            "pais": res.get("country", "Desconocido"),
            "ciudad": res.get("city", "Desconocido"),
            "isp": res.get("isp", "Desconocido")
        }
    except:
        return {
            "pais": "Desconocido",
            "ciudad": "Desconocido",
            "isp": "Desconocido"
        }

@app.route("/")
def inicio():
    # Obtener IP real
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info = obtener_info_ip(ip)

    visitas.append({
        "ip": ip,
        "fecha": fecha,
        "pais": info["pais"],
        "ciudad": info["ciudad"],
        "isp": info["isp"]
    })

    return f"""
    <h1>Bienvenido</h1>
    <p>Tu IP es: {ip}</p>
    <p>{info['ciudad']}, {info['pais']}</p>
    """

@app.route("/admin")
def admin():
    tabla = ""
    for v in visitas:
        tabla += f"""
        <tr>
            <td>{v['ip']}</td>
            <td>{v['fecha']}</td>
            <td>{v['pais']}</td>
            <td>{v['ciudad']}</td>
            <td>{v['isp']}</td>
        </tr>
        """

    return f"""
    <h1>Panel PRO 😎</h1>
    <table border="1">
        <tr>
            <th>IP</th>
            <th>Fecha</th>
            <th>País</th>
            <th>Ciudad</th>
            <th>ISP</th>
        </tr>
        {tabla}
    </table>
    """

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
