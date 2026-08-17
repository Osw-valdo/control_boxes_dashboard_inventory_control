import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, date

st.set_page_config(
    page_title="Control Box Dashboard",
    page_icon="🧰",
    layout="wide"
)

# =========================
# USUARIOS
# =========================

USUARIOS = {
    "operador": {"password": "1234", "rol": "Operador"},
    "tecnico": {"password": "1234", "rol": "Técnico"},
    "supervisor": {"password": "1234", "rol": "Supervisor"},
    "admin": {"password": "admin", "rol": "Admin"}
}

def tiene_permiso(roles_permitidos):
    return st.session_state.get("rol") in roles_permitidos


# =========================
# ARCHIVOS
# =========================

ARCHIVO = "avance_control_boxes.csv"
ARCHIVO_INFO = "info_control_boxes.csv"
ARCHIVO_HISTORIAL = "historial_control_boxes.csv"
ARCHIVO_REPORTE = "reporte_control_boxes.xlsx"

puntos_iniciales = [
    "Montaje de gabinete",
    "Instalación de canaletas",
    "Instalación de riel DIN",
    "Montaje de fuente 24V",
    "Montaje de PLC",
    "Montaje de relevadores",
    "Montaje de borneras",
    "Cableado de alimentación",
    "Cableado de señales",
    "Etiquetado de cables",
    "Prueba de continuidad",
    "Prueba de encendido",
    "Validación final"
]

colores_default = [
    ["#38BDF8", "#1E293B"],
    ["#22C55E", "#1E293B"],
    ["#F97316", "#1E293B"],
    ["#A855F7", "#1E293B"],
    ["#EF4444", "#1E293B"],
    ["#14B8A6", "#1E293B"],
    ["#EAB308", "#1E293B"],
    ["#94A3B8", "#1E293B"]
]

# =========================
# ESTILOS
# =========================

st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top,
        #1E293B 0%,
        #0F172A 45%,
        #020617 100%);
    color: #E5E7EB;
}

.block-container {
    padding-top: 1.3rem;
    padding-left: 2rem;
    padding-right: 2rem;
}


/* ===========================
   CABECERA PRINCIPAL
=========================== */

.hero,
.command-header {

    background: linear-gradient(
        120deg,
        #020617,
        #111827,
        #1E293B
    );

    padding: 28px;

    border-radius: 24px;

    color: white;

    box-shadow: 0px 14px 35px rgba(0,0,0,0.45);

    border: 1px solid #334155;

    margin-bottom: 24px;

    text-align: center;

}

.hero h1,
.command-header h1 {

    font-size: 42px;

    margin-bottom: 4px;

}

.hero p,
.command-header p {

    color: #CBD5E1;

    font-size: 16px;

}


/* ===========================
   TOOLBAR
=========================== */

.toolbar {

    background: rgba(15,23,42,0.92);

    border: 1px solid #334155;

    border-radius: 20px;

    padding: 18px;

    margin-bottom: 25px;

    box-shadow: 0px 8px 24px rgba(0,0,0,0.35);

}

.user-pill {

    display: inline-block;

    padding: 10px 18px;

    border-radius: 999px;

    background: #1E293B;

    border: 1px solid #334155;

    color: white;

    font-size: 16px;

    font-weight: 800;

}


/* ===========================
   TITULOS
=========================== */

.section-title {

    font-size: 24px;

    font-weight: 900;

    color: #F8FAFC;

    margin-top: 18px;

    margin-bottom: 12px;

    text-align: center;

}


/* ===========================
   TARJETAS KPI
=========================== */

.metric-card {

    background: rgba(15,23,42,0.92);

    border: 1px solid #334155;

    border-radius: 20px;

    padding: 20px;

    text-align: center;

    box-shadow: 0px 8px 24px rgba(0,0,0,0.35);

}

.metric-title {

    font-size: 13px;

    color: #94A3B8;

    font-weight: 800;

    text-transform: uppercase;

}

.metric-value {

    font-size: 34px;

    color: #F8FAFC;

    font-weight: 900;

}


/* ===========================
   TARJETAS GENERALES
=========================== */

.soft-card {

    background: rgba(15,23,42,0.92);

    border: 1px solid #334155;

    border-radius: 20px;

    padding: 20px;

    box-shadow: 0px 8px 24px rgba(0,0,0,0.35);

    margin-bottom: 18px;

}


/* ===========================
   ETIQUETAS
=========================== */

.status-pill {

    display: inline-block;

    padding: 7px 13px;

    border-radius: 999px;

    background: #0F766E;

    color: white;

    font-weight: 800;

    margin-top: 5px;

}

.info-pill {

    display: inline-block;

    padding: 6px 11px;

    border-radius: 999px;

    background: #1E293B;

    color: #CBD5E1;

    font-weight: 700;

    margin: 3px;

    border: 1px solid #334155;

}


/* ===========================
   LOGIN
=========================== */

.login-box {

    background: rgba(15,23,42,0.96);

    border: 1px solid #334155;

    border-radius: 28px;

    padding: 38px;

    box-shadow: 0px 18px 45px rgba(0,0,0,0.55);

    text-align: center;

    margin-bottom: 18px;

}

.login-icon {

    font-size: 58px;

    margin-bottom: 8px;

}

.login-title {

    font-size: 30px;

    font-weight: 900;

    color: #F8FAFC;

    margin-bottom: 6px;

}

.login-subtitle {

    font-size: 15px;

    color: #94A3B8;

    margin-bottom: 8px;

}

.login-footer {

    margin-top: 25px;

    color: #64748B;

    font-size: 13px;

    text-align: center;

}


/* ===========================
   BOTONES
=========================== */

.stButton > button {

    width: 100%;

    border-radius: 14px;

    border: 1px solid #334155;

    font-weight: 800;

    transition: 0.25s;

}

.stButton > button:hover {

    border-color: #38BDF8;

    transform: translateY(-2px);

}


/* ===========================
   DATAFRAME
=========================== */

div[data-testid="stDataFrame"] {

    border-radius: 16px;

    overflow: hidden;

}


/* ===========================
   SIDEBAR
=========================== */

section[data-testid="stSidebar"] {

    background-color: #0F172A;

}


/* ===========================
   PLOTLY
=========================== */

.js-plotly-plot {

    border-radius: 18px;

}

