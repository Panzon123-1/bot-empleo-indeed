from flask import Flask, request, jsonify
import re
import unicodedata
import urllib.parse

app = Flask(__name__)

# =========================
# NORMALIZAR TEXTO
# =========================
def normalize(text):
    text = text.lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    return text.strip()

# =========================
# ESTADOS MÉXICO
# =========================
ESTADOS = {
    "aguascalientes","baja california","baja california sur","campeche","coahuila",
    "colima","chiapas","chihuahua","ciudad de mexico","cdmx","durango","guanajuato",
    "guerrero","hidalgo","jalisco","estado de mexico","mexico","michoacan","morelos",
    "nayarit","nuevo leon","oaxaca","puebla","queretaro","quintana roo","san luis potosi",
    "sinaloa","sonora","tabasco","tamaulipas","tlaxcala","veracruz","yucatan","zacatecas"
}

def detect_estado(text):
    for e in ESTADOS:
        if e in text:
            if e == "cdmx":
                return "Ciudad de México"
            if e == "mexico":
                return "Estado de México"
            return e.title()
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
    match = re.search(r'\b(\d{4,6})\b', text)
    if match:
        return match.group(1)
    match = re.search(r'\b(\d+)\s*(mil|k)\b', text)
    if match:
        return str(int(match.group(1)) * 1000)
    return ""

# =========================
# EXTRAER VACANTE (ROBUSTO)
# =========================
def extract_vacante(text, estado, modalidad, sueldo):
    clean = text

    if estado:
        clean = clean.replace(normalize(estado), "")
    if modalidad:
        clean = clean.replace(modalidad, "")
    if sueldo:
        clean = clean.replace(sueldo, "")

    # eliminar frases comunes, NO estructurales
    clean = re.sub(
        r'\b(busco|empleo|trabajo|vacante|puesto|quiero)\b',
        '',
        clean
    )

    # eliminar frases de sueldo
    clean = re.sub(
        r'\bal mes\b|\bmensual(es)?\b|\bpesos\b|\bmxn\b',
        '',
        clean
    )

    clean = re.sub(r'\s{2,}', ' ', clean)

    return clean.strip()

# =========================
# WEBHOOK
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    text_raw = req.get("queryResult", {}).get("queryText", "")
    session = req.get("session")

    text = normalize(text_raw)

    estado = detect_estado(text)
    modalidad = detect_modalidad(text)
    sueldo = detect_sueldo(text)
    vacante = extract_vacante(text, estado, modalidad, sueldo)

    # =========================
    # FLUJO HUMANO
    # =========================
    if not vacante and not estado:
        return simple_response(
            "¿Qué empleo buscas o en qué estado deseas trabajar?\n"
            "Ejemplos:\n"
            "• Puebla\n"
            "• Chofer en Jalisco\n"
            "• Gestor de cobranza en Oaxaca",
            session
        )

    if vacante and not estado:
        return simple_response(
            f"Perfecto 👍 ¿En qué estado buscas trabajo como *{vacante}*?",
            session
        )

    # =========================
    # INDEED
    # =========================
    params = {
        "q": vacante,
        "l": estado,
        "fromage": "7",
        "sort": "date"
    }

    indeed_url = f"https://mx.indeed.com/jobs?{urllib.parse.urlencode(params)}"

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

def simple_response(text, session):
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
