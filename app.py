from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def buscar_empleos_indeed(puesto, ciudad):
    url = f"https://mx.indeed.com/jobs?q={puesto}&l={ciudad}"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    empleos = []
    for job in soup.select("h2.jobTitle span"):
        empleos.append(job.text.strip())

    return empleos


from flask import Flask, request, jsonify

app = Flask(__name__)

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    params = req.get("queryResult", {}).get("parameters", {})

    vacante = params.get("vacante_nombre")
    estado = params.get("estado_mexico")
    modalidad = params.get("tipo_modalidad")
    dias = params.get("dias_laborales")

    if not modalidad:
        return jsonify({
            "fulfillmentText": "¿Qué modalidad prefieres? (presencial, híbrido o remoto)"
        })

    if not dias:
        return jsonify({
            "fulfillmentText": "¿Qué días te gustaría trabajar? (lunes a viernes o lunes a sábado)"
        })

    respuesta = (
        f"🔍 Perfecto, buscaré vacantes reales con estos criterios:\n"
        f"• Vacante: {vacante}\n"
        f"• Ubicación: {estado}\n"
        f"• Modalidad: {modalidad}\n"
        f"• Días laborales: {dias}\n\n"
        "Iniciando búsqueda de empleos reales…"
    )

    return jsonify({
        "fulfillmentText": respuesta
    })

@app.route("/")
def home():
    return "Bot MyJob activo"

def webhook():
    data = request.get_json()

    params = data["queryResult"]["parameters"]
    puesto = params.get("tipo_empleo", "")
    ciudad = params.get("location", {}).get("city", "")

    resultados = buscar_empleos_indeed(puesto, ciudad)

    if not resultados:
        texto = "No encontré vacantes recientes con esos criterios."
    else:
        texto = "📌 Vacantes encontradas:\n\n"
        for r in resultados[:5]:
            texto += f"- {r}\n"

    return jsonify({
        "fulfillmentText": texto
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
