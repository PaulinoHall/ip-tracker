from flask import Flask, request
from datetime import datetime
import requests

app = Flask(__name__)

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

    # Guardar en archivo
    with open("visitas.txt", "a") as f:
        f.write(f"{fecha} - {ip} - {pais}\n")

    return f"""
    <h1>Bienvenido</h1>
    <p>Tu IP es: {ip}</p>
    <p>País: {pais}</p>
    """

import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
