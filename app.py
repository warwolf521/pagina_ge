import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'mysecretkey'  # Clave secreta para la sesión

DB_CONFIG = {
    "host": "localhost",
    "database": "stress",
    "user": "postgres",
    "password": "warwolf521",
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Página principal
@app.route('/')
def index():
    query = request.args.get('q')  # Obtener el parámetro de búsqueda desde la URL
    results = []

    conn = get_db_connection()
    cursor = conn.cursor()

    if query:
        cursor.execute("SELECT * FROM productos WHERE nombre ILIKE %s", (f"%{query}%",))
        results = cursor.fetchall()
        
    else:
        cursor.execute("SELECT * FROM productos ORDER BY RANDOM() LIMIT 15")
        results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    # Obtener el carrito de la sesión
    cart = session.get('cart', [])
    
    # Obtener detalles de los productos en el carrito desde la base de datos
    cart_items = []
    if cart:
        conn = get_db_connection()
        cursor = conn.cursor()
        for item in cart:
            cursor.execute("SELECT * FROM productos WHERE id = %s", (item['id'],))
            product = cursor.fetchone()
            if product:
                cart_items.append({
                    'id': product[0],
                    'nombre': product[1],
                    'precio': product[3],
                    'image_url': product[4],  # Suponiendo que la imagen está en la columna 4
                })
        cursor.close()
        conn.close()

    return render_template('index.html', results=results, query=query, cart=cart_items)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    # Buscar el producto en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    if product:
        # Obtener el carrito de la sesión y agregar el producto
        cart = session.get('cart', [])
        cart.append({'id': product[0], 'nombre': product[1], 'precio': product[3], 'image_url': product[4]})
        session['cart'] = cart  # Guardar el carrito en la sesión

    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    # Mostrar el carrito
    cart = session.get('cart', [])
    cart_items = []
    if cart:
        conn = get_db_connection()
        cursor = conn.cursor()
        for item in cart:
            cursor.execute("SELECT * FROM productos WHERE id = %s", (item['id'],))
            product = cursor.fetchone()
            if product:
                cart_items.append({
                    'id': product[0],
                    'nombre': product[1],
                    'precio': product[3],
                    'image_url': product[5],
                })
        cursor.close()
        conn.close()

    return render_template('cart.html', cart=cart_items)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    # Eliminar el producto del carrito
    cart = session.get('cart', [])
    cart = [product for product in cart if product['id'] != product_id]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    # Obtener el carrito desde la sesión
    cart = session.get('cart', [])
    
    if not cart:
        return redirect(url_for('cart'))  # Redirigir si el carrito está vacío

    total_amount = sum(item['precio'] for item in cart)  # Calcular el monto total

    # Obtener el ID del usuario, si es necesario
    user_id = 1  # O algún valor de la sesión si estás gestionando autenticación

    # Guardar la transacción en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (cart, total_amount) VALUES (%s, %s) RETURNING id",
        (json.dumps(cart), total_amount)  # Convertir el carrito a JSON
    )
    transaction_id = cursor.fetchone()[0]  # Obtener el ID de la transacción insertada
    conn.commit()
    cursor.close()
    conn.close()

    # Eliminar el carrito después de procesar el pago
    session.pop('cart', None)

    # Redirigir a una página de éxito con el ID de la transacción
    return redirect(url_for('transaction_success', transaction_id=transaction_id))

@app.route('/transaction_success/<int:transaction_id>')
def transaction_success(transaction_id):
    # Obtener los detalles de la transacción desde la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = %s", (transaction_id,))
    transaction = cursor.fetchone()
    cursor.close()
    conn.close()

    if transaction:
        return render_template('transaction_success.html', transaction=transaction)
    else:
        return "Transacción no encontrada", 404



# Búsqueda de productos
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')

    # Conexión a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    # Realiza una consulta para buscar productos
    cursor.execute("SELECT * FROM productos WHERE nombre ILIKE %s", (f"%{query}%",))
    results = cursor.fetchall()

    # Cierra la conexión
    cursor.close()
    conn.close()

    # Convierte los resultados en una lista de diccionarios
    products = [{"id": row[0], "nombre": row[1], "precio": row[3]} for row in results]
    return render_template('results.html', query=query, results=products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
