from flask import Flask, request, jsonify
import urllib.parse
import re

app = Flask(__name__)

def limpiar(valor):
    """
    Limpia valores que pueden venir como lista, None o con texto raro
    """
    if isinstance(valor, list):
        valor = valor[0]
    if not valor:
        return ""
    return str(valor).replace('"', '').strip()


def limpiar_sueldo(valor):
    """
    Extrae solo números del sueldo (ej. '15 mil pesos' → 15000)
    """
    if not valor:
        return ""

    if isinstance(valor, list):
        valor = valor[0]

    texto = str(valor).lower()

    # Si dice "mil", multiplicamos
    numeros = re.findall(r'\d+', texto)
    if not numeros:
        return ""

    sueldo = int(numeros[0])

    if "mil" in texto:
        sueldo *= 1000

    return sueldo


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    params = req.get("queryResult", {}).get("parameters", {})

    # 🔹 Parámetros limpios
    vacante = limpiar(params.get("vacante_nombre"))
    ciudad = limpiar(params.get("estado_mexico"))
    modalidad = limpiar(params.get("tipo_modalidad"))
    dias = limpiar(params.get("dias_laborales"))
    sueldo = limpiar_sueldo(params.get("sueldo_mensual"))

    # 🔹 Construcción de búsqueda
    search_terms = []

    if vacante:
        search_terms.append(vacante)

    if modalidad:
        search_terms.append(modalidad)

    query_params = {
        "q": " ".join(search_terms),
        "l": ciudad or "México",
        "fromage": 7,
        "sort": "date"
    }

    if sueldo:
        query_params["salary"] = sueldo

    query = urllib.parse.urlencode(query_params)
    indeed_url = f"https://mx.indeed.com/jobs?{query}"

    # 🔹 Respuesta al usuario
    response_text = (
        "🔍 **Resultados reales encontrados en Indeed**\n\n"
        f"📌 Vacante: {vacante or 'Cualquiera'}\n"
        f"📍 Ubicación: {ciudad or 'México'}\n"
        f"🏢 Modalidad: {modalidad or 'Cualquiera'}\n"
        f"🗓️ Días: {dias or 'Cualquiera'}\n"
        f"💰 Sueldo deseado: ${sueldo:,} MXN\n\n" if sueldo else
        "🔍 **Resultados reales encontrados en Indeed**\n\n"
        f"📌 Vacante: {vacante or 'Cualquiera'}\n"
        f"📍 Ubicación: {ciudad or 'México'}\n"
        f"🏢 Modalidad: {modalidad or 'Cualquiera'}\n"
        f"🗓️ Días: {dias or 'Cualquiera'}\n\n"
    ) + f"👉 Ver vacantes recientes:\n{indeed_url}"

    return jsonify({
        "fulfillmentText": response_text
    })


if __name__ == "__main__":
    app.run()
