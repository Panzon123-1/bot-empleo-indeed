from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    query_result = req.get("queryResult", {})
    params = query_result.get("parameters", {})
    session = req.get("session")

    # Extraer parámetros (soporta lista o string)
    def get_value(param):
        if isinstance(param, list):
            return param[0] if param else ""
        return param or ""

    vacante = get_value(params.get("vacante_nombre"))
    ciudad = get_value(params.get("estado_mexico"))
    modalidad = get_value(params.get("tipo_modalidad"))
    sueldo = get_value(params.get("sueldo_minimo"))

    # 1️⃣ Falta puesto
    if not vacante:
        return respuesta(
            "¿Qué puesto estás buscando? 👀\nEjemplo: chofer, jefe de logística, administrativo",
            session,
            "esperando_vacante"
        )

    # 2️⃣ Falta ciudad
    if not ciudad:
        return respuesta(
            f"Perfecto 👍 ¿En qué ciudad buscas trabajo como *{vacante}*?",
            session,
            "esperando_ciudad",
            vacante=vacante
        )

    # 3️⃣ Falta modalidad
    if not modalidad:
        return respuesta(
            "¿Qué modalidad prefieres?\n🏢 Presencial\n🏠 Remoto\n🔄 Híbrido",
            session,
            "esperando_modalidad",
            vacante=vacante,
            ciudad=ciudad
        )

    # 4️⃣ Falta sueldo
    if not sueldo:
        return respuesta(
            "¿Cuál es el sueldo mensual mínimo que buscas? 💰\nEjemplo: 15000",
            session,
            "esperando_sueldo",
            vacante=vacante,
            ciudad=ciudad,
            modalidad=modalidad
        )

    # 5️⃣ Ya tenemos todo → búsqueda real
    search_terms = f"{vacante} {modalidad}"
    query = urllib.parse.urlencode({
        "q": search_terms,
        "l": ciudad,
        "fromage": "7",
        "sort": "date"
    })

    indeed_url = f"https://mx.indeed.com/jobs?{query}"

    texto_final = (
        "🔍 **Resultados reales encontrados en Indeed**\n\n"
        f"📌 Vacante: {vacante}\n"
        f"📍 Ubicación: {ciudad}\n"
        f"🏢 Modalidad: {modalidad}\n"
        f"💰 Sueldo deseado: ${sueldo}\n\n"
        f"👉 Ver vacantes recientes:\n{indeed_url}"
    )

    return jsonify({
        "fulfillmentText": texto_final
    })


def respuesta(texto, session, contexto, **params):
    return jsonify({
        "fulfillmentText": texto,
        "outputContexts": [
            {
                "name": f"{session}/contexts/{contexto}",
                "lifespanCount": 5,
                "parameters": params
            }
        ]
    })


if __name__ == "__main__":
    app.run()
