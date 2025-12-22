from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)

    params = req.get("queryResult", {}).get("parameters", {})

    vacante = params.get("vacante_nombre", "").strip()
    ciudad = params.get("estado_mexico", "").strip()
    modalidad = params.get("tipo_modalidad", "").strip()
    dias = params.get("dias_laborales", "").strip()

    # Normalizar ciudad
    ciudad = ciudad.title() if ciudad else ""

    # Construcción inteligente de búsqueda para Indeed
    keywords = []
    if vacante:
        keywords.append(vacante)

    # Solo incluir modalidad si aporta valor a Indeed
    if modalidad.lower() in ["remoto", "home office"]:
        keywords.append(modalidad)

    search_terms = " ".join(keywords)

    # Query optimizada para Indeed
    query = urllib.parse.urlencode({
        "q": search_terms,
        "l": ciudad,
        "fromage": "7",   # Vacantes últimos 7 días
        "sort": "date"    # Más recientes primero
    })

    indeed_url = f"https://mx.indeed.com/jobs?{query}"

    # Respuesta del bot
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

if __name__ == "__main__":
    app.run()
