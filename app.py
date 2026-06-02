import streamlit as st
import json
import os
import pandas as pd

# --- CONFIGURACIÓN DE DATOS ---
DATA_FILE = "quiniela_2026_pro.json"

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

# --- PERSISTENCIA Y ESQUEMA ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {"users": {}, "real_results": {"group_results": {}, "ko_results": {}}}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

# --- PROCESAMIENTO DE MATRICES ---
def get_all_group_tables(resultados_dict):
    tables = {}
    thirds = []
    for g in GRUPOS_EQUIPOS.keys():
        equipos = {e: {"Pts": 0, "PJ": 0, "GF": 0, "GC": 0, "GD": 0} for e in GRUPOS_EQUIPOS[g]}
        for i, (loc, vis) in enumerate(PARTIDOS_GRUPOS[g]):
            m_id = f"{g}_{i}"
            if m_id in resultados_dict:
                l_score = resultados_dict[m_id]["l"]
                v_score = resultados_dict[m_id]["v"]
                equipos[loc]["PJ"] += 1; equipos[vis]["PJ"] += 1
                equipos[loc]["GF"] += l_score; equipos[loc]["GC"] += v_score
                equipos[vis]["GF"] += v_score; equipos[vis]["GC"] += l_score
                if l_score > v_score: equipos[loc]["Pts"] += 3
                elif l_score < v_score: equipos[vis]["Pts"] += 3
                else: equipos[loc]["Pts"] += 1; equipos[vis]["Pts"] += 1
        for e in equipos: equipos[e]["GD"] = equipos[e]["GF"] - equipos[e]["GC"]
        df = pd.DataFrame.from_dict(equipos, orient='index').reset_index()
        df.columns = ["Equipo", "Pts", "PJ", "GF", "GC", "GD"]
        df = df.sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
        tables[g] = df
        if len(df) >= 3:
            tercero = df.iloc[2].to_dict()
            tercero["Grupo"] = g
            thirds.append(tercero)
            
    df_thirds = pd.DataFrame(thirds).sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
    
    # Agregamos una columna visual para saber quién pasa
    if not df_thirds.empty:
        df_thirds["Avanza"] = ["✅ Sí" if i < 8 else "❌ No" for i in range(len(df_thirds))]
        
    best_thirds_list = df_thirds.head(8)["Equipo"].tolist() if not df_thirds.empty else []
    return tables, best_thirds_list, df_thirds

def get_winner(match_data, team_l, team_v):
    if not match_data: return "Por definir"
    l_score, v_score = match_data.get("l", 0), match_data.get("v", 0)
    if l_score > v_score: return team_l
    elif l_score < v_score: return team_v
    return team_l if match_data.get("avanza", "L") == "L" else team_v

