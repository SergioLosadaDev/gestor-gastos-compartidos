# PROMPT MAESTRO — "Gestor de Gastos Compartidos"

> Instrucción para la IA generadora: construye una aplicación web en Python
> usando Streamlit, funcional y visualmente equivalente a la especificación
> que sigue. No omitas ninguna sección. Donde se dé un valor exacto (color,
> tamaño, nombre de campo), úsalo literalmente. No inventes funcionalidades
> no descritas aquí ni las omitas.

---

## 1. Resumen del producto

Aplicación web de una sola sesión (single-page app con navegación por
secciones) para que un grupo de personas (familia, roommates, comunidad)
registre gastos compartidos, indique quién pagó y entre quiénes se divide
cada gasto, y consulte automáticamente cuánto debe o le deben a cada
miembro del grupo.

---

## 2. Stack tecnológico y estructura de archivos

- **Lenguaje:** Python 3.10+
- **Framework UI:** Streamlit (>=1.32)
- **Manipulación de datos:** pandas
- **Persistencia:** SQLite (librería estándar `sqlite3`, sin ORM, sin
  servidor externo)
- **Sin backend separado**: Streamlit sirve como frontend y backend a la vez
  (todo corre en el mismo proceso Python).

Estructura de archivos exacta:

```
gastos-compartidos/
├── app.py             # Único archivo con toda la app (UI + lógica + datos)
├── requirements.txt   # streamlit>=1.32 , pandas>=2.0
├── gastos.db          # Se crea automáticamente al primer arranque (SQLite)
└── README.md          # Instrucciones de instalación y despliegue
```

`app.py` se organiza internamente, en este orden, en las siguientes
secciones marcadas con comentarios:

1. Configuración general y constantes de estilo (colores)
2. Capa de datos (conexión SQLite, creación de tablas)
3. Funciones CRUD de miembros
4. Funciones CRUD de gastos
5. Función de cálculo de saldos
6. Interfaz (sidebar + 4 secciones condicionales `if/elif`)

---

## 3. Modelo de datos y relaciones

Dos tablas en SQLite, relación uno-a-muchos (un miembro paga muchos gastos):

**Tabla `miembros`**
| Campo | Tipo | Restricciones |
|--------|---------|------------------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| nombre | TEXT | NOT NULL, UNIQUE |

**Tabla `gastos`**
| Campo | Tipo | Restricciones |
|-----------------|---------|----------------------------------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| descripcion | TEXT | NOT NULL |
| monto | REAL | NOT NULL, debe ser > 0 |
| categoria | TEXT | NOT NULL, uno de los valores del enum |
| fecha | TEXT | NOT NULL, formato ISO `YYYY-MM-DD` |
| pagado_por | INTEGER | NOT NULL, FOREIGN KEY -> miembros.id |
| dividido_entre | TEXT | NOT NULL, lista de IDs separados por comas, ej. "1,2,3" |

Enum de categorías (fijo, usado en un `selectbox`):
`["Arriendo", "Mercado", "Servicios", "Transporte", "Otro"]`

**Relación clave para la lógica de negocio:** un gasto tiene UN pagador
(`pagado_por`) y N participantes (`dividido_entre`), donde el pagador puede
o no estar incluido entre los participantes.

---

## 4. Datos de ejemplo (semilla sugerida)

Al probar la app, usar estos datos representativos:

**Miembros:** `Ana`, `Luis`, `Camila`

**Gastos:**
| descripcion | monto | categoria | fecha | pagado_por | dividido_entre |
|---------------------|---------|------------|-------------|------------|---------------------|
| Mercado quincenal | 180000 | Mercado | 2026-09-01 | Ana | Ana, Luis, Camila |
| Arriendo septiembre | 900000 | Arriendo | 2026-09-01 | Luis | Ana, Luis, Camila |
| Internet | 90000 | Servicios | 2026-09-03 | Camila | Ana, Luis, Camila |
| Uber al aeropuerto | 45000 | Transporte | 2026-09-04 | Ana | Ana, Luis |

Con estos datos, el saldo esperado (verificable) es:

