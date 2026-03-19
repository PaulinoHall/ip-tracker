from flask import Flask, request
from datetime import datetime
import requests
import os

app = Flask(__name__)

visitas = []

# 🔹 Obtener IP real
def obtener_ip_real():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ip = ip.split(',')[0].strip()
    return ip

# 🔹 Obtener información de la IP
def obtener_info_ip(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        return {
            "pais": res.get("country", "Desconocido"),
            "ciudad": res.get("city", "Desconocido"),
            "isp": res.get("isp", "Desconocido"),
            "lat": res.get("lat", 0),
            "lon": res.get("lon", 0)
        }
    except:
        return {
            "pais": "Desconocido",
            "ciudad": "Desconocido",
            "isp": "Desconocido",
            "lat": 0,
            "lon": 0
        }

@app.route("/")
def inicio():
    ip = obtener_ip_real()

    # Detectar tipo de IP
    if ":" in ip:
        tipo = "IPv6"
    else:
        tipo = "IPv4"

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info = obtener_info_ip(ip)

    # Crear link a Google Maps
    mapa = f"https://www.google.com/maps?q={info['lat']},{info['lon']}"

    visitas.append({
        "ip": ip,
        "tipo": tipo,
        "fecha": fecha,
        "pais": info["pais"],
        "ciudad": info["ciudad"],
        "isp": info["isp"],
        "lat": info["lat"],
        "lon": info["lon"],
        "mapa": mapa
    })

    return f"""
    <h1>Bienvenido</h1>
    <p><b>IP:</b> {ip}</p>
    <p><b>Tipo:</b> {tipo}</p>
    <p><b>Ubicación:</b> {info['ciudad']}, {info['pais']}</p>
    <p><b>Coordenadas:</b> {info['lat']}, {info['lon']}</p>
    <p><a href="{mapa}" target="_blank">🌎 Ver en mapa</a></p>
    """

@app.route("/admin")
def admin():
    tabla = ""
    for v in visitas:
        tabla += f"""
        <tr>
            <td>{v['ip']}</td>
            <td>{v['tipo']}</td>
            <td>{v['fecha']}</td>
            <td>{v['pais']}</td>
            <td>{v['ciudad']}</td>
            <td>{v['isp']}</td>
            <td>{v['lat']}, {v['lon']}</td>
            <td><a href="{v['mapa']}" target="_blank">Ver</a></td>
        </tr>
        """

    return f"""
    <h1>Panel PRO 😎</h1>
    <table border="1">
        <tr>
            <th>IP</th>
            <th>Tipo</th>
            <th>Fecha</th>
            <th>País</th>
            <th>Ciudad</th>
            <th>ISP</th>
            <th>Coordenadas</th>
            <th>Mapa</th>
        </tr>
        {tabla}
    </table>
    """

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