def resolve_full_bracket(group_tables, df_thirds, ko_data):
    clasificados = {}
    for g, tabla in group_tables.items():
        if len(tabla) >= 2:
            clasificados[f"1{g[-1]}"] = tabla.iloc[0]["Equipo"]
            clasificados[f"2{g[-1]}"] = tabla.iloc[1]["Equipo"]

    # Extraer la lista de los 8 mejores terceros
    mejores_8_terceros = df_thirds.head(8).to_dict('records') if not df_thirds.empty else []

    # --- ALGORITMO DINÁMICO DE ASIGNACIÓN ---
    asignaciones_terceros = {}
    terceros_disp = mejores_8_terceros.copy()
    
    slots_vs_terceros = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1H"]
    
    for slot in slots_vs_terceros:
        if not terceros_disp: break
        grupo_lider = slot[-1]
        
        asignado = False
        for t in terceros_disp:
            if t["Grupo"][-1] != grupo_lider:
                asignaciones_terceros[slot] = t["Equipo"]
                terceros_disp.remove(t)
                asignado = True
                break
        
        if not asignado and terceros_disp:
            t = terceros_disp.pop(0)
            asignaciones_terceros[slot] = t["Equipo"]

    def get_team(slot):
        if slot.startswith("1") or slot.startswith("2"): 
            return clasificados.get(slot, f"Por definir ({slot})")
        if slot.startswith("3rd_from_"):
            lider_slot = slot.split("_from_")[1]
            return asignaciones_terceros.get(lider_slot, "Esperando Tercero...")
        return slot

    slots_r32 = [
        ("1A", "3rd_from_1A"), ("1B", "3rd_from_1B"), ("1C", "3rd_from_1C"), ("1D", "3rd_from_1D"),
        ("1E", "3rd_from_1E"), ("1F", "3rd_from_1F"), ("1G", "3rd_from_1G"), ("1H", "3rd_from_1H"),
        ("1I", "2J"), ("1J", "2I"), ("1K", "2L"), ("1L", "2K"),
        ("2A", "2B"), ("2C", "2D"), ("2E", "2F"), ("2G", "2H")
    ]
    r32 = [{"id": i, "L_team": get_team(l), "V_team": get_team(v)} for i, (l, v) in enumerate(slots_r32)]
    
    r16_slots = [(0, 12), (1, 13), (2, 14), (3, 15), (4, 8), (5, 9), (6, 10), (7, 11)]
    r16 = [{"id": i, "L_team": get_winner(ko_data.get(f"R32_{l}"), r32[l]["L_team"], r32[l]["V_team"]), "V_team": get_winner(ko_data.get(f"R32_{v}"), r32[v]["L_team"], r32[v]["V_team"])} for i, (l, v) in enumerate(r16_slots)]
    
    qf_slots = [(0, 4), (1, 5), (2, 6), (3, 7)]
    qf = [{"id": i, "L_team": get_winner(ko_data.get(f"R16_{l}"), r16[l]["L_team"], r16[l]["V_team"]), "V_team": get_winner(ko_data.get(f"R16_{v}"), r16[v]["L_team"], r16[v]["V_team"])} for i, (l, v) in enumerate(qf_slots)]
    
    sf_slots = [(0, 2), (1, 3)]
    sf = [{"id": i, "L_team": get_winner(ko_data.get(f"QF_{l}"), qf[l]["L_team"], qf[l]["V_team"]), "V_team": get_winner(ko_data.get(f"QF_{v}"), qf[v]["L_team"], qf[v]["V_team"])} for i, (l, v) in enumerate(sf_slots)]
    
    final = [{"id": 0, "L_team": get_winner(ko_data.get(f"SF_0"), sf[0]["L_team"], sf[0]["V_team"]), "V_team": get_winner(ko_data.get(f"SF_1"), sf[1]["L_team"], sf[1]["V_team"])}]
    campeon = get_winner(ko_data.get("Final_0"), final[0]["L_team"], final[0]["V_team"])
    
    return {"R32": r32, "R16": r16, "QF": qf, "SF": sf, "Final": final, "Campeon": campeon}
    
# --- INTERFAZ ---
st.set_page_config(page_title="Quiniela Pro Mundial 2026", layout="wide")
data = load_data()

st.sidebar.title("🏆 Configuración")
user = st.sidebar.text_input("Tu Nombre de Jugador:")
admin_mode = st.sidebar.toggle("Modo Administrador (Resultados Oficiales)")

if not user:
    st.info("👈 Por favor ingresa tu nombre en la barra lateral para sincronizar tus datos.")
    st.stop()

if user not in data["users"]: data["users"][user] = {"group_predictions": {}, "ko_predictions": {}}
if "group_predictions" not in data["users"][user]: data["users"][user]["group_predictions"] = {}
if "ko_predictions" not in data["users"][user]: data["users"][user]["ko_predictions"] = {}

t_pred, t_real, t_puntos = st.tabs(["🔮 Mi Predicción", "🌍 Realidad del Mundial", "🥇 Ranking y Puntuación"])

