from datetime import datetime, timedelta
import json
import os
import calendar
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Executive Dashboard - Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_FILE = "agenda_executiva_db.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_dados(compromissos):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(compromissos, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Erro ao salvar dados localmente: {e}")

# Estilização Global
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FAF9F6;
        color: #2D2926;
    }
    h1, h2, h3 {
        color: #5D4037;
        font-family: 'Inter', -apple-system, Helvetica, Arial, sans-serif;
    }
    .exec-card {
        background-color: #F3EFEA;
        border: 1px solid #D7CCC8;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .exec-card h3 {
        margin: 0;
        color: #8D6E63;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .exec-card p {
        margin: 8px 0 0 0;
        color: #5D4037;
        font-size: 26px;
        font-weight: bold;
    }
    .alert-card-atraso {
        background-color: #FBE9E7;
        border-left: 5px solid #D32F2F;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 20px;
        color: #B71C1C;
    }
    .stButton>button {
        background-color: #5D4037;
        color: white;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #4E342E;
    }
    </style>
""",
    unsafe_allow_html=True,
)

if "compromissos" not in st.session_state:
    st.session_state.compromissos = carregar_dados()

if "dia_selecionado" not in st.session_state:
    st.session_state.dia_selecionado = datetime.now().date()

st.markdown(
    """
    <div style="padding: 10px 0; border-bottom: 1px solid #D7CCC8; margin-bottom: 25px;">
        <h1 style="margin:0; font-size: 28px;">📊 Executive Dashboard & Calendar</h1>
        <p style="margin:5px 0 0 0; color: #8D6E63; font-size: 15px;">Visão consolidada para hoje, próximos 7 dias e calendário mensal interativo.</p>
    </div>
""",
    unsafe_allow_html=True,
)

hoje_obj = datetime.now().date()
daqui_7_dias_obj = hoje_obj + timedelta(days=7)
hoje_str = hoje_obj.strftime("%Y-%m-%d")

# Alerta de Atraso
tarefas_atrasadas = [
    c for c in st.session_state.compromissos 
    if not c.get("Concluido", False) and c.get("Data", "") < hoje_str
]
if tarefas_atrasadas:
    st.markdown(
        f"""
        <div class="alert-card-atraso">
            <strong>⚠️ ATENÇÃO:</strong> Você possui <b>{len(tarefas_atrasadas)} compromisso(s) pendente(s) de dias anteriores</b>.
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------------------
# DASHBOARD PRINCIPAL: HOJE E DAQUI A 7 DIAS (Topo em Destaque)
# -------------------------------------------------------------
st.markdown("### ⚡ Visão Geral: Hoje & Próximos 7 Dias")
col_dash_1, col_dash_2 = st.columns(2)