- Ana pagó 225000, le corresponde pagar (180000/3 + 900000/3 + 90000/3 + 45000/2) = 60000+300000+30000+22500 = 412500 → saldo = 225000 - 412500 = **-187500** (debe)
- Luis pagó 900000, le corresponde 60000+300000+30000+22500 = 412500 → saldo = **+487500** (le deben)
- Camila pagó 90000, le corresponde 60000+300000+30000 = 390000 → saldo = **-300000** (debe)

(Los tres saldos deben sumar 0 — úsalo como test de validación de la lógica.)

---

## 5. Arquitectura de la interfaz y navegación

Layout general: `st.set_page_config(layout="wide")`. Barra lateral fija
(`st.sidebar`) + panel de contenido principal.

```
┌───────────────┬─────────────────────────────────────────┐
│  SIDEBAR       │   ÁREA DE CONTENIDO                    │
│  (ancho fijo   │   (ancho variable, ocupa el resto)     │
│  ~300px)       │                                        │
│                │                                        │
│  💰 Gestor de  │   Título de la sección (st.title, h1)  │
│    Gastos      │                                        │
│  ──────────    │   Contenido específico de la sección   │
│  ○ Inicio      │   (ver sección 7)                      │
│  ○ Registrar   │                                        │
│  ○ Historial   │                                        │
│  ○ Miembros    │                                        │
└───────────────┴─────────────────────────────────────────┘
```

Navegación: `st.sidebar.radio("Menú", [...])` con 4 opciones exactas, en
este orden: **"Inicio / Resumen"**, **"Registrar gasto"**, **"Historial"**,
**"Miembros"**. No hay rutas de URL separadas (Streamlit renderiza
condicionalmente todo en la misma página según el valor seleccionado en el
radio button — patrón `if/elif` sobre la variable `seccion`).

No hay autenticación ni login. No hay páginas anidadas ni modales
independientes: todo diálogo de confirmación se resuelve con
`st.success` / `st.error` inline, no con popups.

---

## 6. Diseño visual (paleta, tipografía, espaciados, componentes)

### Paleta de colores (usar estos códigos HEX exactos)

| Uso                              | Color                                                               |
| -------------------------------- | ------------------------------------------------------------------- |
| Color primario / marca           | `#2E7D6B` (verde azulado)                                           |
| Saldo negativo / "debe" / alerta | `#D9534F` (rojo)                                                    |
| Saldo positivo / "le deben"      | `#3E8E41` (verde)                                                   |
| Fondo general                    | el fondo por defecto de Streamlit (blanco/gris claro en modo claro) |
| Texto                            | por defecto del tema Streamlit (negro/gris oscuro)                  |

### Tipografía

Usar la tipografía por defecto de Streamlit (sans-serif del sistema, sin
importar fuentes externas). Tamaños:

- Título de sección (`st.title`): tamaño h1 por defecto de Streamlit (~2.25rem, bold)
- Subtítulos (`st.subheader`): ~1.5rem, bold
- Texto normal: ~1rem
- Valor de saldo dentro de tarjeta: ~22px, bold, en el color según signo

### Espaciados y bordes

- Tarjetas de resumen de saldo: `border: 1px solid #ddd`, `border-radius: 10px`, `padding: 12px`, texto centrado.
- Separación entre columnas de tarjetas: la que da por defecto `st.columns()` (~1rem de gap).
- Formularios: usar `st.form` (agrupa inputs con un único botón de envío, evita reruns intermedios), con espaciado vertical por defecto entre campos (~0.5rem).
- Sin sombras (`box-shadow`) adicionales: se usa el estilo plano de Streamlit, solo borde sutil en las tarjetas de saldo.

### Estilo de componentes específicos

- Botones primarios (guardar, agregar): estilo por defecto de `st.form_submit_button` / `st.button` (fondo del color de acento del tema activo de Streamlit, esquinas redondeadas ~6px).
- Botones secundarios (eliminar): mismo componente `st.button`, sin estilo distinto salvo el texto "Eliminar".
- Tablas (historial): `st.dataframe` con `use_container_width=True` y `hide_index=True` (tabla ocupa todo el ancho disponible, sin columna de índice visible, con scroll horizontal si es necesario).
- Gráfico de gasto por categoría: `st.bar_chart` (barras verticales, color por defecto del tema).

---

