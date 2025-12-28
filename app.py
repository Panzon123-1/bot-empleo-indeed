from flask import Flask, request, jsonify
from parser import parse_text
import urllib.parse

app = Flask(__name__)

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
