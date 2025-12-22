from flask import Flask, request, jsonify
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
    sueldo = params.get("sueldo_minimo", None)

    # ---- Construcción del texto de búsqueda ----
    search_parts = []

    if vacante:
        search_parts.append(vacante)

    if modalidad:
        search_parts.append(modalidad)

    # Manejo del sueldo
    sueldo_info = ""
    if sueldo:
        try:
            sueldo_mensual = int(sueldo)
            sueldo_diario = round(sueldo_mensual / 30)
            search_parts.append(str(sueldo_mensual))
            search_parts.append(f"{sueldo_diario} diarios")
            sueldo_info = f"${sueldo_mensual} MXN aprox."
        except:
            sueldo_info = "No especificado"
    else:
        sueldo_info = "No especificado"

    search_terms = " ".join(search_parts)

    # ---- Query Indeed ----
    query = urllib.parse.urlencode({
        "q": search_terms,
        "l": ciudad if ciudad else "México",
        "fromage": 7,
        "sort": "date"
    })

    indeed_url = f"https://mx.indeed.com/jobs?{query}"

    # ---- Respuesta del bot ----
    response_text = (
        "🔍 **Resultados reales encontrados en Indeed**\n\n"
        f"📌 Vacante: {vacante or 'Cualquiera'}\n"
        f"📍 Ubicación: {ciudad or 'México'}\n"
        f"🏢 Modalidad: {modalidad or 'Cualquiera'}\n"
        f"🗓️ Días: {dias or 'Cualquiera'}\n"
        f"💰 Sueldo deseado: {sueldo_info}\n\n"
        f"👉 Ver vacantes recientes:\n{indeed_url}"
    )

    return jsonify({
        "fulfillmentText": response_text
    })

if __name__ == "__main__":
    app.run()
