"""
Gestor de Gastos Compartidos
-----------------------------
App en Streamlit para registrar gastos familiares/comunitarios,
dividirlos entre miembros y calcular saldos automáticamente.

Persistencia: SQLite (gastos.db)
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ----------------------------------------------------------------------
# CONFIGURACIÓN GENERAL Y ESTILO (RNF1 - Usabilidad)
# ----------------------------------------------------------------------
st.set_page_config(page_title="Gestor de Gastos Compartidos", page_icon="💰", layout="wide")

PRIMARY_COLOR = "#2E7D6B"
DEBE_COLOR = "#D9534F"
FAVOR_COLOR = "#3E8E41"

DB_PATH = "gastos.db"


# ----------------------------------------------------------------------
# CAPA DE DATOS (RNF2 - Persistencia con SQLite)
# ----------------------------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS miembros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL,
            categoria TEXT NOT NULL,
            fecha TEXT NOT NULL,
            pagado_por INTEGER NOT NULL,
            dividido_entre TEXT NOT NULL,
            FOREIGN KEY (pagado_por) REFERENCES miembros(id)
        )
    """)
    conn.commit()
    conn.close()


# --- Miembros (RF1) -----------------------------------------------------
def agregar_miembro(nombre):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO miembros (nombre) VALUES (?)", (nombre.strip(),))
        conn.commit()
        return True, "Miembro agregado."
    except sqlite3.IntegrityError:
        return False, "Ese nombre ya existe."
    finally:
        conn.close()


def eliminar_miembro(miembro_id):
    conn = get_connection()
    conn.execute("DELETE FROM miembros WHERE id = ?", (miembro_id,))
    conn.commit()
    conn.close()


def obtener_miembros():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM miembros ORDER BY nombre", conn)
    conn.close()
    return df


