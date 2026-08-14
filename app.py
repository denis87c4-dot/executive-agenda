from datetime import datetime, timedelta
import json
import os
import calendar
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Executive Dashboard - Planner Pro",
    page_icon="📅",
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
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
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
        padding: 6px 12px;
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
    <div style="padding: 10px 0; border-bottom: 1px solid #D7CCC8; margin-bottom: 20px;">
        <h1 style="margin:0; font-size: 26px;">📅 Executive Planner Mensal</h1>
        <p style="margin:5px 0 0 0; color: #8D6E63; font-size: 14px;">Planejamento estilo planner de mesa (Segunda a Domingo) com visão executiva integrada.</p>
    </div>
""",
    unsafe_allow_html=True,
)

hoje_obj = datetime.now().date()
daqui_7_dias_obj = hoje_obj + timedelta(days=7)
hoje_str = hoje_obj.strftime("%Y-%m-%d")

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

aba_planner, aba_novo, aba_editar, aba_completa, aba_backup = st.tabs([
    "🗓️ Planner Mensal (Estilo Mesa)", 
    "➕ Novo Compromisso", 
    "✏️ Editar ou Excluir",
    "📅 Visão Completa", 
    "💾 Backup"
])

with aba_planner:
    c_ano, c_mes = st.columns(2)
    with c_ano:
        ano_selecionado = st.selectbox("Ano", [2025, 2026, 2027], index=1, key="pl_ano")
    with c_mes:
        meses_dict = {
            1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 
            5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO", 
            9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
        }
        mes_selecionado = st.selectbox("Mês", options=list(meses_dict.keys()), format_func=lambda x: meses_dict[x], index=hoje_obj.month - 1, key="pl_mes")

    st.markdown(f"<h2 style='text-align: center; letter-spacing: 3px; color: #5D4037;'>PLANNER MENSAL - {meses_dict[mes_selecionado]} / {ano_selecionado}</h2>", unsafe_allow_html=True)
    st.write("")

    cal_matriz = calendar.Calendar(firstweekday=0).monthdatescalendar(ano_selecionado, mes_selecionado)
    dias_semana_nome = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    
    cols_cab = st.columns(7)
    for i, d_nome in enumerate(dias_semana_nome):
        cor_cab = "#D32F2F" if i >= 5 else "#5D4037"
        cols_cab[i].markdown(f"<div style='text-align: center; font-weight: bold; color: {cor_cab}; font-size: 13px; background-color: #F3EFEA; padding: 6px; border-radius: 4px;'>{d_nome}</div>", unsafe_allow_html=True)
        
    st.write("")

    for semana in cal_matriz:
        cols_semana = st.columns(7)
        for i, data_dt in enumerate(semana):
            with cols_semana[i]:
                dia_num = data_dt.day
                pertence_ao_mes = (data_dt.month == mes_selecionado)
                data_str_atual = data_dt.strftime("%Y-%m-%d")
                
                tarefas_do_dia = [c for c in st.session_state.compromissos if c.get("Data") == data_str_atual and not c.get("Concluido", False)]
                
                if not pertence_ao_mes:
                    st.markdown(f"<div style='background-color: #FAF9F6; border: 1px dashed #E0D9D0; border-radius: 4px; padding: 6px; min-height: 85px; color: #D7CCC8; text-align: right; font-size: 12px;'>{dia_num}</div>", unsafe_allow_html=True)
                else:
                    is_selecionado = (st.session_state.dia_selecionado == data_dt)
                    estilo_fundo = "background-color: #FFFFFF; border: 2px solid #5D4037;" if is_selecionado else "background-color: #FFFFFF; border: 1px solid #D7CCC8;"
                    
                    resumo_tarefas = ""
                    for t in tarefas_do_dia[:3]:
                        prio_cor = "🔴" if t['Prioridade'] == "Alta" else "🟡" if t['Prioridade'] == "Média" else "🟢"
                        resumo_tarefas += f"<div style='font-size: 10px; color: #2D2926; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{prio_cor} {t['Hora']} {t['Titulo']}</div>"
                    
                    if len(tarefas_do_dia) > 3:
                        resumo_tarefas += f"<div style='font-size: 9px; color: #8D6E63;'>+{len(tarefas_do_dia)-3} mais</div>"

                    if st.button(f"{dia_num}", key=f"planner_btn_{data_str_atual}"):
                        st.session_state.dia_selecionado = data_dt
                        st.rerun()
                    
                    st.markdown(f"<div style='{estilo_fundo} border-radius: 4px; padding: 4px 6px; margin-top: -38px; min-height: 80px; pointer-events: none;'><b>{dia_num}</b><hr style='margin: 2px 0; border-top: 1px solid #E0D9D0;'>{resumo_tarefas}</div>", unsafe_allow_html=True)

    st.write("---")
    data_sel_str = st.session_state.dia_selecionado.strftime("%Y-%m-%d")
    data_sel_formatada = st.session_state.dia_selecionado.strftime("%d/%m/%Y")
    dia_semana_nome_sel = dias_semana_nome[st.session_state.dia_selecionado.weekday()]
    
    st.markdown(f"### 📋 Detalhes do Dia: **{dia_semana_nome_sel}, {data_sel_formatada}**", unsafe_allow_html=True)
    
    detalhes_dia = [c for c in st.session_state.compromissos if c.get("Data") == data_sel_str]
    
    if detalhes_dia:
        for d in detalhes_dia:
            real_idx = st.session_state.compromissos.index(d)
            p_cor = "🔴" if d['Prioridade'] == "Alta" else "🟡" if d['Prioridade'] == "Média" else "🟢"
            
            c_info, c_chk = st.columns([5, 1])
            c_info.markdown(f"<div class='exec-card' style='padding: 10px; margin-bottom: 5px;'><b>{d['Hora']}</b> {p_cor} {d['Titulo']} <i>({d['Categoria']})</i><br><span style='font-size: 13px; color: #8D6E63;'>{d.get('Descricao', 'Sem notas.')}</span></div>", unsafe_allow_html=True)
            
            chk_concluido = c_chk.checkbox("Concluir", value=d.get("Concluido", False), key=f"chk_planner_{real_idx}")
            if chk_concluido != d.get("Concluido", False):
                st.session_state.compromissos[real_idx]["Concluido"] = chk_concluido
                salvar_dados(st.session_state.compromissos)
                st.rerun()
    else:
        st.info("Nenhum compromisso agendado para este dia no planner.")

    with st.form(key=f"form_rapido_planner_{data_sel_str}", clear_on_submit=True):
        st.markdown(f"**➕ Adicionar anotação ou compromisso em {data_sel_formatada}**")
        fr_1, fr_2, fr_3, fr_4 = st.columns([2, 1, 1, 1])
        with fr_1:
            novo_tit = st.text_input("Título", placeholder="Compromisso ou tarefa...")
        with fr_2:
            novo_hor = st.time_input("Horário", value=datetime.now())
        with fr_3:
            novo_pri = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
        with fr_4:
            novo_cat = st.text_input("Categoria", value="Geral", placeholder="Ex: Trabalho...")
            
        btn_add = st.form_submit_button(f"Salvar em {data_sel_formatada}")
        if btn_add:
            if not novo_tit:
                st.warning("Insira um título.")
            else:
                novo_item_rapido = {
                    "Titulo": novo_tit,
                    "Data": data_sel_str,
                    "Hora": novo_hor.strftime("%H:%M"),
                    "Prioridade": novo_pri,
                    "Categoria": novo_cat,
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
            categoria = st.text_input("Categoria", value="Geral", placeholder="Ex: Trabalho, Pessoal...")
            local = st.text_input("Local / Link", placeholder="Sala ou Meet")
            
        descricao = st.text_area("Notas / Pautas", placeholder="Detalhes...")
        
        if st.form_submit_button("🚀 Salvar no Planner"):
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
            nc = st.text_input("Categoria", value=item.get("Categoria", "Geral"))
            
            c_b1, c_b2 = st.columns(2)
            if c_b1.form_submit_button("💾 Salvar"):
                st.session_state.compromissos[idx_sel].update({"Titulo": nt, "Data": str(nd), "Hora": str(nh), "Prioridade": np, "Categoria": nc})
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
