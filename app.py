import streamlit as st
import sqlite3
import pandas as pd

# Función para obtener conexión a la base de datos
def get_db_connection():
    # Se crea o abre la base de datos "libredelivery_admin.db"
    conn = sqlite3.connect('libredelivery_admin.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db_connection()

# Función para crear las tablas necesarias si no existen
def create_tables():
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS mercados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                ciudad TEXT NOT NULL,
                descripcion TEXT,
                productos TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idTienda INTEGER,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL,
                foto TEXT,
                FOREIGN KEY(idTienda) REFERENCES mercados(id)
            )
        ''')

create_tables()

# Sidebar para la navegación
st.sidebar.title("Panel Administrativo")
page = st.sidebar.radio("Navegar", ["Mercados", "Productos"])

if page == "Mercados":
    st.title("Gestión de Mercados")
    st.header("Ver Mercados")
    # Consulta para mostrar los mercados existentes
    mercados = pd.read_sql_query("SELECT * FROM mercados", conn)
    st.dataframe(mercados)

    st.header("Agregar Nuevo Mercado")
    with st.form("Agregar Mercado", clear_on_submit=True):
        nombre = st.text_input("Nombre del Mercado")
        ciudad = st.text_input("Ciudad")
        descripcion = st.text_area("Descripción")
        productos_str = st.text_area("Productos (opcional, en formato JSON o CSV)")
        submitted = st.form_submit_button("Agregar Mercado")
        if submitted:
            if nombre and ciudad:
                conn.execute(
                    "INSERT INTO mercados (nombre, ciudad, descripcion, productos) VALUES (?, ?, ?, ?)",
                    (nombre, ciudad, descripcion, productos_str)
                )
                conn.commit()
                st.success("Mercado agregado correctamente.")
            else:
                st.error("Por favor, ingresa al menos el nombre y la ciudad del mercado.")

elif page == "Productos":
    st.title("Gestión de Productos")
    st.header("Agregar Producto")
    
    # Obtener lista de mercados para seleccionar uno
    mercados_df = pd.read_sql_query("SELECT * FROM mercados", conn)
    if not mercados_df.empty:
        mercado_options = mercados_df[['id', 'nombre']].to_dict('records')
        market_names = {mercado['id']: mercado['nombre'] for mercado in mercado_options}
        selected_market = st.selectbox(
            "Selecciona un Mercado", 
            options=list(market_names.keys()), 
            format_func=lambda x: market_names[x]
        )
    else:
        st.warning("Primero debes agregar un mercado.")
        selected_market = None

    if selected_market is not None:
        with st.form("Agregar Producto", clear_on_submit=True):
            nombre = st.text_input("Nombre del Producto")
            descripcion = st.text_area("Descripción")
            precio = st.number_input("Precio", min_value=0.0, format="%.2f")
            foto = st.text_input("URL de la Foto")
            submitted = st.form_submit_button("Agregar Producto")
            if submitted:
                if nombre:
                    conn.execute(
                        "INSERT INTO productos (idTienda, nombre, descripcion, precio, foto) VALUES (?, ?, ?, ?, ?)",
                        (selected_market, nombre, descripcion, precio, foto)
                    )
                    conn.commit()
                    st.success("Producto agregado correctamente.")
                else:
                    st.error("El nombre del producto es obligatorio.")

        st.header("Ver Productos del Mercado")
        query = "SELECT * FROM productos WHERE idTienda = ?"
        productos_df = pd.read_sql_query(query, conn, params=(selected_market,))
        st.dataframe(productos_df)
    else:
        st.info("Agrega un mercado primero para poder agregar productos.")
