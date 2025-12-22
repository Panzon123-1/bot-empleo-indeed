from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    params = req.get("queryResult", {}).get("parameters", {})

    # Parámetros (pueden venir vacíos)
    vacante = params.get("vacante_nombre", "")
    ciudad = params.get("estado_mexico", "")
    modalidad = params.get("tipo_modalidad", "")
    dias = params.get("dias_laborales", "")

    # Normalizar valores (por si vienen como listas)
    if isinstance(vacante, list): vacante = vacante[0]
    if isinstance(ciudad, list): ciudad = ciudad[0]
    if isinstance(modalidad, list): modalidad = modalidad[0]
    if isinstance(dias, list): dias = dias[0]

    # 🔎 CASO 1: Usuario no dijo NADA útil
    if not any([vacante, ciudad, modalidad, dias]):
        return jsonify({
            "fulfillmentText": (
                "👋 Puedo ayudarte a encontrar empleo.\n\n"
                "Dime por ejemplo:\n"
                "• Vacante (chofer, vendedor, repartidor)\n"
                "• Ciudad\n"
                "• Modalidad (presencial, remoto)\n\n"
                "Ejemplo: *Busco trabajo de chofer presencial en Puebla*"
            )
        })

    # 🔎 Construcción de búsqueda
    search_terms = vacante
    if modalidad:
        search_terms = f"{search_terms} {modalidad}".strip()

    query = urllib.parse.urlencode({
        "q": search_terms,
        "l": ciudad
    })

    indeed_url = f"https://mx.indeed.com/jobs?{query}"

    # ✅ RESPUESTA FINAL
    response_text = (
        "🔍 **Resultados encontrados en Indeed**\n\n"
        f"📌 Vacante: {vacante or 'Cualquiera'}\n"
        f"📍 Ubicación: {ciudad or 'México'}\n"
        f"🏢 Modalidad: {modalidad or 'No especificada'}\n"
        f"🗓️ Días: {dias or 'No especificado'}\n\n"
        f"👉 Ver vacantes disponibles:\n{indeed_url}"
    )

    return jsonify({
        "fulfillmentText": response_text
    })

if __name__ == "__main__":
    app.run()