## 7. Componentes y funcionalidad por pantalla

### 7.1 Inicio / Resumen

- Si no hay miembros: mensaje `st.info` invitando a ir a la sección Miembros.
- Si hay miembros: una fila de tarjetas (una `st.columns(n)` por cada miembro), cada tarjeta muestra: nombre en negrita, monto absoluto del saldo en grande y coloreado (verde si `saldo >= 0`, rojo si negativo), y la palabra "le deben" o "debe" debajo según el signo.
- Debajo de las tarjetas, si hay gastos registrados: subtítulo "Gasto por categoría" + `st.bar_chart` con el total de gastos agrupado por categoría.

### 7.2 Registrar gasto

- Si no hay miembros: `st.warning` pidiendo crear miembros primero (bloquea el formulario).
- Si hay miembros: un `st.form` con, en este orden: campo de texto "Descripción", campo numérico "Monto" (mínimo 0, step 1000, sin decimales), `selectbox` "Categoría" (con el enum de la sección 3), `date_input` "Fecha" (valor por defecto: hoy), `selectbox` "¿Quién pagó?" (lista de miembros), `multiselect` "¿Entre quiénes se divide?" (lista de miembros, con todos preseleccionados por defecto), y un botón de envío "Guardar gasto".
- Al enviar: valida (ver sección 9) y muestra `st.success` o `st.error` según el resultado; si tiene éxito, limpia el formulario (`clear_on_submit=True`).

### 7.3 Historial

- Si no hay gastos: `st.info` indicando que no hay registros.
- Si hay gastos: dos filtros lado a lado (`st.columns(2)`): `multiselect` "Filtrar por categoría" y `multiselect` "Filtrar por quién pagó". Debajo, una tabla (`st.dataframe`) con las columnas: id, descripción, monto, categoría, fecha, pagado_por — ya filtrada según los selectores.
- Debajo de la tabla, dos columnas: a la izquierda un `selectbox` para elegir un ID de gasto a eliminar + botón "Eliminar" (con confirmación implícita al hacer clic, sin modal, y recarga de la página tras eliminar); a la derecha un `download_button` "Exportar a CSV" que descarga la vista filtrada actual.

### 7.4 Miembros

- Un `st.form` con un campo de texto "Nombre del nuevo miembro" y botón "Agregar".
- Debajo, si hay miembros, un listado: por cada miembro una fila con dos columnas (`st.columns([4,1])`): el nombre a la izquierda, un botón "Eliminar" a la derecha (cada botón con `key` único basado en el id del miembro para evitar colisiones de Streamlit).

---

## 8. Comportamiento responsive

Streamlit es responsive por defecto mediante su sistema de columnas
(`st.columns`), que apila las columnas verticalmente en pantallas angostas
(móvil) y las muestra en fila en pantallas anchas (tablet/escritorio) sin
necesidad de media queries manuales. Reglas a mantener:

- No usar anchos fijos en píxeles para contenedores principales; usar
  siempre `use_container_width=True` en tablas, gráficos y botones de
  descarga.
- El sidebar se colapsa automáticamente en pantallas móviles (comportamiento
  nativo de Streamlit, con un botón "»" para expandirlo). No se debe forzar
  a que el sidebar permanezca siempre visible.
- Las tarjetas de saldo (`st.columns(n)` en Inicio) deben degradarse
  correctamente cuando `n` es grande (más de 4-5 miembros): en pantallas
  angostas Streamlit las apila en una sola columna; esto es aceptable y
  esperado, no requiere lógica adicional.
- Formularios: los campos dentro de `st.form` se apilan verticalmente en
  cualquier tamaño de pantalla (comportamiento nativo, no se debe forzar
  una grilla de 2 columnas para los campos del formulario).

---

## 9. Interacciones, estados y validaciones (reglas de negocio)

- **RN1 — Monto positivo:** un gasto con monto ≤ 0 se rechaza; al enviar el
  formulario se muestra `st.error("El monto debe ser mayor que cero.")` y
  no se guarda el registro.
- **RN2 — División no vacía:** un gasto sin al menos un participante
  seleccionado en "dividido_entre" se rechaza con
  `st.error("Debes seleccionar al menos un miembro para dividir el gasto.")`.
