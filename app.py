from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    params = req.get("queryResult", {}).get("parameters", {})

    vacante = params.get("vacante_nombre", "")
    ciudad = params.get("estado_mexico", "")
    modalidad = params.get("tipo_modalidad", "")
    dias = params.get("dias_laborales", "")

    # Construcción inteligente de búsqueda
    search_terms = vacante
    if modalidad:
        search_terms = f"{vacante} {modalidad}"

    query = urllib.parse.urlencode({
        "q": search_terms,
        "l": ciudad
    })

    indeed_url = f"https://mx.indeed.com/jobs?{query}"

    response_text = (
        "🔍 **Resultados reales encontrados en Indeed**\n\n"
        f"📌 Vacante: {vacante or 'No especificado'}\n"
        f"📍 Ubicación: {ciudad or 'No especificado'}\n"
        f"🏢 Modalidad: {modalidad or 'No especificado'}\n"
        f"🗓️ Días: {dias or 'No especificado'}\n\n"
        f"👉 Ver vacantes disponibles:\n{indeed_url}"
    )

    return jsonify({
        "fulfillmentText": response_text
    })

if __name__ == "__main__":
    app.run()
