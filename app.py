import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os

# Configuração da página
st.set_page_config(
    page_title="Dashboard CX - Talqui",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar dados com otimizações para deploy
@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_data():
    """Carrega e processa os dados do arquivo CSV Sindicompany"""
    try:
        # Carregar dados Sindicompany - arquivo principal V3
        sindicompany_file = "data/[ Talqui ] Sindicompany - Data_V3_Julho_20_26.csv"
        if os.path.exists(sindicompany_file):
            data = pd.read_csv(sindicompany_file, low_memory=False)
            
            # Converter datas - formato "2025-06-01 1:09:48"
            date_columns = ['queuedAt', 'manualAt', 'closedAt', 'createdAt', 'updatedAt', 'sessionRatingAt']
            for col in date_columns:
                if col in data.columns:
                    data[col] = pd.to_datetime(data[col], errors='coerce')
            
            # Adicionar colunas derivadas baseadas em createdAt
            if 'createdAt' in data.columns and not data['createdAt'].isna().all():
                data['date'] = data['createdAt'].dt.date
                data['hour'] = data['createdAt'].dt.hour
                data['weekday'] = data['createdAt'].dt.day_name()
            
            # Processar durações (converter de segundos para minutos)
            duration_columns = ['__sessionDuration', '__sessionQueueDuration', '__sessionManualDuration']
            for col in duration_columns:
                if col in data.columns:
                    data[f'{col}_minutes'] = pd.to_numeric(data[col], errors='coerce') / 60
            
            # Processar ratings
            if 'sessionRatingStars' in data.columns:
                data['sessionRatingStars'] = pd.to_numeric(data['sessionRatingStars'], errors='coerce')
            
            # Processar contadores de mensagens
            if '__sessionMessagesCount' in data.columns:
                data['__sessionMessagesCount'] = pd.to_numeric(data['__sessionMessagesCount'], errors='coerce')
            
            return data
        else:
            st.error(f"Arquivo não encontrado: {sindicompany_file}")
            return pd.DataFrame()
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        st.info("💡 **Arquivo necessário**: `data/[ Talqui ] Sindicompany - Data_V3_Julho_20_26.csv`")
        return pd.DataFrame()

def main():
    st.title("📊 Dashboard CX - Talqui")
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        data = load_data()
    
    if data.empty:
        st.error("Não foi possível carregar os dados. Verifique se o arquivo CSV está no diretório 'data/'")
        return
    
    # Sidebar com filtros de data
    st.sidebar.header("📅 Filtros")
    
    # Filtro de data baseado nos dados
    if not data.empty and 'createdAt' in data.columns:
        min_date = data['createdAt'].min().date()
        max_date = data['createdAt'].max().date()
        today = datetime.now().date()
        
        # Filtros predefinidos
        filter_options = {
            "Todo o período": (min_date, max_date),
            "Hoje": (today, today),
            "Ontem": (today - timedelta(days=1), today - timedelta(days=1)),
            "Últimos 7 dias": (today - timedelta(days=6), today),
            "Esta semana": (today - timedelta(days=today.weekday()), today),
            "Semana passada": (today - timedelta(days=today.weekday() + 7), today - timedelta(days=today.weekday() + 1)),
            "Últimos 30 dias": (today - timedelta(days=29), today),
            "Este mês": (today.replace(day=1), today),
            "Mês passado": ((today.replace(day=1) - timedelta(days=1)).replace(day=1), today.replace(day=1) - timedelta(days=1)),
            "Últimos 90 dias": (today - timedelta(days=89), today),
            "Personalizado": None
        }
        
        selected_filter = st.sidebar.selectbox(
            "📅 Período:",
            options=list(filter_options.keys()),
            index=0  # Default: Todo o período
        )
        
        if filter_options[selected_filter] is not None:
            start_date, end_date = filter_options[selected_filter]
            # Ajustar datas para não exceder os limites dos dados
            start_date = max(start_date, min_date)
            end_date = min(end_date, max_date)
        else:
            # Filtro personalizado
            st.sidebar.markdown("**Período personalizado:**")
            date_range = st.sidebar.date_input(
                "Selecione o período:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            if len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date, end_date = min_date, max_date
        
        # Mostrar período selecionado
        st.sidebar.info(f"📅 **Período ativo:**\n{start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}")
        
        # Aplicar filtro de data primeiro
        data_filtered = data[
            (data['date'] >= start_date) & 
            (data['date'] <= end_date)
        ]
        
        # Filtro por Operador/Síndico (pluginConnectionLabel)
        if 'pluginConnectionLabel' in data_filtered.columns:
            st.sidebar.header("👤 Filtro por Operador")
            
            # Obter valores únicos da coluna pluginConnectionLabel
            unique_operators = sorted(data_filtered['pluginConnectionLabel'].dropna().unique())
            
            # Adicionar opção "Todos" no início
            operator_options = ["Todos"] + unique_operators
            
            # Selectbox para escolher o operador
            selected_operator = st.sidebar.selectbox(
                "🎯 Selecionar Operador:",
                options=operator_options,
                index=0  # Default: Todos
            )
            
            # Aplicar filtro por operador se não for "Todos"
            if selected_operator != "Todos":
                data_filtered = data_filtered[
                    data_filtered['pluginConnectionLabel'] == selected_operator
                ]
                st.sidebar.info(f"👤 **Operador ativo:** {selected_operator}")
        
        # Mostrar estatísticas do filtro
        total_sessions_original = len(data)
        total_sessions_filtered = len(data_filtered)
        
        if total_sessions_filtered != total_sessions_original:
            st.sidebar.metric(
                "Sessões no período",
                f"{total_sessions_filtered:,}",
                delta=f"{total_sessions_filtered - total_sessions_original:,}"
            )
        else:
            st.sidebar.metric("Total de Sessões", f"{total_sessions_filtered:,}")
            
    else:
        data_filtered = data
        st.sidebar.info("📋 Filtros de data não disponíveis - dados de data não encontrados")
        
        # Ainda assim, adicionar filtro por operador se disponível
        if 'pluginConnectionLabel' in data.columns:
            st.sidebar.header("👤 Filtro por Operador")
            
            # Obter valores únicos da coluna pluginConnectionLabel
            unique_operators = sorted(data['pluginConnectionLabel'].dropna().unique())
            
            # Adicionar opção "Todos" no início
            operator_options = ["Todos"] + unique_operators
            
            # Selectbox para escolher o operador
            selected_operator = st.sidebar.selectbox(
                "🎯 Selecionar Operador:",
                options=operator_options,
                index=0  # Default: Todos
            )
            
            # Aplicar filtro por operador se não for "Todos"
            if selected_operator != "Todos":
                data_filtered = data_filtered[
                    data_filtered['pluginConnectionLabel'] == selected_operator
                ]
                st.sidebar.info(f"👤 **Operador ativo:** {selected_operator}")
    
    # Análise Sindicompany como conteúdo principal
    st.header("🏢 Análise Sindicompany")
    
    if not data_filtered.empty:
        # Métricas principais Sindicompany
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_sessions_sindi = len(data_filtered)
            st.metric("Total de Sessões", f"{total_sessions_sindi:,}")
        
        with col2:
            if 'contactID' in data_filtered.columns:
                unique_contacts_sindi = data_filtered['contactID'].nunique()
                st.metric("Contatos Únicos", f"{unique_contacts_sindi:,}")
            else:
                st.metric("Contatos Únicos", "N/A")
        
        with col3:
            if '__sessionDuration' in data_filtered.columns:
                avg_duration_seconds = data_filtered['__sessionDuration'].mean()
                hours = int(avg_duration_seconds // 3600)
                minutes = int((avg_duration_seconds % 3600) // 60)
                seconds = int(avg_duration_seconds % 60)
                st.metric("Duração Média", f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                st.metric("Duração Média", "N/A")
        
        with col4:
            # Calcular tempo de espera usando __sessionQueueDuration
            if '__sessionQueueDuration' in data_filtered.columns:
                avg_queue_duration = data_filtered['__sessionQueueDuration'].mean()
                if pd.notna(avg_queue_duration) and avg_queue_duration > 0:
                    hours = int(avg_queue_duration // 3600)
                    minutes = int((avg_queue_duration % 3600) // 60)
                    seconds = int(avg_queue_duration % 60)
                    st.metric("Tempo de Espera Médio", f"{hours:02d}:{minutes:02d}:{seconds:02d}")
                else:
                    st.metric("Tempo de Espera Médio", "N/A")
            else:
                st.metric("Tempo de Espera Médio", "N/A")
        
        with col5:
            # Calcular indicador de Inatividade
            if 'closeMotive' in data_filtered.columns:
                inactivity_count = len(data_filtered[data_filtered['closeMotive'] == 'INACTIVITY'])
                total_sessions = len(data_filtered)
                inactivity_percentage = (inactivity_count / total_sessions * 100) if total_sessions > 0 else 0
                st.metric(
                    "Inatividade", 
                    f"{inactivity_count:,}", 
                    delta=f"{inactivity_percentage:.1f}%"
                )
            else:
                st.metric("Inatividade", "N/A")
        
        # Gráficos Sindicompany
        col1, col2 = st.columns(2)
        
        with col1:
            # Sessões por dia
            if 'date' in data_filtered.columns:
                daily_sessions_sindi = data_filtered.groupby('date').size().reset_index(name='count')
                fig_daily_sindi = px.bar(
                    daily_sessions_sindi, 
                    x='date', 
                    y='count',
                    title="Sessões por Dia",
                    labels={'count': 'Número de Sessões', 'date': 'Data'}
                )
                fig_daily_sindi.update_layout(height=400)
                st.plotly_chart(fig_daily_sindi, use_container_width=True)
            else:
                st.info("Dados de data não disponíveis")
        
        with col2:
            # Sessões por hora do dia
            if 'hour' in data_filtered.columns:
                hourly_sessions_sindi = data_filtered.groupby('hour').size().reset_index(name='count')
                fig_hourly_sindi = px.bar(
                    hourly_sessions_sindi,
                    x='hour',
                    y='count',
                    title="Sessões por Hora do Dia",
                    labels={'count': 'Número de Sessões', 'hour': 'Hora'}
                )
                fig_hourly_sindi.update_layout(height=400)
                st.plotly_chart(fig_hourly_sindi, use_container_width=True)
            else:
                st.info("Dados de hora não disponíveis")
        
        # Análise de síndicos
        if 'pluginConnectionLabel' in data_filtered.columns:
            st.subheader("👥 Síndicos Sindicompany")
            
            # Contar sessões por síndico incluindo tempo de espera
            operator_sessions = data_filtered.groupby('pluginConnectionLabel').agg({
                'sessionID': 'count',
                '__sessionDuration': 'mean',
                '__sessionQueueDuration': 'mean',
                '__sessionMessagesCount': 'mean'
            }).round(2)
            
            # Formatação da duração média em HH:MM:SS
            def format_duration(seconds):
                if pd.isna(seconds) or seconds <= 0:
                    return "N/A"
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                secs = int(seconds % 60)
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"
            
            operator_sessions['Duração Média'] = operator_sessions['__sessionDuration'].apply(format_duration)
            operator_sessions['Tempo de Espera Médio'] = operator_sessions['__sessionQueueDuration'].apply(format_duration)
            operator_sessions = operator_sessions[['sessionID', 'Duração Média', 'Tempo de Espera Médio', '__sessionMessagesCount']]
            operator_sessions.columns = ['Total de Sessões', 'Duração Média', 'Tempo de Espera Médio', 'Mensagens Média']
            operator_sessions = operator_sessions.sort_values('Total de Sessões', ascending=False)
            
            # Gráfico de pizza dos síndicos
            if len(operator_sessions) > 0:
                fig_operators = px.pie(
                    values=operator_sessions['Total de Sessões'],
                    names=operator_sessions.index,
                    title="Distribuição de Sessões por Síndico"
                )
                fig_operators.update_layout(height=400)
                st.plotly_chart(fig_operators, use_container_width=True)
            
            # Tabela de síndicos em linha separada
            st.markdown("**Detalhes dos Síndicos:**")
            
            # Configurar formatação da tabela com alinhamento à direita para colunas numéricas
            styled_table = operator_sessions.style.set_properties(**{
                'text-align': 'right'
            }, subset=['Duração Média', 'Tempo de Espera Médio']).set_properties(**{
                'text-align': 'center'
            }, subset=['Total de Sessões', 'Mensagens Média']).format({
                'Mensagens Média': '{:.2f}'
            })
            
            st.dataframe(
                styled_table,
                use_container_width=True
            )
        
        # Nova tabela: Sessões por dia do mês por síndico
        if 'date' in data_filtered.columns and 'pluginConnectionLabel' in data_filtered.columns:
            st.subheader("📅 Sessões por Dia do Mês por Síndico")
            
            # Criar cópia dos dados para evitar warnings
            temp_data = data_filtered.copy()
            temp_data['day'] = temp_data['date'].apply(lambda x: x.day)
            
            daily_operator_sessions = temp_data.groupby(['day', 'pluginConnectionLabel']).size().reset_index(name='sessions')
            
            # Criar pivot table
            pivot_table = daily_operator_sessions.pivot(index='day', columns='pluginConnectionLabel', values='sessions').fillna(0).astype(int)
            
            # Criar tabela de totais separadamente
            totals = pivot_table.sum()
            
            # Mostrar a tabela principal
            st.dataframe(
                pivot_table,
                use_container_width=True
            )
            
            # Mostrar totais em uma linha separada
            st.subheader("📊 Total de Sessões por Síndico")
            totals_df = pd.DataFrame([totals], index=['Total'])
            st.dataframe(
                totals_df,
                use_container_width=True
            )
            
            # Informações adicionais
            st.caption(f"📊 Tabela mostra o número de sessões por dia do mês para cada síndico.")
        
        # Análise por dia da semana
        if 'weekday' in data_filtered.columns:
            st.subheader("📅 Sessões por Dia da Semana")
            
            weekday_sessions_sindi = data_filtered.groupby('weekday').size().reindex([
                'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
            ]).reset_index(name='count')
            weekday_sessions_sindi['weekday_pt'] = weekday_sessions_sindi['weekday'].map({
                'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
                'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            })
            
            fig_weekday_sindi = px.bar(
                weekday_sessions_sindi,
                x='weekday_pt',
                y='count',
                title="Distribuição de Sessões por Dia da Semana",
                labels={'count': 'Número de Sessões', 'weekday_pt': 'Dia da Semana'}
            )
            fig_weekday_sindi.update_layout(height=400)
            st.plotly_chart(fig_weekday_sindi, use_container_width=True)
    
    else:
        st.info("📋 Dados Sindicompany não disponíveis")
    
    # Footer
    st.markdown("---")
    st.markdown("📊 Dashboard CX - Talqui | Dados atualizados em tempo real")

if __name__ == "__main__":
    main()