# --- FUNCION INTERACTIVA PARA BRACKETS ---
def UI_fase_eliminatoria(bracket_dict, storage_path, key_prefix, read_only=False):
    rondas = [("R32", "Dieciseisavos de Final"), ("R16", "Octavos de Final"), ("QF", "Cuartos de Final"), ("SF", "Semifinales"), ("Final", "Gran Final")]
    for r_key, r_name in rondas:
        with st.expander(f"➔ {r_name}", expanded=True):
            for match in bracket_dict[r_key]:
                m_id = f"{r_key}_{match['id']}"
                cur = storage_path.get(m_id, {"l": 0, "v": 0, "avanza": "L"})
                
                bloqueado = "Por definir" in match["L_team"] or "Por definir" in match["V_team"] or "Mejor" in match["L_team"] or read_only
                
                c1, c2, c3, c4, c5, c6 = st.columns([3, 1, 1, 1, 3, 2])
                c1.write(f"**{match['L_team']}**")
                l_in = c2.number_input("", 0, 15, cur["l"], key=f"{key_prefix}_l_{m_id}", disabled=bloqueado, label_visibility="collapsed")
                c3.write("vs")
                v_in = c4.number_input("", 0, 15, cur["v"], key=f"{key_prefix}_v_{m_id}", disabled=bloqueado, label_visibility="collapsed")
                c5.write(f"**{match['V_team']}**")
                
                if l_in == v_in and not bloqueado:
                    av = c6.selectbox("¿Quién pasa?", ["Local", "Visita"], index=0 if cur.get("avanza", "L") == "L" else 1, key=f"{key_prefix}_av_{m_id}")
                    if not read_only: storage_path[m_id] = {"l": l_in, "v": v_in, "avanza": "L" if av == "Local" else "V"}
                elif not bloqueado:
                    c6.caption("Ganador directo")
                    if not read_only: storage_path[m_id] = {"l": l_in, "v": v_in, "avanza": "L" if l_in > v_in else "V"}
                else:
                    c6.caption("Esperando cruces...")
            
            if not read_only:
                st.write("") 
                if st.button(f"Actualizar y Avanzar a la siguiente ronda ({r_name})", key=f"btn_save_ko_{key_prefix}_{r_key}"):
                    save_data(data)
                    st.rerun() 

# ================= TAB 1: MI PREDICCIÓN =================
with t_pred:
    st.header(f"Simulación Completa de {user}")
    st_p1, st_p2 = st.tabs(["Fase de Grupos", "Fase Eliminatoria (Bracket)"])
    
    with st_p1:
        g_sel = st.selectbox("Selecciona un grupo para predecir:", list(PARTIDOS_GRUPOS.keys()), key="p_g_sel")
        with st.form(f"form_user_{g_sel}"):
            for i, (l, v) in enumerate(PARTIDOS_GRUPOS[g_sel]):
                m_id = f"{g_sel}_{i}"
                cur = data["users"][user]["group_predictions"].get(m_id, {"l": 0, "v": 0})
                c1, c2, c3, c4, c5 = st.columns([3,1,1,1,3])
                c1.write(l); l_in = c2.number_input("", 0, 20, cur["l"], key=f"u_l_{m_id}", label_visibility="collapsed")
                c3.write("vs"); v_in = c4.number_input("", 0, 20, cur["v"], key=f"u_v_{m_id}", label_visibility="collapsed")
                c5.write(v)
            if st.form_submit_button("Guardar Resultados del Grupo"):
                for i, _ in enumerate(PARTIDOS_GRUPOS[g_sel]):
                    m_id = f"{g_sel}_{i}"
                    data["users"][user]["group_predictions"][m_id] = {"l": st.session_state[f"u_l_{m_id}"], "v": st.session_state[f"u_v_{m_id}"]}
                save_data(data)
                st.success("Grupo simulado.")
        
        u_tables, _, df_u_thirds = get_all_group_tables(data["users"][user]["group_predictions"])
        st.subheader("📋 Así lucen tus grupos según tus predicciones:")
        cx = st.columns(3)
        for idx, g in enumerate(PARTIDOS_GRUPOS.keys()):
            with cx[idx % 3]:
                st.write(f"**{g}**")
                st.dataframe(u_tables[g][["Equipo", "Pts", "GD"]], hide_index=True)
                
        # AHORA SÍ SE IMPRIME LA TABLA DE TERCEROS EN TU PREDICCIÓN
        st.divider()
        st.subheader("🥉 Tus Mejores Terceros")
        st.dataframe(df_u_thirds[["Grupo", "Equipo", "Pts", "GD", "GF", "Avanza"]], hide_index=True)

    with st_p2:
        st.subheader("🎯 Tu Camino Hacia El Campeón")
        u_tables, _, df_u_thirds = get_all_group_tables(data["users"][user]["group_predictions"])
        user_bracket = resolve_full_bracket(u_tables, df_u_thirds, data["users"][user]["ko_predictions"])
        
        st.metric(label="🏆 TU CAMPEÓN PREDICHO", value=user_bracket["Campeon"])
        UI_fase_eliminatoria(user_bracket, data["users"][user]["ko_predictions"], "u_ko")

