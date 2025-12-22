from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

def limpiar(valor):
    """
    Limpia valores que pueden venir como lista, None o con comillas raras
    """
    if isinstance(valor, list):
        return valor[0]
    if not valor:
        return ""
    return str(valor).replace('"', '').strip()


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    params = req.get("queryResult", {}).get("parameters", {})

    # 🔹 Limpiar parámetros
    vacante = limpiar(params.get("vacante_nombre"))
    ciudad = limpiar(params.get("estado_mexico"))
    modalidad = limpiar(params.get("tipo_modalidad"))
    dias = limpiar(params.get("dias_laborales"))

    # 🔹 Construcción inteligente de búsqueda
    search_terms = []

    if vacante:
        search_terms.append(vacante)

    if modalidad:
        search_terms.append(modalidad)

    query = urllib.parse.urlencode({
        "q": " ".join(search_terms),
        "l": ciudad,
        "fromage": 7,     # últimos 7 días
        "sort": "date"    # más recientes primero
    })

    indeed_url = f"https://mx.indeed.com/jobs?{query}"

    # 🔹 Texto final del bot
    response_text = (
        "🔍 **Resultados reales encontrados en Indeed**\n\n"
        f"📌 Vacante: {vacante or 'Cualquiera'}\n"
        f"📍 Ubicación: {ciudad or 'México'}\n"
        f"🏢 Modalidad: {modalidad or 'Cualquiera'}\n"
        f"🗓️ Días: {dias or 'Cualquiera'}\n\n"
        "👉 Ver vacantes recientes:\n"
        f"{indeed_url}"
    )

    return jsonify({
        "fulfillmentText": response_text
    })


if __name__ == "__main__":
    app.run()
