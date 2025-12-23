from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    query_result = req.get("queryResult", {})
    parameters = query_result.get("parameters", {})

    # ===== EXTRAER PARÁMETROS =====
    vacante = extract_value(parameters.get("vacante_nombre"))
    ciudad = extract_value(parameters.get("estado_mexico"))
    modalidad = extract_value(parameters.get("tipo_modalidad"))
    dias = extract_value(parameters.get("dias_laborales"))
    sueldo = extract_value(parameters.get("sueldo_minimo"))

    # ===== VALIDACIÓN BÁSICA =====
    if not vacante:
        return jsonify({
            "fulfillmentText": (
                "👀 ¿Qué puesto estás buscando?\n"
                "Ejemplos:\n"
                "- chofer\n"
                "- auxiliar administrativo\n"
                "- vendedor\n"
                "- programador remoto"
            )
        })

    # ===== CONSTRUIR BÚSQUEDA =====
    search_terms = " ".join(
        filter(None, [
            vacante,
            modalidad,
            f"${sueldo}" if sueldo else ""
        ])
    )

    encoded_search = urllib.parse.quote_plus(search_terms)
    encoded_city = urllib.parse.quote_plus(ciudad if ciudad else "México")

    indeed_url = (
        f"https://mx.indeed.com/jobs?"
        f"q={encoded_search}&"
        f"l={encoded_city}&"
        f"fromage=7&sort=date"
    )

    # ===== RESPUESTA AL USUARIO =====
    response_text = (
        "✅ ¡Perfecto! Esto es lo que entendí de tu búsqueda:\n\n"
        f"📌 Puesto: {vacante}\n"
        f"📍 Ubicación: {ciudad or 'México'}\n"
        f"🏢 Modalidad: {modalidad or 'Cualquiera'}\n"
        f"🗓️ Días: {dias or 'Cualquiera'}\n"
        f"💰 Sueldo mínimo: ${sueldo or 'No especificado'} MXN\n\n"
        "🔍 Encontré vacantes reales publicadas recientemente:\n"
        f"👉 {indeed_url}\n\n"
        "📲 ¿Quieres que te avise automáticamente cuando aparezcan nuevas vacantes?"
    )

    return jsonify({
        "fulfillmentText": response_text
    })


def extract_value(value):
    """
    Dialogflow a veces manda strings y a veces listas.
    Esta función normaliza el valor.
    """
    if isinstance(value, list):
        return value[0] if value else None
    return value


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
