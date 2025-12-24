from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

# Estados de México (normalizados)
ESTADOS_MEXICO = {
    "aguascalientes", "baja california", "baja california sur", "campeche",
    "chiapas", "chihuahua", "coahuila", "colima", "durango",
    "guanajuato", "guerrero", "hidalgo", "jalisco", "mexico",
    "estado de mexico", "michoacan", "morelos", "nayarit",
    "nuevo leon", "oaxaca", "puebla", "queretaro",
    "quintana roo", "san luis potosi", "sinaloa", "sonora",
    "tabasco", "tamaulipas", "tlaxcala", "veracruz",
    "yucatan", "zacatecas", "cdmx", "ciudad de mexico"
}

def normalizar(texto):
    return texto.lower().strip()

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    query_result = req.get("queryResult", {})
    params = query_result.get("parameters", {})
    contexts = query_result.get("outputContexts", [])
    session = req.get("session")
    user_text = normalizar(query_result.get("queryText", ""))

    def get_value(param):
        if isinstance(param, list):
            return param[0] if param else ""
        return param or ""

    def has_context(name):
        return any(name in c.get("name", "") for c in contexts)

    vacante = get_value(params.get("vacante_nombre"))
    ciudad = get_value(params.get("estado_mexico"))
    modalidad = get_value(params.get("tipo_modalidad"))
    sueldo = get_value(params.get("sueldo_minimo"))

    # 1️⃣ Puesto
    if not vacante:
        return respuesta(
            "¿Qué puesto estás buscando? 👀\nEjemplo: chofer, jefe de logística",
            session,
            "esperando_vacante"
        )

    # 2️⃣ Ciudad (validación real México)
    if not ciudad:
        if has_context("esperando_ciudad") and user_text:
            if user_text in ESTADOS_MEXICO:
                ciudad = user_text
            else:
                return respuesta(
                    "No reconocí esa ciudad 😅\nEscribe un estado de México.\nEjemplo: Puebla, CDMX, Jalisco",
                    session,
                    "esperando_ciudad",
                    vacante=vacante
                )
        else:
            return respuesta(
                f"¿En qué estado de México buscas trabajo como *{vacante}*?",
                session,
                "esperando_ciudad",
                vacante=vacante
            )

    # 3️⃣ Modalidad
    if not modalidad:
        if has_context("esperando_modalidad") and user_text:
            if "remot" in user_text:
                modalidad = "remoto"
            elif "hibrid" in user_text:
                modalidad = "híbrido"
            elif "presen" in user_text:
                modalidad = "presencial"
            else:
                return respuesta(
                    "Elige una modalidad:\n🏢 Presencial\n🏠 Remoto\n🔄 Híbrido",
                    session,
                    "esperando_modalidad",
                    vacante=vacante,
                    ciudad=ciudad
                )
        else:
            return respuesta(
                "¿Qué modalidad prefieres?\n🏢 Presencial\n🏠 Remoto\n🔄 Híbrido",
                session,
                "esperando_modalidad",
                vacante=vacante,
                ciudad=ciudad
            )

    # 4️⃣ Sueldo
    if not sueldo:
        return respuesta(
            "¿Cuál es el sueldo mensual mínimo que buscas? 💰\nEjemplo: 15000",
            session,
            "esperando_sueldo",
            vacante=vacante,
            ciudad=ciudad,
            modalidad=modalidad
        )

    # 5️⃣ Búsqueda final
    query = urllib.parse.urlencode({
        "q": f"{vacante} {modalidad}",
        "l": ciudad,
        "fromage": "7",
        "sort": "date"
    })

    indeed_url = f"https://mx.indeed.com/jobs?{query}"

    texto_final = (
        "🔍 **Resultados reales encontrados en Indeed**\n\n"
        f"📌 Vacante: {vacante}\n"
        f"📍 Ubicación: {ciudad.title()}\n"
        f"🏢 Modalidad: {modalidad}\n"
        f"💰 Sueldo deseado: ${sueldo}\n\n"
        f"👉 Ver vacantes recientes:\n{indeed_url}"
    )

    return jsonify({"fulfillmentText": texto_final})


def respuesta(texto, session, contexto, **params):
    return jsonify({
        "fulfillmentText": texto,
        "outputContexts": [{
            "name": f"{session}/contexts/{contexto}",
            "lifespanCount": 5,
            "parameters": params
        }]
    })


if __name__ == "__main__":
    app.run()