</style>
""", unsafe_allow_html=True)


# =========================
# FUNCIONES
# =========================

import hashlib
import shutil

ARCHIVO_PROYECTOS = "proyectos.csv"
ARCHIVO_MARCADOR_MIGRACION = ".multiproyecto_v1_migrado"

COLORES_PROYECTO = [
    "#FACC15",  # amarillo
    "#38BDF8",  # azul
    "#22C55E",  # verde
    "#F97316",  # naranja
    "#A855F7",  # morado
    "#EF4444",  # rojo
    "#14B8A6",  # turquesa
    "#E879F9",  # rosa
    "#84CC16",  # lima
    "#FB7185",  # coral
]


def clave_proyecto(proyecto):
    """Clave estable para widgets Streamlit."""
    return hashlib.sha1(str(proyecto).encode("utf-8")).hexdigest()[:10]


def crear_proyectos_iniciales():
    return pd.DataFrame([
        {"Proyecto": "Proyecto 1", "Color": COLORES_PROYECTO[0]}
    ])


def siguiente_color_proyecto(df_proyectos):
    usados = set(df_proyectos.get("Color", pd.Series(dtype=str)).dropna().astype(str).tolist())
    for color in COLORES_PROYECTO:
        if color not in usados:
            return color
    return COLORES_PROYECTO[len(df_proyectos) % len(COLORES_PROYECTO)]


def guardar_proyectos(df_proyectos):
    df_proyectos.to_csv(ARCHIVO_PROYECTOS, index=False)


def crear_datos_iniciales(proyecto="Proyecto 1"):
    data = []
    for i in range(1, 6):
        for punto in puntos_iniciales:
            data.append({
                "Proyecto": proyecto,
                "Control Box": f"Control Box {i}",
                "Punto": punto,
                "Completado": False
            })
    return pd.DataFrame(data)


def crear_info_inicial(proyecto, control_boxes):
    data = []
    for box in control_boxes:
        data.append({
            "Proyecto": proyecto,
            "Control Box": box,
            "Responsable": "",
            "Fecha Inicio": "",
            "Fecha Estimada": ""
        })
    return pd.DataFrame(data)


def crear_historial_vacio():
    return pd.DataFrame(columns=[
        "Fecha/Hora",
        "Usuario",
        "Rol",
        "Proyecto",
        "Control Box",
        "Punto",
        "Accion",
        "Estado",
        "Responsable"
    ])


def guardar(df):
    df.to_csv(ARCHIVO, index=False)


def guardar_info(df_info):
    df_info.to_csv(ARCHIVO_INFO, index=False)


def guardar_historial(df_historial):
    df_historial.to_csv(ARCHIVO_HISTORIAL, index=False)


def normalizar_booleanos(df):
    if "Completado" not in df.columns:
        df["Completado"] = False

    df["Completado"] = df["Completado"].astype(str).str.lower().map({
        "true": True,
        "false": False
    }).fillna(False)
    return df


def obtener_avance(df_filtrado):
    total = len(df_filtrado)
    completados = int(df_filtrado["Completado"].sum()) if total > 0 else 0
    pendientes = total - completados
    porcentaje = (completados / total) * 100 if total > 0 else 0
    return total, completados, pendientes, porcentaje


def obtener_fecha_valida(valor):
    if pd.isna(valor) or str(valor).strip() == "":
        return None
    try:
        return pd.to_datetime(valor).date()
    except Exception:
        return None


def calcular_tiempo_transcurrido(fecha_inicio):
    if fecha_inicio is None:
        return "Sin fecha"

    dias = (date.today() - fecha_inicio).days

    if dias < 0:
        return "Aún no inicia"
    if dias == 0:
        return "Hoy"
    if dias == 1:
        return "1 día"

    return f"{dias} días"


def calcular_estado_entrega(fecha_estimada):
    if fecha_estimada is None:
        return "Sin fecha estimada"

    dias = (fecha_estimada - date.today()).days

    if dias < 0:
        return f"Vencida por {abs(dias)} días"
    if dias == 0:
        return "Entrega hoy"
    if dias == 1:
        return "Falta 1 día"

    return f"Faltan {dias} días"


def grafica_dona(
    titulo,
    completados,
    pendientes,
    porcentaje,
    colores,
    altura=260,
    leyenda=False
):
    # Si la gráfica tiene leyenda, reservamos espacio a la derecha
    # y mantenemos la dona centrada en el área visible.
    dominio_x = [0.30, 0.70] if leyenda else [0.0, 1.0]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Completado", "Pendiente"],
                values=[completados, pendientes],
                hole=0.68,
                marker=dict(colors=colores),
                textinfo="none",
                hovertemplate="%{label}: %{value}<extra></extra>",
                domain=dict(
                    x=dominio_x,
                    y=[0.0, 1.0]
                )
            )
        ]
    )

    fig.add_annotation(
        text=f"<b>{porcentaje:.1f}%</b>",
        x=0.5,
        y=0.5,
        font=dict(size=30, color="#F8FAFC"),
        showarrow=False
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>",
            x=0.5,
            xanchor="center",
            font=dict(size=17, color="#F8FAFC")
        ),
        showlegend=leyenda,
        height=altura,
        margin=dict(t=58, b=20, l=12, r=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            x=0.74,
            y=0.50,
            xanchor="left",
            yanchor="middle",
            font=dict(color="#E5E7EB")
        )
    )

    return fig


def agregar_historial(df_historial, proyecto, control_box, punto, estado, responsable):
    accion = "Marcado como completado" if estado else "Marcado como pendiente"

    nueva_fila = pd.DataFrame([{
        "Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuario": st.session_state.get("usuario", ""),
        "Rol": st.session_state.get("rol", ""),
        "Proyecto": proyecto,
        "Control Box": control_box,
        "Punto": punto,
        "Accion": accion,
        "Estado": estado,
        "Responsable": responsable
    }])

    return pd.concat([df_historial, nueva_fila], ignore_index=True)


def obtener_responsable(df_info, proyecto, control_box):
    fila = df_info[
        (df_info["Proyecto"].astype(str) == str(proyecto)) &
        (df_info["Control Box"].astype(str) == str(control_box))
    ]
    if len(fila) == 0:
        return ""
    return str(fila.iloc[0]["Responsable"])


def sincronizar_info_con_boxes(df_info, proyecto, control_boxes):
    mask_proyecto = df_info["Proyecto"].astype(str) == str(proyecto)
    existentes = df_info.loc[mask_proyecto, "Control Box"].astype(str).unique().tolist()
    nuevas_filas = []

    for box in control_boxes:
        if box not in existentes:
            nuevas_filas.append({
                "Proyecto": proyecto,
                "Control Box": box,
                "Responsable": "",
                "Fecha Inicio": "",
                "Fecha Estimada": ""
            })

    if nuevas_filas:
        df_info = pd.concat([df_info, pd.DataFrame(nuevas_filas)], ignore_index=True)

    # Elimina información huérfana solo del proyecto actual.
    mask_proyecto = df_info["Proyecto"].astype(str) == str(proyecto)
    conservar = (~mask_proyecto) | df_info["Control Box"].astype(str).isin(control_boxes)
    return df_info[conservar].copy()


def exportar_reporte_excel(df, df_info, df_historial):
    resumen = []

    for proyecto in sorted(df["Proyecto"].dropna().astype(str).unique().tolist()):
        df_proyecto = df[df["Proyecto"].astype(str) == str(proyecto)]
        control_boxes = sorted(df_proyecto["Control Box"].dropna().astype(str).unique().tolist())

        for box in control_boxes:
            df_box = df_proyecto[df_proyecto["Control Box"].astype(str) == str(box)]
            total, completados, pendientes, porcentaje = obtener_avance(df_box)
            info = df_info[
                (df_info["Proyecto"].astype(str) == str(proyecto)) &
                (df_info["Control Box"].astype(str) == str(box))
            ]

            if len(info) > 0:
                responsable = info.iloc[0]["Responsable"]
                fecha_inicio = info.iloc[0]["Fecha Inicio"]
                fecha_estimada = info.iloc[0]["Fecha Estimada"]
            else:
                responsable = ""
                fecha_inicio = ""
                fecha_estimada = ""

            resumen.append({
                "Proyecto": proyecto,
                "Control Box": box,
                "Responsable": responsable,
                "Fecha Inicio": fecha_inicio,
                "Fecha Estimada": fecha_estimada,
                "Total Checks": total,
                "Completados": completados,
                "Pendientes": pendientes,
                "Avance %": round(porcentaje, 2)
            })

    df_resumen = pd.DataFrame(resumen)

    with pd.ExcelWriter(ARCHIVO_REPORTE, engine="openpyxl") as writer:
        df_resumen.to_excel(writer, sheet_name="Resumen", index=False)
        df.to_excel(writer, sheet_name="Checklist", index=False)
        df_info.to_excel(writer, sheet_name="Info Control Boxes", index=False)
        df_historial.to_excel(writer, sheet_name="Historial", index=False)

    return ARCHIVO_REPORTE


# =========================
# LOGIN
# =========================

if "login" not in st.session_state:
    st.session_state["login"] = False

if not st.session_state["login"]:

    st.markdown("""
    <div class="hero">
        <h1>🧰 Control Box Command Center</h1>
        <p>Sistema de seguimiento para armado de Control Boxes</p>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1.2, 1, 1.2])

    with col_b:
        st.markdown("""
        <div class="login-box">
            <div class="login-icon">🧰</div>
            <div class="login-title">Bienvenido</div>
            <div class="login-subtitle">Inicia sesión para continuar</div>
        </div>
        """, unsafe_allow_html=True)

        usuario = st.text_input(
            label="Usuario",
            placeholder="👤 Usuario",
            label_visibility="collapsed"
        )

        password = st.text_input(
            label="Contraseña",
            placeholder="🔒 Contraseña",
            type="password",
            label_visibility="collapsed"
        )

        if st.button("🔐 Iniciar sesión", width="stretch"):
            if usuario in USUARIOS and password == USUARIOS[usuario]["password"]:
                st.session_state["login"] = True
                st.session_state["usuario"] = usuario
                st.session_state["rol"] = USUARIOS[usuario]["rol"]
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

        st.markdown("""
        <div class="login-footer">
            NS Fabricación de Equipos
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# =========================
# CARGAR / MIGRAR PROYECTOS
# =========================

if not os.path.exists(ARCHIVO_PROYECTOS) or os.path.getsize(ARCHIVO_PROYECTOS) == 0:
    df_proyectos = crear_proyectos_iniciales()
    guardar_proyectos(df_proyectos)
else:
    try:
        df_proyectos = pd.read_csv(ARCHIVO_PROYECTOS)
    except pd.errors.EmptyDataError:
        df_proyectos = crear_proyectos_iniciales()
        guardar_proyectos(df_proyectos)

if "Proyecto" not in df_proyectos.columns:
    df_proyectos = crear_proyectos_iniciales()

if "Color" not in df_proyectos.columns:
    df_proyectos["Color"] = [
        COLORES_PROYECTO[i % len(COLORES_PROYECTO)] for i in range(len(df_proyectos))
    ]

# Limpieza de catálogo.
df_proyectos["Proyecto"] = df_proyectos["Proyecto"].fillna("").astype(str).str.strip()
df_proyectos = df_proyectos[df_proyectos["Proyecto"] != ""].drop_duplicates("Proyecto").reset_index(drop=True)

if len(df_proyectos) == 0:
    df_proyectos = crear_proyectos_iniciales()

for i in range(len(df_proyectos)):
    color = str(df_proyectos.loc[i, "Color"]).strip()
    if not color.startswith("#"):
        df_proyectos.loc[i, "Color"] = COLORES_PROYECTO[i % len(COLORES_PROYECTO)]

proyecto_legacy = str(df_proyectos.iloc[0]["Proyecto"])


# =========================
# CARGAR / MIGRAR CHECKLIST
# =========================

if not os.path.exists(ARCHIVO) or os.path.getsize(ARCHIVO) == 0:
    df = crear_datos_iniciales(proyecto_legacy)
    guardar(df)
else:
    try:
        df = pd.read_csv(ARCHIVO)
    except pd.errors.EmptyDataError:
        df = crear_datos_iniciales(proyecto_legacy)
        guardar(df)

# MIGRACIÓN AUTOMÁTICA: conserva todo el avance anterior.
# Antes de modificar el formato de los CSV antiguos, crea una copia de seguridad
# automática una sola vez.
if "Proyecto" not in df.columns and not os.path.exists(ARCHIVO_MARCADOR_MIGRACION):
    carpeta_backup = f"backup_pre_multiproyecto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(carpeta_backup, exist_ok=True)

    for archivo_backup in [ARCHIVO, ARCHIVO_INFO, ARCHIVO_HISTORIAL, ARCHIVO_REPORTE]:
        if os.path.exists(archivo_backup):
            shutil.copy2(archivo_backup, os.path.join(carpeta_backup, os.path.basename(archivo_backup)))

    with open(ARCHIVO_MARCADOR_MIGRACION, "w", encoding="utf-8") as marcador:
        marcador.write(carpeta_backup)

if "Proyecto" not in df.columns:
    df.insert(0, "Proyecto", proyecto_legacy)

for columna, valor in {
    "Control Box": "",
    "Punto": "",
    "Completado": False,
}.items():
    if columna not in df.columns:
        df[columna] = valor

df["Proyecto"] = df["Proyecto"].fillna(proyecto_legacy).astype(str)
df["Control Box"] = df["Control Box"].fillna("").astype(str)
df["Punto"] = df["Punto"].fillna("").astype(str)
df = normalizar_booleanos(df)


# =========================
# CARGAR / MIGRAR INFO
# =========================

if not os.path.exists(ARCHIVO_INFO) or os.path.getsize(ARCHIVO_INFO) == 0:
    piezas_info = []
    for proyecto in df_proyectos["Proyecto"].tolist():
        boxes = sorted(df.loc[df["Proyecto"] == proyecto, "Control Box"].unique().tolist())
        piezas_info.append(crear_info_inicial(proyecto, boxes))
    df_info = pd.concat(piezas_info, ignore_index=True) if piezas_info else pd.DataFrame()
    guardar_info(df_info)
else:
    try:
        df_info = pd.read_csv(ARCHIVO_INFO)
    except pd.errors.EmptyDataError:
        df_info = pd.DataFrame()

if "Proyecto" not in df_info.columns:
    df_info.insert(0, "Proyecto", proyecto_legacy)

for columna in ["Proyecto", "Control Box", "Responsable", "Fecha Inicio", "Fecha Estimada"]:
    if columna not in df_info.columns:
        df_info[columna] = ""
    df_info[columna] = df_info[columna].fillna("").astype(str)


# =========================
# CARGAR / MIGRAR HISTORIAL
# =========================

if not os.path.exists(ARCHIVO_HISTORIAL) or os.path.getsize(ARCHIVO_HISTORIAL) == 0:
    df_historial = crear_historial_vacio()
    guardar_historial(df_historial)
else:
    try:
        df_historial = pd.read_csv(ARCHIVO_HISTORIAL)
    except pd.errors.EmptyDataError:
        df_historial = crear_historial_vacio()

if "Proyecto" not in df_historial.columns:
    df_historial["Proyecto"] = proyecto_legacy

for columna in crear_historial_vacio().columns:
    if columna not in df_historial.columns:
        df_historial[columna] = ""


# Si aparecen proyectos en los CSV que no están en proyectos.csv, los incorporamos.
proyectos_detectados = set(df["Proyecto"].dropna().astype(str).tolist())
proyectos_detectados.update(df_info["Proyecto"].dropna().astype(str).tolist())
proyectos_detectados.update(df_historial["Proyecto"].dropna().astype(str).tolist())
proyectos_detectados.discard("")

for proyecto in sorted(proyectos_detectados):
    if proyecto not in df_proyectos["Proyecto"].tolist():
        nuevo_color = siguiente_color_proyecto(df_proyectos)
        df_proyectos = pd.concat([
            df_proyectos,
            pd.DataFrame([{"Proyecto": proyecto, "Color": nuevo_color}])
        ], ignore_index=True)

# Sincronizar info de cada proyecto con sus Control Boxes.
for proyecto in df_proyectos["Proyecto"].tolist():
    boxes = sorted(
        df.loc[df["Proyecto"].astype(str) == str(proyecto), "Control Box"]
        .dropna().astype(str).unique().tolist()
    )
    df_info = sincronizar_info_con_boxes(df_info, proyecto, boxes)

# Asegurar tipos finales.
for columna in ["Proyecto", "Control Box", "Responsable", "Fecha Inicio", "Fecha Estimada"]:
    df_info[columna] = df_info[columna].fillna("").astype(str)

# Persistir migración una sola vez sin perder el avance.
guardar(df)
guardar_info(df_info)
guardar_historial(df_historial)
guardar_proyectos(df_proyectos)


# =========================
# ENCABEZADO + TOOLBAR GLOBAL
# =========================

st.markdown("""
<div class="command-header">
    <h1>🧰 Control Box Command Center</h1>
    <p>Dashboard multiproyecto para seguimiento de armado, validación y avance general.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='toolbar'>", unsafe_allow_html=True)

col_user, col_save, col_excel, col_download, col_logout = st.columns([2.8, 1.2, 1.3, 1.5, 1.2])

with col_user:
    st.markdown(
        f"""
        <div class="user-pill">
            👤 {st.session_state["usuario"]} &nbsp; | &nbsp; 🟢 {st.session_state["rol"]}
        </div>
        """,
        unsafe_allow_html=True
    )

with col_save:
    if st.button("💾 Guardar", width="stretch", key="global_guardar"):
        guardar(df)
        guardar_info(df_info)
        guardar_historial(df_historial)
        guardar_proyectos(df_proyectos)
        st.toast("Cambios guardados correctamente ✅")

with col_excel:
    if tiene_permiso(["Supervisor", "Admin"]):
        if st.button("📊 Exportar", width="stretch", key="global_exportar"):
            guardar(df)
            guardar_info(df_info)
            guardar_historial(df_historial)
            guardar_proyectos(df_proyectos)
            exportar_reporte_excel(df, df_info, df_historial)
            st.toast("Reporte Excel multiproyecto generado ✅")

with col_download:
    if tiene_permiso(["Supervisor", "Admin"]) and os.path.exists(ARCHIVO_REPORTE):
        with open(ARCHIVO_REPORTE, "rb") as file:
            st.download_button(
                label="⬇️ Descargar",
                data=file,
                file_name="reporte_control_boxes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
                key="global_descargar"
            )

with col_logout:
    if st.button("🚪 Salir", width="stretch", key="global_salir"):
        st.session_state["login"] = False
        st.session_state["usuario"] = ""
        st.session_state["rol"] = ""
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# GESTIÓN DE PROYECTOS
# =========================

if tiene_permiso(["Supervisor", "Admin"]):
    with st.expander("⚙️ Gestión de proyectos", expanded=False):
        col_p1, col_p2, col_p3 = st.columns(3)

        with col_p1:
            st.markdown("### Crear proyecto")
            nuevo_proyecto = st.text_input(
                "Nombre del nuevo proyecto",
                placeholder="Ej. Línea F09 - Agosto",
                key="proyecto_nuevo_nombre"
            )

            opciones_plantilla = ["Estructura base"] + df_proyectos["Proyecto"].tolist()
            plantilla = st.selectbox(
                "Plantilla",
                opciones_plantilla,
                key="proyecto_plantilla",
                help="Estructura base crea 5 Control Boxes. También puedes duplicar la estructura de otro proyecto."
            )

            copiar_avance = False
            if plantilla != "Estructura base":
                copiar_avance = st.checkbox(
                    "Copiar también el avance actual",
                    value=False,
                    key="proyecto_copiar_avance"
                )

            if st.button("➕ Crear proyecto", width="stretch", key="proyecto_crear"):
                nombre = nuevo_proyecto.strip()

                if nombre == "":
                    st.warning("Escribe un nombre para el proyecto.")
                elif nombre in df_proyectos["Proyecto"].tolist():
                    st.warning("Ya existe un proyecto con ese nombre.")
                else:
                    color = siguiente_color_proyecto(df_proyectos)
                    df_proyectos = pd.concat([
                        df_proyectos,
                        pd.DataFrame([{"Proyecto": nombre, "Color": color}])
                    ], ignore_index=True)

                    if plantilla == "Estructura base":
                        nuevos_datos = crear_datos_iniciales(nombre)
                        boxes_nuevos = sorted(nuevos_datos["Control Box"].unique().tolist())
                        nueva_info = crear_info_inicial(nombre, boxes_nuevos)
                    else:
                        origen = df[df["Proyecto"].astype(str) == str(plantilla)].copy()
                        origen["Proyecto"] = nombre
                        if not copiar_avance:
                            origen["Completado"] = False
                        nuevos_datos = origen

                        boxes_nuevos = sorted(origen["Control Box"].unique().tolist())
                        nueva_info = crear_info_inicial(nombre, boxes_nuevos)

                    df = pd.concat([df, nuevos_datos], ignore_index=True)
                    df_info = pd.concat([df_info, nueva_info], ignore_index=True)

                    guardar(df)
                    guardar_info(df_info)
                    guardar_proyectos(df_proyectos)
                    st.rerun()

        with col_p2:
            st.markdown("### Renombrar / color")
            proyecto_editar = st.selectbox(
                "Proyecto",
                df_proyectos["Proyecto"].tolist(),
                key="proyecto_editar_select"
            )

            nombre_renombrado = st.text_input(
                "Nuevo nombre",
                value=proyecto_editar,
                key="proyecto_renombrar_nombre"
            )

            color_actual = str(
                df_proyectos.loc[df_proyectos["Proyecto"] == proyecto_editar, "Color"].iloc[0]
            )
            color_nuevo = st.color_picker(
                "Color de avance total",
                value=color_actual,
                key="proyecto_color"
            )

            if st.button("💾 Guardar proyecto", width="stretch", key="proyecto_guardar_cambios"):
                nuevo_nombre = nombre_renombrado.strip()

                if nuevo_nombre == "":
                    st.warning("El nombre no puede quedar vacío.")
                elif nuevo_nombre != proyecto_editar and nuevo_nombre in df_proyectos["Proyecto"].tolist():
                    st.warning("Ya existe otro proyecto con ese nombre.")
                else:
                    mask_catalogo = df_proyectos["Proyecto"] == proyecto_editar
                    df_proyectos.loc[mask_catalogo, "Proyecto"] = nuevo_nombre
                    df_proyectos.loc[df_proyectos["Proyecto"] == nuevo_nombre, "Color"] = color_nuevo

                    df.loc[df["Proyecto"].astype(str) == str(proyecto_editar), "Proyecto"] = nuevo_nombre
                    df_info.loc[df_info["Proyecto"].astype(str) == str(proyecto_editar), "Proyecto"] = nuevo_nombre
                    df_historial.loc[df_historial["Proyecto"].astype(str) == str(proyecto_editar), "Proyecto"] = nuevo_nombre

                    guardar(df)
                    guardar_info(df_info)
                    guardar_historial(df_historial)
                    guardar_proyectos(df_proyectos)
                    st.rerun()

        with col_p3:
            st.markdown("### Eliminar proyecto")

            if tiene_permiso(["Admin"]):
                proyecto_borrar = st.selectbox(
                    "Proyecto a eliminar",
                    df_proyectos["Proyecto"].tolist(),
                    key="proyecto_borrar_select"
                )

                confirmar_proyecto = st.checkbox(
                    "Confirmo eliminar todo el proyecto",
                    key="proyecto_borrar_confirmar"
                )

                if st.button("🗑️ Eliminar proyecto", width="stretch", key="proyecto_borrar_boton"):
                    if len(df_proyectos) <= 1:
                        st.warning("Debe existir al menos un proyecto.")
                    elif not confirmar_proyecto:
                        st.warning("Activa la confirmación antes de eliminar.")
                    else:
                        df = df[df["Proyecto"].astype(str) != str(proyecto_borrar)].copy()
                        df_info = df_info[df_info["Proyecto"].astype(str) != str(proyecto_borrar)].copy()
                        df_historial = df_historial[df_historial["Proyecto"].astype(str) != str(proyecto_borrar)].copy()
                        df_proyectos = df_proyectos[df_proyectos["Proyecto"].astype(str) != str(proyecto_borrar)].copy()

                        guardar(df)
                        guardar_info(df_info)
                        guardar_historial(df_historial)
                        guardar_proyectos(df_proyectos)
                        st.rerun()
            else:
                st.warning("Solo Admin puede eliminar proyectos.")


# =========================
# DASHBOARD DE CADA PROYECTO
# =========================

def render_proyecto(proyecto, color_proyecto):
    global df, df_info, df_historial

    k = clave_proyecto(proyecto)

    df_proyecto = df[df["Proyecto"].astype(str) == str(proyecto)].copy()
    info_proyecto = df_info[df_info["Proyecto"].astype(str) == str(proyecto)].copy()
    historial_proyecto = df_historial[df_historial["Proyecto"].astype(str) == str(proyecto)].copy()

    control_boxes = sorted(df_proyecto["Control Box"].dropna().astype(str).unique().tolist())

    st.markdown(
        f'<div class="section-title">Proyecto: {proyecto}</div>',
        unsafe_allow_html=True
    )

    # =========================
    # DASHBOARD GENERAL
    # =========================

    total_puntos, total_completados, total_pendientes, porcentaje_total = obtener_avance(df_proyecto)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    with col_m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avance total</div>
            <div class="metric-value">{porcentaje_total:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Completados</div>
            <div class="metric-value">{total_completados}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Pendientes</div>
            <div class="metric-value">{total_pendientes}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Control Boxes</div>
            <div class="metric-value">{len(control_boxes)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Avance total del proyecto</div>', unsafe_allow_html=True)

    fig_total = grafica_dona(
        proyecto,
        total_completados,
        total_pendientes,
        porcentaje_total,
        [color_proyecto, "#334155"],
        altura=430,
        leyenda=True
    )

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.plotly_chart(fig_total, width="stretch", key=f"chart_total_{k}")

    # =========================
    # AVANCE POR CONTROL BOX
    # =========================

    st.markdown("---")
    st.markdown('<div class="section-title">Avance por Control Box</div>', unsafe_allow_html=True)

    if len(control_boxes) > 0:
        columnas = st.columns(min(len(control_boxes), 5))

        for i, box in enumerate(control_boxes):
            df_box = df_proyecto[df_proyecto["Control Box"].astype(str) == str(box)]
            total_box, completados_box, pendientes_box, porcentaje_box = obtener_avance(df_box)
            colores = colores_default[i % len(colores_default)]

            info_box = info_proyecto[info_proyecto["Control Box"].astype(str) == str(box)]

            if len(info_box) > 0:
                responsable = str(info_box.iloc[0]["Responsable"])
                fecha_inicio = obtener_fecha_valida(info_box.iloc[0]["Fecha Inicio"])
                fecha_estimada = obtener_fecha_valida(info_box.iloc[0]["Fecha Estimada"])
            else:
                responsable = ""
                fecha_inicio = None
                fecha_estimada = None

            tiempo_transcurrido = calcular_tiempo_transcurrido(fecha_inicio)
            estado_entrega = calcular_estado_entrega(fecha_estimada)

            fig_box = grafica_dona(
                box,
                completados_box,
                pendientes_box,
                porcentaje_box,
                colores,
                altura=270
            )

            with columnas[i % len(columnas)]:
                st.plotly_chart(fig_box, width="stretch", key=f"chart_box_{k}_{i}")
                st.markdown(
                    f"""
                    <div style="text-align:center;">
                        <span class="status-pill">✅ {completados_box}/{total_box} checks</span><br>
                        <span class="info-pill">👤 {responsable if responsable else "Sin responsable"}</span><br>
                        <span class="info-pill">⏱️ {tiempo_transcurrido}</span><br>
                        <span class="info-pill">📅 {estado_entrega}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("Este proyecto aún no tiene Control Boxes.")

    # =========================
    # PANEL DE ADMINISTRACIÓN
    # =========================

    st.markdown("---")
    st.markdown('<div class="section-title">Panel de administración</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "➕ Crear / Eliminar",
        "✏️ Renombrar",
        "📋 Copiar checklist",
        "✅ Editar avance",
        "👤 Info / Fechas",
        "🕓 Historial"
    ])

    # =========================
    # TAB 1 - CREAR / ELIMINAR
    # =========================

    with tab1:
        if tiene_permiso(["Supervisor", "Admin"]):
            col_crear, col_borrar = st.columns(2)

            with col_crear:
                st.markdown("### Crear Control Box")

                nueva_control_box = st.text_input(
                    "Nombre de la nueva Control Box",
                    placeholder="Ej. CB-F09-001",
                    key=f"{k}_nueva_box"
                )

                if st.button("➕ Crear Control Box", key=f"{k}_crear_box"):
                    nuevo_nombre = nueva_control_box.strip()

                    if nuevo_nombre == "":
                        st.warning("Escribe un nombre válido.")
                    elif nuevo_nombre in control_boxes:
                        st.warning("Ya existe una Control Box con ese nombre en este proyecto.")
                    else:
                        nuevas_filas = []

                        for punto in puntos_iniciales:
                            nuevas_filas.append({
                                "Proyecto": proyecto,
                                "Control Box": nuevo_nombre,
                                "Punto": punto,
                                "Completado": False
                            })

                        nueva_info = pd.DataFrame([{
                            "Proyecto": proyecto,
                            "Control Box": nuevo_nombre,
                            "Responsable": "",
                            "Fecha Inicio": "",
                            "Fecha Estimada": ""
                        }])

                        df = pd.concat([df, pd.DataFrame(nuevas_filas)], ignore_index=True)
                        df_info = pd.concat([df_info, nueva_info], ignore_index=True)

                        guardar(df)
                        guardar_info(df_info)
                        st.rerun()

            with col_borrar:
                st.markdown("### Eliminar Control Box")

                if tiene_permiso(["Admin"]):
                    if len(control_boxes) > 0:
                        control_box_borrar = st.selectbox(
                            "Control Box a eliminar",
                            control_boxes,
                            key=f"{k}_borrar_box_select"
                        )

                        confirmar_borrado = st.checkbox(
                            "Confirmo que deseo eliminar esta Control Box",
                            key=f"{k}_confirmar_borrado_box"
                        )

                        if st.button("🗑️ Eliminar Control Box", key=f"{k}_borrar_box_btn"):
                            if confirmar_borrado:
                                mask_box = (
                                    (df["Proyecto"].astype(str) == str(proyecto)) &
                                    (df["Control Box"].astype(str) == str(control_box_borrar))
                                )
                                df = df[~mask_box].copy()

                                mask_info = (
                                    (df_info["Proyecto"].astype(str) == str(proyecto)) &
                                    (df_info["Control Box"].astype(str) == str(control_box_borrar))
                                )
                                df_info = df_info[~mask_info].copy()

                                mask_hist = (
                                    (df_historial["Proyecto"].astype(str) == str(proyecto)) &
                                    (df_historial["Control Box"].astype(str) == str(control_box_borrar))
                                )
                                df_historial = df_historial[~mask_hist].copy()

                                guardar(df)
                                guardar_info(df_info)
                                guardar_historial(df_historial)
                                st.rerun()
                            else:
                                st.warning("Activa la confirmación antes de eliminar.")
                    else:
                        st.info("No hay Control Boxes para eliminar.")
                else:
                    st.warning("Solo Admin puede eliminar Control Boxes.")
        else:
            st.warning("No tienes permiso para crear o eliminar Control Boxes.")

    # =========================
    # TAB 2 - RENOMBRAR
    # =========================

    with tab2:
        if tiene_permiso(["Supervisor", "Admin"]):
            st.markdown("### Renombrar Control Box")

            col_ren1, col_ren2 = st.columns(2)

            with col_ren1:
                if len(control_boxes) > 0:
                    box_a_renombrar = st.selectbox(
                        "Selecciona la Control Box",
                        control_boxes,
                        key=f"{k}_box_renombrar"
                    )
                else:
                    box_a_renombrar = None
                    st.info("No hay Control Boxes disponibles.")

            with col_ren2:
                nuevo_nombre_box = st.text_input(
                    "Nuevo nombre",
                    placeholder="Ej. CB-F09-001",
                    key=f"{k}_nuevo_nombre_box"
                )

            if st.button("Guardar nuevo nombre", key=f"{k}_guardar_nombre_box"):
                if box_a_renombrar is None:
                    st.warning("No hay Control Box para renombrar.")
                elif nuevo_nombre_box.strip() == "":
                    st.warning("Escribe un nuevo nombre.")
                elif nuevo_nombre_box.strip() in control_boxes:
                    st.warning("Ese nombre ya existe dentro de este proyecto.")
                else:
                    nuevo_nombre = nuevo_nombre_box.strip()

                    mask_df = (
                        (df["Proyecto"].astype(str) == str(proyecto)) &
                        (df["Control Box"].astype(str) == str(box_a_renombrar))
                    )
                    df.loc[mask_df, "Control Box"] = nuevo_nombre

                    mask_info = (
                        (df_info["Proyecto"].astype(str) == str(proyecto)) &
                        (df_info["Control Box"].astype(str) == str(box_a_renombrar))
                    )
                    df_info.loc[mask_info, "Control Box"] = nuevo_nombre

                    mask_hist = (
                        (df_historial["Proyecto"].astype(str) == str(proyecto)) &
                        (df_historial["Control Box"].astype(str) == str(box_a_renombrar))
                    )
                    df_historial.loc[mask_hist, "Control Box"] = nuevo_nombre

                    guardar(df)
                    guardar_info(df_info)
                    guardar_historial(df_historial)
                    st.rerun()
        else:
            st.warning("No tienes permiso para renombrar Control Boxes.")

    # =========================
    # TAB 3 - COPIAR CHECKLIST
    # =========================

    with tab3:
        if tiene_permiso(["Supervisor", "Admin"]):
            st.markdown("### Copiar checklist entre Control Boxes")

            if len(control_boxes) >= 2:
                col_copy1, col_copy2 = st.columns(2)

                with col_copy1:
                    box_origen = st.selectbox(
                        "Copiar tareas desde",
                        control_boxes,
                        key=f"{k}_box_origen"
                    )

                with col_copy2:
                    opciones_destino = [box for box in control_boxes if box != box_origen]

                    box_destino = st.selectbox(
                        "Copiar tareas hacia",
                        opciones_destino,
                        key=f"{k}_box_destino"
                    )

                copiar_estado = st.checkbox(
                    "Copiar también el estado de completado",
                    value=False,
                    key=f"{k}_copiar_estado"
                )

                col_btn1, col_btn2 = st.columns(2)

                with col_btn1:
                    if st.button("Copiar a Control Box seleccionada", key=f"{k}_copiar_una"):
                        df_origen = df_proyecto[df_proyecto["Control Box"].astype(str) == str(box_origen)].copy()

                        if copiar_estado:
                            nuevas_tareas = df_origen[["Punto", "Completado"]].copy()
                        else:
                            nuevas_tareas = df_origen[["Punto"]].copy()
                            nuevas_tareas["Completado"] = False

                        nuevas_tareas["Proyecto"] = proyecto
                        nuevas_tareas["Control Box"] = box_destino
                        nuevas_tareas = nuevas_tareas[["Proyecto", "Control Box", "Punto", "Completado"]]

                        mask_destino = (
                            (df["Proyecto"].astype(str) == str(proyecto)) &
                            (df["Control Box"].astype(str) == str(box_destino))
                        )
                        df = df[~mask_destino].copy()
                        df = pd.concat([df, nuevas_tareas], ignore_index=True)

                        guardar(df)
                        st.rerun()

                with col_btn2:
                    if st.button("Copiar a todas las demás", key=f"{k}_copiar_todas"):
                        df_origen = df_proyecto[df_proyecto["Control Box"].astype(str) == str(box_origen)].copy()
                        mask_proyecto = df["Proyecto"].astype(str) == str(proyecto)
                        df_fuera = df[~mask_proyecto].copy()
                        df_nuevo_proyecto = df_proyecto[df_proyecto["Control Box"].astype(str) == str(box_origen)].copy()

                        for destino in opciones_destino:
                            if copiar_estado:
                                nuevas_tareas = df_origen[["Punto", "Completado"]].copy()
                            else:
                                nuevas_tareas = df_origen[["Punto"]].copy()
                                nuevas_tareas["Completado"] = False

                            nuevas_tareas["Proyecto"] = proyecto
                            nuevas_tareas["Control Box"] = destino
                            nuevas_tareas = nuevas_tareas[["Proyecto", "Control Box", "Punto", "Completado"]]
                            df_nuevo_proyecto = pd.concat([df_nuevo_proyecto, nuevas_tareas], ignore_index=True)

                        df = pd.concat([df_fuera, df_nuevo_proyecto], ignore_index=True)
                        guardar(df)
                        st.rerun()
            else:
                st.info("Necesitas al menos 2 Control Boxes para copiar tareas.")
        else:
            st.warning("No tienes permiso para copiar checklists.")

    # =========================
    # TAB 4 - EDITAR AVANCE
    # =========================

    with tab4:
        st.markdown("### Editar checklist")

        if len(control_boxes) > 0:
            control_box_seleccionada = st.selectbox(
                "Selecciona la Control Box que deseas editar",
                control_boxes,
                key=f"{k}_editar_box"
            )

            df_seleccionada = df_proyecto[
                df_proyecto["Control Box"].astype(str) == str(control_box_seleccionada)
            ].copy()

            total_sel, comp_sel, pend_sel, porc_sel = obtener_avance(df_seleccionada)
            responsable_actual = obtener_responsable(df_info, proyecto, control_box_seleccionada)

            st.markdown(
                f"""<div class="soft-card">
<h3>{control_box_seleccionada}</h3>
<p>
<b>Avance:</b> {porc_sel:.1f}%
&nbsp; | &nbsp;
<b>Completados:</b> {comp_sel}/{total_sel}
&nbsp; | &nbsp;
<b>Pendientes:</b> {pend_sel}
&nbsp; | &nbsp;
<b>Responsable:</b> {responsable_actual if responsable_actual else "Sin responsable"}
</p>
</div>""",
                unsafe_allow_html=True
            )

            df_anterior = df_seleccionada[["Punto", "Completado"]].copy()

            with st.form(
                key=f"{k}_form_checklist_{clave_proyecto(control_box_seleccionada)}",
                clear_on_submit=False
            ):
                df_editado = st.data_editor(
                    df_seleccionada[["Punto", "Completado"]],
                    width="stretch",
                    hide_index=True,
                    key=f"{k}_editor_{clave_proyecto(control_box_seleccionada)}",
                    disabled=["Punto"],
                    column_config={
                        "Punto": st.column_config.TextColumn(
                            "Punto de armado",
                            width="large"
                        ),
                        "Completado": st.column_config.CheckboxColumn(
                            "Completado",
                            help="Marca todas las tareas necesarias y después presiona Guardar avance",
                            default=False
                        )
                    }
                )

                guardar_avance = st.form_submit_button(
                    "💾 Guardar avance",
                    width="stretch"
                )

            if guardar_avance:
                cambios_realizados = 0

                for _, row in df_editado.iterrows():
                    punto = row["Punto"]
                    completado_nuevo = bool(row["Completado"])

                    valor_anterior = df_anterior[
                        df_anterior["Punto"].astype(str) == str(punto)
                    ]["Completado"]

                    if len(valor_anterior) > 0:
                        completado_anterior = bool(valor_anterior.iloc[0])

                        if completado_anterior != completado_nuevo:
                            cambios_realizados += 1
                            df_historial = agregar_historial(
                                df_historial,
                                proyecto,
                                control_box_seleccionada,
                                punto,
                                completado_nuevo,
                                responsable_actual
                            )

                    mask_punto = (
                        (df["Proyecto"].astype(str) == str(proyecto)) &
                        (df["Control Box"].astype(str) == str(control_box_seleccionada)) &
                        (df["Punto"].astype(str) == str(punto))
                    )
                    df.loc[mask_punto, "Completado"] = completado_nuevo

                guardar(df)
                guardar_historial(df_historial)

                if cambios_realizados > 0:
                    st.success(f"✅ {cambios_realizados} cambios guardados correctamente.")
                else:
                    st.info("No se detectaron cambios.")

                st.rerun()

            # Administrar tareas
            if tiene_permiso(["Técnico", "Supervisor", "Admin"]):
                st.markdown("### Administrar tareas de esta Control Box")
                col_agregar, col_eliminar = st.columns(2)

                with col_agregar:
                    nueva_tarea = st.text_input(
                        "Nueva tarea",
                        placeholder="Ej. Validar comunicación Ethernet",
                        key=f"{k}_nueva_tarea_editor"
                    )

                    if st.button("➕ Agregar tarea", key=f"{k}_agregar_tarea_editor"):
                        if nueva_tarea.strip() != "":
                            nueva_fila = pd.DataFrame({
                                "Proyecto": [proyecto],
                                "Control Box": [control_box_seleccionada],
                                "Punto": [nueva_tarea.strip()],
                                "Completado": [False]
                            })
                            df = pd.concat([df, nueva_fila], ignore_index=True)
                            guardar(df)
                            st.rerun()
                        else:
                            st.warning("Escribe el nombre de la tarea.")

                with col_eliminar:
                    if tiene_permiso(["Admin"]):
                        if len(df_seleccionada) > 0:
                            tarea_eliminar = st.selectbox(
                                "Tarea a eliminar",
                                df_seleccionada["Punto"],
                                key=f"{k}_eliminar_tarea_editor"
                            )

                            if st.button("🗑️ Eliminar tarea", key=f"{k}_boton_eliminar_tarea"):
                                mask_tarea = (
                                    (df["Proyecto"].astype(str) == str(proyecto)) &
                                    (df["Control Box"].astype(str) == str(control_box_seleccionada)) &
                                    (df["Punto"].astype(str) == str(tarea_eliminar))
                                )
                                df = df[~mask_tarea].copy()
                                guardar(df)
                                st.rerun()
                        else:
                            st.info("No hay tareas para eliminar.")
                    else:
                        st.warning("Solo Admin puede eliminar tareas.")

            # Reinicio
            if tiene_permiso(["Admin"]):
                st.markdown("### Reinicio")
                col_reset1, col_reset2 = st.columns(2)

                with col_reset1:
                    if st.button("Reiniciar esta Control Box", key=f"{k}_reiniciar_box_editor"):
                        mask_box = (
                            (df["Proyecto"].astype(str) == str(proyecto)) &
                            (df["Control Box"].astype(str) == str(control_box_seleccionada))
                        )
                        df.loc[mask_box, "Completado"] = False
                        guardar(df)
                        st.rerun()

                with col_reset2:
                    confirmar_reset = st.checkbox(
                        f"Confirmo reiniciar todo {proyecto}",
                        key=f"{k}_confirmar_reset_editor"
                    )

                    if st.button("Reiniciar todo el proyecto", key=f"{k}_reiniciar_proyecto_editor"):
                        if confirmar_reset:
                            mask_proyecto = df["Proyecto"].astype(str) == str(proyecto)
                            df.loc[mask_proyecto, "Completado"] = False
                            guardar(df)
                            st.rerun()
                        else:
                            st.warning("Activa la confirmación antes de reiniciar todo el proyecto.")
        else:
            st.warning("No hay Control Boxes creadas. Crea una para comenzar.")

    # =========================
    # TAB 5 - INFO Y FECHAS
    # =========================

    with tab5:
        if tiene_permiso(["Supervisor", "Admin"]):
            st.markdown("### Responsable, fechas y tiempo transcurrido")

            if len(control_boxes) > 0:
                box_info = st.selectbox(
                    "Selecciona la Control Box",
                    control_boxes,
                    key=f"{k}_info_box"
                )

                fila_info = df_info[
                    (df_info["Proyecto"].astype(str) == str(proyecto)) &
                    (df_info["Control Box"].astype(str) == str(box_info))
                ]

                if len(fila_info) > 0:
                    responsable_actual = str(fila_info.iloc[0]["Responsable"])
                    fecha_inicio_actual = obtener_fecha_valida(fila_info.iloc[0]["Fecha Inicio"])
                    fecha_estimada_actual = obtener_fecha_valida(fila_info.iloc[0]["Fecha Estimada"])
                else:
                    responsable_actual = ""
                    fecha_inicio_actual = None
                    fecha_estimada_actual = None

                col_info1, col_info2, col_info3 = st.columns(3)

                with col_info1:
                    responsable_nuevo = st.text_input(
                        "Responsable",
                        value=responsable_actual,
                        placeholder="Ej. Oswaldo Cantú",
                        key=f"{k}_responsable_info"
                    )

                with col_info2:
                    fecha_inicio_nueva = st.date_input(
                        "Fecha de inicio",
                        value=fecha_inicio_actual if fecha_inicio_actual else date.today(),
                        key=f"{k}_fecha_inicio_info"
                    )

                with col_info3:
                    fecha_estimada_nueva = st.date_input(
                        "Fecha estimada",
                        value=fecha_estimada_actual if fecha_estimada_actual else date.today(),
                        key=f"{k}_fecha_estimada_info"
                    )

                tiempo_transcurrido = calcular_tiempo_transcurrido(fecha_inicio_nueva)
                estado_entrega = calcular_estado_entrega(fecha_estimada_nueva)

                st.markdown(f"""
                <div class="soft-card">
                    <h3>{box_info}</h3>
                    <p><b>Responsable:</b> {responsable_nuevo if responsable_nuevo else "Sin responsable"}</p>
                    <p><b>Tiempo transcurrido:</b> {tiempo_transcurrido}</p>
                    <p><b>Estado de entrega:</b> {estado_entrega}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Guardar información de Control Box", key=f"{k}_guardar_info_box"):
                    mask = (
                        (df_info["Proyecto"].astype(str) == str(proyecto)) &
                        (df_info["Control Box"].astype(str) == str(box_info))
                    )

                    if not mask.any():
                        nueva_info = pd.DataFrame([{
                            "Proyecto": proyecto,
                            "Control Box": box_info,
                            "Responsable": str(responsable_nuevo),
                            "Fecha Inicio": fecha_inicio_nueva.strftime("%Y-%m-%d"),
                            "Fecha Estimada": fecha_estimada_nueva.strftime("%Y-%m-%d")
                        }])
                        df_info = pd.concat([df_info, nueva_info], ignore_index=True)
                    else:
                        df_info.loc[mask, "Responsable"] = str(responsable_nuevo)
                        df_info.loc[mask, "Fecha Inicio"] = fecha_inicio_nueva.strftime("%Y-%m-%d")
                        df_info.loc[mask, "Fecha Estimada"] = fecha_estimada_nueva.strftime("%Y-%m-%d")

                    guardar_info(df_info)
                    st.success("Información guardada correctamente ✅")
                    st.rerun()
            else:
                st.info("No hay Control Boxes creadas.")
        else:
            st.warning("No tienes permiso para editar responsables o fechas.")

    # =========================
    # TAB 6 - HISTORIAL
    # =========================

    with tab6:
        st.markdown("### Historial de marcado")

        if len(historial_proyecto) > 0:
            filtro_historial = st.selectbox(
                "Filtrar por Control Box",
                ["Todas"] + sorted(historial_proyecto["Control Box"].dropna().astype(str).unique().tolist()),
                key=f"{k}_filtro_historial"
            )

            if filtro_historial != "Todas":
                df_historial_mostrar = historial_proyecto[
                    historial_proyecto["Control Box"].astype(str) == str(filtro_historial)
                ]
            else:
                df_historial_mostrar = historial_proyecto

            st.dataframe(
                df_historial_mostrar.sort_values("Fecha/Hora", ascending=False),
                width="stretch",
                hide_index=True
            )

            if tiene_permiso(["Admin"]):
                if st.button("🗑️ Limpiar historial de este proyecto", key=f"{k}_limpiar_historial"):
                    df_historial = df_historial[
                        df_historial["Proyecto"].astype(str) != str(proyecto)
                    ].copy()
                    guardar_historial(df_historial)
                    st.rerun()
        else:
            st.info("Aún no hay historial de marcado para este proyecto.")


# =========================
# PESTAÑAS DINÁMICAS DE PROYECTOS
# =========================

nombres_proyectos = df_proyectos["Proyecto"].astype(str).tolist()

if len(nombres_proyectos) > 0:
    tabs_proyectos = st.tabs(nombres_proyectos)

    for tab_proyecto, nombre in zip(tabs_proyectos, nombres_proyectos):
        color = str(
            df_proyectos.loc[df_proyectos["Proyecto"].astype(str) == str(nombre), "Color"].iloc[0]
        )

        with tab_proyecto:
            render_proyecto(nombre, color)
else:
    st.warning("No hay proyectos configurados.")
