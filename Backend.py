from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE = 'canchatec.db'

# ==================== FUNCIONES DE BASE DE DATOS ====================

def get_db_connection():
    """Conectar a la base de datos SQLite"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crear las tablas si no existen"""
    conn = get_db_connection()
    
    # Tabla de usuarios
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
    
    # Tabla de canchas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS canchas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            capacidad TEXT NOT NULL,
            precio_hora REAL NOT NULL,
            estado TEXT DEFAULT 'disponible'
        )
    ''')
    
    # Tabla de reservas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            cancha_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL,
            estado TEXT DEFAULT 'pendiente',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (cancha_id) REFERENCES canchas(id)
        )
    ''')
    
    conn.commit()
    
    # Insertar canchas por defecto si no existen
    canchas_existentes = conn.execute('SELECT COUNT(*) FROM canchas').fetchone()[0]
    if canchas_existentes == 0:
        canchas_default = [
            ('Cancha Principal', 'Sintética', '7x7', 50000),
            ('Cancha Secundaria', 'Sintética', '7x7', 45000),
            ('Cancha de Torneos', 'Sintética', '7x7', 60000)
        ]
        conn.executemany(
            'INSERT INTO canchas (nombre, tipo, capacidad, precio_hora) VALUES (?, ?, ?, ?)',
            canchas_default
        )
        conn.commit()
        print("✅ Canchas por defecto creadas")
    
    conn.close()
    print("✅ Base de datos inicializada correctamente")

# ==================== RUTAS DE USUARIOS ====================

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'API CanchaTec funcionando correctamente',
        'version': '1.0',
        'database': 'SQLite'
    })

