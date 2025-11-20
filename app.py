from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde Angular

DATABASE = 'canchatec.db'

# ==================== FUNCIONES DE BASE DE DATOS ====================

def get_db_connection():
    """Conectar a la base de datos SQLite"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
    return conn

def init_db():
    """Crear la tabla de usuarios si no existe"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            tipo_usuario TEXT DEFAULT 'usuario',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente")

# ==================== RUTAS DE LA API ====================

@app.route('/', methods=['GET'])
def index():
    """Ruta de prueba para verificar que la API funciona"""
    return jsonify({
        'message': 'API CanchaTec funcionando correctamente',
        'version': '1.0',
        'database': 'SQLite'
    })

@app.route('/api/Register', methods=['POST'])
def register():
    """Registrar un nuevo usuario"""
    try:
        data = request.get_json()
        
        # Validar que lleguen todos los datos
        if not all(k in data for k in ('nombre', 'email', 'password', 'tipo_usuario')):
            return jsonify({'message': 'Datos incompletos'}), 400
        
        nombre = data['nombre']
        email = data['email']
        password = data['password']
        tipo_usuario = data['tipo_usuario']
        
        # Validar tipo de usuario
        if tipo_usuario not in ['usuario', 'administrador']:
            return jsonify({'message': 'Tipo de usuario inválido'}), 400
        
        conn = get_db_connection()
        
        # Verificar si el email ya existe
        existing = conn.execute('SELECT id FROM usuarios WHERE email = ?', (email,)).fetchone()
        if existing:
            conn.close()
            return jsonify({'message': 'El email ya está registrado'}), 400
        
        # Encriptar la contraseña
        hashed_password = generate_password_hash(password)
        
        # Insertar el nuevo usuario
        cursor = conn.execute(
            'INSERT INTO usuarios (nombre, email, password, tipo_usuario) VALUES (?, ?, ?, ?)',
            (nombre, email, hashed_password, tipo_usuario)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        print(f"✅ Usuario registrado: {email}")
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'id': user_id
        }), 201
        
    except Exception as e:
        print(f"Error en registro: {str(e)}")
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/Login', methods=['POST'])
def login():
    """Iniciar sesión"""
    try:
        data = request.get_json()
        
        # Validar datos
        if not all(k in data for k in ('email', 'password')):
            return jsonify({'message': 'Datos incompletos'}), 400
        
        email = data['email']
        password = data['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, nombre, email, password, tipo_usuario FROM usuarios WHERE email = ?',
            (email,)
        ).fetchone()
        conn.close()
        
        # Verificar si existe el usuario
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        # Verificar contraseña
        if not check_password_hash(user['password'], password):
            return jsonify({'message': 'Contraseña incorrecta'}), 401
        
        print(f"✅ Login exitoso: {email}")
        
        # Login exitoso
        return jsonify({
            'message': 'Login exitoso',
            'user': {
                'id': user['id'],
                'nombre': user['nombre'],
                'email': user['email'],
                'tipo_usuario': user['tipo_usuario']
            }
        }), 200
        
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Obtener todos los usuarios (para administradores)"""
    try:
        conn = get_db_connection()
        users = conn.execute(
            'SELECT id, nombre, email, tipo_usuario, fecha_registro FROM usuarios'
        ).fetchall()
        conn.close()
        
        users_list = [{
            'id': user['id'],
            'nombre': user['nombre'],
            'email': user['email'],
            'tipo_usuario': user['tipo_usuario'],
            'fecha_registro': user['fecha_registro']
        } for user in users]
        
        return jsonify({'users': users_list}), 200
        
    except Exception as e:
        print(f"Error al obtener usuarios: {str(e)}")
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtener información de un usuario específico"""
    try:
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, nombre, email, tipo_usuario, fecha_registro FROM usuarios WHERE id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'user': {
                'id': user['id'],
                'nombre': user['nombre'],
                'email': user['email'],
                'tipo_usuario': user['tipo_usuario'],
                'fecha_registro': user['fecha_registro']
            }
        }), 200
        
    except Exception as e:
        print(f"Error al obtener usuario: {str(e)}")
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

# ==================== INICIAR SERVIDOR ====================

if __name__ == '__main__':
    init_db()  # Crear la base de datos al iniciar
    print("🚀 Servidor Flask iniciado en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)