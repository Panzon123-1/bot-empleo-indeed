from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    params = req.get("queryResult", {}).get("parameters", {})

    vacante = params.get("vacante_nombre", "")
    ciudad = params.get("estado_mexico", "")
    modalidad = params.get("tipo_modalidad", "")
    dias = params.get("dias_laborales", "")

    # Construir búsqueda
    search_terms = " ".join(filter(None, [vacante, modalidad]))
    query = urllib.parse.urlencode({
        "q": search_terms,
        "l": ciudad
    })

    indeed_url = f"https://mx.indeed.com/jobs?{query}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(indeed_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        cards = soup.select("a.tapItem")[:5]

        for card in cards:
            titulo = card.select_one("h2 span")
            empresa = card.select_one(".companyName")
            ubicacion = card.select_one(".companyLocation")
            link = "https://mx.indeed.com" + card.get("href")

            results.append(
                f"• {titulo.text.strip() if titulo else 'Vacante'}\n"
                f"  Empresa: {empresa.text.strip() if empresa else 'No visible'}\n"
                f"  Ubicación: {ubicacion.text.strip() if ubicacion else 'No visible'}\n"
                f"  👉 {link}\n"
            )

        if results:
            texto_resultados = "\n".join(results)
        else:
            texto_resultados = "No encontré vacantes recientes con esos criterios."

    except Exception as e:
        texto_resultados = "Ocurrió un error al buscar vacantes. Intenta más tarde."

    respuesta = (
        "🔍 Búsqueda de empleo lista\n\n"
    f"📌 Vacante: {vacante or 'No especificado'}\n"
    f"📍 Ubicación: {ciudad or 'No especificado'}\n"
    f"🏢 Modalidad: {modalidad or 'No especificado'}\n"
    f"🗓️ Días laborales: {dias or 'No especificado'}\n\n"
    "👉 Te muestro vacantes reales y actualizadas publicadas en Indeed.\n"
    "Los resultados pueden variar según disponibilidad del día.\n\n"
    "🔗 Ver vacantes disponibles:\n"
    f"{indeed_url}"
)

    return jsonify({
        "fulfillmentText": respuesta
    })


if __name__ == "__main__":
    app.run()