with col_dash_1:
    st.markdown(f"<div class='exec-card'><h3>📌 Para Hoje ({hoje_obj.strftime('%d/%m/%Y')})</h3>", unsafe_allow_html=True)
    tarefas_hoje = [c for c in st.session_state.compromissos if c.get("Data") == hoje_str]
    if tarefas_hoje:
        for item in tarefas_hoje:
            real_idx = st.session_state.compromissos.index(item)
            p_cor = "🔴" if item['Prioridade'] == "Alta" else "🟡" if item['Prioridade'] == "Média" else "🟢"
            chk = st.checkbox(f"{p_cor} **{item['Hora']}** - {item['Titulo']} *[{item['Categoria']}]*", value=item.get("Concluido", False), key=f"dash_hoje_{real_idx}")
            if chk != item.get("Concluido", False):
                st.session_state.compromissos[real_idx]["Concluido"] = chk
                salvar_dados(st.session_state.compromissos)
                st.rerun()
    else:
        st.write("Nenhum compromisso para hoje.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_dash_2:
    st.markdown(f"<div class='exec-card'><h3>⏳ Próximos 7 Dias (Até {daqui_7_dias_obj.strftime('%d/%m/%Y')})</h3>", unsafe_allow_html=True)
    tarefas_7 = []
    for c in st.session_state.compromissos:
        if c.get("Data") and not c.get("Concluido", False):
            try:
                d_item = datetime.strptime(c.get("Data"), "%Y-%m-%d").date()
                if hoje_obj < d_item <= daqui_7_dias_obj:
                    tarefas_7.append(c)
            except Exception:
                pass
    if tarefas_7:
        tarefas_7_ord = sorted(tarefas_7, key=lambda x: (x.get("Data"), x.get("Hora")))
        for item in tarefas_7_ord:
            cor_p = "🔴" if item['Prioridade'] == "Alta" else "🟡" if item['Prioridade'] == "Média" else "🟢"
            st.markdown(f"- {cor_p} **{item['Data']} às {item['Hora']}**: {item['Titulo']} *({item['Categoria']})*")
    else:
        st.write("Nenhum compromisso nos próximos 7 dias.")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# -------------------------------------------------------------
# ABAS DE NAVEGAÇÃO COMPLETA
# -------------------------------------------------------------
aba_calendario, aba_novo, aba_editar, aba_completa, aba_backup = st.tabs([
    "🗓️ Calendário Mensal", 
    "➕ Novo Compromisso", 
    "✏️ Editar ou Excluir",
    "📅 Visão Completa", 
    "💾 Backup"
])

with aba_calendario:
    st.subheader("🗓️ Calendário Mensal Estilo Grade Horizontal")
    
    # Seletor de Mês e Ano
    c_ano, c_mes = st.columns(2)
    with c_ano:
        ano_selecionado = st.selectbox("Ano", [2025, 2026, 2027], index=1, key="cal_ano_h")
    with c_mes:
        meses_dict = {
            1: "JAN", 2: "FEV", 3: "MAR", 4: "ABR", 
            5: "MAI", 6: "JUN", 7: "JUL", 8: "AGO", 
            9: "SET", 10: "OUT", 11: "NOV", 12: "DEZ"
        }
        mes_selecionado = st.selectbox("Mês", options=list(meses_dict.keys()), format_func=lambda x: meses_dict[x], index=hoje_obj.month - 1, key="cal_mes_h")

    st.markdown(f"<h2 style='text-align: center; letter-spacing: 2px; color: #5D4037;'>{meses_dict[mes_selecionado]} {ano_selecionado}</h2>", unsafe_allow_html=True)
    st.write("")

    # Grade padrão horizontal (Iniciando no Domingo)
    cal_matriz = calendar.Calendar(firstweekday=6).monthdatescalendar(ano_selecionado, mes_selecionado)
    dias_cabecalho = ["S", "M", "T", "W", "T", "F", "S"]  # Domingo a Sábado (ou S/M/T...)
    dias_nomes_completos = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    
    # Cabeçalho Horizontal dos Dias da Semana
    cols_cab = st.columns(7)
    for i, d_nome in enumerate(["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]):
        cor_cab = "#D32F2F" if i == 0 else "#5D4037"
        cols_cab[i].markdown(f"<div style='text-align: center; font-weight: bold; color: {cor_cab}; font-size: 13px;'>{d_nome}</div>", unsafe_allow_html=True)
        
    st.write("")

    # Renderização da grade linha por linha (horizontal)
    for semana in cal_matriz:
        cols_semana = st.columns(7)
        for i, data_dt in enumerate(semana):
            with cols_semana[i]:
                dia_num = data_dt.day
                pertence_ao_mes = (data_dt.month == mes_selecionado)
                data_str_atual = data_dt.strftime("%Y-%m-%d")
                
                # Buscar tarefas ativas do dia
                tarefas_do_dia = [c for c in st.session_state.compromissos if c.get("Data") == data_str_atual and not c.get("Concluido", False)]
                
                # Indicadores em bolinhas (maiores para Alta, menores para Média/Baixa)
                indicadores = ""
                for t in tarefas_do_dia:
                    prio = t.get("Prioridade", "Média")
                    cor = "#D32F2F" if prio == "Alta" else "#FBC02D" if prio == "Média" else "#388E3C"
                    tamanho = "9px" if prio == "Alta" else "6px"
                    indicadores += f"<span style='height:{tamanho}; width:{tamanho}; background-color:{cor}; border-radius:50%; display:inline-block; margin:1px;' title='{t['Titulo']}'></span>"

                if not pertence_ao_mes:
                    st.markdown(f"<div style='text-align: center; color: #D7CCC8; padding: 6px; font-size: 13px;'>{dia_num}</div>", unsafe_allow_html=True)
                else:
                    if st.button(f"{dia_num}", key=f"btn_h_{data_str_atual}"):
                        st.session_state.dia_selecionado = data_dt
                        st.rerun()
                    
                    st.markdown(f"<div style='margin-top:-6px; text-align:center; min-height:12px;'>{indicadores}</div>", unsafe_allow_html=True)

    # Painel Inferior: Detalhes da Data Selecionada + Adicionar Rápido
    st.write("---")
    data_sel_str = st.session_state.dia_selecionado.strftime("%Y-%m-%d")
    data_sel_formatada = st.session_state.dia_selecionado.strftime("%d %b %Y").upper()
    dia_semana_nome = st.session_state.dia_selecionado.strftime("%A").upper()
    
    st.markdown(f"### **{st.session_state.dia_selecionado.day}** <span style='font-size: 16px; color: #8D6E63;'>{dia_semana_nome} ({data_sel_str})</span>", unsafe_allow_html=True)
    
    detalhes_dia = [c for c in st.session_state.compromissos if c.get("Data") == data_sel_str]
    
    if detalhes_dia:
        for d in detalhes_dia:
            p_cor = "🔴" if d['Prioridade'] == "Alta" else "🟡" if d['Prioridade'] == "Média" else "🟢"
            estado_txt = "✅ Concluído" if d.get("Concluido") else "⏳ Pendente"
            st.markdown(f"<div class='exec-card' style='margin-bottom: 8px; padding: 10px;'><b>{d['Hora']}</b> {p_cor} {d['Titulo']} <i>({d['Categoria']})</i> - {estado_txt}<br><span style='color: #8D6E63; font-size: 13px;'>{d.get('Descricao', 'Sem notas.')}</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: #8D6E63; font-style: italic;'>Nenhum compromisso neste dia. Use o campo abaixo para adicionar.</p>", unsafe_allow_html=True)

    # Caixa rápida para adicionar compromisso na data selecionada
    with st.form(key=f"form_rapido_h_{data_sel_str}", clear_on_submit=True):
        st.markdown(f"**Adicionar compromisso em {data_sel_formatada}**")
        fr_1, fr_2, fr_3 = st.columns([3, 1, 2])
        with fr_1:
            novo_tit = st.text_input("Título", placeholder="Título...", label_visibility="collapsed")
        with fr_2:
            novo_hor = st.time_input("Horário", value=datetime.now(), label_visibility="collapsed")
        with fr_3:
            novo_pri = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"], label_visibility="collapsed")
            
        btn_add = st.form_submit_button(f"+ Add on {data_sel_formatada}")
        if btn_add:
            if not novo_tit:
                st.warning("Insira um título.")
            else:
                novo_item_rapido = {
                    "Titulo": novo_tit,
                    "Data": data_sel_str,
                    "Hora": novo_hor.strftime("%H:%M"),
                    "Prioridade": novo_pri,
                    "Categoria": "Geral",
                    "Local": "",
                    "Descricao": "",
                    "Concluido": False,
                    "CriadoEm": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.compromissos.append(novo_item_rapido)
                salvar_dados(st.session_state.compromissos)
                st.success("Adicionado com sucesso!")
                st.rerun()

with aba_novo:
    st.subheader("➕ Adicionar Novo Compromisso Completo")
    with st.form("form_novo_completo", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            titulo = st.text_input("Título", placeholder="Ex: Reunião")
            data_compromisso = st.date_input("Data", value=st.session_state.dia_selecionado)
        with c2:
            hora_compromisso = st.time_input("Horário", value=datetime.now())
            prioridade = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
        with c3:
            categoria = st.selectbox("Categoria", ["Reunião", "Prazo Crítico", "Pessoal", "Projeto", "Viagem", "Geral"])
            local = st.text_input("Local / Link", placeholder="Sala ou Meet")
            
        descricao = st.text_area("Notas / Pautas", placeholder="Detalhes...")
        
        if st.form_submit_button("🚀 Salvar Compromisso"):
            if not titulo:
                st.warning("O título é obrigatório.")
            else:
                novo_item = {
                    "Titulo": titulo,
                    "Data": data_compromisso.strftime("%Y-%m-%d"),
                    "Hora": hora_compromisso.strftime("%H:%M"),
                    "Prioridade": prioridade,
                    "Categoria": categoria,
                    "Local": local,
                    "Descricao": descricao,
                    "Concluido": False,
                    "CriadoEm": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.compromissos.append(novo_item)
                salvar_dados(st.session_state.compromissos)
                st.success("Salvo com sucesso!")
                st.rerun()

with aba_editar:
    st.subheader("✏️ Editar ou Excluir Compromissos")
    if st.session_state.compromissos:
        opcoes = {f"[{c['Data']} - {c['Hora']}] {c['Titulo']}": idx for idx, c in enumerate(st.session_state.compromissos)}
        escolha = st.selectbox("Selecione:", list(opcoes.keys()))
        idx_sel = opcoes[escolha]
        item = st.session_state.compromissos[idx_sel]
        
        with st.form("form_edicao_item"):
            nt = st.text_input("Título", value=item["Titulo"])
            nd = st.date_input("Data", value=datetime.strptime(item["Data"], "%Y-%m-%d").date())
            nh = st.time_input("Hora", value=datetime.strptime(item["Hora"], "%H:%M").time())
            np = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"], index=["Alta", "Média", "Baixa"].index(item.get("Prioridade", "Média")))
            
            c_b1, c_b2 = st.columns(2)
            if c_b1.form_submit_button("💾 Salvar"):
                st.session_state.compromissos[idx_sel].update({"Titulo": nt, "Data": str(nd), "Hora": str(nh), "Prioridade": np})
                salvar_dados(st.session_state.compromissos)
                st.success("Atualizado!")
                st.rerun()
            if c_b2.form_submit_button("🗑️ Excluir"):
                st.session_state.compromissos.pop(idx_sel)
                salvar_dados(st.session_state.compromissos)
                st.success("Excluído!")
                st.rerun()
    else:
        st.info("Nenhum compromisso cadastrado.")

with aba_completa:
    st.subheader("📅 Visão Geral Consolidada")
    if st.session_state.compromissos:
        df = pd.DataFrame(st.session_state.compromissos)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Sem dados.")

with aba_backup:
    st.subheader("💾 Backup e Sincronização")
    if st.session_state.compromissos:
        st.download_button("Baixar JSON", json.dumps(st.session_state.compromissos, ensure_ascii=False, indent=4), "agenda.json")