@app.route('/api/Register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ('nombre', 'email', 'password', 'tipo_usuario')):
            return jsonify({'message': 'Datos incompletos'}), 400
        
        nombre = data['nombre']
        email = data['email']
        password = data['password']
        tipo_usuario = data['tipo_usuario']
        
        if tipo_usuario not in ['usuario', 'administrador']:
            return jsonify({'message': 'Tipo de usuario inválido'}), 400
        
        conn = get_db_connection()
        
        existing = conn.execute('SELECT id FROM usuarios WHERE email = ?', (email,)).fetchone()
        if existing:
            conn.close()
            return jsonify({'message': 'El email ya está registrado'}), 400
        
        hashed_password = generate_password_hash(password)
        
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
        print(f" Error en registro: {str(e)}")
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/Login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
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
        
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        if not check_password_hash(user['password'], password):
            return jsonify({'message': 'Contraseña incorrecta'}), 401
        
        print(f"✅ Login exitoso: {email}")
        
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
        print(f"❌ Error en login: {str(e)}")
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

# ==================== RUTAS DE CANCHAS ====================

@app.route('/api/canchas', methods=['GET'])
def get_canchas():
    """Obtener todas las canchas disponibles"""
    try:
        conn = get_db_connection()
        canchas = conn.execute('SELECT * FROM canchas WHERE estado = "disponible"').fetchall()
        conn.close()
        
        canchas_list = [{
            'id': cancha['id'],
            'nombre': cancha['nombre'],
            'tipo': cancha['tipo'],
            'capacidad': cancha['capacidad'],
            'precio_hora': cancha['precio_hora'],
            'estado': cancha['estado']
        } for cancha in canchas]
        
        return jsonify({'canchas': canchas_list}), 200
        
    except Exception as e:
        print(f"❌ Error al obtener canchas: {str(e)}")
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

# ==================== RUTAS DE RESERVAS ====================

@app.route('/api/reservas', methods=['POST'])
def crear_reserva():
    """Crear una nueva reserva (Cliente)"""
    try:
        data = request.get_json()
        
        required_fields = ['usuario_id', 'cancha_id', 'fecha', 'hora_inicio', 'hora_fin']
        if not all(k in data for k in required_fields):
            return jsonify({'message': 'Datos incompletos'}), 400
        
        conn = get_db_connection()
        
        # Verificar disponibilidad
        conflicto = conn.execute('''
            SELECT id FROM reservas 
            WHERE cancha_id = ? 
            AND fecha = ? 
            AND estado != 'rechazada'
            AND (
                (hora_inicio <= ? AND hora_fin > ?) OR
                (hora_inicio < ? AND hora_fin >= ?) OR
                (hora_inicio >= ? AND hora_fin <= ?)
            )
        ''', (
            data['cancha_id'], data['fecha'],
            data['hora_inicio'], data['hora_inicio'],
            data['hora_fin'], data['hora_fin'],
            data['hora_inicio'], data['hora_fin']
        )).fetchone()
        
        if conflicto:
            conn.close()
            return jsonify({'message': 'Ya existe una reserva en ese horario'}), 400
        
        # Crear reserva
        cursor = conn.execute('''
            INSERT INTO reservas (usuario_id, cancha_id, fecha, hora_inicio, hora_fin, estado)
            VALUES (?, ?, ?, ?, ?, 'pendiente')
        ''', (
            data['usuario_id'],
            data['cancha_id'],
            data['fecha'],
            data['hora_inicio'],
            data['hora_fin']
        ))
        
        conn.commit()
        reserva_id = cursor.lastrowid
        conn.close()
        
        print(f"✅ Reserva creada: ID {reserva_id}")
        
        return jsonify({
            'message': 'Reserva creada exitosamente',
            'id': reserva_id
        }), 201
        
    except Exception as e:
        print(f"❌ Error al crear reserva: {str(e)}")
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/reservas/usuario/<int:usuario_id>', methods=['GET'])
def get_reservas_usuario(usuario_id):
    """Obtener reservas de un usuario (Cliente)"""
    try:
        conn = get_db_connection()
        reservas = conn.execute('''
            SELECT r.*, c.nombre as cancha_nombre, c.tipo as cancha_tipo
            FROM reservas r
            JOIN canchas c ON r.cancha_id = c.id
            WHERE r.usuario_id = ?
            ORDER BY r.fecha DESC, r.hora_inicio DESC
        ''', (usuario_id,)).fetchall()
        conn.close()
        
        reservas_list = [{
            'id': r['id'],
            'cancha_id': r['cancha_id'],
            'cancha_nombre': r['cancha_nombre'],
            'cancha_tipo': r['cancha_tipo'],
            'fecha': r['fecha'],
            'hora_inicio': r['hora_inicio'],
            'hora_fin': r['hora_fin'],
            'estado': r['estado'],
            'fecha_creacion': r['fecha_creacion']
        } for r in reservas]
        
        return jsonify({'reservas': reservas_list}), 200
        
    except Exception as e:
        print(f" Error al obtener reservas: {str(e)}")
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/reservas', methods=['GET'])
def get_todas_reservas():
    """Obtener todas las reservas (Admin)"""
    try:
        conn = get_db_connection()
        reservas = conn.execute('''
            SELECT r.*, u.nombre as usuario_nombre, u.email as usuario_email,
                   c.nombre as cancha_nombre, c.tipo as cancha_tipo
            FROM reservas r
            JOIN usuarios u ON r.usuario_id = u.id
            JOIN canchas c ON r.cancha_id = c.id
            ORDER BY r.fecha DESC, r.hora_inicio DESC
        ''').fetchall()
        conn.close()
        
        reservas_list = [{
            'id': r['id'],
            'usuario_id': r['usuario_id'],
            'usuario_nombre': r['usuario_nombre'],
            'usuario_email': r['usuario_email'],
            'cancha_id': r['cancha_id'],
            'cancha_nombre': r['cancha_nombre'],
            'cancha_tipo': r['cancha_tipo'],
            'fecha': r['fecha'],
            'hora_inicio': r['hora_inicio'],
            'hora_fin': r['hora_fin'],
            'estado': r['estado'],
            'fecha_creacion': r['fecha_creacion']
        } for r in reservas]
        
        return jsonify({'reservas': reservas_list}), 200
        
    except Exception as e:
        print(f"❌ Error al obtener reservas: {str(e)}")
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/reservas/<int:reserva_id>/estado', methods=['PUT'])
def actualizar_estado_reserva(reserva_id):
    """Actualizar estado de una reserva (Admin)"""
    try:
        data = request.get_json()
        
        if 'estado' not in data:
            return jsonify({'message': 'Estado requerido'}), 400
        
        estado = data['estado']
        if estado not in ['pendiente', 'aprobada', 'rechazada', 'cancelada']:
            return jsonify({'message': 'Estado inválido'}), 400
        
        conn = get_db_connection()
        
        # Verificar que existe
        reserva = conn.execute('SELECT id FROM reservas WHERE id = ?', (reserva_id,)).fetchone()
        if not reserva:
            conn.close()
            return jsonify({'message': 'Reserva no encontrada'}), 404
        
        # Actualizar estado
        conn.execute('UPDATE reservas SET estado = ? WHERE id = ?', (estado, reserva_id))
        conn.commit()
        conn.close()
        
        print(f"✅ Reserva {reserva_id} actualizada a: {estado}")
        
        return jsonify({'message': 'Estado actualizado exitosamente'}), 200
        
    except Exception as e:
        print(f"❌ Error al actualizar reserva: {str(e)}")
        return jsonify({'message': f'Error en el servidor: {str(e)}'}), 500

# ==================== INICIAR SERVIDOR ====================

if __name__ == '__main__':
    init_db()
    print("🚀 Servidor Flask iniciado en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)