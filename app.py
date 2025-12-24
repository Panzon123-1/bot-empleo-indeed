from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

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


def obtener_contexto(contexts, nombre):
    for c in contexts:
        if nombre in c["name"]:
            return c
    return None


def respuesta(texto, session, contexto, **params):
    return jsonify({
        "fulfillmentText": texto,
        "outputContexts": [{
            "name": f"{session}/contexts/{contexto}",
            "lifespanCount": 5,
            "parameters": params
        }]
    })


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    query = req["queryResult"]
    session = req["session"]

    texto = normalizar(query.get("queryText", ""))
    params = query.get("parameters", {})
    contexts = query.get("outputContexts", [])

    ctx_vacante = obtener_contexto(contexts, "esperando_vacante")
    ctx_ciudad = obtener_contexto(contexts, "esperando_ciudad")
    ctx_modalidad = obtener_contexto(contexts, "esperando_modalidad")
    ctx_sueldo = obtener_contexto(contexts, "esperando_sueldo")

    vacante = params.get("vacante_nombre") or (ctx_ciudad and ctx_ciudad["parameters"].get("vacante"))
    ciudad = ctx_modalidad and ctx_modalidad["parameters"].get("ciudad")
    modalidad = ctx_sueldo and ctx_sueldo["parameters"].get("modalidad")
    sueldo = None

    # 1️⃣ PUESTO
    if not vacante:
        return respuesta(
            "¿Qué puesto estás buscando? 👀\nEjemplo: chofer, jefe de logística",
            session,
            "esperando_vacante"
        )

    if ctx_vacante:
        vacante = texto
        return respuesta(
            f"Perfecto 👍 ¿En qué estado de México buscas trabajo como *{vacante}*?",
            session,
            "esperando_ciudad",
            vacante=vacante
        )

    # 2️⃣ CIUDAD
    if ctx_ciudad and not ciudad:
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

    # 3️⃣ MODALIDAD
    if ctx_modalidad and not modalidad:
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

    # 4️⃣ SUELDO
    if ctx_sueldo:
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

        query_url = urllib.parse.urlencode({
            "q": f"{vacante} {modalidad}",
            "l": ciudad,
            "fromage": "7",
            "sort": "date"
        })

        url = f"https://mx.indeed.com/jobs?{query_url}"

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
