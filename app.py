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


def norm(txt):
    return txt.lower().strip()


def ctx(contexts, name):
    for c in contexts:
        if name in c["name"]:
            return c
    return None


def responder(texto, session, contexto, data):
    return jsonify({
        "fulfillmentText": texto,
        "outputContexts": [{
            "name": f"{session}/contexts/{contexto}",
            "lifespanCount": 5,
            "parameters": data
        }]
    })


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    session = req["session"]
    texto = norm(req["queryResult"]["queryText"])
    contexts = req["queryResult"].get("outputContexts", [])

    c_vac = ctx(contexts, "vacante")
    c_ciu = ctx(contexts, "ciudad")
    c_mod = ctx(contexts, "modalidad")
    c_sue = ctx(contexts, "sueldo")

    # 1️⃣ PUESTO
    if not c_vac:
        return responder(
            "¿Qué puesto estás buscando? 👀\nEjemplo: chofer, jefe de logística",
            session,
            "vacante",
            {}
        )

    if c_vac and not c_ciu:
        return responder(
            f"Perfecto 👍 ¿En qué estado de México buscas trabajo como *{texto}*?",
            session,
            "ciudad",
            {"vacante": texto}
        )

    # 2️⃣ CIUDAD
    if c_ciu and not c_mod:
        if texto not in ESTADOS:
            return responder(
                "No reconocí esa ciudad 😅\nEjemplo: Puebla, CDMX, Jalisco",
                session,
                "ciudad",
                c_ciu["parameters"]
            )

        data = c_ciu["parameters"]
        data["ciudad"] = texto
        return responder(
            "¿Qué modalidad prefieres?\nPresencial, Remoto o Híbrido",
            session,
            "modalidad",
            data
        )

    # 3️⃣ MODALIDAD
    if c_mod and not c_sue:
        if texto not in MODALIDADES:
            return responder(
                "Escribe: Presencial, Remoto o Híbrido",
                session,
                "modalidad",
                c_mod["parameters"]
            )

        data = c_mod["parameters"]
        data["modalidad"] = texto
        return responder(
            "¿Cuál es el sueldo mensual mínimo que buscas? 💰\nEjemplo: 15000",
            session,
            "sueldo",
            data
        )

    # 4️⃣ SUELDO
    if c_sue:
        try:
            sueldo = int(texto)
        except:
            return responder(
                "Escribe solo el número del sueldo 🙂",
                session,
                "sueldo",
                c_sue["parameters"]
            )

        d = c_sue["parameters"]

        query = urllib.parse.urlencode({
            "q": f"{d['vacante']} {d['modalidad']}",
            "l": d["ciudad"],
            "fromage": "7",
            "sort": "date"
        })

        return jsonify({
            "fulfillmentText":
                f"🔍 **Vacantes encontradas**\n\n"
                f"📌 Puesto: {d['vacante']}\n"
                f"📍 Ubicación: {d['ciudad']}\n"
                f"🏢 Modalidad: {d['modalidad']}\n"
                f"💰 Sueldo mínimo: ${sueldo}\n\n"
                f"https://mx.indeed.com/jobs?{query}"
        })


if __name__ == "__main__":
    app.run()
