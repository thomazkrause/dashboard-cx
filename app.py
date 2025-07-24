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
    """Carrega e processa os dados dos arquivos CSV"""
    try:
        # Carregar mensagens
        messages_file = "data/2025-07-20T11_47_45+00_00_wa7m.csv"
        if os.path.exists(messages_file):
            messages = pd.read_csv(messages_file, low_memory=False)
            # Converter datas com formato ISO8601
            messages['createdAt'] = pd.to_datetime(messages['createdAt'], format='ISO8601')
            messages['updatedAt'] = pd.to_datetime(messages['updatedAt'], format='ISO8601')
            # Adicionar colunas calculadas
            messages['date'] = messages['createdAt'].dt.date
            messages['hour'] = messages['createdAt'].dt.hour
            messages['weekday'] = messages['createdAt'].dt.day_name()
        else:
            messages = pd.DataFrame()
        
        # Carregar sessões com plugins para pluginConnectionLabel
        sessions_plugins_file = "data/2025-07-20T11_48_28+00_00_ry7w.csv"
        if os.path.exists(sessions_plugins_file):
            sessions_plugins = pd.read_csv(sessions_plugins_file, low_memory=False)
            # Converter datas com formato ISO8601
            date_columns = ['queuedAt', 'manualAt', 'closedAt', 'createdAt', 'updatedAt']
            for col in date_columns:
                if col in sessions_plugins.columns:
                    sessions_plugins[col] = pd.to_datetime(sessions_plugins[col], format='ISO8601', errors='coerce')
            
            # Adicionar coluna de data
            if 'createdAt' in sessions_plugins.columns:
                sessions_plugins['date'] = sessions_plugins['createdAt'].dt.date
                sessions_plugins['hour'] = sessions_plugins['createdAt'].dt.hour
        else:
            sessions_plugins = pd.DataFrame()
        
        # Carregar dados Sindicompany
        sindicompany_file = "data/[ Talqui ] Sindicompany - Data_Julho_15-22.csv"
        if os.path.exists(sindicompany_file):
            sindicompany = pd.read_csv(sindicompany_file, low_memory=False)
            # Converter datas
            date_columns = ['queuedAt', 'manualAt', 'closedAt', 'createdAt', 'updatedAt', 'sessionRatingAt']
            for col in date_columns:
                if col in sindicompany.columns:
                    sindicompany[col] = pd.to_datetime(sindicompany[col], errors='coerce')
            
            # Adicionar colunas derivadas
            if 'createdAt' in sindicompany.columns:
                sindicompany['date'] = sindicompany['createdAt'].dt.date
                sindicompany['hour'] = sindicompany['createdAt'].dt.hour
                sindicompany['weekday'] = sindicompany['createdAt'].dt.day_name()
        else:
            sindicompany = pd.DataFrame()
        
        return messages, sessions_plugins, sindicompany
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        st.info("💡 **Para usar no Streamlit Cloud**: Faça upload dos arquivos CSV para o repositório na pasta 'data/'")
        st.markdown("""
        **Arquivos necessários:**
        - `data/2025-07-20T11_47_45+00_00_wa7m.csv` (mensagens)
        - `data/2025-07-20T11_48_28+00_00_ry7w.csv` (sessões com plugins)
        - `data/[ Talqui ] Sindicompany - Data_Julho_15-22.csv` (dados Sindicompany)
        """)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def main():
    st.title("📊 Dashboard CX - Talqui")
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        messages, sessions_plugins, sindicompany = load_data()
    
    if messages.empty and sindicompany.empty:
        st.error("Não foi possível carregar os dados. Verifique se os arquivos CSV estão no diretório 'data/'")
        return
    
    # Sidebar com filtros de data para Sindicompany
    st.sidebar.header("📅 Filtros")
    
    # Filtro de data baseado nos dados Sindicompany
    if not sindicompany.empty and 'createdAt' in sindicompany.columns:
        min_date = sindicompany['createdAt'].min().date()
        max_date = sindicompany['createdAt'].max().date()
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
        
        # Aplicar filtro aos dados Sindicompany
        sindicompany_filtered = sindicompany[
            (sindicompany['date'] >= start_date) & 
            (sindicompany['date'] <= end_date)
        ]
        
        # Mostrar estatísticas do filtro
        total_sessions_original = len(sindicompany)
        total_sessions_filtered = len(sindicompany_filtered)
        
        if total_sessions_filtered != total_sessions_original:
            st.sidebar.metric(
                "Sessões no período",
                f"{total_sessions_filtered:,}",
                delta=f"{total_sessions_filtered - total_sessions_original:,}"
            )
        else:
            st.sidebar.metric("Total de Sessões", f"{total_sessions_filtered:,}")
            
    else:
        sindicompany_filtered = sindicompany
        st.sidebar.info("📋 Filtros não disponíveis - dados de data não encontrados")
    
    # Análise Sindicompany como conteúdo principal
    st.header("🏢 Análise Sindicompany")
    
    if not sindicompany_filtered.empty:
        # Métricas principais Sindicompany
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_sessions_sindi = len(sindicompany_filtered)
            st.metric("Total de Sessões", f"{total_sessions_sindi:,}")
        
        with col2:
            if 'contactID' in sindicompany_filtered.columns:
                unique_contacts_sindi = sindicompany_filtered['contactID'].nunique()
                st.metric("Contatos Únicos", f"{unique_contacts_sindi:,}")
            else:
                st.metric("Contatos Únicos", "N/A")
        
        with col3:
            if '__sessionDuration' in sindicompany_filtered.columns:
                avg_duration_seconds = sindicompany_filtered['__sessionDuration'].mean()
                hours = int(avg_duration_seconds // 3600)
                minutes = int((avg_duration_seconds % 3600) // 60)
                seconds = int(avg_duration_seconds % 60)
                st.metric("Duração Média", f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                st.metric("Duração Média", "N/A")
        
        # Gráficos Sindicompany
        col1, col2 = st.columns(2)
        
        with col1:
            # Sessões por dia
            if 'date' in sindicompany_filtered.columns:
                daily_sessions_sindi = sindicompany_filtered.groupby('date').size().reset_index(name='count')
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
            if 'hour' in sindicompany_filtered.columns:
                hourly_sessions_sindi = sindicompany_filtered.groupby('hour').size().reset_index(name='count')
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
        
        # Análise de operadores
        if 'pluginConnectionLabel' in sindicompany_filtered.columns:
            st.subheader("👥 Operadores Sindicompany")
            
            # Contar sessões por operador
            operator_sessions = sindicompany_filtered.groupby('pluginConnectionLabel').agg({
                'sessionID': 'count',
                '__sessionDuration': 'mean',
                '__sessionMessagesCount': 'mean'
            }).round(2)
            
            # Formatação da duração média em HH:MM:SS
            def format_duration(seconds):
                if pd.isna(seconds):
                    return "N/A"
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                secs = int(seconds % 60)
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"
            
            operator_sessions['Duração Média'] = operator_sessions['__sessionDuration'].apply(format_duration)
            operator_sessions = operator_sessions[['sessionID', 'Duração Média', '__sessionMessagesCount']]
            operator_sessions.columns = ['Total de Sessões', 'Duração Média', 'Mensagens Média']
            operator_sessions = operator_sessions.sort_values('Total de Sessões', ascending=False)
            
            # Layout em colunas
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Gráfico de pizza dos operadores
                if len(operator_sessions) > 0:
                    fig_operators = px.pie(
                        values=operator_sessions['Total de Sessões'],
                        names=operator_sessions.index,
                        title="Distribuição de Sessões por Operador"
                    )
                    fig_operators.update_layout(height=400)
                    st.plotly_chart(fig_operators, use_container_width=True)
            
            with col2:
                # Tabela de operadores
                st.markdown("**Detalhes dos Operadores:**")
                st.dataframe(
                    operator_sessions,
                    use_container_width=True
                )
        
        # Análise por dia da semana
        if 'weekday' in sindicompany_filtered.columns:
            st.subheader("📅 Sessões por Dia da Semana")
            
            weekday_sessions_sindi = sindicompany_filtered.groupby('weekday').size().reindex([
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