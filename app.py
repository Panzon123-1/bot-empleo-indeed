from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

def get_value(param):
    if isinstance(param, list) and len(param) > 0:
        return param[0]
    return param or ""

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    params = req.get("queryResult", {}).get("parameters", {})

    vacante = get_value(params.get("vacante_nombre"))
    ciudad = get_value(params.get("estado_mexico"))
    modalidad = get_value(params.get("tipo_modalidad"))
    dias = get_value(params.get("dias_laborales"))
    sueldo = get_value(params.get("sueldo_minimo"))

    search_terms = " ".join(filter(None, [vacante, modalidad]))

    query = urllib.parse.urlencode({
        "q": search_terms,
        "l": ciudad,
        "fromage": 7,
        "sort": "date"
    })

    indeed_url = f"https://mx.indeed.com/jobs?{query}"

    response_text = (
        "🔍 **Resultados reales encontrados en Indeed**\n\n"
        f"📌 Vacante: {vacante or 'Cualquiera'}\n"
        f"📍 Ubicación: {ciudad or 'México'}\n"
        f"🏢 Modalidad: {modalidad or 'Cualquiera'}\n"
        f"🗓️ Días: {dias or 'Cualquiera'}\n"
        f"💰 Sueldo mínimo: ${sueldo or 'No especificado'}\n\n"
        f"👉 Ver vacantes recientes:\n{indeed_url}"
    )

    return jsonify({
        "fulfillmentText": response_text
    })

if __name__ == "__main__":
    app.run()
