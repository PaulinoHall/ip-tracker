from flask import Flask, request
from datetime import datetime
import requests
import os

app = Flask(__name__)

visitas = []

# 🔹 Obtener IP real (compatible con proxies, IPv4 e IPv6)
def obtener_ip_real():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ip = ip.split(',')[0].strip()
    return ip

# 🔹 Obtener info de la IP
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
    ip = obtener_ip_real()

    # Detectar tipo de IP
    if ":" in ip:
        tipo = "IPv6"
    else:
        tipo = "IPv4"

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info = obtener_info_ip(ip)

    visitas.append({
        "ip": ip,
        "tipo": tipo,
        "fecha": fecha,
        "pais": info["pais"],
        "ciudad": info["ciudad"],
        "isp": info["isp"]
    })

    return f"""
    <h1>Bienvenido</h1>
    <p><b>IP:</b> {ip}</p>
    <p><b>Tipo:</b> {tipo}</p>
    <p><b>Ubicación:</b> {info['ciudad']}, {info['pais']}</p>
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
        </tr>
        {tabla}
    </table>
    """

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
