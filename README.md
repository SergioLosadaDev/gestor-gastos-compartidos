# App: Gestor de gastos compartidos

## Descripcion

> En muchas familias o grupos comunitarios (roommates, junta de acción comunal, grupo de amigos que viven juntos) los gastos compartidos —arriendo, mercado, servicios públicos— se anotan en papel o en chats de WhatsApp, lo que genera confusión sobre quién ha pagado, cuánto debe cada persona y si las cuentas están saldadas. Se necesita una aplicación sencilla donde cualquier miembro registre un gasto, indique quién lo pagó y entre quiénes se divide, y que calcule automáticamente los saldos (quién le debe a quién), evitando discusiones y facilitando la transparencia del grupo.

## Stakeholders

> - Usuario: miembros de un hogar o grupo comunitario que comparten gastos.
> - Tarea/decisión que se mejora: decidir y verificar cuánto debe pagar cada persona en un momento dado, sin depender de cálculos manuales.

## Requisitos del sistema

### Funcionales

- RF1 — El sistema debe permitir registrar miembros del grupo (nombre).
- RF2 — El sistema debe permitir registrar un gasto con: monto, descripción, categoría, fecha, quién pagó y entre quiénes se divide.
- RF3 — El sistema debe calcular automáticamente el saldo neto de cada miembro (cuánto le deben o cuánto debe).
- RF4 — El sistema debe mostrar el historial de gastos, con filtro por miembro, categoría o rango de fechas.
- RF5 — El sistema debe permitir editar o eliminar un gasto registrado.

### No Funcionales

- RNF1 — Usabilidad: interfaz en español, clara e intuitiva, usable sin entrenamiento previo (menú lateral con máximo 4 secciones).
- RNF2 — Persistencia: los datos deben conservarse entre sesiones, almacenados en una base de datos local SQLite (no se pierden al cerrar la app).
- RNF3 — Rendimiento: las operaciones de consulta y cálculo de saldos deben responder en menos de 2 segundos con hasta 1000 registros.

## Prompt para generar la App

> [Prompt Maestro](prompt-maestro.md)

## Persitencia de datos

> La persistencia de datos en el proyecto se implementa mediante SQLite, una base de datos relacional embebida que se almacena en un único archivo local (gastos.db). Al iniciar la aplicación, esta crea automáticamente las tablas miembros y gastos si no existen, mediante la función init_db(). Cada operación del usuario (registrar un miembro, agregar un gasto, editarlo o eliminarlo) se ejecuta directamente sobre la base de datos a través de consultas SQL (INSERT, DELETE, SELECT), por lo que la información queda almacenada de forma permanente en disco y no depende de la memoria de la sesión. Esto garantiza que los datos se conserven íntegros incluso después de cerrar la aplicación, reiniciar el equipo o volver a ejecutar el programa en otro momento.

## Ejecucion

### Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abrirá en `http://localhost:8501`. La primera vez se crea automáticamente
el archivo `gastos.db` (persistencia SQLite).

### Desplegar en Streamlit Community Cloud (gratis)

1. Entra a https://share.streamlit.io con tu cuenta de GitHub.
2. Clic en "New app".
3. Selecciona el repositorio, la rama `main` y el archivo `app.py`.
4. Clic en "Deploy". En 1–2 minutos tendrás una URL pública para compartir.
