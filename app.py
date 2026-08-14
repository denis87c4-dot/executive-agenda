from datetime import datetime, timedelta
import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Executive Agenda - Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Arquivo local para salvar os dados permanentemente
DB_FILE = "agenda_executiva_db.json"

def carregar_dados():
    """Carrega os compromissos do arquivo JSON local se ele existir."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_dados(compromissos):
    """Salva os compromissos no arquivo JSON local."""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(compromissos, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Erro ao salvar dados localmente: {e}")

# Estilização Executiva
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    h1, h2, h3 {
        color: #FFFFFF;
        font-family: 'Inter', -apple-system, Helvetica, Arial, sans-serif;
    }
    .exec-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .exec-card h3 {
        margin: 0;
        color: #94A3B8;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .exec-card p {
        margin: 8px 0 0 0;
        color: #38BDF8;
        font-size: 26px;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #0284C7;
        color: white;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #0369A1;
    }
    </style>
""",
    unsafe_allow_html=True,
)

if "compromissos" not in st.session_state:
    st.session_state.compromissos = carregar_dados()

st.markdown(
    """
    <div style="padding: 10px 0; border-bottom: 1px solid #334155; margin-bottom: 25px;">
        <h1 style="margin:0; font-size: 28px;">💼 Executive Agenda Pro</h1>
        <p style="margin:5px 0 0 0; color: #94A3B8; font-size: 15px;">Gestão estratégica de compromissos com persistência e edição flexível.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Datas de referência
hoje_obj = datetime.now().date()
daqui_7_dias_obj = hoje_obj + timedelta(days=7)

# Cards de Resumo Executivo Rápido
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

total_tarefas = len(st.session_state.compromissos)
compromissos_hoje = sum(
    1 for c in st.session_state.compromissos if c.get("Data") == hoje_obj.strftime("%Y-%m-%d") and not c.get("Concluido", False)
)

compromissos_7dias = 0
for c in st.session_state.compromissos:
    if not c.get("Concluido", False) and c.get("Data"):
        try:
            data_item = datetime.strptime(c.get("Data"), "%Y-%m-%d").date()
            if hoje_obj <= data_item <= daqui_7_dias_obj:
                compromissos_7dias += 1
        except Exception:
            pass

with col_m1:
    st.markdown(f"<div class='exec-card'><h3>Compromissos Hoje</h3><p>{compromissos_hoje}</p></div>", unsafe_allow_html=True)
with col_m2:
    st.markdown(f"<div class='exec-card'><h3>Próximos 7 Dias</h3><p>{compromissos_7dias}</p></div>", unsafe_allow_html=True)
with col_m3:
    st.markdown(f"<div class='exec-card'><h3>Total na Agenda</h3><p style='color: #F8FAFC;'>{total_tarefas}</p></div>", unsafe_allow_html=True)
with col_m4:
    st.markdown(f"<div class='exec-card'><h3>Status do Núcleo</h3><p style='color: #4ADE80; font-size: 18px; margin-top: 8px;'>● Salvo em Disco</p></div>", unsafe_allow_html=True)

st.write("---")

# Adicionando a aba "✏️ Editar ou Excluir"
aba_hoje_7dias, aba_agenda, aba_novo, aba_editar, aba_widget, aba_backup = st.tabs([
    "⚡ Visão Foco (Hoje & 7 Dias)", 
    "📅 Visão Completa", 
    "➕ Novo Compromisso", 
    "✏️ Editar ou Excluir",
    "📱 Widget Simplificado", 
    "💾 Backup & Dados"
])

with aba_hoje_7dias:
    st.subheader("🎯 Radar Executivo: O que tenho para hoje e daqui a 7 dias?")
    
    col_h, col_s = st.columns(2)
    
    with col_h:
        st.markdown(f"### 📌 Para Hoje ({hoje_obj.strftime('%d/%m/%Y')})")
        tarefas_hoje = [c for c in st.session_state.compromissos if c.get("Data") == hoje_obj.strftime("%Y-%m-%d")]
        
        if tarefas_hoje:
            for item in tarefas_hoje:
                real_idx = st.session_state.compromissos.index(item)
                status_box = st.checkbox(f"**{item['Hora']}** - {item['Titulo']} [{item['Prioridade']}]", value=item.get("Concluido", False), key=f"hoje_{real_idx}")
                if status_box != item.get("Concluido", False):
                    st.session_state.compromissos[real_idx]["Concluido"] = status_box
                    salvar_dados(st.session_state.compromissos)
                    st.rerun()
        else:
            st.info("Nenhum compromisso agendado para hoje. Aproveite o foco estratégico!")

    with col_s:
        st.markdown(f"### ⏳ Próximos 7 Dias (Até {daqui_7_dias_obj.strftime('%d/%m/%Y')})")
        
        tarefas_7 = []
        for c in st.session_state.compromissos:
            if c.get("Data"):
                try:
                    d_item = datetime.strptime(c.get("Data"), "%Y-%m-%d").date()
                    if hoje_obj <= d_item <= daqui_7_dias_obj:
                        tarefas_7.append(c)
                except Exception:
                    pass
        
        if tarefas_7:
            tarefas_7_ordenadas = sorted(tarefas_7, key=lambda x: (x.get("Data"), x.get("Hora")))
            for item in tarefas_7_ordenadas:
                cor_prioridade = "🔴" if item['Prioridade'] == "Alta" else "🟡" if item['Prioridade'] == "Média" else "🟢"
                st.markdown(f"- {cor_prioridade} **{item['Data']} às {item['Hora']}**: {item['Titulo']} *({item['Categoria']})*")
        else:
            st.info("Agenda limpa para a próxima semana.")

with aba_novo:
    st.subheader("➕ Adicionar Novo Compromisso ou Tarefa")
    
    with st.form("form_agenda", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            titulo = st.text_input("Título do Compromisso", placeholder="Ex: Reunião Diretoria / Projeto X")
            data_compromisso = st.date_input("Data", value=hoje_obj)
        with c2:
            hora_compromisso = st.time_input("Horário", value=datetime.now())
            prioridade = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
        with c3:
            lista_categorias = ["Reunião", "Prazo Crítico", "Pessoal", "Projeto", "Viagem", "Outra..."]
            categoria_escolhida = st.selectbox("Categoria", lista_categorias)
            categoria_custom = st.text_input("Especifique a Categoria", placeholder="Digite se escolheu 'Outra...'")
            local = st.text_input("Local / Link", placeholder="Ex: Sala de Reuniões 3 ou Meet")
            
        descricao = st.text_area("Notas / Pautas importantes", placeholder="Detalhes rápidos...")
        
        submitted = st.form_submit_button("🚀 Agendar na Agenda Executiva")
        if submitted:
            if not titulo:
                st.warning("⚠️ O título do compromisso é obrigatório.")
            else:
                cat_final = categoria_custom.strip() if categoria_escolhida == "Outra..." and categoria_custom.strip() else categoria_escolhida
                if cat_final == "Outra...":
                    cat_final = "Geral"

                novo_item = {
                    "Titulo": titulo,
                    "Data": data_compromisso.strftime("%Y-%m-%d"),
                    "Hora": hora_compromisso.strftime("%H:%M"),
                    "Prioridade": prioridade,
                    "Categoria": cat_final,
                    "Local": local,
                    "Descricao": descricao,
                    "Concluido": False,
                    "CriadoEm": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.compromissos.append(novo_item)
                salvar_dados(st.session_state.compromissos)
                st.success("✅ Compromisso adicionado e salvo com sucesso!")

with aba_editar:
    st.subheader("✏️ Editar ou Excluir Compromissos Existentes")
    
    if st.session_state.compromissos:
        # Criar rótulos claros para identificar cada compromisso no Selectbox
        opcoes_compromissos = {
            f"[{c['Data']} - {c['Hora']}] {c['Titulo']} ({c['Categoria']})": idx 
            for idx, c in enumerate(st.session_state.compromissos)
        }
        
        escolha_str = st.selectbox("Selecione o compromisso que deseja alterar:", list(opcoes_compromissos.keys()))
        idx_selecionado = opcoes_compromissos[escolha_str]
        item_atual = st.session_state.compromissos[idx_selecionado]
        
        st.write("---")
        st.markdown(f"### Editando: **{item_atual['Titulo']}**")
        
        with st.form("form_edicao"):
            e1, e2, e3 = st.columns(3)
            with e1:
                novo_titulo = st.text_input("Título", value=item_atual.get("Titulo", ""))
                try:
                    data_inicial = datetime.strptime(item_atual.get("Data", hoje_obj.strftime("%Y-%m-%d")), "%Y-%m-%d").date()
                except Exception:
                    data_inicial = hoje_obj
                nova_data = st.date_input("Data", value=data_inicial)
            with e2:
                try:
                    hora_inicial = datetime.strptime(item_atual.get("Hora", "09:00"), "%H:%M").time()
                except Exception:
                    hora_inicial = datetime.now().time()
                nova_hora = st.time_input("Horário", value=hora_inicial)
                
                prioridades_disponiveis = ["Alta", "Média", "Baixa"]
                idx_prio = prioridades_disponiveis.index(item_atual.get("Prioridade", "Média")) if item_atual.get("Prioridade") in prioridades_disponiveis else 1
                nova_prio = st.selectbox("Prioridade", prioridades_disponiveis, index=idx_prio)
            with e3:
                cats_base = ["Reunião", "Prazo Crítico", "Pessoal", "Projeto", "Viagem"]
                cat_atual = item_atual.get("Categoria", "Reunião")
                if cat_atual not in cats_base:
                    cats_base.append(cat_atual)
                cats_base.append("Outra...")
                
                idx_cat = cats_base.index(cat_atual) if cat_atual in cats_base else 0
                nova_cat_escolha = st.selectbox("Categoria", cats_base, index=idx_cat)
                nova_cat_custom = st.text_input("Nova Categoria (se escolheu Outra...)", placeholder="")
                
                novo_local = st.text_input("Local / Link", value=item_atual.get("Local", ""))
                
            nova_desc = st.text_area("Notas / Pautas", value=item_atual.get("Descricao", ""))
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                salvar_edicao = st.form_submit_button("💾 Salvar Alterações")
            with col_b2:
                excluir_item = st.form_submit_button("🗑️ Excluir Este Compromisso")
                
            if salvar_edicao:
                if not novo_titulo:
                    st.warning("⚠️ O título não pode ficar em branco.")
                else:
                    cat_final = nova_cat_custom.strip() if nova_cat_escolha == "Outra..." and nova_cat_custom.strip() else nova_cat_escolha
                    if cat_final == "Outra...":
                        cat_final = "Geral"
                        
                    st.session_state.compromissos[idx_selecionado].update({
                        "Titulo": novo_titulo,
                        "Data": nova_data.strftime("%Y-%m-%d"),
                        "Hora": nova_hora.strftime("%H:%M"),
                        "Prioridade": nova_prio,
                        "Categoria": cat_final,
                        "Local": novo_local,
                        "Descricao": nova_desc
                    })
                    salvar_dados(st.session_state.compromissos)
                    st.success("🎉 Compromisso atualizado com sucesso!")
                    st.rerun()
                    
            if excluir_item:
                st.session_state.compromissos.pop(idx_selecionado)
                salvar_dados(st.session_state.compromissos)
                st.success("🗑️ Compromisso excluído com sucesso!")
                st.rerun()
    else:
        st.info("Nenhum compromisso cadastrado para editar.")

with aba_agenda:
    st.subheader("📅 Visão Consolidada (Filtros por Mês e Semana)")
    
    if st.session_state.compromissos:
        df_agenda = pd.DataFrame(st.session_state.compromissos)
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            filtro_cat = st.selectbox("Filtrar por Categoria", ["Todas"] + sorted(df_agenda["Categoria"].unique().tolist()))
        with f_col2:
            filtro_prio = st.selectbox("Filtrar por Prioridade", ["Todas", "Alta", "Média", "Baixa"])
            
        df_view = df_agenda.copy()
        if filtro_cat != "Todas":
            df_view = df_view[df_view["Categoria"] == filtro_cat]
        if filtro_prio != "Todas":
            df_view = df_view[df_view["Prioridade"] == filtro_prio]
            
        st.dataframe(
            df_view[["Data", "Hora", "Titulo", "Prioridade", "Categoria", "Local", "Concluido"]],
            use_container_width=True
        )
        
        st.write("### 🛠️ Marcar Concluído")
        for idx, row in df_view.iterrows():
            real_idx = st.session_state.compromissos.index(row.to_dict()) if row.to_dict() in st.session_state.compromissos else idx
            c_info, c_check = st.columns([5, 1])
            c_info.text(f"[{row['Data']} - {row['Hora']}] {row['Titulo']} ({row['Categoria']})")
            
            estado_atual = row["Concluido"]
            novo_estado = c_check.checkbox("Concluir", value=estado_atual, key=f"chk_vis_{idx}")
            if novo_estado != estado_atual:
                st.session_state.compromissos[real_idx]["Concluido"] = novo_estado
                salvar_dados(st.session_state.compromissos)
                st.rerun()
    else:
        st.info("Nenhum compromisso cadastrado no sistema.")

with aba_widget:
    st.subheader("📱 Widget Simplificado (Visão de Bolso / Celular)")
    st.markdown("Uma interface minimalista voltada para consulta rápida vertical ideal para abrir no celular entre reuniões.")
    
    st.markdown("<div class='exec-card'>", unsafe_allow_html=True)
    st.markdown("### ⚡ QUICK WIDGET - PRÓXIMOS EVENTOS")
    
    if st.session_state.compromissos:
        pendentes_widget = [c for c in st.session_state.compromissos if not c.get("Concluido")]
        if pendentes_widget:
            for w_item in pendentes_widget[:5]:
                p_cor = "🔴" if w_item['Prioridade'] == "Alta" else "⚡"
                st.markdown(f"**{w_item['Data']} | {w_item['Hora']}** {p_cor} {w_item['Titulo']}")
        else:
            st.success("Tudo em dia! Sem pendências ativas.")
    else:
        st.info("Agenda vazia.")
    st.markdown("</div>", unsafe_allow_html=True)

with aba_backup:
    st.subheader("💾 Central de Sincronização e Backup")
    
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.markdown("### 📤 Exportar Dados")
        if st.session_state.compromissos:
            json_data = json.dumps(st.session_state.compromissos, ensure_ascii=False, indent=4)
            st.download_button(
                "📥 Baixar Backup Executivo (.json)",
                data=json_data,
                file_name=f"agenda_executiva_{datetime.now().strftime('%Y-%m-%d')}.json",
                mime="application/json"
            )
    with b_col2:
        st.markdown("### 📥 Importar Dados")
        uploaded_file = st.file_uploader("Carregar arquivo de agenda (.json)", type=["json"])
        if uploaded_file is not None:
            try:
                dados_carregados = json.load(uploaded_file)
                if isinstance(dados_carregados, list):
                    st.session_state.compromissos = dados_carregados
                    salvar_dados(st.session_state.compromissos)
                    st.success("🎉 Agenda sincronizada, restaurada e salva localmente!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao carregar arquivo: {e}")
