from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True)

    if not req:
        return jsonify({
            "fulfillmentText": "No se recibió información válida."
        })

    params = req.get("queryResult", {}).get("parameters", {})

    vacante = params.get("vacante_nombre", "")
    ciudad = params.get("estado_mexico", "")
    modalidad = params.get("tipo_modalidad", "")
    dias = params.get("dias_laborales", "")

    # Construcción de términos de búsqueda
    ciudad = ciudad.title()

keywords = [vacante]

if modalidad.lower() in ["remoto", "home office"]:
    keywords.append(modalidad)

search_terms = " ".join(keywords)

query = urllib.parse.urlencode({
    "q": search_terms,
    "l": ciudad,
    "fromage": "7",
    "sort": "date"
})

    indeed_url = f"https://mx.indeed.com/jobs?{query}"

    response_text = (
        "🔍 **Resultados reales encontrados en Indeed**\n\n"
        f"📌 Vacante: {vacante or 'No especificado'}\n"
        f"📍 Ubicación: {ciudad or 'No especificado'}\n"
        f"🏢 Modalidad: {modalidad or 'No especificado'}\n"
        f"🗓️ Días: {dias or 'No especificado'}\n\n"
        "👉 Ver vacantes disponibles:\n"
        f"{indeed_url}"
    )

    return jsonify({
        "fulfillmentText": response_text
    })


@app.route("/", methods=["GET"])
def home():
    return "Bot de empleo activo 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
