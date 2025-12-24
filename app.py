from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

# ===============================
# UTILIDADES
# ===============================

ESTADOS_MEXICO = [
    "aguascalientes", "baja california", "baja california sur", "campeche",
    "chiapas", "chihuahua", "cdmx", "ciudad de mexico", "coahuila", "colima",
    "durango", "estado de mexico", "edomex", "guanajuato", "guerrero",
    "hidalgo", "jalisco", "michoacan", "morelos", "nayarit", "nuevo leon",
    "oaxaca", "puebla", "queretaro", "quintana roo", "san luis potosi",
    "sinaloa", "sonora", "tabasco", "tamaulipas", "tlaxcala", "veracruz",
    "yucatan", "zacatecas"
]

MODALIDADES = ["presencial", "remoto", "hibrido", "híbrido"]


def normalizar(texto):
    return texto.lower().strip()


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


# ===============================
# WEBHOOK
# ===============================

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    query_result = req.get("queryResult", {})
    session = req.get("session")
    texto_usuario = normalizar(query_result.get("queryText", ""))

    params = query_result.get("parameters", {})
    contexts = query_result.get("outputContexts", [])
    context_names = [c["name"] for c in contexts]

    def tiene_contexto(nombre):
        return any(nombre in c for c in context_names)

    vacante = params.get("vacante_nombre", "")
    sueldo = params.get("sueldo_minimo", "")

    # ===============================
    # 1️⃣ ESPERANDO VACANTE
    # ===============================
    if tiene_contexto("esperando_vacante") or not vacante:
        vacante = texto_usuario
        return respuesta(
            f"Perfecto 👍 ¿En qué estado de México buscas trabajo como *{vacante}*?",
            session,
            "esperando_ciudad",
            vacante=vacante
        )

    # ===============================
    # 2️⃣ ESPERANDO CIUDAD
    # ===============================
    if tiene_contexto("esperando_ciudad"):
        ciudad = texto_usuario

        if ciudad not in ESTADOS_MEXICO:
            return respuesta(
                "No reconocí esa ciudad 😅\n"
                "Escribe un estado de México.\n"
                "Ejemplo: Puebla, CDMX, Jalisco",
                session,
                "esperando_ciudad",
                vacante=vacante
            )

        return respuesta(
            "Excelente 👍 ¿Qué modalidad prefieres?\n"
            "🏢 Presencial\n"
            "🏠 Remoto\n"
            "🔄 Híbrido",
            session,
            "esperando_modalidad",
            vacante=vacante,
            ciudad=ciudad
        )

    # ===============================
    # 3️⃣ ESPERANDO MODALIDAD
    # ===============================
    if tiene_contexto("esperando_modalidad"):
        modalidad = texto_usuario

        if modalidad not in MODALIDADES:
            return respuesta(
                "No entendí la modalidad 😅\n"
                "Escribe: Presencial, Remoto o Híbrido",
                session,
                "esperando_modalidad",
                vacante=vacante,
                ciudad=params.get("ciudad", "")
            )

        return respuesta(
            "Perfecto 💰 ¿Cuál es el sueldo mensual mínimo que buscas?\n"
            "Ejemplo: 15000",
            session,
            "esperando_sueldo",
            vacante=vacante,
            ciudad=params.get("ciudad", ""),
            modalidad=modalidad
        )

    # ===============================
    # 4️⃣ ESPERANDO SUELDO
    # ===============================
    if tiene_contexto("esperando_sueldo"):
        try:
            sueldo = int(texto_usuario)
        except:
            return respuesta(
                "Escribe solo el número del sueldo 😄\nEjemplo: 15000",
                session,
                "esperando_sueldo",
                vacante=vacante,
                ciudad=params.get("ciudad", ""),
                modalidad=params.get("modalidad", "")
            )

        # ===============================
        # 5️⃣ BÚSQUEDA FINAL
        # ===============================
        search_terms = f"{vacante} {params.get('modalidad', '')}"
        query = urllib.parse.urlencode({
            "q": search_terms,
            "l": params.get("ciudad", ""),
            "fromage": "7",
            "sort": "date"
        })

        indeed_url = f"https://mx.indeed.com/jobs?{query}"

        texto_final = (
            "🔍 **Resultados reales encontrados en Indeed**\n\n"
            f"📌 Vacante: {vacante}\n"
            f"📍 Ubicación: {params.get('ciudad')}\n"
            f"🏢 Modalidad: {params.get('modalidad')}\n"
            f"💰 Sueldo deseado: ${sueldo}\n\n"
            f"👉 Ver vacantes recientes:\n{indeed_url}"
        )

        return jsonify({"fulfillmentText": texto_final})

    # ===============================
    # FALLBACK GENERAL
    # ===============================
    return respuesta(
        "¿Qué puesto estás buscando? 👀\nEjemplo: chofer, jefe de logística",
        session,
        "esperando_vacante"
    )


if __name__ == "__main__":
    app.run()
