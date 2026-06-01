import streamlit as st
import json
import os
import pandas as pd

# --- CONFIGURACIÓN DE DATOS ---
DATA_FILE = "quiniela_2026_auto.json"

GRUPOS_EQUIPOS = {
    "Grupo A": ["México", "Sudáfrica", "Corea del Sur", "Chequia"],
    "Grupo B": ["Canadá", "Bosnia y Herzegovina", "Catar", "Suiza"],
    "Grupo C": ["Brasil", "Marruecos", "Haití", "Escocia"],
    "Grupo D": ["Estados Unidos", "Paraguay", "Australia", "Turquía"],
    "Grupo E": ["Alemania", "Curazao", "Costa de Marfil", "Ecuador"],
    "Grupo F": ["Países Bajos", "Japón", "Suecia", "Túnez"],
    "Grupo G": ["Bélgica", "Egipto", "Irán", "Nueva Zelanda"],
    "Grupo H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
    "Grupo I": ["Francia", "Senegal", "Irak", "Noruega"],
    "Grupo J": ["Argentina", "Argelia", "Austria", "Jordania"],
    "Grupo K": ["Portugal", "RD Congo", "Uzbekistán", "Colombia"],
    "Grupo L": ["Inglaterra", "Croacia", "Ghana", "Panamá"]
}

# Definición de partidos por grupo (Fixture entregado)
PARTIDOS_GRUPOS = {
    "Grupo A": [("México", "Sudáfrica"), ("Corea del Sur", "Chequia"), ("Chequia", "Sudáfrica"), ("México", "Corea del Sur"), ("Chequia", "México"), ("Sudáfrica", "Corea del Sur")],
    "Grupo B": [("Canadá", "Bosnia y Herzegovina"), ("Catar", "Suiza"), ("Suiza", "Bosnia y Herzegovina"), ("Canadá", "Catar"), ("Suiza", "Canadá"), ("Bosnia y Herzegovina", "Catar")],
    "Grupo C": [("Brasil", "Marruecos"), ("Haití", "Escocia"), ("Escocia", "Marruecos"), ("Brasil", "Haití"), ("Escocia", "Brasil"), ("Marruecos", "Haití")],
    "Grupo D": [("Estados Unidos", "Paraguay"), ("Australia", "Turquía"), ("Turquía", "Paraguay"), ("Estados Unidos", "Australia"), ("Turquía", "Estados Unidos"), ("Paraguay", "Australia")],
    "Grupo E": [("Alemania", "Curazao"), ("Costa de Marfil", "Ecuador"), ("Ecuador", "Curazao"), ("Alemania", "Costa de Marfil"), ("Ecuador", "Alemania"), ("Curazao", "Costa de Marfil")],
    "Grupo F": [("Países Bajos", "Japón"), ("Suecia", "Túnez"), ("Túnez", "Japón"), ("Países Bajos", "Suecia"), ("Túnez", "Países Bajos"), ("Japón", "Suecia")],
    "Grupo G": [("Bélgica", "Egipto"), ("Irán", "Nueva Zelanda"), ("Nueva Zelanda", "Egipto"), ("Bélgica", "Irán"), ("Nueva Zelanda", "Bélgica"), ("Egipto", "Irán")],
    "Grupo H": [("España", "Cabo Verde"), ("Arabia Saudita", "Uruguay"), ("Uruguay", "Cabo Verde"), ("España", "Arabia Saudita"), ("Uruguay", "España"), ("Cabo Verde", "Arabia Saudita")],
    "Grupo I": [("Francia", "Senegal"), ("Irak", "Noruega"), ("Noruega", "Senegal"), ("Francia", "Irak"), ("Noruega", "Francia"), ("Senegal", "Irak")],
    "Grupo J": [("Argentina", "Argelia"), ("Austria", "Jordania"), ("Jordania", "Argelia"), ("Argentina", "Austria"), ("Argelia", "Austria"), ("Jordania", "Argentina")],
    "Grupo K": [("Portugal", "RD Congo"), ("Uzbekistán", "Colombia"), ("Colombia", "RD Congo"), ("Portugal", "Uzbekistán"), ("Colombia", "Portugal"), ("RD Congo", "Uzbekistán")],
    "Grupo L": [("Inglaterra", "Croacia"), ("Ghana", "Panamá"), ("Panamá", "Croacia"), ("Inglaterra", "Ghana"), ("Panamá", "Inglaterra"), ("Croacia", "Ghana")]
}

