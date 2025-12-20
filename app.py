from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def buscar_empleos_indeed(puesto, ciudad):
    url = f"https://mx.indeed.com/jobs?q={puesto}&l={ciudad}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    empleos = []

    for job in soup.select("h2.jobTitle span"):
        empleos.append(job.text.strip())

    return empleos[:5]  # máximo 5 resultados


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    # Extraer parámetros de Dialogflow
    parameters = req.get("queryResult", {}).get("parameters", {})
    tipo_empleo = parameters.get("tipo_empleo")
    ubicacion = parameters.get("location", {}).get("city")

    if not tipo_empleo or not ubicacion:
        return jsonify({
            "fulfillmentText": "Por favor dime el tipo de empleo y la ubicación."
        })

    resultados = buscar_empleos_indeed(tipo_empleo, ubicacion)

    if not resultados:
        texto = "No encontré vacantes recientes con esos criterios."
    else:
        texto = "📌 Vacantes encontradas:\n\n"
        for r in resultados:
            texto += f"- {r}\n"

    return jsonify({
        "fulfillmentText": texto
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

