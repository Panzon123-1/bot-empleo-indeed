from flask import Flask, request, jsonify
import re
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

def extraer_sueldo(texto):
    m = re.search(r"\b(\d{4,6})\b", texto)
    return int(m.group(1)) if m else None

def extraer_estado(texto):
    for e in ESTADOS:
        if e in texto:
            return e
    return None

def extraer_modalidad(texto):
    for m in MODALIDADES:
        if m in texto:
            return m
    return None

def limpiar_texto(texto):
    for e in ESTADOS + MODALIDADES:
        texto = texto.replace(e, "")
    texto = re.sub(r"\d{4,6}", "", texto)
    return texto.strip()

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    session = req["session"]
    texto = norm(req["queryResult"]["queryText"])

    contexts = req["queryResult"].get("outputContexts", [])
    flujo = next((c for c in contexts if "flujo" in c["name"]), None)
    data = flujo["parameters"] if flujo else {}

    # 🔹 EXTRACCIÓN INTELIGENTE
    estado = extraer_estado(texto)
    modalidad = extraer_modalidad(texto)
    sueldo = extraer_sueldo(texto)

    if estado:
        data["ciudad"] = estado
    if modalidad:
        data["modalidad"] = modalidad
    if sueldo:
        data["sueldo"] = sueldo

    posible_vacante = limpiar_texto(texto)
    if posible_vacante and not data.get("vacante"):
        data["vacante"] = posible_vacante

    # 🔹 VALIDACIÓN MÍNIMA
    if not data.get("vacante") or not data.get("ciudad"):
        faltantes = []
        if not data.get("vacante"):
            faltantes.append("puesto")
        if not data.get("ciudad"):
            faltantes.append("estado")

        return jsonify({
            "fulfillmentText":
                f"Para buscar empleo necesito al menos:\n"
                f"👉 {', '.join(faltantes)}\n\n"
                f"Ejemplo:\n"
                f"Director comercial en Puebla",
            "outputContexts": [{
                "name": f"{session}/contexts/flujo",
                "lifespanCount": 10,
                "parameters": data
            }]
        })

    # 🔹 BÚSQUEDA
    query = f"{data['vacante']} {data.get('modalidad','')}".strip()
    url = urllib.parse.urlencode({
        "q": query,
        "l": data["ciudad"]
    })

    respuesta = (
        f"🔍 Vacantes encontradas:\n\n"
        f"📌 Puesto: {data['vacante']}\n"
        f"📍 Estado: {data['ciudad']}\n"
    )

    if data.get("modalidad"):
        respuesta += f"🏢 Modalidad: {data['modalidad']}\n"
    if data.get("sueldo"):
        respuesta += f"💰 Sueldo desde: ${data['sueldo']}\n"

    respuesta += f"\nhttps://mx.indeed.com/jobs?{url}\n\n"
    respuesta += "¿Deseas refinar la búsqueda? (sueldo, modalidad, jornada)"

    return jsonify({
        "fulfillmentText": respuesta,
        "outputContexts": [{
            "name": f"{session}/contexts/flujo",
            "lifespanCount": 10,
            "parameters": data
        }]
    })

if __name__ == "__main__":
    app.run(port=5000)
