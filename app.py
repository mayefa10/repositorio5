from flask import Flask
import os

import functools
import yagmail as yagmail
from flask import Flask, render_template, flash, request, redirect, session, url_for, jsonify, g, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from formulario import Contactenos
import utils
from db import get_db
import sqlite3
app = Flask( __name__ )
app.secret_key = os.urandom( 24 )

@app.route( '/' )
def index():
    if g.user:
        return redirect( url_for( 'inicio' ) )
    return render_template( 'login.html' )
    

@app.route( '/register', methods=('GET', 'POST') )
def register():
    if g.user:
        return redirect( url_for( 'inicio' ))
    try:
        if request.method == 'POST':
            name= request.form['nombre']
            username = request.form['username']
            segname = request.form['segname']
            sexo = request.form['sexo']
            email = request.form['correo']
            password = request.form['password']
            documento = request.form['documento']
            inputNdoc = request.form['inputNdoc']
            inputEstC = request.form['inputEstC']
            inputDirec = request.form['inputDirec']
            nombreContact = request.form['nombreContact']
            parentescoContact = request.form['parentescoContact']
            telefonoContact= request.form['telefonoContact']
            estudios = request.form['estudios']
            idioma = request.form['idioma']
            carrera = request.form['carrera']

            
            error = None

            if not utils.isUsernameValid( username ):
                error = "El usuario debe ser alfanumerico o incluir solo '.','_','-'"
                flash( error )
                return render_template( 'register.html' )

            if not utils.isPasswordValid( password ):
                error = 'La contraseña debe contener al menos una minúscula, una mayúscula, un número y 8 caracteres'
                flash( error )
                return render_template( 'register.html' )

            if not utils.isEmailValid( email ):
                error = 'Correo invalido'
                flash( error )
                return render_template( 'register.html' )

            password = generate_password_hash(password)
            db = get_db()
            cur = db.cursor()
            cur.executescript("INSERT INTO datos (nombre, usuario, apellidos, genero, correo, contraseña, tipo_documento, N_documento, estado_civil, direccion, nombre_contacto, perentesco, telef_celu,  estudios, idioma, carrera) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (name, username, segname, sexo, email, password, documento, inputNdoc, inputEstC, inputDirec, nombreContact, parentescoContact, telefonoContact, estudios, idioma, carrera))
            db.commit()
     
            return render_template( 'login.html' )
        return render_template( 'register.html' )
    except:
        return render_template( 'register.html' )

@app.route( '/login', methods=('GET', 'POST') )
def login():
    try:
        if request.method == 'POST':
            db = get_db()
            error = None
            username = request.form['username']
            password = request.form['password']

            if not username:
                error = 'Debes ingresar el usuario'
                flash( error )
                return render_template( 'login.html' )

            if not password:
                error = 'Contraseña requerida'
                flash( error )
                return render_template( 'login.html' )
            
            cur = db.execute(
                'SELECT * FROM datos WHERE usuario = ?', (username,)
            ).fetchone()

            
            if cur is None:
                error = 'Usuario no válido'
            else:
                if check_password_hash(cur[6], password):
                   print('logeado')
                   session.clear()
                   session['user_id'] = cur[0]
                   print(session['user_id'])
                   resp = make_response(redirect(url_for ('inicio')))
                   resp.set_cookie('username', username)
                   return resp
                   
                else:
                    error = 'Contraseña no válida'
                
            flash( error )
        return render_template( 'login.html' )
    except:
        return render_template( 'login.html' )

@app.route('/inicio')
def inicio():
   return render_template( 'inicio.html' )

    

@app.route( '/contactos', methods=('GET', 'POST'))
def contactos():
    form = Contactenos()
    return render_template('contacto.html', form=form)

def login_required(f):
    @functools.wraps(f)
    def decorated_view():
        if g.user is None:
            return redirect( url_for( 'login' ) )
        return f()
    return decorated_view

@app.route( '/send', methods=['GET', 'POST'])
@login_required
def send():
    if request.method == 'POST':
        #from_id = session.get('user_id')
        from_id = g.user['id']
        print(from_id)
        to_username = request.form['para']
        subject = request.form['asunto']
        body = request.form['mensaje']

        cookie = request.cookies.get('username')
        print(cookie)

        if not to_username:
            flash('campo (Destinatario) es requerido')
            return render_template('send.html' )

        if not subject:
            flash('campo (Asunto) es requerido')
            return render_template('send.html' )

        if not body:
            flash('campo (Mensaje) es requerido')
            return render_template('send.html' )

        db = get_db()
        error = None
        cur = None

        cur = db.execute(
            "SELECT * FROM usuario WHERE usuario = ? ",
            (to_username,)).fetchone()

        if cur is None:
            error = 'Destinatario no existe'
        
        if error is not None:
            flash(error)
            flash(cookie)
        
        else:
            db = get_db()
            db.execute(
                'INSERT INTO mensajes (from_id, to_id, asunto, mensaje)'
                ' VALUES (?, ?, ?, ?)',
                (g.user['id'], cur['id'], subject, body)
            )
            db.commit()
            flash('Mensaje enviado successfully')

    return render_template('send.html')

@app.before_request
def load_logged_in_user():
    user_id = session.get( 'user_id' )

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM datos WHERE id = ?', (user_id,)
        ).fetchone()


@app.route( '/downloadpdf', methods=['GET', 'POST'])
@login_required
def downloadpdf():
    return send_file("resources/actividades.pdf", as_attachment=True)

@app.route( '/downloadimage', methods=['GET', 'POST'])
@login_required
def downloadimage():
    return send_file("resources/logo.png", as_attachment=True)


@app.route( '/logout' )
def logout():
    session.clear()
    return redirect( url_for( 'login' ) )



@app.route('/infodocen') 
def infodocen():
    return render_template( 'infodocen.html' )
@app.route('/infoest') 
def infoest():
    return render_template( 'infoest.html' )

@app.route('/detalleact') 
def detalleact():
    return render_template( 'detalleact.html' )    
@app.route('/curso') 
def curso():
    return render_template('curso.html' )
    
if __name__ == '__main__':
    app.run()