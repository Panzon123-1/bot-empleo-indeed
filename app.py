from flask import Flask, request, jsonify
import urllib.parse

app = Flask(__name__)

ESTADOS = [
    "aguascalientes","baja california","baja california sur","campeche","chiapas",
    "chihuahua","cdmx","ciudad de mexico","coahuila","colima","durango",
    "estado de mexico","edomex","guanajuato","guerrero","hidalgo","jalisco",
    "michoacan","morelos","nayarit","nuevo leon","oaxaca","puebla","queretaro",
    "quintana roo","san luis potosi","sinaloa","sonora","tabasco","tamaulipas",
    "tlaxcala","veracruz","yucatan","zacatecas"
]

MODALIDADES = ["presencial", "remoto", "hibrido", "híbrido"]

def norm(t):
    return t.lower().strip()

def get_ctx(contexts, name):
    for c in contexts:
        if name in c["name"]:
            return c
    return None

def responder(texto, session, paso, data):
    return jsonify({
        "fulfillmentText": texto,
        "outputContexts": [{
            "name": f"{session}/contexts/flujo",
            "lifespanCount": 10,
            "parameters": {
                "paso": paso,
                **data
            }
        }]
    })

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    session = req["session"]
    texto = norm(req["queryResult"]["queryText"])
    contexts = req["queryResult"].get("outputContexts", [])

    flujo = get_ctx(contexts, "flujo")
    paso = flujo["parameters"].get("paso") if flujo else None
    data = flujo["parameters"] if flujo else {}

    # 🔹 INICIO INTELIGENTE
    if not paso:
        if texto in ESTADOS:
            data["ciudad"] = texto
            return responder(
                "Perfecto 👍 ¿Qué puesto estás buscando?",
                session,
                "vacante",
                data
            )
        else:
            data["vacante"] = texto
            return responder(
                "¿En qué estado de México buscas trabajo?",
                session,
                "ciudad",
                data
            )

    # 🔹 CIUDAD
    if paso == "ciudad":
        if texto not in ESTADOS:
            return responder(
                "No reconocí ese estado 😅\nEjemplo: Puebla, CDMX, Jalisco",
                session,
                "ciudad",
                data
            )
        data["ciudad"] = texto
        return responder(
            "¿Qué modalidad prefieres?\nPresencial, Remoto o Híbrido",
            session,
            "modalidad",
            data
        )

    # 🔹 VACANTE
    if paso == "vacante":
        data["vacante"] = texto
        return responder(
            "¿Qué modalidad prefieres?\nPresencial, Remoto o Híbrido",
            session,
            "modalidad",
            data
        )

    # 🔹 MODALIDAD
    if paso == "modalidad":
        if texto not in MODALIDADES:
            return responder(
                "Escribe: Presencial, Remoto o Híbrido",
                session,
                "modalidad",
                data
            )
        data["modalidad"] = texto
        return responder(
            "¿Cuál es el sueldo mínimo mensual que buscas? 💰\nEjemplo: 15000",
            session,
            "sueldo",
            data
        )

    # 🔹 SUELDO
    if paso == "sueldo":
        try:
            sueldo = int(texto)
        except:
            return responder(
                "Escribe solo el número del sueldo 🙂",
                session,
                "sueldo",
                data
            )

        query = urllib.parse.urlencode({
            "q": f"{data['vacante']} {data['modalidad']}",
            "l": data["ciudad"]
        })

        return jsonify({
            "fulfillmentText":
                f"🔍 Vacantes encontradas:\n\n"
                f"📌 {data['vacante']}\n"
                f"📍 {data['ciudad']}\n"
                f"🏢 {data['modalidad']}\n"
                f"💰 Desde ${sueldo}\n\n"
                f"https://mx.indeed.com/jobs?{query}"
        })

if __name__ == "__main__":
    app.run(port=5000)