- **RN3 — Nombre de miembro único:** intentar crear un miembro con un
  nombre ya existente falla por restricción `UNIQUE` de la base de datos y
  se captura mostrando `st.error("Ese nombre ya existe.")`.
- **RN4 — División equitativa:** el monto de un gasto se divide siempre en
  partes iguales entre todos los IDs listados en `dividido_entre` (monto /
  cantidad de participantes). No hay división por porcentajes ni montos
  desiguales en esta versión.
- **RN5 — Cálculo de saldo neto:** para cada miembro, el saldo es la suma
  de todos los montos que pagó (columna `pagado_por`) menos la suma de su
  parte proporcional en cada gasto en el que aparece como participante
  (esté o no como pagador también). Saldo positivo = el grupo le debe a esa
  persona; saldo negativo = esa persona debe al grupo.
- **RN6 — Eliminar es inmediato y sin confirmación modal:** al pulsar
  "Eliminar" (gasto o miembro) la acción se ejecuta de inmediato contra la
  base de datos y se recarga la vista (`st.rerun()`); no existe una
  ventana de confirmación intermedia.
- **Estado tras éxito:** mensajes de éxito usan `st.success(...)`.
- **Estado tras error:** mensajes de error usan `st.error(...)`, nunca
  excepciones sin manejar visibles al usuario.
- **Estado vacío:** toda sección que dependa de datos inexistentes
  (sin miembros, sin gastos) debe mostrar un `st.info` o `st.warning`
  explicativo en vez de una tabla o gráfico vacío sin contexto.

---

## 10. Lógica funcional principal (pseudocódigo de referencia)

```
función calcular_saldos():
    miembros = obtener_todos_los_miembros()
    saldos = { id_miembro: 0.0 para cada miembro }

    para cada gasto en obtener_todos_los_gastos():
        participantes = lista_de_ids(gasto.dividido_entre)
        parte = gasto.monto / cantidad(participantes)

        saldos[gasto.pagado_por] += gasto.monto   # quien pagó, se le abona el total
        para cada id_participante en participantes:
            saldos[id_participante] -= parte      # a cada participante se le carga su parte

    retornar saldos  # mapa nombre -> saldo neto (positivo = le deben, negativo = debe)
```

Esta es la única fuente de verdad para "quién debe a quién": no se
almacenan deudas explícitas en la base de datos, se recalculan siempre a
partir del historial completo de gastos. La suma de todos los saldos del
grupo debe dar siempre 0 (verificación de consistencia).

---

## 11. Requisitos funcionales y no funcionales (contrato del sistema)

**Funcionales**

1. Registrar miembros del grupo (nombre único).
2. Registrar un gasto con monto, descripción, categoría, fecha, pagador y participantes.
3. Calcular automáticamente el saldo neto de cada miembro.
4. Mostrar historial de gastos filtrable por miembro, categoría o rango de fechas.
5. Editar o eliminar un gasto registrado.
6. Exportar el historial de gastos (filtrado) a CSV.

**No funcionales**

1. Usabilidad: interfaz completamente en español, navegación de máximo 4 secciones.
2. Persistencia: los datos sobreviven al cierre y reapertura de la app (SQLite en disco, no en memoria).
3. Rendimiento: cálculo de saldos e historial responden en menos de 2 segundos con hasta 1000 registros.
4. Portabilidad: debe ejecutarse igual en local (`streamlit run app.py`) y en Streamlit Community Cloud, sin cambios de código.

---

## 12. Instrucción final para la IA generadora de código

Genera el archivo `app.py` completo (y `requirements.txt`) implementando
exactamente lo descrito en las secciones 1 a 11: mismo modelo de datos,
misma navegación de 4 secciones vía `st.sidebar.radio`, mismos colores
HEX, mismas reglas de negocio y validaciones, y la misma lógica de cálculo
de saldos del pseudocódigo de la sección 10. El código debe estar
comentado por bloques (siguiendo el orden de la sección 2), dividido en
funciones puras para cada operación CRUD, sin frameworks adicionales fuera
de Streamlit, pandas y sqlite3 de la librería estándar. No agregues
autenticación, no agregues bases de datos externas, no cambies el enum de
categorías ni el orden de las secciones del menú.
