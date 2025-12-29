from flask import Flask, request, jsonify
from parser import parse_text
import urllib.parse

app = Flask(__name__)


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
        r'\b(busco|empleo|trabajo|vacante|puesto|quiero|en)\b',
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


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    text = req.get("message", "").strip()

    if not text:
        return jsonify({"text": "Escribe la vacante o ciudad que deseas buscar."})

    data = parse_text(text)

    vacante = data.get("vacante")
    ciudad = data.get("ciudad")
    sueldo = data.get("sueldo")
    modalidad = data.get("modalidad")

    # ======================
    # FLUJO HUMANO
    # ======================
    if not vacante and not ciudad:
        return jsonify({
            "text": (
                "¿Qué empleo buscas o en qué ciudad deseas trabajar?\n\n"
                "Ejemplos:\n"
                "• Puebla\n"
                "• Chofer en Colima\n"
                "• Gestor de cobranza en Oaxaca 10000"
            )
        })

    if vacante and not ciudad:
        return jsonify({
            "text": f"Perfecto 👍 ¿En qué ciudad buscas trabajo como *{vacante}*?"
        })

    # ======================
    # LINK INDEED
    # ======================
    params = {
        "q": vacante if vacante else "",
        "l": ciudad,
        "sort": "date"
    }

    url = f"https://mx.indeed.com/jobs?{urllib.parse.urlencode(params)}"

    response = (
        "🔍 **Resultados encontrados**\n\n"
        f"📌 Vacante: {vacante if vacante else 'Todas'}\n"
        f"📍 Ciudad: {ciudad}\n"
    )

    if sueldo:
        response += f"💰 Sueldo deseado: ${sueldo}\n"
    if modalidad:
        response += f"🏢 Modalidad: {modalidad}\n"

    response += f"\n👉 Ver vacantes:\n{url}\n\n"
    response += (
        "¿Deseas refinar la búsqueda?\n"
        "Puedes indicar:\n"
        "• Sueldo\n"
        "• Modalidad\n"
        "• Tipo de empleo\n"
        "• Industria"
    )

    return jsonify({"text": response})


if __name__ == "__main__":
    app.run(debug=True)
