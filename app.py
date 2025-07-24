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
    st.markdown("Dashboard para análise de dados de Customer Experience")
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        messages, sessions_plugins, sindicompany = load_data()
    
    if messages.empty and sindicompany.empty:
        st.error("Não foi possível carregar os dados. Verifique se os arquivos CSV estão no diretório 'data/'")
        return
    
    # Sidebar com filtros
    st.sidebar.header("📅 Filtros")
    
    # Filtro de data
    if not messages.empty:
        min_date = messages['createdAt'].min().date()
        max_date = messages['createdAt'].max().date()
        today = datetime.now().date()
        
        # Filtros predefinidos
        filter_options = {
            "Personalizado": None,
            "Hoje": (today, today),
            "Ontem": (today - timedelta(days=1), today - timedelta(days=1)),
            "Últimos 7 dias": (today - timedelta(days=6), today),
            "Esta semana": (today - timedelta(days=today.weekday()), today),
            "Semana passada": (today - timedelta(days=today.weekday() + 7), today - timedelta(days=today.weekday() + 1)),
            "Últimos 30 dias": (today - timedelta(days=29), today),
            "Este mês": (today.replace(day=1), today),
            "Mês passado": ((today.replace(day=1) - timedelta(days=1)).replace(day=1), today.replace(day=1) - timedelta(days=1)),
            "Últimos 90 dias": (today - timedelta(days=89), today),
            "Todo o período": (min_date, max_date)
        }
        
        selected_filter = st.sidebar.selectbox(
            "Período rápido:",
            options=list(filter_options.keys()),
            index=len(filter_options) - 1  # Default: Todo o período
        )
        
        if filter_options[selected_filter] is not None:
            start_date, end_date = filter_options[selected_filter]
            # Ajustar datas para não exceder os limites dos dados
            start_date = max(start_date, min_date)
            end_date = min(end_date, max_date)
        else:
            # Filtro personalizado
            date_range = st.sidebar.date_input(
                "Período personalizado:",
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
        
        # Aplicar filtros
        messages_filtered = messages[
            (messages['date'] >= start_date) & 
            (messages['date'] <= end_date)
        ]
        sessions_plugins_filtered = sessions_plugins[
            (sessions_plugins['date'] >= start_date) & 
            (sessions_plugins['date'] <= end_date)
        ] if not sessions_plugins.empty and 'date' in sessions_plugins.columns else sessions_plugins
    else:
        messages_filtered = messages
        sessions_plugins_filtered = sessions_plugins
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_messages = len(messages_filtered)
        st.metric("Total de Mensagens", f"{total_messages:,}")
    
    with col2:
        if not messages_filtered.empty and 'sessionID' in messages_filtered.columns:
            unique_sessions = messages_filtered['sessionID'].nunique()
            st.metric("Sessões Únicas", f"{unique_sessions:,}")
        else:
            st.metric("Sessões Únicas", "N/A")
    
    with col3:
        if not messages_filtered.empty:
            inbound_messages = len(messages_filtered[messages_filtered['messageDirection'] == 'inbound'])
            st.metric("Mensagens Recebidas", f"{inbound_messages:,}")
        else:
            st.metric("Mensagens Recebidas", "N/A")
    
    with col4:
        if not messages_filtered.empty and 'contactID' in messages_filtered.columns:
            unique_contacts = messages_filtered['contactID'].nunique()
            st.metric("Contatos Únicos", f"{unique_contacts:,}")
        else:
            st.metric("Contatos Únicos", "N/A")
    
    # Análise Sindicompany como conteúdo principal
    st.header("🏢 Análise Sindicompany")
    
    if not sindicompany.empty:
        # Métricas principais Sindicompany
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sessions_sindi = len(sindicompany)
            st.metric("Total de Sessões", f"{total_sessions_sindi:,}")
        
        with col2:
            if 'contactID' in sindicompany.columns:
                unique_contacts_sindi = sindicompany['contactID'].nunique()
                st.metric("Contatos Únicos", f"{unique_contacts_sindi:,}")
            else:
                st.metric("Contatos Únicos", "N/A")
        
        with col3:
            if 'sessionRatingStars' in sindicompany.columns:
                avg_rating = sindicompany['sessionRatingStars'].mean()
                st.metric("Avaliação Média", f"{avg_rating:.1f}⭐" if avg_rating > 0 else "N/A")
            else:
                st.metric("Avaliação Média", "N/A")
        
        with col4:
            if '__sessionDuration' in sindicompany.columns:
                avg_duration = sindicompany['__sessionDuration'].mean() / 60  # converter para minutos
                st.metric("Duração Média", f"{avg_duration:.1f} min")
            else:
                st.metric("Duração Média", "N/A")
        
        # Gráficos Sindicompany
        col1, col2 = st.columns(2)
        
        with col1:
            # Sessões por dia
            if 'date' in sindicompany.columns:
                daily_sessions_sindi = sindicompany.groupby('date').size().reset_index(name='count')
                fig_daily_sindi = px.line(
                    daily_sessions_sindi, 
                    x='date', 
                    y='count',
                    title="Sessões Sindicompany por Dia",
                    labels={'count': 'Número de Sessões', 'date': 'Data'}
                )
                fig_daily_sindi.update_layout(height=400)
                st.plotly_chart(fig_daily_sindi, use_container_width=True)
            else:
                st.info("Dados de data não disponíveis")
        
        with col2:
            # Motivos de fechamento
            if 'closeMotive' in sindicompany.columns:
                close_motives = sindicompany['closeMotive'].value_counts()
                fig_motives = px.pie(
                    values=close_motives.values,
                    names=close_motives.index,
                    title="Motivos de Fechamento"
                )
                fig_motives.update_layout(height=400)
                st.plotly_chart(fig_motives, use_container_width=True)
            else:
                st.info("Dados de motivos de fechamento não disponíveis")
        
        # Análise de operadores
        if 'pluginConnectionLabel' in sindicompany.columns:
            st.subheader("👥 Operadores Sindicompany")
            
            # Contar sessões por operador
            operator_sessions = sindicompany.groupby('pluginConnectionLabel').agg({
                'sessionID': 'count',
                '__sessionDuration': 'mean',
                'sessionRatingStars': 'mean',
                '__sessionMessagesCount': 'mean'
            }).round(2)
            
            operator_sessions.columns = ['Total de Sessões', 'Duração Média (seg)', 'Avaliação Média', 'Mensagens Média']
            operator_sessions = operator_sessions.sort_values('Total de Sessões', ascending=False)
            
            # Mostrar tabela de operadores
            st.dataframe(
                operator_sessions,
                use_container_width=True
            )
            
            # Gráfico de performance dos operadores
            if len(operator_sessions) > 1:
                fig_operators = px.bar(
                    x=operator_sessions.index,
                    y=operator_sessions['Total de Sessões'],
                    title="Sessões por Operador",
                    labels={'x': 'Operador', 'y': 'Total de Sessões'}
                )
                fig_operators.update_layout(height=400)
                fig_operators.update_xaxes(tickangle=45)
                st.plotly_chart(fig_operators, use_container_width=True)
        
        # Análise temporal detalhada
        if 'hour' in sindicompany.columns:
            st.subheader("⏰ Análise Temporal")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Sessões por hora
                hourly_sessions_sindi = sindicompany.groupby('hour').size().reset_index(name='count')
                fig_hourly_sindi = px.bar(
                    hourly_sessions_sindi,
                    x='hour',
                    y='count',
                    title="Sessões por Hora do Dia",
                    labels={'count': 'Número de Sessões', 'hour': 'Hora'}
                )
                fig_hourly_sindi.update_layout(height=400)
                st.plotly_chart(fig_hourly_sindi, use_container_width=True)
            
            with col2:
                # Sessões por dia da semana
                if 'weekday' in sindicompany.columns:
                    weekday_sessions_sindi = sindicompany.groupby('weekday').size().reindex([
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
                        title="Sessões por Dia da Semana",
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