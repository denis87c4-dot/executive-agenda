from datetime import datetime, timedelta
import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Executive Dashboard - Planner Pro",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_FILE = "agenda_executiva_db.json"
DB_DATAS_IMPORTANTES = "datas_importantes_db.json"

def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_dados(dados, arquivo):
    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
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
    st.session_state.compromissos = carregar_dados(DB_FILE)

if "datas_importantes" not in st.session_state:
    st.session_state.datas_importantes = carregar_dados(DB_DATAS_IMPORTANTES)

st.markdown(
    """
    <div style="padding: 10px 0; border-bottom: 1px solid #D7CCC8; margin-bottom: 20px;">
        <h1 style="margin:0; font-size: 26px;">📅 Executive Dashboard Executivo</h1>
        <p style="margin:5px 0 0 0; color: #8D6E63; font-size: 14px;">Gestão centralizada de compromissos e datas importantes.</p>
    </div>
""",
    unsafe_allow_html=True,
)

hoje_obj = datetime.now().date()
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

# -------------------------------------------------------------
# DASHBOARD SUPERIOR: HOJE E DATAS IMPORTANTES
# -------------------------------------------------------------
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
                salvar_dados(st.session_state.compromissos, DB_FILE)
                st.rerun()
    else:
        st.write("Nenhum compromisso para hoje.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_dash_2:
    st.markdown(f"<div class='exec-card'><h3>⭐ Próximas Datas Importantes</h3>", unsafe_allow_html=True)
    importantes_futuras = []
    for d in st.session_state.datas_importantes:
        if d.get("Data"):
            try:
                d_item = datetime.strptime(d.get("Data"), "%Y-%m-%d").date()
                if d_item >= hoje_obj:
                    importantes_futuras.append(d)
            except Exception:
                pass
    if importantes_futuras:
        importantes_ord = sorted(importantes_futuras, key=lambda x: x.get("Data"))
        for item in importantes_ord[:5]:
            st.markdown(f"- ⭐ **{datetime.strptime(item['Data'], '%Y-%m-%d').strftime('%d/%m/%Y')}**: {item['Titulo']} *({item.get('Categoria', 'Marco')})*")
    else:
        st.write("Nenhuma data importante cadastrada para os próximos dias.")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# -------------------------------------------------------------
# ABAS DO SISTEMA (VISÃO COMPLETA NO LUGAR DO PLANNER MENSAL)
# -------------------------------------------------------------
aba_completa, aba_novo, aba_datas, aba_editar, aba_backup = st.tabs([
    "📅 Visão Completa", 
    "➕ Novo Compromisso", 
    "⭐ Datas Importantes",
    "✏️ Editar / Excluir",
    "💾 Backup"
])

with aba_completa:
    st.subheader("📅 Visão Geral Consolidada de Compromissos")
    if st.session_state.compromissos:
        df = pd.DataFrame(st.session_state.compromissos)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum compromisso cadastrado ainda.")

with aba_novo:
    st.subheader("➕ Adicionar Novo Compromisso Completo")
    with st.form("form_novo_completo", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            titulo = st.text_input("Título", placeholder="Ex: Reunião")
            data_compromisso = st.date_input("Data", value=datetime.now())
        with c2:
            hora_compromisso = st.time_input("Horário", value=datetime.now())
            prioridade = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
        with c3:
            categoria = st.text_input("Categoria", value="Geral", placeholder="Ex: Trabalho, Pessoal...")
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
                salvar_dados(st.session_state.compromissos, DB_FILE)
                st.success("Salvo com sucesso!")
                st.rerun()

with aba_datas:
    st.subheader("⭐ Gerenciador de Datas Importantes")
    st.write("Cadastre aniversários, feriados, prazos de entrega ou marcos que merecem destaque.")
    
    with st.form("form_data_importante", clear_on_submit=True):
        di_1, di_2, di_3 = st.columns(3)
        with di_1:
            di_tit = st.text_input("Descrição do Marco / Data", placeholder="Ex: Aniversário / Prazo Final")
        with di_2:
            di_data = st.date_input("Data do Marco")
        with di_3:
            di_cat = st.text_input("Categoria", value="Marco", placeholder="Ex: Aniversário, Projeto...")
            
        if st.form_submit_button("⭐ Salvar Data Importante"):
            if not di_tit:
                st.warning("Informe o título da data.")
            else:
                nova_di = {
                    "Titulo": di_tit,
                    "Data": di_data.strftime("%Y-%m-%d"),
                    "Categoria": di_cat
                }
                st.session_state.datas_importantes.append(nova_di)
                salvar_dados(st.session_state.datas_importantes, DB_DATAS_IMPORTANTES)
                st.success("Data importante salva com sucesso!")
                st.rerun()

    st.write("---")
    st.markdown("### 📋 Datas Importantes Cadastradas")
    if st.session_state.datas_importantes:
        for idx, item in enumerate(st.session_state.datas_importantes):
            col_di1, col_di2 = st.columns([5, 1])
            col_di1.markdown(f"- ⭐ **{datetime.strptime(item['Data'], '%Y-%m-%d').strftime('%d/%m/%Y')}**: {item['Titulo']} *({item.get('Categoria', 'Marco')})*")
            if col_di2.button("Excluir", key=f"del_di_{idx}"):
                st.session_state.datas_importantes.pop(idx)
                salvar_dados(st.session_state.datas_importantes, DB_DATAS_IMPORTANTES)
                st.rerun()
    else:
        st.info("Nenhuma data importante cadastrada.")

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
                salvar_dados(st.session_state.compromissos, DB_FILE)
                st.success("Atualizado!")
                st.rerun()
            if c_b2.form_submit_button("🗑️ Excluir"):
                st.session_state.compromissos.pop(idx_sel)
                salvar_dados(st.session_state.compromissos, DB_FILE)
                st.success("Excluído!")
                st.rerun()
    else:
        st.info("Nenhum compromisso cadastrado.")

with aba_backup:
    st.subheader("💾 Backup e Sincronização")
    if st.session_state.compromissos:
        st.download_button("Baixar JSON Compromissos", json.dumps(st.session_state.compromissos, ensure_ascii=False, indent=4), "agenda.json")
    if st.session_state.datas_importantes:
        st.download_button("Baixar JSON Datas Importantes", json.dumps(st.session_state.datas_importantes, ensure_ascii=False, indent=4), "datas_importantes.json")
