from datetime import datetime, timedelta
from app.validation import *
from app.reading import *
from flask import request, jsonify, redirect, url_for, render_template, session, flash
from app import app

app.secret_key = 'your_secret_key'

# Variables globales para intentos fallidos
MAX_ATTEMPTS = 3
LOCKOUT_TIME = timedelta(minutes=5)
attempts = {}

#  Función para verificar si un usuario está bloqueado
def is_locked(email):
    if email in attempts and attempts[email]["locked_until"]:
        if datetime.now() < attempts[email]["locked_until"]:
            return True, attempts[email]["locked_until"] - datetime.now()
    return False, None

#  Registra intentos fallidos y bloquea al usuario si excede el límite
def register_attempt(email):
    if email not in attempts:
        attempts[email] = {"count": 0, "locked_until": None}
    attempts[email]["count"] += 1
    if attempts[email]["count"] >= MAX_ATTEMPTS:
        attempts[email]["locked_until"] = datetime.now() + LOCKOUT_TIME

#  Resetea intentos fallidos si el login es exitoso
def reset_attempts(email):
    if email in attempts:
        attempts[email] = {"count": 0, "locked_until": None}


#  Registro de usuario con validaciones
@app.route('/api/users', methods=['POST'])
def create_record():
    data = request.form
    email = normalize_input(data.get('email'))
    username = normalize_input(data.get('username'))
    nombre = normalize_input(data.get('nombre'))
    apellido = normalize_input(data.get('apellido'))
    password = data.get('password')
    dni = data.get('dni')
    dob = data.get('dob')

    errores = []

    #  Validaciones
    if not validate_email(email):
        errores.append("Email inválido. Debe ser @urosario.edu.co")
    if not validate_pswd(password):
        errores.append("Contraseña no cumple con los requisitos.")
    if not validate_dob(dob):
        errores.append("Fecha de nacimiento inválida.")
    if not validate_dni(dni):
        errores.append("DNI inválido.")
    if not validate_user(username):
        errores.append("Usuario inválido.")
    if not validate_name(nombre):
        errores.append("Nombre inválido.")
    if not validate_name(apellido):
        errores.append("Apellido inválido.")

    if errores:
        return render_template('form.html', error=errores)

    #  Guardar en la base de datos
    db = read_db("db.txt")
    db[email] = {
        'nombre': nombre,
        'apellido': apellido,
        'username': username,
        'password': password,
        "dni": dni,
        'dob': dob,
        "role": "user"  # Todos los nuevos usuarios son "user" por defecto
    }
    write_db("db.txt", db)

    flash("Usuario registrado exitosamente.", "success")
    return redirect("/login")


#  **Login con intentos fallidos y bloqueo**
@app.route('/api/login', methods=['POST'])
def api_login():
    email = normalize_input(request.form['email'])
    password = request.form['password']

    #  Verificar si la cuenta está bloqueada
    locked, remaining_time = is_locked(email)
    if locked:
        flash(f"Cuenta bloqueada. Inténtelo en {remaining_time.seconds // 60} minutos.", 'danger')
        return redirect(url_for('login'))

    db = read_db("db.txt")

    if email not in db:
        flash("Credenciales inválidas.", "danger")
        register_attempt(email)
        return render_template('login.html')

    user = db[email]
    if user["password"] == password:
        session['user'] = email
        session['role'] = user['role']
        reset_attempts(email)  #  Resetea intentos fallidos
        return redirect(url_for('customer_menu'))
    else:
        register_attempt(email)  #  Registrar intento fallido
        flash("Correo o contraseña incorrectos.", "danger")
        return render_template('login.html')


#  Acceso a registros (solo admin)
@app.route('/records', methods=['GET'])
def read_record():
    if 'user' not in session or session.get('role') != 'admin':
        flash("Acceso denegado.", "danger")
        return redirect(url_for('customer_menu'))

    db = read_db("db.txt")
    return render_template('records.html', users=db, role=session.get('role'))


#  **Edición de usuario con validaciones**
@app.route('/update_user/<email>', methods=['POST'])
def update_user(email):
    db = read_db("db.txt")

    if email not in db:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for('read_record'))

    #  Solo el usuario o un admin pueden modificar
    if 'user' not in session or (session['user'] != email and session['role'] != 'admin'):
        flash("No tienes permisos para modificar este usuario.", "danger")
        return redirect(url_for("customer_menu"))

    username = request.form['username']
    dni = request.form['dni']
    dob = request.form['dob']
    nombre = request.form['nombre']
    apellido = request.form['apellido']

    errores = []

    #  Validaciones
    if not validate_dob(dob):
        errores.append("Fecha de nacimiento inválida")
    if not validate_dni(dni):
        errores.append("DNI inválido")
    if not validate_user(username):
        errores.append("Usuario inválido")
    if not validate_name(nombre):
        errores.append("Nombre inválido")
    if not validate_name(apellido):
        errores.append("Apellido inválido")

    if errores:
        return render_template('edit_user.html', user_data=db[email], email=email, error=errores)

    #  Guardar cambios
    db[email]['username'] = username
    db[email]['nombre'] = nombre
    db[email]['apellido'] = apellido
    db[email]['dni'] = dni
    db[email]['dob'] = dob
    write_db("db.txt", db)

    flash("Información actualizada correctamente.", "success")
    return redirect(url_for('read_record'))


#  **Eliminar usuarios (solo admin)**
@app.route('/delete_user/<email>', methods=['POST'])
def delete_user(email):
    if 'user' not in session or session['role'] != 'admin':
        flash("No tienes permisos para eliminar usuarios.", 'danger')
        return redirect(url_for('customer_menu'))

    db = read_db("db.txt")
    if email in db:
        del db[email]
        write_db("db.txt", db)
        flash(f"Usuario {email} eliminado.", 'success')

    return redirect(url_for('read_record'))
