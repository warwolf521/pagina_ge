import psycopg2

# Conéctate a tu base de datos PostgreSQL
conn = psycopg2.connect(
    user="postgres",
    dbname= "stress",
    password="warwolf521",
    host="localhost",  # O el host de tu base de datos
)
cursor = conn.cursor()

# Ejecutar la consulta SQL
cursor.execute("SELECT nombre FROM productos;")

# Obtener los resultados como una lista
productos = [row[0] for row in cursor.fetchall()]

# Imprimir el array de productos
print(productos)

# Cerrar la conexión
cursor.close()
conn.close()