from flask import Flask, render_template, request, redirect, session, url_for, flash
import os
import mysql.connector
from datetime import datetime
from flask import send_from_directory


app = Flask(__name__)

app.secret_key='develoteca'

# Configuración de la conexión a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Contraseña de tu base de datos
    database="sitio"
)

cursor = db.cursor()

CARPETA=os.path.join('/templates/uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<imagen>')
def imagenes(imagen):
    print(imagen)
    
    return send_from_directory(os.path.join('templates/uploads/'),imagen)

@app.route('/css/<archivocss>')
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'),archivocss)

@app.route('/')
def inicio():
    return render_template('sitio/index.html')


@app.route('/productos')
def productos():
    cursor.execute("SELECT * FROM `productos`")  # Reemplaza tu_tabla con el nombre de tu tabla
    productos = cursor.fetchall()
    return render_template('sitio/productos.html', productos=productos)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/admin/')
def admin_index():
    if not 'login' in session:
        return redirect("/admin/login")
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')


@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    print(_usuario)
    print(_password)
    
    if _usuario=="mikitoloco" and _password=="mikitoloco123":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")
    
    
    return render_template('admin/login.html', mensaje="Acceso denegado")

@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect("/admin/login")

@app.route('/admin/productos')
def admin_productos():
    if not 'login' in session:
        return redirect("/admin/login")
    cursor.execute("SELECT * FROM `productos`")  
    productos = cursor.fetchall()
    print('esto es laaaa productossss', productos)
    return render_template('admin/productos.html', productos=productos)

@app.route('/admin/productos/guardar', methods=['POST'])
def admin_productos_guardar():
    if not 'login' in session:
        return redirect("/admin/login")

    _nombre = request.form['txtNombre']
    _archivo = request.files['txtImagen']
    _descripcion = request.form['txtDescripcion']
    _precio = request.form['txtPrecio']
    
    if _nombre=='' or _archivo=='' or _descripcion=='' or _precio=='':
        flash('Recuerda llenar todos los campos')
        return redirect(url_for('admin_productos'))
    
    tiempo=datetime.now()
    
    horaActual = tiempo.strftime('%Y%H%M%S')
    
    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/uploads/"+nuevoNombre)
        
        # Configurar tu sentencia SQL para insertar en la base de datos
        sql = "INSERT INTO `productos` (`id`, `nombre`, `imagen`, `descripcion`, `precio`) VALUES (NULL, %s, %s, %s, %s)"
        valores = (_nombre, nuevoNombre, _descripcion, _precio)
                # Ejecutar la consulta con los valores
        cursor.execute(sql, valores)
        db.commit()

        return redirect('/admin/productos')
        

    return "Error al guardar el producto. Archivo no encontrado."

@app.route('/admin/productos/borrar', methods=['POST'])
def admin_productos_borrar():
    if not 'login' in session:
        return redirect("/admin/login")
    
    _id = request.form.get("txtID")  # Utiliza .get() en lugar de acceder directamente para evitar errores si la clave no está presente
    if _id is not None:
        print('ESTEEEE ES ELLL ',_id)
        
        
        cursor.execute("SELECT imagen FROM `productos` WHERE id=%s", (_id,))  
        producto = cursor.fetchall()
        print('esto es elll productoooooo', producto)
        
        if os.path.exists("templates/uploads/"+str(producto[0][0])):
            os.unlink("templates/uploads/"+str(producto[0][0]))
        
        cursor.execute("DELETE FROM productos WHERE id=%s", (_id,))  
        producto = cursor.fetchall()
        print('esto es elll productoooooo', producto)
        
        # Realiza la lógica de borrado o redirecciona
        return redirect('/admin/productos')

    return "ID no encontrado en la solicitud."

@app.route('/edit/<int:id>')
def edit(id):
    if not 'login' in session:
        return redirect("/admin/login")
    
    _id = id
    
    if _id is not None:
        print('ESTEEEE ES ELLL ', _id)
        
        cursor.execute("SELECT * FROM `productos` WHERE id=%s", (_id,))
        producto = cursor.fetchall()
        print('esto es elll productoooooo a editarrrr', producto)
        
        return render_template('admin/edit.html', productos=producto)  # Observa que aquí se usa 'productos' en lugar de 'producto'
    
    # Manejar el caso donde _id no está presente
    return "ID no encontrado en la solicitud."

@app.route('/admin/productos/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _descripcion = request.form['txtDescripcion']
    _precio = request.form['txtPrecio']
    _id = request.form['txtID']

    # Configurar tu sentencia SQL para actualizar en la base de datos
    sql = "UPDATE productos SET `nombre`=%s, `descripcion`=%s, `precio`=%s WHERE id=%s"
    valores = (_nombre, _descripcion, _precio, _id)
    
    cursor.execute(sql, valores)
    db.commit()
    
    return redirect('/admin/productos')



if __name__ == '__main__':
    app.run(debug=True)


""" 
    # Asegúrate de que el directorio de subida (uploads) exista
    uploads_dir = os.path.join(app.root_path, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    if _archivo:
        
        archivo_path = os.path.join(uploads_dir, _archivo.filename)
        _archivo.save(archivo_path)
        
        
        # Configurar tu sentencia SQL para insertar en la base de datos
        sql = "INSERT INTO `productos` (`id`, `nombre`, `imagen`, `descripcion`, `precio`) VALUES (NULL, %s, %s, %s, %s)"
        valores = (_nombre, archivo_path, _descripcion, _precio)

        # Ejecutar la consulta con los valores
        cursor.execute(sql, valores)
        db.commit()

        return redirect('/admin/productos')
 """