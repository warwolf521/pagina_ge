import requests
from bs4 import BeautifulSoup
import psycopg2

# Función para obtener la URL de la imagen de un producto
def obtener_imagen_url(producto):
    # Realiza la búsqueda en Google (o en una URL específica de tienda)
    url = f"https://www.google.com/search?hl=en&tbm=isch&q={producto}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extrae las URLs de las imágenes
    images = soup.find_all('img')
    image_urls = [img['src'] for img in images if 'src' in img.attrs]
    
    # Filtra las imágenes que no son relevantes, como el logo de Google
    valid_image_urls = [url for url in image_urls if not url.startswith('/images/branding')]

    # Si hay imágenes válidas, devolver la primera, si no devolver None
    return valid_image_urls[0] if valid_image_urls else None

# Conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    user="postgres",
    dbname= "stress",
    password="warwolf521",
    host="localhost",  # O el host de tu base de datos
)
cursor = conn.cursor()

# Lista de productos
productos = ['Polera', 'Camiseta de algodón', 'Zapatos deportivos', 'Laptop portátil', 'Auriculares inalámbricos', 'Mochila escolar', 'Reloj inteligente', 'Cámara fotográfica', 'Silla ergonómica', 'Smartphone', 'Tablet', 'Cargador portátil', 'Teclado mecánico', 'Monitor 24 pulgadas', 'Ventilador de pie', 'Plancha de vapor', 'Juego de ollas', 'Cafetera', 'Silla gaming', 'Lámpara LED', 'Saco de dormir', 'Cámara de seguridad', 'Bicicleta de montaña', 'Cortadora de césped', 'Pava eléctrica', 'Silla de oficina', 'Frigorífico', 'Horno microondas', 'Lavadora', 'Aspiradora robot', 'Secador de pelo', 'Escalera de mano', 'Estufa eléctrica', 'Bañera portátil', 'Cuna de bebé', 'Bicicleta estática', 'Patineta eléctrica', 'Kit de jardinería', 'Arco de futbol', 'Bomba de agua', 'Extractor de jugo', 'Silla de playa', 'Cámara instantánea', 'Altavoces bluetooth', 'Mochila de senderismo', 'Termo de acero', 'Gafas de sol', 'Chaqueta impermeable', 'Sombrero de invierno', 'Raqueta de tenis', 'Bolsa de gimnasio']

# Iterar sobre cada producto, obtener la URL de la imagen y actualizar la base de datos
for producto in productos:
    print(f"Buscando imágenes para {producto}...")
    url_imagen = obtener_imagen_url(producto)
    if url_imagen:
        # Insertar la URL de la imagen en la base de datos para el producto correspondiente
        query = """
            UPDATE productos
            SET image_url = %s
            WHERE nombre = %s;
        """
        cursor.execute(query, (url_imagen, producto))
        conn.commit()
        print(f"URL de imagen actualizada para {producto}: {url_imagen}")
    else:
        print(f"No se encontró una imagen para {producto}")

# Cerrar la conexión a la base de datos
cursor.close()
conn.close()