# ================= TAB 2: REALIDAD =================
with t_real:
    st.header("🌍 Estado Real del Mundial")
    
    if admin_mode:
        st.subheader("🛠️ Panel de Carga de Datos Oficiales (Admin)")
        adm_mode_sel = st.radio("¿Qué deseas actualizar?", ["Resultados de Grupos", "Fase Eliminatoria"])
        
        if adm_mode_sel == "Resultados de Grupos":
            g_adm = st.selectbox("Grupo Real:", list(PARTIDOS_GRUPOS.keys()))
            with st.form("f_real_grp"):
                for i, (l, v) in enumerate(PARTIDOS_GRUPOS[g_adm]):
                    m_id = f"{g_adm}_{i}"
                    cur = data["real_results"]["group_results"].get(m_id, {"l": 0, "v": 0})
                    c1, c2, c3, c4, c5 = st.columns([3,1,1,1,3])
                    c1.write(l); l_a = c2.number_input("", 0, 20, cur["l"], key=f"r_l_{m_id}", label_visibility="collapsed")
                    c3.write("vs"); v_a = c4.number_input("", 0, 20, cur["v"], key=f"r_v_{m_id}", label_visibility="collapsed")
                    c5.write(v)
                if st.form_submit_button("Publicar Resultados Reales de Grupo"):
                    for i, _ in enumerate(PARTIDOS_GRUPOS[g_adm]):
                        m_id = f"{g_adm}_{i}"
                        data["real_results"]["group_results"][m_id] = {"l": st.session_state[f"r_l_{m_id}"], "v": st.session_state[f"r_v_{m_id}"]}
                    save_data(data)
                    st.success("Datos oficiales guardados.")
        else:
            r_tables, _, df_r_thirds = get_all_group_tables(data["real_results"]["group_results"])
            real_bracket = resolve_full_bracket(r_tables, df_r_thirds, data["real_results"]["ko_results"])
            UI_fase_eliminatoria(real_bracket, data["real_results"]["ko_results"], "r_ko")

    st.divider()
    
    st.subheader("📊 Tablas de Posiciones Reales de la FIFA")
    r_tables, _, df_r_thirds = get_all_group_tables(data["real_results"]["group_results"])
    
    cx2 = st.columns(3)
    for idx, g in enumerate(PARTIDOS_GRUPOS.keys()):
        with cx2[idx % 3]:
            st.write(f"**{g}**")
            st.dataframe(r_tables[g], hide_index=True)
            
    st.subheader("🥉 Tabla Oficial de Terceros")
    st.dataframe(df_r_thirds[["Grupo", "Equipo", "Pts", "GD", "GF", "Avanza"]], hide_index=True)
    
    st.subheader("🌳 Llave de Eliminación Oficial Actualizada")
    real_bracket = resolve_full_bracket(r_tables, df_r_thirds, data["real_results"]["ko_results"])
    st.success(f"🏆 CAMPEÓN REAL ACTUAL: {real_bracket['Campeon']}")
    UI_fase_eliminatoria(real_bracket, {}, "view_real_ko", read_only=True)

