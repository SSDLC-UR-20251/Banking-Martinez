from flask import render_template, redirect, url_for, session, request, flash
from app import app
from app.reading import read_db, write_db  # Necesitas una función para escribir en la base de datos
import re
from datetime import datetime

# Expresiones regulares para validaciones
USERNAME_REGEX = re.compile(r'^[a-zA-Z.]+$')
ID_REGEX = re.compile(r'^100000000\\d{0,1}$')

@app.route('/edit_user/<email>', methods=['GET'])
def edit_user(email):
    db = read_db("db.txt")

    if email not in db:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for('index'))

    user_info = db[email]

    #  permisos
    if 'user' not in session:
        flash("Debes iniciar sesión.", "danger")
        return redirect(url_for("login"))

    if session['user'] != email and session['role'] != 'admin':
        flash("No tienes permisos para modificar este usuario.", "danger")
        return redirect(url_for("index"))

    return render_template('edit_user.html', user_data=user_info, email=email)

@app.route('/update_user/<email>', methods=['POST'])
def update_user(email):
    db = read_db("db.txt")

    if email not in db:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for('index'))

    if 'user' not in session:
        flash("Debes iniciar sesión.", "danger")
        return redirect(url_for("login"))

    if session['user'] != email and session['role'] != 'admin':
        flash("No tienes permisos para modificar este usuario.", "danger")
        return redirect(url_for("index"))

    nombre = request.form['nombre']
    apellido = request.form['apellido']
    username = request.form['username']
    dni = request.form['dni']
    dob = request.form['dob']

    # Validaciones
    if not USERNAME_REGEX.match(username):
        flash("El nombre de usuario solo puede contener letras y puntos.", "danger")
        return redirect(url_for('edit_user', email=email))

    if not ID_REGEX.match(dni):
        flash("El DNI debe empezar con '1000000000' y tener máximo 10 dígitos.", "danger")
        return redirect(url_for('edit_user', email=email))

    birth_year = int(dob.split('-')[0])
    current_year = datetime.now().year
    if current_year - birth_year < 16:
        flash("Debes ser mayor de 16 años.", "danger")
        return redirect(url_for('edit_user', email=email))

    #  Actualización de datos
    db[email]['nombre'] = nombre
    db[email]['apellido'] = apellido
    db[email]['username'] = username
    db[email]['dni'] = dni
    db[email]['dob'] = dob

    # Guardar cambios en la base de datos
    write_db("db.txt", db)

    flash("Información actualizada con éxito.", "success")
    return redirect(url_for('records'))

