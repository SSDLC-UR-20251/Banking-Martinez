import unicodedata
import re
import dns.resolver
from datetime import datetime

def normalizar_nfkd(texto):
    return unicodedata.normalize("NFKD", texto)

# Validar usuario
def validar_usuario(usuario):
    # Expresión regular: solo letras y punto (.)
    patron = r'^[a-zA-Z.]+$'

    if not re.match(patron, usuario):
        return False, "El nombre de usuario solo puede contener letras y el punto (.)"

    return True, "Nombre de usuario válido"

# Validar contraseña
def validar_contraseña(contraseña):
    # Expresión regular para cumplir con los requisitos de seguridad
    patron = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#@$%&\-!=+?])[A-Za-z\d#@$%&\-!=+?]{8,35}$'

    if not re.match(patron, contraseña):
        return False, "La contraseña no cumple con los requisitos de seguridad"

    return True, "Contraseña válida"

# Validar documento de identidad
def validar_documento(doc_id):
    # Verificar que tenga exactamente 10 dígitos y sea numérico
    if not doc_id.isdigit() or len(doc_id) != 10:
        return False, "El documento debe contener exactamente 10 dígitos numéricos"
    
    # Verificar que empiece con "1"
    if not doc_id.startswith("1"):
        return False, "El documento debe comenzar con '1'"
    
    return True, "Documento válido"

# Validar correo electrónico
def validar_correo(email):
    # Expresión regular para validar formato del correo
    patron = r'^[a-zA-Z0-9_.+-]+@urosario\.edu\.co$'
    
    if not re.match(patron, email):
        return False, "Correo no permitido"
    
    # Verificar si el dominio tiene registros MX
    dominio = email.split("@")[-1]
    try:
        dns.resolver.resolve(dominio, 'MX')
        return True, "Correo válido"
    except dns.resolver.NoAnswer:
        return False, "El dominio del correo no tiene registros MX"

# Validar fecha de nacimiento
def validar_fecha_nacimiento(fecha_nacimiento):
    try:
        fecha = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")  # Validar formato
    except ValueError:
        return False, "Formato de fecha inválido. Usa YYYY-MM-DD"

    edad_minima = 16
    fecha_actual = datetime.today()
    edad_usuario = fecha_actual.year - fecha.year - ((fecha_actual.month, fecha_actual.day) < (fecha.month, fecha.day))

    if edad_usuario < edad_minima:
        return False, "Debes ser mayor de 16 años"
    
    return True, "Fecha válida"
