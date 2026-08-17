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

def crear_datos_iniciales():
    data = []
    for i in range(1, 6):
        for punto in puntos_iniciales:
            data.append({
                "Control Box": f"Control Box {i}",
                "Punto": punto,
                "Completado": False
            })
    return pd.DataFrame(data)


def crear_info_inicial(control_boxes):
    data = []
    for box in control_boxes:
        data.append({
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

def agregar_historial(df_historial, control_box, punto, estado, responsable):
    accion = "Marcado como completado" if estado else "Marcado como pendiente"

    nueva_fila = pd.DataFrame([{
        "Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuario": st.session_state.get("usuario", ""),
        "Rol": st.session_state.get("rol", ""),
        "Control Box": control_box,
        "Punto": punto,
        "Accion": accion,
        "Estado": estado,
        "Responsable": responsable
    }])

    return pd.concat([df_historial, nueva_fila], ignore_index=True)


def obtener_responsable(df_info, control_box):
    fila = df_info[df_info["Control Box"] == control_box]
    if len(fila) == 0:
        return ""
    return str(fila.iloc[0]["Responsable"])


def sincronizar_info_con_boxes(df_info, control_boxes):
    existentes = df_info["Control Box"].unique().tolist()
    nuevas_filas = []

    for box in control_boxes:
        if box not in existentes:
            nuevas_filas.append({
                "Control Box": box,
                "Responsable": "",
                "Fecha Inicio": "",
                "Fecha Estimada": ""
            })

    if nuevas_filas:
        df_info = pd.concat([df_info, pd.DataFrame(nuevas_filas)], ignore_index=True)

    df_info = df_info[df_info["Control Box"].isin(control_boxes)]

    return df_info


def exportar_reporte_excel(df, df_info, df_historial):
    resumen = []
    control_boxes = sorted(df["Control Box"].unique().tolist())

    for box in control_boxes:
        df_box = df[df["Control Box"] == box]
        total, completados, pendientes, porcentaje = obtener_avance(df_box)
        info = df_info[df_info["Control Box"] == box]

        if len(info) > 0:
            responsable = info.iloc[0]["Responsable"]
            fecha_inicio = info.iloc[0]["Fecha Inicio"]
            fecha_estimada = info.iloc[0]["Fecha Estimada"]
        else:
            responsable = ""
            fecha_inicio = ""
            fecha_estimada = ""

        resumen.append({
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
# CARGAR DATOS
# =========================

if not os.path.exists(ARCHIVO):
    df = crear_datos_iniciales()
    guardar(df)
else:
    df = pd.read_csv(ARCHIVO)

df = normalizar_booleanos(df)
control_boxes = sorted(df["Control Box"].unique().tolist())

if not os.path.exists(ARCHIVO_INFO) or os.path.getsize(ARCHIVO_INFO) == 0:
    df_info = crear_info_inicial(control_boxes)
    guardar_info(df_info)
else:
    df_info = pd.read_csv(ARCHIVO_INFO)

# Corregir tipos de datos de df_info
df_info["Control Box"] = df_info["Control Box"].fillna("").astype(str)
df_info["Responsable"] = df_info["Responsable"].fillna("").astype(str)
df_info["Fecha Inicio"] = df_info["Fecha Inicio"].fillna("").astype(str)
df_info["Fecha Estimada"] = df_info["Fecha Estimada"].fillna("").astype(str)

if not os.path.exists(ARCHIVO_HISTORIAL) or os.path.getsize(ARCHIVO_HISTORIAL) == 0:
    df_historial = crear_historial_vacio()
    guardar_historial(df_historial)
else:
    df_historial = pd.read_csv(ARCHIVO_HISTORIAL)

df_info = sincronizar_info_con_boxes(df_info, control_boxes)

# Volver a asegurar tipos después de sincronizar
df_info["Control Box"] = df_info["Control Box"].fillna("").astype(str)
df_info["Responsable"] = df_info["Responsable"].fillna("").astype(str)
df_info["Fecha Inicio"] = df_info["Fecha Inicio"].fillna("").astype(str)
df_info["Fecha Estimada"] = df_info["Fecha Estimada"].fillna("").astype(str)

guardar_info(df_info)


# =========================
# ENCABEZADO + TOOLBAR
# =========================

st.markdown("""
<div class="command-header">
    <h1>🧰 Control Box Command Center</h1>
    <p>Dashboard industrial para seguimiento de armado, validación y avance general.</p>
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
    if st.button("💾 Guardar", width="stretch"):
        guardar(df)
        guardar_info(df_info)
        guardar_historial(df_historial)
        st.toast("Cambios guardados correctamente ✅")

with col_excel:
    if tiene_permiso(["Supervisor", "Admin"]):
        if st.button("📊 Exportar", width="stretch"):
            guardar(df)
            guardar_info(df_info)
            guardar_historial(df_historial)

            archivo_excel = exportar_reporte_excel(df, df_info, df_historial)
            st.toast("Reporte Excel generado ✅")

with col_download:
    if tiene_permiso(["Supervisor", "Admin"]) and os.path.exists(ARCHIVO_REPORTE):
        with open(ARCHIVO_REPORTE, "rb") as file:
            st.download_button(
                label="⬇️ Descargar",
                data=file,
                file_name="reporte_control_boxes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )

with col_logout:
    if st.button("🚪 Salir", width="stretch"):
        st.session_state["login"] = False
        st.session_state["usuario"] = ""
        st.session_state["rol"] = ""
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# DASHBOARD GENERAL
# =========================

total_puntos, total_completados, total_pendientes, porcentaje_total = obtener_avance(df)

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
    "Proyecto completo",
    total_completados,
    total_pendientes,
    porcentaje_total,
    ["#FACC15", "#334155"],
    altura=430,
    leyenda=True
)

col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    st.plotly_chart(fig_total, width="stretch")


# =========================
# AVANCE POR CONTROL BOX
# =========================

st.markdown("---")
st.markdown('<div class="section-title">Avance por Control Box</div>', unsafe_allow_html=True)

if len(control_boxes) > 0:
    columnas = st.columns(min(len(control_boxes), 5))

    for i, box in enumerate(control_boxes):
        df_box = df[df["Control Box"] == box]
        total_box, completados_box, pendientes_box, porcentaje_box = obtener_avance(df_box)
        colores = colores_default[i % len(colores_default)]

        info_box = df_info[df_info["Control Box"] == box]

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

        with columnas[i % 5]:
            st.plotly_chart(fig_box, width="stretch")
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
    st.info("No hay Control Boxes creadas.")


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
                placeholder="Ej. CB-F09-001"
            )

            if st.button("➕ Crear Control Box"):
                nuevo_nombre = nueva_control_box.strip()

                if nuevo_nombre == "":
                    st.warning("Escribe un nombre válido.")
                elif nuevo_nombre in control_boxes:
                    st.warning("Ya existe una Control Box con ese nombre.")
                else:
                    nuevas_filas = []

                    for punto in puntos_iniciales:
                        nuevas_filas.append({
                            "Control Box": nuevo_nombre,
                            "Punto": punto,
                            "Completado": False
                        })

                    nueva_info = pd.DataFrame([{
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
                        key="borrar_box"
                    )

                    confirmar_borrado = st.checkbox(
                        "Confirmo que deseo eliminar esta Control Box",
                        key="confirmar_borrado"
                    )

                    if st.button("🗑️ Eliminar Control Box"):
                        if confirmar_borrado:
                            df = df[df["Control Box"] != control_box_borrar]
                            df_info = df_info[df_info["Control Box"] != control_box_borrar]
                            df_historial = df_historial[df_historial["Control Box"] != control_box_borrar]

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
                    key="box_renombrar"
                )
            else:
                box_a_renombrar = None
                st.info("No hay Control Boxes disponibles.")

        with col_ren2:
            nuevo_nombre_box = st.text_input(
                "Nuevo nombre",
                placeholder="Ej. CB-F09-001"
            )

        if st.button("Guardar nuevo nombre"):
            if box_a_renombrar is None:
                st.warning("No hay Control Box para renombrar.")
            elif nuevo_nombre_box.strip() == "":
                st.warning("Escribe un nuevo nombre.")
            elif nuevo_nombre_box.strip() in control_boxes:
                st.warning("Ese nombre ya existe.")
            else:
                nuevo_nombre = nuevo_nombre_box.strip()

                df.loc[df["Control Box"] == box_a_renombrar, "Control Box"] = nuevo_nombre
                df_info.loc[df_info["Control Box"] == box_a_renombrar, "Control Box"] = nuevo_nombre
                df_historial.loc[df_historial["Control Box"] == box_a_renombrar, "Control Box"] = nuevo_nombre

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
                    key="box_origen"
                )

            with col_copy2:
                opciones_destino = [box for box in control_boxes if box != box_origen]

                box_destino = st.selectbox(
                    "Copiar tareas hacia",
                    opciones_destino,
                    key="box_destino"
                )

            copiar_estado = st.checkbox(
                "Copiar también el estado de completado",
                value=False
            )

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button("Copiar a Control Box seleccionada"):
                    df_origen = df[df["Control Box"] == box_origen].copy()

                    if copiar_estado:
                        nuevas_tareas = df_origen[["Punto", "Completado"]].copy()
                    else:
                        nuevas_tareas = df_origen[["Punto"]].copy()
                        nuevas_tareas["Completado"] = False

                    nuevas_tareas["Control Box"] = box_destino
                    nuevas_tareas = nuevas_tareas[["Control Box", "Punto", "Completado"]]

                    df = df[df["Control Box"] != box_destino]
                    df = pd.concat([df, nuevas_tareas], ignore_index=True)

                    guardar(df)
                    st.rerun()

            with col_btn2:
                if st.button("Copiar a todas las demás"):
                    df_origen = df[df["Control Box"] == box_origen].copy()
                    df = df[df["Control Box"] == box_origen]

                    for destino in opciones_destino:
                        if copiar_estado:
                            nuevas_tareas = df_origen[["Punto", "Completado"]].copy()
                        else:
                            nuevas_tareas = df_origen[["Punto"]].copy()
                            nuevas_tareas["Completado"] = False

                        nuevas_tareas["Control Box"] = destino
                        nuevas_tareas = nuevas_tareas[["Control Box", "Punto", "Completado"]]

                        df = pd.concat([df, nuevas_tareas], ignore_index=True)

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

    control_boxes = sorted(
        df["Control Box"].unique().tolist()
    )

    if len(control_boxes) > 0:

        control_box_seleccionada = st.selectbox(
            "Selecciona la Control Box que deseas editar",
            control_boxes,
            key="editar_box"
        )

        df_seleccionada = df[
            df["Control Box"] == control_box_seleccionada
        ].copy()

        total_sel, comp_sel, pend_sel, porc_sel = obtener_avance(
            df_seleccionada
        )

        responsable_actual = obtener_responsable(
            df_info,
            control_box_seleccionada
        )

        # =========================
        # TARJETA DE INFORMACIÓN
        # =========================

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

        # Guardamos una copia del estado anterior
        df_anterior = df_seleccionada[
            ["Punto", "Completado"]
        ].copy()

        # =========================
        # FORMULARIO CHECKLIST
        # =========================

        with st.form(
            key=f"form_checklist_{control_box_seleccionada}",
            clear_on_submit=False
        ):

            df_editado = st.data_editor(
                df_seleccionada[
                    ["Punto", "Completado"]
                ],
                width="stretch",
                hide_index=True,
                key=f"editor_{control_box_seleccionada}",

                # No permitir editar el nombre
                # de la actividad aquí
                disabled=["Punto"],

                column_config={

                    "Punto":
                        st.column_config.TextColumn(
                            "Punto de armado",
                            width="large"
                        ),

                    "Completado":
                        st.column_config.CheckboxColumn(
                            "Completado",
                            help=(
                                "Marca todas las tareas necesarias "
                                "y después presiona Guardar avance"
                            ),
                            default=False
                        )
                }
            )

            guardar_avance = st.form_submit_button(
                "💾 Guardar avance",
                width="stretch"
            )

        # =========================
        # GUARDAR TODOS LOS CAMBIOS
        # =========================

        if guardar_avance:

            cambios_realizados = 0

            for _, row in df_editado.iterrows():

                punto = row["Punto"]

                completado_nuevo = bool(
                    row["Completado"]
                )

                valor_anterior = df_anterior[
                    df_anterior["Punto"] == punto
                ]["Completado"]

                if len(valor_anterior) > 0:

                    completado_anterior = bool(
                        valor_anterior.iloc[0]
                    )

                    # Registrar solamente si cambió
                    if completado_anterior != completado_nuevo:

                        cambios_realizados += 1

                        df_historial = agregar_historial(
                            df_historial,
                            control_box_seleccionada,
                            punto,
                            completado_nuevo,
                            responsable_actual
                        )

                # Actualizar dataframe principal
                df.loc[
                    (
                        df["Control Box"]
                        == control_box_seleccionada
                    )
                    &
                    (
                        df["Punto"]
                        == punto
                    ),
                    "Completado"
                ] = completado_nuevo

            # Guardar después de procesar
            # TODAS las actividades
            guardar(df)
            guardar_historial(df_historial)

            if cambios_realizados > 0:

                st.success(
                    f"✅ {cambios_realizados} cambios guardados correctamente."
                )

            else:

                st.info(
                    "No se detectaron cambios."
                )

            st.rerun()

        # =========================
        # ADMINISTRAR TAREAS
        # =========================

        if tiene_permiso(
            ["Técnico", "Supervisor", "Admin"]
        ):

            st.markdown(
                "### Administrar tareas de esta Control Box"
            )

            col_agregar, col_eliminar = st.columns(2)

            with col_agregar:

                nueva_tarea = st.text_input(
                    "Nueva tarea",
                    placeholder=(
                        "Ej. Validar comunicación Ethernet"
                    ),
                    key="nueva_tarea_editor"
                )

                if st.button(
                    "➕ Agregar tarea",
                    key="agregar_tarea_editor"
                ):

                    if nueva_tarea.strip() != "":

                        nueva_fila = pd.DataFrame({
                            "Control Box": [
                                control_box_seleccionada
                            ],
                            "Punto": [
                                nueva_tarea.strip()
                            ],
                            "Completado": [
                                False
                            ]
                        })

                        df = pd.concat(
                            [df, nueva_fila],
                            ignore_index=True
                        )

                        guardar(df)

                        st.rerun()

                    else:

                        st.warning(
                            "Escribe el nombre de la tarea."
                        )

            with col_eliminar:

                if tiene_permiso(["Admin"]):

                    if len(df_seleccionada) > 0:

                        tarea_eliminar = st.selectbox(
                            "Tarea a eliminar",
                            df_seleccionada["Punto"],
                            key="eliminar_tarea_editor"
                        )

                        if st.button(
                            "🗑️ Eliminar tarea",
                            key="boton_eliminar_tarea"
                        ):

                            df = df[
                                ~(
                                    (
                                        df["Control Box"]
                                        == control_box_seleccionada
                                    )
                                    &
                                    (
                                        df["Punto"]
                                        == tarea_eliminar
                                    )
                                )
                            ]

                            guardar(df)

                            st.rerun()

                    else:

                        st.info(
                            "No hay tareas para eliminar."
                        )

                else:

                    st.warning(
                        "Solo Admin puede eliminar tareas."
                    )

        # =========================
        # REINICIO
        # =========================

        if tiene_permiso(["Admin"]):

            st.markdown("### Reinicio")

            col_reset1, col_reset2 = st.columns(2)

            with col_reset1:

                if st.button(
                    "Reiniciar esta Control Box",
                    key="reiniciar_box_editor"
                ):

                    df.loc[
                        df["Control Box"]
                        == control_box_seleccionada,
                        "Completado"
                    ] = False

                    guardar(df)

                    st.rerun()

            with col_reset2:

                confirmar_reset = st.checkbox(
                    "Confirmo reiniciar todo el proyecto",
                    key="confirmar_reset_editor"
                )

                if st.button(
                    "Reiniciar todo el proyecto",
                    key="reiniciar_proyecto_editor"
                ):

                    if confirmar_reset:

                        df["Completado"] = False

                        guardar(df)

                        st.rerun()

                    else:

                        st.warning(
                            "Activa la confirmación antes "
                            "de reiniciar todo."
                        )

    else:

        st.warning(
            "No hay Control Boxes creadas. "
            "Crea una para comenzar."
        )

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
                key="info_box"
            )

            fila_info = df_info[df_info["Control Box"].astype(str) == str(box_info)]

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
                    placeholder="Ej. Oswaldo Cantú"
                )

            with col_info2:
                fecha_inicio_nueva = st.date_input(
                    "Fecha de inicio",
                    value=fecha_inicio_actual if fecha_inicio_actual else date.today()
                )

            with col_info3:
                fecha_estimada_nueva = st.date_input(
                    "Fecha estimada",
                    value=fecha_estimada_actual if fecha_estimada_actual else date.today()
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

            if st.button("Guardar información de Control Box"):
                mask = df_info["Control Box"].astype(str) == str(box_info)

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

    if len(df_historial) > 0:
        filtro_historial = st.selectbox(
            "Filtrar por Control Box",
            ["Todas"] + sorted(df_historial["Control Box"].dropna().unique().tolist())
        )

        if filtro_historial != "Todas":
            df_historial_mostrar = df_historial[df_historial["Control Box"] == filtro_historial]
        else:
            df_historial_mostrar = df_historial

        st.dataframe(
            df_historial_mostrar.sort_values("Fecha/Hora", ascending=False),
            width="stretch",
            hide_index=True
        )

        if tiene_permiso(["Admin"]):
            if st.button("🗑️ Limpiar historial"):
                df_historial = crear_historial_vacio()
                guardar_historial(df_historial)
                st.rerun()
    else:
        st.info("Aún no hay historial de marcado.")