from datetime import datetime, timedelta
import json
import os
import calendar
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

# Estilização inspirada no app Samsung Calendar / Clean Minimalista
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
        padding: 10px 20px;
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
        <h1 style="margin:0; font-size: 28px;">💼 Executive Agenda Pro</h1>
        <p style="margin:5px 0 0 0; color: #8D6E63; font-size: 15px;">Interface limpa estilo calendário mobile com gestão estratégica de compromissos.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Datas de referência
hoje_obj = datetime.now().date()
daqui_7_dias_obj = hoje_obj + timedelta(days=7)
hoje_str = hoje_obj.strftime("%Y-%m-%d")

# Verificação de itens atrasados
tarefas_atrasadas = [
    c for c in st.session_state.compromissos 
    if not c.get("Concluido", False) and c.get("Data", "") < hoje_str
]

if tarefas_atrasadas:
    st.markdown(
        f"""
        <div class="alert-card-atraso">
            <strong>⚠️ ATENÇÃO EXECUTIVA:</strong> Você possui <b>{len(tarefas_atrasadas)} compromisso(s) pendente(s) de dias anteriores</b> que não foram concluídos.
        </div>
        """,
        unsafe_allow_html=True
    )

# Cards de Resumo Executivo Rápido
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

total_tarefas = len(st.session_state.compromissos)
compromissos_hoje = sum(
    1 for c in st.session_state.compromissos if c.get("Data") == hoje_str and not c.get("Concluido", False)
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
    st.markdown(f"<div class='exec-card'><h3>Total na Agenda</h3><p style='color: #5D4037;'>{total_tarefas}</p></div>", unsafe_allow_html=True)
with col_m4:
    st.markdown(f"<div class='exec-card'><h3>Status do Núcleo</h3><p style='color: #2E7D32; font-size: 18px; margin-top: 8px;'>● Salvo em Disco</p></div>", unsafe_allow_html=True)

st.write("---")

# Abas de Navegação
aba_hoje_7dias, aba_calendario, aba_agenda, aba_novo, aba_editar, aba_widget, aba_backup = st.tabs([
    "⚡ Visão Foco (Hoje & 7 Dias)", 
    "🗓️ Calendário Estilo Samsung",
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
        tarefas_hoje = [c for c in st.session_state.compromissos if c.get("Data") == hoje_str]
        
        if tarefas_hoje:
            ordem_prio = {"Alta": 1, "Média": 2, "Baixa": 3}
            tarefas_hoje_ordenadas = sorted(tarefas_hoje, key=lambda x: (ordem_prio.get(x.get("Prioridade", "Média"), 2), x.get("Hora", "00:00")))
            
            for item in tarefas_hoje_ordenadas:
                real_idx = st.session_state.compromissos.index(item)
                p_cor = "🔴" if item['Prioridade'] == "Alta" else "🟡" if item['Prioridade'] == "Média" else "🟢"
                label_txt = f"{p_cor} **{item['Hora']}** - {item['Titulo']} *[{item['Categoria']}]*"
                
                status_box = st.checkbox(label_txt, value=item.get("Concluido", False), key=f"hoje_{real_idx}")
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
            if c.get("Data") and not c.get("Concluido", False):
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

with aba_calendario:
    # Seletor de Mês e Ano Estilo Limpo
    c_ano, c_mes = st.columns(2)
    with c_ano:
        ano_selecionado = st.selectbox("Ano", [2025, 2026, 2027], index=1, key="cal_ano")
    with c_mes:
        meses_dict = {
            1: "JAN", 2: "FEV", 3: "MAR", 4: "ABR", 
            5: "MAI", 6: "JUN", 7: "JUL", 8: "AGO", 
            9: "SET", 10: "OUT", 11: "NOV", 12: "DEZ"
        }
        mes_selecionado = st.selectbox("Mês", options=list(meses_dict.keys()), format_func=lambda x: meses_dict[x], index=hoje_obj.month - 1, key="cal_mes")

    st.markdown(f"<h2 style='text-align: center; letter-spacing: 2px; color: #5D4037; margin-top: 10px;'>{meses_dict[mes_selecionado]} {ano_selecionado}</h2>", unsafe_allow_html=True)
    st.write("")

    # Configuração de Calendário (Começando no Domingo como na imagem)
    cal = calendar.Calendar(firstweekday=6).monthdatescalendar(ano_selecionado, mes_selecionado)
    dias_semana = ["S", "M", "T", "W", "T", "F", "S"]  # Estilo limpo de iniciais
    
    cols_cabecalho = st.columns(7)
    for i, d_nome in enumerate(["S", "M", "T", "W", "T", "F", "S"]):
        cor_cab = "#D32F2F" if i == 0 else "#5D4037" # Domingo em destaque vermelho
        cols_cabecalho[i].markdown(f"<div style='text-align: center; font-weight: bold; color: {cor_cab}; font-size: 14px;'>{d_nome}</div>", unsafe_allow_html=True)
        
    st.write("")

    # Renderização da grade idêntica ao app
    for semana in cal:
        cols_semana = st.columns(7)
        for i, data_dt in enumerate(semana):
            with cols_semana[i]:
                dia_num = data_dt.day
                pertence_ao_mes = (data_dt.month == mes_selecionado)
                data_str_atual = data_dt.strftime("%Y-%m-%d")
                
                # Buscar tarefas ativas do dia
                tarefas_do_dia = [c for c in st.session_state.compromissos if c.get("Data") == data_str_atual and not c.get("Concluido", False)]
                
                # Montar bolinhas de prioridade maiores ou menores
                indicadores = ""
                for t in tarefas_do_dia:
                    prio = t.get("Prioridade", "Média")
                    cor = "#D32F2F" if prio == "Alta" else "#FBC02D" if prio == "Média" else "#388E3C"
                    tamanho = "10px" if prio == "Alta" else "6px"
                    indicadores += f"<span style='height:{tamanho}; width:{tamanho}; background-color:{cor}; border-radius:50%; display:inline-block; margin:1px;' title='{t['Titulo']}'></span>"

                # Estilo se for o dia selecionado ou o dia de hoje
                is_selecionado = (st.session_state.dia_selecionado == data_dt)
                is_hoje = (data_dt == hoje_obj)
                
                estilo_btn = "background-color: transparent; color: #2D2926; border: none;"
                if is_selecionado:
                    estilo_btn = "background-color: #5D4037; color: white; border-radius: 50%; font-weight: bold;"
                elif is_hoje:
                    estilo_btn = "border: 2px solid #5D4037; border-radius: 50%; font-weight: bold;"
                
                if not pertence_ao_mes:
                    # Dias cinzas do mês anterior/seguinte
                    st.markdown(f"<div style='text-align: center; color: #D7CCC8; padding: 8px; font-size: 14px;'>{dia_num}</div>", unsafe_allow_html=True)
                else:
                    if st.button(f"{dia_num}", key=f"samsung_btn_{data_str_atual}"):
                        st.session_state.dia_selecionado = data_dt
                        st.rerun()
                    
                    st.markdown(f"<div style='margin-top:-6px; text-align:center; min-height:14px;'>{indicadores}</div>", unsafe_allow_html=True)

    # Painel inferior idêntico ao modelo (Detalhes do dia selecionado e botão de adicionar)
    st.write("---")
    data_sel_str = st.session_state.dia_selecionado.strftime("%Y-%m-%d")
    data_sel_formatada = st.session_state.dia_selecionado.strftime("%d %b %Y").upper()
    dia_semana_nome = st.session_state.dia_selecionado.strftime("%A").upper()
    
    st.markdown(f"### **{st.session_state.dia_selecionado.day}** <span style='font-size: 16px; color: #8D6E63;'>{dia_semana_nome}</span>", unsafe_allow_html=True)
    
    detalhes_dia = [c for c in st.session_state.compromissos if c.get("Data") == data_sel_str]
    
    if detalhes_dia:
        for d in detalhes_dia:
            p_cor = "🔴" if d['Prioridade'] == "Alta" else "🟡" if d['Prioridade'] == "Média" else "🟢"
            estado_txt = "✅ Concluído" if d.get("Concluido") else "⏳ Pendente"
            st.markdown(f"<div class='exec-card' style='margin-bottom: 10px; padding: 12px;'><b>{d['Hora']}</b> {p_cor} {d['Titulo']} <i>({d['Categoria']})</i> - {estado_txt}<br><span style='color: #8D6E63; font-size: 13px;'>{d.get('Descricao', 'Sem notas adicionais.')}</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: #8D6E63; font-style: italic;'>Tap to add a sticker or tasks to this day.</p>", unsafe_allow_html=True)

    # Caixa rápida para adicionar compromisso na data selecionada clicada
    with st.form(key=f"form_rapido_{data_sel_str}", clear_on_submit=True):
        st.markdown(f"**Adicionar compromisso em {data_sel_formatada}**")
        fr_col1, fr_col2, fr_col3 = st.columns([3, 1, 2])
        with fr_col1:
            novo_tit = st.text_input("Título", placeholder="Título rápido...", label_visibility="collapsed")
        with fr_col2:
            novo_hor = st.time_input("Horário", value=datetime.now(), label_visibility="collapsed")
        with fr_col3:
            novo_pri = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"], label_visibility="collapsed")
            
        btn_adicionar_rapido = st.form_submit_button(f"+ Add on {data_sel_formatada}")
        if btn_adicionar_rapido:
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
    st.subheader("➕ Adicionar Novo Compromisso ou Tarefa Completa")
    
    with st.form("form_agenda", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            titulo = st.text_input("Título do Compromisso", placeholder="Ex: Reunião Diretoria / Projeto X")
            data_compromisso = st.date_input("Data", value=st.session_state.dia_selecionado)
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
                    data_inicial = datetime.strptime(item_atual.get("Data", hoje_str), "%Y-%m-%d").date()
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
    st.subheader("📅 Visão Consolidada (Filtros por Categoria e Prioridade)")
    
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
    st.subheader("📱 Widget Simplificado (Visão de Bolso)")
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
