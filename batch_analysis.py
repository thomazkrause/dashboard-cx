#!/usr/bin/env python3
"""
Análise em batch dos dados de CX - gera relatórios estáticos
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data_processor import DataProcessor
from analytics import CXAnalytics
import os
from datetime import datetime

def create_static_reports():
    """Cria relatórios estáticos em HTML e imagens"""
    
    print("📊 Iniciando análise em batch...")
    
    # Carregar dados
    processor = DataProcessor()
    processor.load_all_data()
    
    if processor.messages is None or processor.messages.empty:
        print("❌ Não foi possível carregar os dados")
        return
    
    # Criar diretório de relatórios
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Criar analytics
    analytics = CXAnalytics(processor.messages, processor.sessions)
    
    # Gerar insights
    insights = analytics.generate_insights_report()
    
    # Criar relatório HTML
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relatório CX - Talqui</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #1f77b4; color: white; padding: 20px; border-radius: 10px; }}
            .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .insight {{ background: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Relatório CX - Talqui</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
    """
    
    # Estatísticas gerais
    stats = processor.get_summary_stats()
    
    html_report += "<h2>📈 Estatísticas Gerais</h2>"
    
    if 'messages' in stats:
        msg_stats = stats['messages']
        html_report += f"""
        <div class="metric">
            <h3>Mensagens</h3>
            <ul>
                <li>Total: {msg_stats['total']:,}</li>
                <li>Período: {msg_stats['date_range'][0]} a {msg_stats['date_range'][1]}</li>
                <li>Recebidas: {msg_stats['inbound']:,}</li>
                <li>Enviadas: {msg_stats['outbound']:,}</li>
                <li>Contatos únicos: {msg_stats['unique_contacts']:,}</li>
                <li>Sessões únicas: {msg_stats['unique_sessions']:,}</li>
            </ul>
        </div>
        """
    
    if 'sessions' in stats:
        sess_stats = stats['sessions']
        html_report += f"""
        <div class="metric">
            <h3>Sessões</h3>
            <ul>
                <li>Total: {sess_stats['total']:,}</li>
                <li>Duração média: {sess_stats['avg_duration_minutes']:.1f} min</li>
                <li>Tempo médio de fila: {sess_stats['avg_queue_time_minutes']:.1f} min</li>
                <li>Avaliação média: {sess_stats['avg_rating']:.2f}⭐</li>
                <li>Operadores únicos: {sess_stats['unique_operators']}</li>
            </ul>
        </div>
        """
    
    # Insights principais
    html_report += "<h2>🎯 Insights Principais</h2>"
    for insight in insights:
        html_report += f'<div class="insight">{insight}</div>'
    
    # Performance dos operadores
    operator_perf = analytics.operator_performance_analysis()
    if operator_perf is not None:
        html_report += "<h2>👥 Performance dos Operadores</h2>"
        html_report += operator_perf.to_html(classes="table")
    
    # Análise de sentimento
    sentiment = analytics.message_sentiment_analysis()
    if sentiment is not None:
        html_report += "<h2>😊 Análise de Sentimento</h2>"
        html_report += f"""
        <div class="metric">
            <h3>Distribuição de Sentimentos</h3>
            <ul>
                <li>Positivo: {sentiment['overall'].get('positive', 0):,}</li>
                <li>Neutro: {sentiment['overall'].get('neutral', 0):,}</li>
                <li>Negativo: {sentiment['overall'].get('negative', 0):,}</li>
            </ul>
        </div>
        """
        
        if 'sample_negative' in sentiment and sentiment['sample_negative']:
            html_report += "<h3>Exemplos de Mensagens Negativas</h3><ul>"
            for msg in sentiment['sample_negative'][:5]:
                html_report += f"<li>{msg[:100]}...</li>"
            html_report += "</ul>"
    
    # Fechar HTML
    html_report += """
        <div style="margin-top: 50px; text-align: center; color: #666;">
            <p>📊 Dashboard CX - Talqui | Relatório gerado automaticamente</p>
        </div>
    </body>
    </html>
    """
    
    # Salvar relatório HTML
    html_file = os.path.join(reports_dir, f"relatorio_cx_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"📄 Relatório HTML salvo: {html_file}")
    
    # Criar gráficos estáticos
    create_static_charts(processor, analytics, reports_dir)
    
    print("✅ Análise em batch concluída!")
    print(f"📁 Arquivos salvos em: {reports_dir}/")

def create_static_charts(processor, analytics, output_dir):
    """Cria gráficos estáticos usando matplotlib/seaborn"""
    
    plt.style.use('seaborn-v0_8')
    
    # 1. Volume de mensagens por dia
    if not processor.messages.empty:
        plt.figure(figsize=(12, 6))
        daily_volume = processor.messages.groupby('date').size()
        plt.plot(daily_volume.index, daily_volume.values, marker='o')
        plt.title('Volume de Mensagens por Dia')
        plt.xlabel('Data')
        plt.ylabel('Número de Mensagens')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'volume_diario.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 2. Mensagens por hora
    if not processor.messages.empty:
        plt.figure(figsize=(12, 6))
        hourly_volume = processor.messages.groupby('hour').size()
        plt.bar(hourly_volume.index, hourly_volume.values)
        plt.title('Distribuição de Mensagens por Hora')
        plt.xlabel('Hora do Dia')
        plt.ylabel('Número de Mensagens')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'volume_por_hora.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 3. Performance dos operadores
    operator_perf = analytics.operator_performance_analysis()
    if operator_perf is not None:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Sessões por operador
        operator_perf['total_sessions'].plot(kind='bar', ax=ax1)
        ax1.set_title('Total de Sessões por Operador')
        ax1.set_ylabel('Número de Sessões')
        
        # Avaliação média
        operator_perf['avg_rating'].plot(kind='bar', ax=ax2, color='green')
        ax2.set_title('Avaliação Média por Operador')
        ax2.set_ylabel('Avaliação (1-5)')
        
        # Tempo médio de sessão
        (operator_perf['avg_duration'] / 60).plot(kind='bar', ax=ax3, color='orange')
        ax3.set_title('Duração Média das Sessões (minutos)')
        ax3.set_ylabel('Minutos')
        
        # Taxa de satisfação
        operator_perf['satisfaction_rate'].plot(kind='bar', ax=ax4, color='blue')
        ax4.set_title('Taxa de Satisfação (%)')
        ax4.set_ylabel('Porcentagem')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'performance_operadores.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 4. Heatmap de atividade
    peak_data = analytics.peak_hours_analysis()
    if peak_data and 'heatmap_data' in peak_data:
        plt.figure(figsize=(15, 8))
        heatmap_data = peak_data['heatmap_data']
        pivot_data = heatmap_data.pivot(index='weekday_num', columns='hour', values='volume')
        
        # Mapear números para nomes dos dias
        day_names = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 
                    4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
        pivot_data.index = [day_names.get(i, i) for i in pivot_data.index]
        
        sns.heatmap(pivot_data, annot=False, cmap='YlOrRd', cbar_kws={'label': 'Volume de Mensagens'})
        plt.title('Mapa de Calor: Atividade por Hora e Dia da Semana')
        plt.xlabel('Hora do Dia')
        plt.ylabel('Dia da Semana')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'heatmap_atividade.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 5. Distribuição de tempos de resposta
    if not processor.sessions.empty and '__sessionQueueDuration' in processor.sessions.columns:
        plt.figure(figsize=(12, 6))
        queue_times = processor.sessions['__sessionQueueDuration'].dropna() / 60  # minutos
        
        plt.subplot(1, 2, 1)
        plt.hist(queue_times, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Distribuição do Tempo de Fila')
        plt.xlabel('Tempo (minutos)')
        plt.ylabel('Frequência')
        
        plt.subplot(1, 2, 2)
        plt.boxplot(queue_times)
        plt.title('Box Plot - Tempo de Fila')
        plt.ylabel('Tempo (minutos)')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'tempos_resposta.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    print("📊 Gráficos estáticos criados com sucesso!")

if __name__ == "__main__":
    create_static_reports()