# --- LÓGICA DE PERSISTENCIA ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {"users": {}, "real_results": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

# --- PROCESAMIENTO DE TABLAS ---
def get_group_table(grupo_nombre, resultados_reales):
    equipos = {e: {"Pts": 0, "PJ": 0, "GF": 0, "GC": 0, "GD": 0} for e in GRUPOS_EQUIPOS[grupo_nombre]}
    for i, (loc, vis) in enumerate(PARTIDOS_GRUPOS[grupo_nombre]):
        m_id = f"{grupo_nombre}_{i}"
        if m_id in resultados_reales:
            l_score = resultados_reales[m_id]["l"]
            v_score = resultados_reales[m_id]["v"]
            equipos[loc]["PJ"] += 1
            equipos[vis]["PJ"] += 1
            equipos[loc]["GF"] += l_score
            equipos[loc]["GC"] += v_score
            equipos[vis]["GF"] += v_score
            equipos[vis]["GC"] += l_score
            if l_score > v_score: equipos[loc]["Pts"] += 3
            elif l_score < v_score: equipos[vis]["Pts"] += 3
            else:
                equipos[loc]["Pts"] += 1
                equipos[vis]["Pts"] += 1
    
    for e in equipos: equipos[e]["GD"] = equipos[e]["GF"] - equipos[e]["GC"]
    
    df = pd.DataFrame.from_dict(equipos, orient='index').reset_index()
    df.columns = ["Equipo", "Pts", "PJ", "GF", "GC", "GD"]
    return df.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)

# --- INTERFAZ ---
st.set_page_config(page_title="Prode Mundial 2026", layout="wide")
data = load_data()

st.sidebar.title("⚽ Panel de Control")
user = st.sidebar.text_input("Tu nombre:")
admin_mode = st.sidebar.toggle("Modo Administrador")

if not user:
    st.warning("Escribe tu nombre para participar.")
    st.stop()

if user not in data["users"]:
    data["users"][user] = {}
    save_data(data)

t1, t2, t3, t4 = st.tabs(["📋 Mis Predicciones", "📊 Tablas de Grupos", "🏆 Dieciseisavos (Auto)", "🥇 Ranking Polla"])

# --- T1: PREDICCIONES ---
with t1:
    st.header(f"Predicciones de {user}")
    g_sel = st.selectbox("Grupo:", list(PARTIDOS_GRUPOS.keys()))
    with st.form(f"f_{g_sel}"):
        for i, (l, v) in enumerate(PARTIDOS_GRUPOS[g_sel]):
            m_id = f"{g_sel}_{i}"
            cur = data["users"][user].get(m_id, {"l": 0, "v": 0})
            c1, c2, c3, c4, c5 = st.columns([3,1,1,1,3])
            c1.write(l)
            l_in = c2.number_input("", 0, 15, cur["l"], key=f"up_l_{m_id}", label_visibility="collapsed")
            c3.write("vs")
            v_in = c4.number_input("", 0, 15, cur["v"], key=f"up_v_{m_id}", label_visibility="collapsed")
            c5.write(v)
        if st.form_submit_button("Guardar"):
            for i, _ in enumerate(PARTIDOS_GRUPOS[g_sel]):
                m_id = f"{g_sel}_{i}"
                data["users"][user][m_id] = {"l": st.session_state[f"up_l_{m_id}"], "v": st.session_state[f"up_v_{m_id}"]}
            save_data(data)
            st.success("Guardado.")

