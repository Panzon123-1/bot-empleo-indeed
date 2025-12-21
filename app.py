from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
       req = request.get_json()
    params = req.get("queryResult", {}).get("parameters", {})

    vacante = params.get("vacante_nombre", "")
    ciudad = params.get("estado_mexico", "")
    modalidad = params.get("tipo_modalidad", "")
    dias = params.get("dias_laborales", "")

    import urllib.parse

    search_terms = " ".join(filter(None, [vacante, modalidad]))

    indeed_url = "https://mx.indeed.com/jobs?" + urllib.parse.urlencode({
        "q": search_terms,
        "l": ciudad
    })

    response_text = (
        "🔍 Búsqueda recibida\n"
        f"• Vacante: {vacante or 'No especificado'}\n"
        f"• Ubicación: {ciudad or 'No especificado'}\n"
        f"• Modalidad: {modalidad or 'No especificado'}\n"
        f"• Días laborales: {dias or 'No especificado'}\n\n"
        "👉 Vacantes reales en Indeed:\n"
        f"{indeed_url}"
    )

    return jsonify({
        "fulfillmentText": response_text
    })

        "fulfillmentText": respuesta
    })

if __name__ == "__main__":
    app.run(debug=True)
