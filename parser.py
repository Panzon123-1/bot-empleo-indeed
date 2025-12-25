import re
import unicodedata
def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto.strip()
ESTADOS_MEXICO = [
    "aguascalientes", "baja california", "baja california sur",
    "campeche", "chiapas", "chihuahua", "ciudad de mexico", "cdmx",
    "coahuila", "colima", "durango", "guanajuato", "guerrero",
    "hidalgo", "jalisco", "mexico", "michoacan", "morelos",
    "nayarit", "nuevo leon", "oaxaca", "puebla", "queretaro",
    "quintana roo", "san luis potosi", "sinaloa", "sonora",
    "tabasco", "tamaulipas", "tlaxcala", "veracruz", "yucatan",
    "zacatecas"
]
def extraer_sueldo(texto: str):
    texto = texto.replace(",", "")
    match = re.search(r'(\d{4,6})', texto)
    if match:
        return int(match.group(1))
    return None
def extraer_estado(texto: str):
    for estado in ESTADOS_MEXICO:
        if estado in texto:
            return estado
    return None
MODALIDADES = ["remoto", "home office", "presencial", "hibrido"]

def extraer_modalidad(texto: str):
    for m in MODALIDADES:
        if m in texto:
            return m
    return None
def limpiar_texto(texto: str, *valores):
    limpio = texto
    for v in valores:
        if v:
            limpio = limpio.replace(v, "")
    return limpio.strip()
def parsear(texto_original: str):
    texto = normalizar(texto_original)

    sueldo = extraer_sueldo(texto)
    estado = extraer_estado(texto)
    modalidad = extraer_modalidad(texto)

    texto_limpio = limpiar_texto(
        texto,
        str(sueldo) if sueldo else None,
        estado,
        modalidad,
        "en"
    )

    vacante = texto_limpio.strip()
    if vacante == "":
        vacante = None

    return {
        "vacante": vacante,
        "ciudad": estado,
        "sueldo": sueldo,
        "modalidad": modalidad
    }