# --- T2: TABLAS Y ADMIN ---
with t2:
    if admin_mode:
        st.subheader("⚠️ Cargar Resultados REALES (Admin)")
        g_adm = st.selectbox("Actualizar Grupo:", list(PARTIDOS_GRUPOS.keys()), key="sadm")
        with st.form("f_adm"):
            for i, (l, v) in enumerate(PARTIDOS_GRUPOS[g_adm]):
                m_id = f"{g_adm}_{i}"
                cur = data["real_results"].get(m_id, {"l": 0, "v": 0})
                c1, c2, c3, c4, c5 = st.columns([3,1,1,1,3])
                c1.write(l); l_a = c2.number_input("", 0, 15, cur["l"], key=f"ar_l_{m_id}", label_visibility="collapsed")
                c3.write("-"); v_a = c4.number_input("", 0, 15, cur["v"], key=f"ar_v_{m_id}", label_visibility="collapsed")
                c5.write(v)
            if st.form_submit_button("Publicar Resultados"):
                for i, _ in enumerate(PARTIDOS_GRUPOS[g_adm]):
                    m_id = f"{g_adm}_{i}"
                    data["real_results"][m_id] = {"l": st.session_state[f"ar_l_{m_id}"], "v": st.session_state[f"ar_v_{m_id}"]}
                save_data(data)
    
    st.divider()
    cols = st.columns(3)
    clasificados = {} # Para la fase final
    todos_los_terceros = []

    for idx, g in enumerate(PARTIDOS_GRUPOS.keys()):
        tabla = get_group_table(g, data["real_results"])
        with cols[idx % 3]:
            st.write(f"**{g}**")
            st.dataframe(tabla, hide_index=True)
            # Guardamos clasificados (1ero y 2do)
            clasificados[f"1{g[-1]}"] = tabla.iloc[0]["Equipo"]
            clasificados[f"2{g[-1]}"] = tabla.iloc[1]["Equipo"]
            # Guardamos el tercero para el ranking
            tercero = tabla.iloc[2].to_dict()
            tercero["Grupo"] = g
            todos_los_terceros.append(tercero)

    # Ranking mejores terceros
    st.subheader("🥉 Ranking de Mejores Terceros")
    df_terceros = pd.DataFrame(todos_los_terceros).sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
    df_terceros.index += 1
    st.table(df_terceros)
    
    mejores_8_terceros = df_terceros.head(8)["Equipo"].tolist()

# --- T3: ELIMINACIÓN AUTOMÁTICA ---
with t3:
    st.header("Bracket de Dieciseisavos de Final")
    st.caption("Calculado automáticamente según los resultados reales de los grupos.")
    
    # Mapeo aproximado basado en Proyecciones FIFA 2026 (Simplified)
    bracket_mapping = [
        ("1A", "3C/E/F/H/I"), ("1E", "3A/B/C/D/F"), ("1F", "3A/B/C/D"), ("1C", "3A/B/F/G/I"),
        ("2A", "2B"), ("2C", "2D"), ("1B", "3A/C/E/F/G"), ("1G", "3A/B/E/I/J"),
        ("1I", "3C/D/E/G/H"), ("1K", "3H/I/J/L"), ("1L", "3G/I/J/K"), ("2E", "2F"),
        ("2G", "2H"), ("2I", "2K"), ("1H", "2J"), ("1J", "2H")
    ]

    r32_cols = st.columns(2)
    terceros_lista = mejores_8_terceros.copy()
    
    for i, (local_slot, visita_slot) in enumerate(bracket_mapping):
        equipo_l = clasificados.get(local_slot, f"Ganador {local_slot}")
        
        # Asignación simple de mejores terceros por orden de aparición
        if "3" in visita_slot:
            if terceros_lista:
                equipo_v = terceros_lista.pop(0)
            else:
                equipo_v = "Esperando Tercero..."
        else:
            equipo_v = clasificados.get(visita_slot, f"Segundo {visita_slot}")

        with r32_cols[i % 2]:
            st.info(f"⚽ **M{49+i}:** {equipo_l} vs {equipo_v}")

# --- T4: RANKING QUINIELA ---
with t4:
    st.header("🏆 Tabla de Posiciones de la Quiniela")
    leaderboard = []
    for u, preds in data["users"].items():
        puntos = 0
        for m_id, real in data["real_results"].items():
            if m_id in preds:
                pl, pv = preds[m_id]["l"], preds[m_id]["v"]
                rl, rv = real["l"], real["v"]
                if pl == rl and pv == rv: puntos += 3
                elif (pl > pv and rl > rv) or (pl < pv and rl < rv) or (pl == pv and rl == rv): puntos += 1
        leaderboard.append({"Jugador": u, "Puntos": puntos})
    
    df_lead = pd.DataFrame(leaderboard).sort_values("Puntos", ascending=False)
    st.table(df_lead)