from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import re
from app import app
from app.reading import read_db

app.secret_key = 'your_secret_key'  #  Cambia esto en producción

# 🔹 Variables para el control de intentos fallidos
MAX_ATTEMPTS = 3
LOCKOUT_TIME = timedelta(minutes=5)
attempts = {}

# 🔹 Validaciones
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@urosario\\.edu\\.co$')
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[#*@\\$%&\\-!+=?]).{8,35}$')
USERNAME_REGEX = re.compile(r'^[a-zA-Z.]+$')
ID_REGEX = re.compile(r'^100000000\\d{0,1}$')

# 🔹 Simulación de Base de Datos
users = {
    "admin@urosario.edu.co": {"password": "Admin#123", "role": "admin"},
    "user@urosario.edu.co": {"password": "User@2023", "role": "user"},
}

#  Funciones de control de intentos fallidos
def is_locked(email):
    if email in attempts and attempts[email]["locked_until"]:
        if datetime.now() < attempts[email]["locked_until"]:
            return True, attempts[email]["locked_until"] - datetime.now()
    return False, None

def register_attempt(email):
    if email not in attempts:
        attempts[email] = {"count": 0, "locked_until": None}
    attempts[email]["count"] += 1
    if attempts[email]["count"] >= MAX_ATTEMPTS:
        attempts[email]["locked_until"] = datetime.now() + LOCKOUT_TIME

def reset_attempts(email):
    if email in attempts:
        attempts[email] = {"count": 0, "locked_until": None}

#  Página de inicio
@app.route('/')
def index():
    return render_template('index.html')

#  Registro de usuario
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]
        user_id = request.form["id"]

        #  Validaciones
        if not EMAIL_REGEX.match(email):
            flash("Correo inválido. Debe ser @urosario.edu.co", "danger")
        elif not PASSWORD_REGEX.match(password):
            flash("Contraseña no cumple los requisitos.", "danger")
        elif not USERNAME_REGEX.match(username):
            flash("Nombre de usuario inválido.", "danger")
        elif not ID_REGEX.match(user_id):
            flash("Documento de identificación inválido.", "danger")
        else:
            users[email] = {"password": password, "role": "user"}
            flash("Usuario registrado exitosamente.", "success")
            return redirect(url_for("login"))

    return render_template("form.html")

#  Inicio de sesión con intentos fallidos
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # 🚨 Bloqueo de usuario
        locked, remaining_time = is_locked(email)
        if locked:
            flash(f"Cuenta bloqueada. Intente en {remaining_time.seconds // 60} minutos.", "danger")
            return redirect(url_for("login"))

        #  Validación de credenciales
        user = users.get(email)
        if user and user["password"] == password:
            session["user"] = email
            session["role"] = user["role"]
            reset_attempts(email)
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("dashboard"))
        else:
            register_attempt(email)
            flash("Correo o contraseña incorrectos.", "danger")

    return render_template("login.html")

#  Ruta protegida según rol
@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return f"Bienvenido, {session['user']}! Rol: {session['role']}"

#  Acceso a registros solo para admins
@app.route('/records')
def records():
    if "user" not in session or session["role"] != "admin":
        flash("Acceso denegado.", "danger")
        return redirect(url_for("dashboard"))
    return "Lista de registros (solo admin)"

#  Eliminar usuarios (solo admin)
@app.route('/delete_user/<email>', methods=["POST"])
def delete_user(email):
    if "user" not in session or session["role"] != "admin":
        flash("No tienes permisos para eliminar usuarios.", "danger")
        return redirect(url_for("dashboard"))

    if email in users:
        del users[email]
        flash(f"Usuario {email} eliminado.", "success")
    return redirect(url_for("dashboard"))