# --- Gastos (RF2, RF4, RF5, RF6) -----------------------------------------
def agregar_gasto(descripcion, monto, categoria, fecha, pagado_por, dividido_entre):
    if monto <= 0:
        return False, "El monto debe ser mayor que cero."
    if not dividido_entre:
        return False, "Debes seleccionar al menos un miembro para dividir el gasto."

    conn = get_connection()
    conn.execute(
        """INSERT INTO gastos (descripcion, monto, categoria, fecha, pagado_por, dividido_entre)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (descripcion.strip(), monto, categoria, str(fecha), pagado_por, ",".join(map(str, dividido_entre))),
    )
    conn.commit()
    conn.close()
    return True, "Gasto registrado."


def eliminar_gasto(gasto_id):
    conn = get_connection()
    conn.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
    conn.commit()
    conn.close()


def obtener_gastos():
    conn = get_connection()
    query = """
        SELECT g.id, g.descripcion, g.monto, g.categoria, g.fecha,
               m.nombre AS pagado_por, g.dividido_entre, g.pagado_por AS pagado_por_id
        FROM gastos g
        JOIN miembros m ON g.pagado_por = m.id
        ORDER BY g.fecha DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# --- Cálculo de saldos (RF3) ---------------------------------------------
def calcular_saldos():
    miembros = obtener_miembros()
    gastos = obtener_gastos()

    saldos = {row["id"]: 0.0 for _, row in miembros.iterrows()}
    nombres = {row["id"]: row["nombre"] for _, row in miembros.iterrows()}

    for _, gasto in gastos.iterrows():
        participantes = [int(x) for x in gasto["dividido_entre"].split(",") if x]
        if not participantes:
            continue
        parte = gasto["monto"] / len(participantes)

        saldos[gasto["pagado_por_id"]] = saldos.get(gasto["pagado_por_id"], 0) + gasto["monto"]
        for pid in participantes:
            saldos[pid] = saldos.get(pid, 0) - parte

    return {nombres[mid]: saldo for mid, saldo in saldos.items()}


# ----------------------------------------------------------------------
# INTERFAZ (arquitectura definida en prompt.md)
# ----------------------------------------------------------------------
init_db()

st.sidebar.markdown(f"<h2 style='color:{PRIMARY_COLOR}'>💰 Gestor de Gastos</h2>", unsafe_allow_html=True)
seccion = st.sidebar.radio(
    "Menú",
    ["Inicio / Resumen", "Registrar gasto", "Historial", "Miembros"],
)

miembros_df = obtener_miembros()

# --- INICIO / RESUMEN -----------------------------------------------------
if seccion == "Inicio / Resumen":
    st.title("Resumen de saldos")

    if miembros_df.empty:
        st.info("Aún no hay miembros registrados. Ve a la sección 'Miembros' para agregar el grupo.")
    else:
        saldos = calcular_saldos()
        cols = st.columns(len(saldos)) if saldos else [st]
        for col, (nombre, saldo) in zip(cols, saldos.items()):
            color = FAVOR_COLOR if saldo >= 0 else DEBE_COLOR
            etiqueta = "le deben" if saldo >= 0 else "debe"
            col.markdown(
                f"""
                <div style='border:1px solid #ddd; border-radius:10px; padding:12px; text-align:center'>
                    <b>{nombre}</b><br>
                    <span style='color:{color}; font-size:22px'>${abs(saldo):,.0f}</span><br>
                    <small>{etiqueta}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

        gastos_df = obtener_gastos()
        if not gastos_df.empty:
            st.subheader("Gasto por categoría")
            resumen_cat = gastos_df.groupby("categoria")["monto"].sum()
            st.bar_chart(resumen_cat)

# --- REGISTRAR GASTO -------------------------------------------------------
elif seccion == "Registrar gasto":
    st.title("Registrar nuevo gasto")

    if miembros_df.empty:
        st.warning("Primero agrega miembros en la sección 'Miembros'.")
    else:
        with st.form("form_gasto", clear_on_submit=True):
            descripcion = st.text_input("Descripción")
            monto = st.number_input("Monto", min_value=0.0, step=1000.0, format="%.0f")
            categoria = st.selectbox(
                "Categoría", ["Arriendo", "Mercado", "Servicios", "Transporte", "Otro"]
            )
            fecha = st.date_input("Fecha", value=date.today())
            pagado_por = st.selectbox(
                "¿Quién pagó?", miembros_df["id"], format_func=lambda x: miembros_df.set_index("id").loc[x, "nombre"]
            )
            dividido_entre = st.multiselect(
                "¿Entre quiénes se divide?",
                miembros_df["id"],
                default=list(miembros_df["id"]),
                format_func=lambda x: miembros_df.set_index("id").loc[x, "nombre"],
            )
            enviado = st.form_submit_button("Guardar gasto")

            if enviado:
                ok, msg = agregar_gasto(descripcion, monto, categoria, fecha, pagado_por, dividido_entre)
                st.success(msg) if ok else st.error(msg)

# --- HISTORIAL ---------------------------------------------------------
elif seccion == "Historial":
    st.title("Historial de gastos")
    gastos_df = obtener_gastos()

    if gastos_df.empty:
        st.info("No hay gastos registrados todavía.")
    else:
        col1, col2 = st.columns(2)
        filtro_cat = col1.multiselect("Filtrar por categoría", gastos_df["categoria"].unique())
        filtro_miembro = col2.multiselect("Filtrar por quién pagó", gastos_df["pagado_por"].unique())

        vista = gastos_df.copy()
        if filtro_cat:
            vista = vista[vista["categoria"].isin(filtro_cat)]
        if filtro_miembro:
            vista = vista[vista["pagado_por"].isin(filtro_miembro)]

        st.dataframe(
            vista[["id", "descripcion", "monto", "categoria", "fecha", "pagado_por"]],
            use_container_width=True,
            hide_index=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            gasto_a_borrar = st.selectbox("Eliminar gasto (por ID)", [None] + list(vista["id"]))
            if st.button("Eliminar") and gasto_a_borrar:
                eliminar_gasto(gasto_a_borrar)
                st.success("Gasto eliminado.")
                st.rerun()
        with col_b:
            csv = vista.to_csv(index=False).encode("utf-8")
            st.download_button("Exportar a CSV", csv, "gastos.csv", "text/csv")

# --- MIEMBROS -----------------------------------------------------------
elif seccion == "Miembros":
    st.title("Miembros del grupo")

    with st.form("form_miembro", clear_on_submit=True):
        nombre = st.text_input("Nombre del nuevo miembro")
        enviado = st.form_submit_button("Agregar")
        if enviado and nombre.strip():
            ok, msg = agregar_miembro(nombre)
            st.success(msg) if ok else st.error(msg)

    if not miembros_df.empty:
        st.subheader("Miembros actuales")
        for _, row in miembros_df.iterrows():
            c1, c2 = st.columns([4, 1])
            c1.write(row["nombre"])
            if c2.button("Eliminar", key=f"del_{row['id']}"):
                eliminar_miembro(row["id"])
                st.rerun()
