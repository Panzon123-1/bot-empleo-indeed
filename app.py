from flask import Flask, request, jsonify
import re
import unicodedata
import urllib.parse

app = Flask(__name__)

# =========================
# NORMALIZACIÓN
# =========================
def normalize(text):
    text = text.lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    return text.strip()

# =========================
# ESTADOS DE MÉXICO
# =========================
ESTADOS = {
    "aguascalientes","baja california","baja california sur","campeche","coahuila",
    "colima","chiapas","chihuahua","ciudad de mexico","cdmx","durango","guanajuato",
    "guerrero","hidalgo","jalisco","estado de mexico","mexico","michoacan","morelos",
    "nayarit","nuevo leon","oaxaca","puebla","queretaro","quintana roo","san luis potosi",
    "sinaloa","sonora","tabasco","tamaulipas","tlaxcala","veracruz","yucatan","zacatecas"
}

def detect_estado(text):
    for estado in ESTADOS:
        if estado in text:
            if estado == "cdmx":
                return "Ciudad de México"
            if estado == "mexico":
                return "Estado de México"
            return estado.title()
    return ""

# =========================
# MODALIDAD
# =========================
def detect_modalidad(text):
    if "remoto" in text or "home office" in text:
        return "remoto"
    if "hibrido" in text:
        return "hibrido"
    if "presencial" in text:
        return "presencial"
    return ""

# =========================
# SUELDO
# =========================
def detect_sueldo(text):
    text = text.replace(",", "")
    match = re.search(r'\$?\b(\d{4,6})\b', text)
    if match:
        return match.group(1)
    match = re.search(r'\b(\d+)\s?k\b', text)
    if match:
        return str(int(match.group(1)) * 1000)
    match = re.search(r'\b(\d+)\s*mil\b', text)
    if match:
        return str(int(match.group(1)) * 1000)
    return ""

# =========================
# LIMPIAR TEXTO PARA VACANTE
# =========================
def extract_vacante(text, estado, modalidad, sueldo):
    clean = text

    if estado:
        clean = clean.replace(normalize(estado), "")
    if modalidad:
        clean = clean.replace(modalidad, "")
    if sueldo:
        clean = clean.replace(sueldo, "")

    # eliminar frases de sueldo comunes
    clean = re.sub(r'\bal mes\b|\bmensual(es)?\b|\bmxn\b|\bpesos\b', '', clean)

    # eliminar frases genéricas
    clean = re.sub(r'\b(busco|empleo|trabajo|vacante|puesto)\b', '', clean)

    return clean.strip()

# =========================
# WEBHOOK
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    query = req.get("queryResult", {}).get("queryText", "")
    session = req.get("session")

    text = normalize(query)

    estado = detect_estado(text)
    modalidad = detect_modalidad(text)
    sueldo = detect_sueldo(text)
    vacante = extract_vacante(text, estado, modalidad, sueldo)

    # =========================
    # FLUJO CONVERSACIONAL
    # =========================
    if not vacante and not estado:
        return respond(
            "¿Qué empleo buscas o en qué estado deseas trabajar?\nEjemplos:\n• Puebla\n• Chofer en Jalisco\n• Gestor de cobranza en Oaxaca",
            session
        )

    if vacante and not estado:
        return respond(
            f"Perfecto 👍 ¿En qué estado de México buscas trabajo como *{vacante}*?",
            session
        )

    # =========================
    # BÚSQUEDA INDEED
    # =========================
    search_terms = vacante if vacante else ""
    query_params = {
        "q": search_terms,
        "l": estado,
        "fromage": "7",
        "sort": "date"
    }

    indeed_url = f"https://mx.indeed.com/jobs?{urllib.parse.urlencode(query_params)}"

    response = (
        "🔍 **Resultados reales encontrados en Indeed**\n\n"
        f"📌 Vacante: {vacante if vacante else 'Todas'}\n"
        f"📍 Ubicación: {estado}\n"
    )

    if modalidad:
        response += f"🏢 Modalidad: {modalidad}\n"
    if sueldo:
        response += f"💰 Sueldo deseado: ${sueldo}\n"

    response += f"\n👉 Ver vacantes recientes:\n{indeed_url}"

    return jsonify({"fulfillmentText": response})


def respond(text, session):
    return jsonify({
        "fulfillmentText": text,
        "outputContexts": [
            {
                "name": f"{session}/contexts/flujo",
                "lifespanCount": 5
            }
        ]
    })


if __name__ == "__main__":
    app.run()
