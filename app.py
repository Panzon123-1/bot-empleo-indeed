from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    text = req["queryResult"]["queryText"].lower()

    # Detectar modalidad
    modalidad = None
    if "presencial" in text:
        modalidad = "presencial"
    elif "remoto" in text or "home office" in text:
        modalidad = "remoto"
    elif "híbrido" in text or "hibrido" in text or "mixto" in text:
        modalidad = "híbrido"

    # Detectar días
    dias = None
    if "lunes a viernes" in text:
        dias = "lunes a viernes"
    elif "lunes a sábado" in text or "lunes a sabado" in text:
        dias = "lunes a sábado"

    # Detectar vacante
    vacante = None
    vacantes = [
        "chofer", "conductor", "repartidor",
        "vendedor", "ventas",
        "administrativo", "oficina",
        "gerente", "jefe", "supervisor"
    ]
    for v in vacantes:
        if v in text:
            vacante = v
            break

    # Detectar ubicación
    ubicacion = None
    ciudades = [
        "puebla", "cholula", "tehuacán", "tehuacan",
        "tlaxcala", "cdmx", "ciudad de mexico"
    ]
    for c in ciudades:
        if c in text:
            ubicacion = c
            break

    respuesta = (
        "🔍 Búsqueda recibida:\n"
        f"• Vacante: {vacante or 'no especificada'}\n"
        f"• Ubicación: {ubicacion or 'no especificada'}\n"
        f"• Modalidad: {modalidad or 'no especificada'}\n"
        f"• Días laborales: {dias or 'no especificados'}\n\n"
        "Estoy buscando vacantes reales para ti…"
    )

    return jsonify({
        "fulfillmentText": respuesta
    })

if __name__ == "__main__":
    app.run(debug=True)
