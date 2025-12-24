from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

# ===============================
# CATÁLOGOS
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


def normalizar(txt):
    return txt.lower().strip()


def get_context_params(contexts, nombre):
    for c in contexts:
        if nombre in c["name"]:
            return c.get("parameters", {})
    return {}


def respuesta(texto, session, contexto, **params):
    return jsonify({
        "fulfillmentText": texto,
        "outputContexts": [{
            "name": f"{session}/contexts/{contexto}",
            "lifespanCount": 5,
            "parameters": params
        }]
    })


# ===============================
# WEBHOOK
# ===============================

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    query = req["queryResult"]
    session = req["session"]

    texto = normalizar(query.get("queryText", ""))
    contexts = query.get("outputContexts", [])

    esperando_vacante = any("esperando_vacante" in c["name"] for c in contexts)
    esperando_ciudad = any("esperando_ciudad" in c["name"] for c in contexts)
    esperando_modalidad = any("esperando_modalidad" in c["name"] for c in contexts)
    esperando_sueldo = any("esperando_sueldo" in c["name"] for c in contexts)

    params = get_context_params(contexts, "esperando")

    vacante = params.get("vacante")
    ciudad = params.get("ciudad")
    modalidad = params.get("modalidad")
    sueldo = params.get("sueldo")

    # ===============================
    # 1️⃣ PUESTO
    # ===============================
    if not vacante:
        return respuesta(
            "¿Qué puesto estás buscando? 👀\nEjemplo: chofer, jefe de logística",
            session,
            "esperando_vacante"
        )

    if esperando_vacante:
        vacante = texto
        return respuesta(
            f"Perfecto 👍 ¿En qué estado de México buscas trabajo como *{vacante}*?",
            session,
            "esperando_ciudad",
            vacante=vacante
        )

    # ===============================
    # 2️⃣ CIUDAD
    # ===============================
    if esperando_ciudad:
        ciudad = texto

        if ciudad not in ESTADOS_MEXICO:
            return respuesta(
                "No reconocí esa ciudad 😅\nEjemplo: Puebla, CDMX, Jalisco",
                session,
                "esperando_ciudad",
                vacante=vacante
            )

        return respuesta(
            "Excelente 👍 ¿Qué modalidad prefieres?\nPresencial, Remoto o Híbrido",
            session,
            "esperando_modalidad",
            vacante=vacante,
            ciudad=ciudad
        )

    # ===============================
    # 3️⃣ MODALIDAD
    # ===============================
    if esperando_modalidad:
        modalidad = texto

        if modalidad not in MODALIDADES:
            return respuesta(
                "Escribe: Presencial, Remoto o Híbrido",
                session,
                "esperando_modalidad",
                vacante=vacante,
                ciudad=ciudad
            )

        return respuesta(
            "¿Cuál es el sueldo mensual mínimo que buscas? 💰\nEjemplo: 15000",
            session,
            "esperando_sueldo",
            vacante=vacante,
            ciudad=ciudad,
            modalidad=modalidad
        )

    # ===============================
    # 4️⃣ SUELDO
    # ===============================
    if esperando_sueldo:
        try:
            sueldo = int(texto)
        except:
            return respuesta(
                "Escribe solo el número del sueldo 😄",
                session,
                "esperando_sueldo",
                vacante=vacante,
                ciudad=ciudad,
                modalidad=modalidad
            )

        query = urllib.parse.urlencode({
            "q": f"{vacante} {modalidad}",
            "l": ciudad,
            "fromage": "7",
            "sort": "date"
        })

        url = f"https://mx.indeed.com/jobs?{query}"

        return jsonify({
            "fulfillmentText":
                f"🔍 **Vacantes encontradas**\n\n"
                f"📌 Puesto: {vacante}\n"
                f"📍 Ubicación: {ciudad}\n"
                f"🏢 Modalidad: {modalidad}\n"
                f"💰 Sueldo mínimo: ${sueldo}\n\n"
                f"👉 {url}"
        })


if __name__ == "__main__":
    app.run()
