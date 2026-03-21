from flask import Flask, request, Response
from datetime import datetime
import requests
import os

app = Flask(__name__)

visitas = []

# 🔐 Credenciales
USUARIO = os.environ.get("USER", "admin")
PASSWORD = os.environ.get("PASS", "1234")

# 🔐 Auth
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

# 🌐 IP real
def obtener_ip_real():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return ip.split(',')[0].strip()

# 🌍 Info IP
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
        return {"pais":"?","ciudad":"?","isp":"?","lat":0,"lon":0}

# 📱 Detectar dispositivo
def detectar_dispositivo(user_agent):
    ua = user_agent.lower()
    if "mobile" in ua:
        return "📱 Móvil"
    elif "tablet" in ua:
        return "📟 Tablet"
    else:
        return "💻 PC"

# 🏠 Página principal (404)
@app.route("/")
def inicio():
    ip = obtener_ip_real()
    tipo = "IPv6" if ":" in ip else "IPv4"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info = obtener_info_ip(ip)

    user_agent = request.headers.get('User-Agent', 'N/A')
    idioma = request.headers.get('Accept-Language', 'N/A')
    referer = request.headers.get('Referer', 'Directo')

    dispositivo = detectar_dispositivo(user_agent)

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
        "mapa": mapa,
        "user_agent": user_agent,
        "idioma": idioma,
        "referer": referer,
        "dispositivo": dispositivo
    })

    return "<h1>404 Not Found</h1>", 404

# 🔐 Panel admin
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
            <td><a href="{v['mapa']}" target="_blank">🌎</a></td>
            <td>{v['dispositivo']}</td>
            <td>{v['idioma']}</td>
            <td>{v['referer']}</td>
            <td style="max-width:200px;overflow:auto;">{v['user_agent']}</td>
        </tr>
        """

    return f"""
    <h1>Panel Avanzado 🔐</h1>
    <table border="1">
        <tr>
            <th>IP</th>
            <th>Tipo</th>
            <th>Fecha</th>
            <th>País</th>
            <th>Ciudad</th>
            <th>ISP</th>
            <th>Coords</th>
            <th>Mapa</th>
            <th>Dispositivo</th>
            <th>Idioma</th>
            <th>Referer</th>
            <th>User-Agent</th>
        </tr>
        {tabla}
    </table>
    """

# 🚀 Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
