import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import re
from collections import Counter

class CXAnalytics:
    """Classe para análises avançadas de Customer Experience"""
    
    def __init__(self, messages_df, sessions_df):
        self.messages = messages_df
        self.sessions = sessions_df
    
    def operator_performance_analysis(self):
        """Análise detalhada de performance dos operadores"""
        if self.sessions.empty or 'operatorFirstname' not in self.sessions.columns:
            return None
        
        # Métricas por operador
        operator_metrics = self.sessions.groupby('operatorFirstname').agg({
            'sessionID': 'count',  # Total de sessões
            '__sessionDuration': ['mean', 'median', 'std'],  # Duração das sessões
            '__sessionQueueDuration': ['mean', 'median'],  # Tempo de fila
            '__sessionManualDuration': ['mean', 'median'],  # Tempo manual
            'sessionRatingStars': ['mean', 'count'],  # Avaliações
            '__sessionMessagesCount': ['sum', 'mean']  # Mensagens
        }).round(2)
        
        # Achatar colunas multi-nível
        operator_metrics.columns = [
            'total_sessions', 'avg_duration', 'median_duration', 'std_duration',
            'avg_queue_time', 'median_queue_time', 'avg_manual_time', 'median_manual_time',
            'avg_rating', 'total_ratings', 'total_messages', 'avg_messages_per_session'
        ]
        
        # Calcular eficiência (sessões por hora trabalhada)
        operator_metrics['efficiency_sessions_per_hour'] = (
            operator_metrics['total_sessions'] / 
            (operator_metrics['avg_duration'] / 3600)
        ).round(2)
        
        # Calcular satisfação do cliente (% de avaliações >= 4)
        satisfaction_rates = []
        for operator in operator_metrics.index:
            operator_sessions = self.sessions[self.sessions['operatorFirstname'] == operator]
            high_ratings = len(operator_sessions[operator_sessions['sessionRatingStars'] >= 4])
            total_ratings = len(operator_sessions[operator_sessions['sessionRatingStars'].notna()])
            satisfaction_rate = (high_ratings / total_ratings * 100) if total_ratings > 0 else 0
            satisfaction_rates.append(satisfaction_rate)
        
        operator_metrics['satisfaction_rate'] = satisfaction_rates
        
        return operator_metrics.sort_values('total_sessions', ascending=False)
    
    def response_time_analysis(self):
        """Análise de tempos de resposta por período"""
        if self.sessions.empty:
            return None
        
        # Análise por hora do dia
        hourly_response = self.sessions.groupby('hour').agg({
            '__sessionQueueDuration': ['mean', 'median', 'count'],
            '__sessionDuration': ['mean', 'median']
        }).round(2)
        
        # Análise por dia da semana
        weekly_response = self.sessions.groupby('weekday').agg({
            '__sessionQueueDuration': ['mean', 'median', 'count'],
            '__sessionDuration': ['mean', 'median']
        }).round(2)
        
        return {
            'hourly': hourly_response,
            'weekly': weekly_response
        }
    
    def message_sentiment_analysis(self):
        """Análise básica de sentimento das mensagens"""
        if self.messages.empty or 'messageValue' not in self.messages.columns:
            return None
        
        # Palavras indicativas de problemas/reclamações
        problem_keywords = [
            'problema', 'erro', 'falha', 'ruim', 'péssimo', 'terrível', 'horrível',
            'demora', 'lento', 'não funciona', 'quebrado', 'defeito', 'reclamação',
            'insatisfeito', 'cancelar', 'reembolso', 'devolver'
        ]
        
        # Palavras indicativas de satisfação
        positive_keywords = [
            'obrigado', 'obrigada', 'excelente', 'ótimo', 'perfeito', 'maravilhoso',
            'satisfeito', 'feliz', 'recomendo', 'parabéns', 'adorei', 'amei'
        ]
        
        # Analisar mensagens de entrada (dos clientes)
        inbound_messages = self.messages[
            (self.messages['messageDirection'] == 'inbound') & 
            (self.messages['messageValue'].notna())
        ].copy()
        
        if inbound_messages.empty:
            return None
        
        # Converter para lowercase para análise
        inbound_messages['message_lower'] = inbound_messages['messageValue'].str.lower()
        
        # Detectar sentimentos
        def detect_sentiment(text):
            if pd.isna(text):
                return 'neutral'
            
            problem_count = sum(1 for keyword in problem_keywords if keyword in text)
            positive_count = sum(1 for keyword in positive_keywords if keyword in text)
            
            if problem_count > positive_count:
                return 'negative'
            elif positive_count > problem_count:
                return 'positive'
            else:
                return 'neutral'
        
        inbound_messages['sentiment'] = inbound_messages['message_lower'].apply(detect_sentiment)
        
        # Estatísticas de sentimento
        sentiment_stats = inbound_messages['sentiment'].value_counts()
        sentiment_by_date = inbound_messages.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
        
        return {
            'overall': sentiment_stats,
            'by_date': sentiment_by_date,
            'sample_negative': inbound_messages[inbound_messages['sentiment'] == 'negative']['messageValue'].head(10).tolist()
        }
    
    def peak_hours_analysis(self):
        """Análise dos horários de pico"""
        if self.messages.empty:
            return None
        
        # Análise por hora
        hourly_volume = self.messages.groupby(['hour', 'messageDirection']).size().unstack(fill_value=0)
        
        # Identificar horários de pico
        total_hourly = hourly_volume.sum(axis=1)
        peak_threshold = total_hourly.quantile(0.8)  # Top 20%
        peak_hours = total_hourly[total_hourly >= peak_threshold].index.tolist()
        
        # Análise por dia da semana e hora
        heatmap_data = self.messages.groupby(['weekday_num', 'hour']).size().reset_index(name='volume')
        
        return {
            'hourly_volume': hourly_volume,
            'peak_hours': peak_hours,
            'heatmap_data': heatmap_data
        }
    
    def channel_efficiency_analysis(self):
        """Análise de eficiência por canal"""
        if self.messages.empty or 'messageChannel' not in self.messages.columns:
            return None
        
        # Métricas por canal
        channel_stats = self.messages.groupby('messageChannel').agg({
            'messageID': 'count',
            'sessionID': 'nunique',
            'contactID': 'nunique'
        }).rename(columns={
            'messageID': 'total_messages',
            'sessionID': 'unique_sessions',
            'contactID': 'unique_contacts'
        })
        
        # Calcular mensagens por sessão por canal
        channel_stats['messages_per_session'] = (
            channel_stats['total_messages'] / channel_stats['unique_sessions']
        ).round(2)
        
        return channel_stats.sort_values('total_messages', ascending=False)
    
    def resolution_pattern_analysis(self):
        """Análise de padrões de resolução"""
        if self.sessions.empty:
            return None
        
        # Análise por motivo de fechamento
        if 'closeMotive' in self.sessions.columns:
            close_motive_stats = self.sessions.groupby('closeMotive').agg({
                'sessionID': 'count',
                '__sessionDuration': 'mean',
                '__sessionMessagesCount': 'mean',
                'sessionRatingStars': 'mean'
            }).round(2)
            
            close_motive_stats.columns = [
                'total_sessions', 'avg_duration', 'avg_messages', 'avg_rating'
            ]
        else:
            close_motive_stats = None
        
        # Análise de sessões por duração
        if '__sessionDuration' in self.sessions.columns:
            duration_categories = pd.cut(
                self.sessions['__sessionDuration'] / 60,  # converter para minutos
                bins=[0, 5, 15, 30, 60, float('inf')],
                labels=['Muito Rápida (0-5min)', 'Rápida (5-15min)', 'Média (15-30min)', 
                       'Longa (30-60min)', 'Muito Longa (60min+)']
            )
            
            duration_analysis = pd.DataFrame({
                'category': duration_categories,
                'rating': self.sessions['sessionRatingStars']
            }).groupby('category')['rating'].agg(['count', 'mean']).round(2)
        else:
            duration_analysis = None
        
        return {
            'close_motives': close_motive_stats,
            'duration_analysis': duration_analysis
        }
    
    def customer_journey_analysis(self):
        """Análise da jornada do cliente"""
        if self.messages.empty:
            return None
        
        # Análise por contato
        contact_journey = self.messages.groupby('contactID').agg({
            'sessionID': 'nunique',  # Número de sessões
            'messageID': 'count',  # Total de mensagens
            'createdAt': ['min', 'max']  # Primeira e última interação
        })
        
        contact_journey.columns = [
            'total_sessions', 'total_messages', 'first_contact', 'last_contact'
        ]
        
        # Calcular duração do relacionamento
        contact_journey['relationship_days'] = (
            contact_journey['last_contact'] - contact_journey['first_contact']
        ).dt.days
        
        # Classificar clientes
        def classify_customer(row):
            if row['total_sessions'] == 1:
                return 'Único Contato'
            elif row['total_sessions'] <= 3:
                return 'Ocasional'
            elif row['total_sessions'] <= 10:
                return 'Regular'
            else:
                return 'Frequente'
        
        contact_journey['customer_type'] = contact_journey.apply(classify_customer, axis=1)
        
        # Estatísticas por tipo de cliente
        customer_type_stats = contact_journey.groupby('customer_type').agg({
            'total_sessions': 'mean',
            'total_messages': 'mean',
            'relationship_days': 'mean'
        }).round(2)
        
        return {
            'individual_journey': contact_journey,
            'customer_types': customer_type_stats,
            'type_distribution': contact_journey['customer_type'].value_counts()
        }
    
    def generate_insights_report(self):
        """Gera relatório com insights principais"""
        insights = []
        
        # Performance dos operadores
        operator_perf = self.operator_performance_analysis()
        if operator_perf is not None:
            best_operator = operator_perf.loc[operator_perf['avg_rating'].idxmax()]
            most_efficient = operator_perf.loc[operator_perf['efficiency_sessions_per_hour'].idxmax()]
            
            insights.append(f"🏆 Melhor avaliado: {best_operator.name} ({best_operator['avg_rating']:.1f}⭐)")
            insights.append(f"⚡ Mais eficiente: {most_efficient.name} ({most_efficient['efficiency_sessions_per_hour']:.1f} sessões/hora)")
        
        # Análise de sentimento
        sentiment = self.message_sentiment_analysis()
        if sentiment is not None:
            negative_pct = (sentiment['overall'].get('negative', 0) / sentiment['overall'].sum() * 100)
            insights.append(f"😟 {negative_pct:.1f}% das mensagens têm sentimento negativo")
        
        # Horários de pico
        peak_analysis = self.peak_hours_analysis()
        if peak_analysis is not None:
            peak_hours = peak_analysis['peak_hours']
            insights.append(f"📈 Horários de pico: {', '.join(map(str, peak_hours))}h")
        
        # Jornada do cliente
        journey = self.customer_journey_analysis()
        if journey is not None:
            frequent_customers = (journey['type_distribution'].get('Frequente', 0) / 
                                journey['type_distribution'].sum() * 100)
            insights.append(f"👥 {frequent_customers:.1f}% são clientes frequentes")
        
        return insights

# Função para criar gráficos avançados
def create_advanced_charts(analytics):
    """Cria gráficos avançados para análise"""
    charts = {}
    
    # Heatmap de atividade
    peak_data = analytics.peak_hours_analysis()
    if peak_data:
        heatmap_data = peak_data['heatmap_data']
        pivot_data = heatmap_data.pivot(index='weekday_num', columns='hour', values='volume')
        
        charts['activity_heatmap'] = px.imshow(
            pivot_data,
            title="Mapa de Calor: Atividade por Hora e Dia da Semana",
            labels={'x': 'Hora', 'y': 'Dia da Semana', 'color': 'Volume'},
            color_continuous_scale='Viridis'
        )
    
    # Gráfico de performance dos operadores
    operator_perf = analytics.operator_performance_analysis()
    if operator_perf is not None:
        charts['operator_scatter'] = px.scatter(
            x=operator_perf['avg_rating'],
            y=operator_perf['efficiency_sessions_per_hour'],
            size=operator_perf['total_sessions'],
            hover_name=operator_perf.index,
            title="Performance dos Operadores: Avaliação vs Eficiência",
            labels={'x': 'Avaliação Média', 'y': 'Eficiência (sessões/hora)'}
        )
    
    return charts