# ================= TAB 3: POSICIONES Y REGLAS =================
with t_puntos:
    st.header("🏆 Tabla de Clasificación de la Quiniela")
    
    def calcular_puntos_totales(user_obj, real_obj):
        pts = 0
        u_grp = user_obj.get("group_predictions", {})
        r_grp = real_obj.get("group_results", {})
        for m_id, r_res in r_grp.items():
            if m_id in u_grp:
                pl, pv = u_grp[m_id]["l"], u_grp[m_id]["v"]
                rl, rv = r_res["l"], r_res["v"]
                if pl == rl and pv == rv: pts += 3
                elif (pl > pv and rl > rv) or (pl < pv and rl < rv) or (pl == pv and rl == rv): pts += 1
                
        def extraer_equipos(round_matches):
            eqs = set()
            for m in round_matches:
                for k in ["L_team", "V_team"]:
                    if not any(f in m[k] for f in ["Por definir", "Mejor", "Esperando"]): eqs.add(m[k])
            return eqs

        r_tables, _, df_r_thirds = get_all_group_tables(r_grp)
        u_tables, _, df_u_thirds = get_all_group_tables(u_grp)
        
        rb = resolve_full_bracket(r_tables, df_r_thirds, real_obj.get("ko_results", {}))
        ub = resolve_full_bracket(u_tables, df_u_thirds, user_obj.get("ko_predictions", {}))
        
        pts += len(extraer_equipos(ub["R16"]).intersection(extraer_equipos(rb["R16"]))) * 2
        pts += len(extraer_equipos(ub["QF"]).intersection(extraer_equipos(rb["QF"]))) * 4
        pts += len(extraer_equipos(ub["SF"]).intersection(extraer_equipos(rb["SF"]))) * 8
        pts += len(extraer_equipos(ub["Final"]).intersection(extraer_equipos(rb["Final"]))) * 16
        
        if ub["Campeon"] == rb["Campeon"] and rb["Campeon"] != "Por definir": pts += 32
        return pts

    ranking = []
    for u_name, u_data in data["users"].items():
        total_p = calcular_puntos_totales(u_data, data["real_results"])
        ranking.append({"Jugador": u_name, "Puntos Totales": total_p})
        
    if ranking:
        df_rank = pd.DataFrame(ranking).sort_values("Puntos Totales", ascending=False).reset_index(drop=True)
        df_rank.index += 1
        st.table(df_rank)
    else:
        st.info("No hay datos de jugadores aún.")
        
    st.divider()
    
    st.subheader("📖 Explicación del Criterio de Puntos")
    st.markdown("""
    Para evaluar un torneo completo con fase eliminatoria (*Bracket Challenge*), aplicar puntos por goles en llaves avanzadas castiga al jugador si su equipo fue eliminado antes. Por ello, se utiliza el **Criterio de Progresión Exponencial**, el estándar de la FIFA:
    
    1. **En Fase de Grupos (Por Partido):**
       * **3 Puntos:** Resultado Exacto (Le acertaste al marcador idéntico).
       * **1 Punto:** Tendencia Correcta (Acertaste al ganador o al empate, pero con otro marcador).
       
    2. **En Fase Eliminatoria (Por Equipo Clasificado):**
       * **2 Puntos** por cada equipo que metas correctamente en **Octavos de Final** (R16).
       * **4 Puntos** por cada equipo que metas correctamente en **Cuartos de Final** (QF).
       * **8 Puntos** por cada equipo que metas correctamente en **Semifinales** (SF).
       * **16 Puntos** por cada equipo que metas correctamente en la **Gran Final**.
       * **32 Puntos** adicionales si aciertas exactamente al **Campeón del Mundo**.
    """)
