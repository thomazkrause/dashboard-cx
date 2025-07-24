#!/usr/bin/env python3
"""
Script para testar o carregamento e processamento dos dados
"""

import pandas as pd
import os
from data_processor import DataProcessor
from analytics import CXAnalytics

def test_data_loading():
    """Testa o carregamento dos dados"""
    print("🔍 Testando carregamento de dados...")
    
    # Verificar se arquivos existem
    data_files = [
        "data/2025-07-20T11_47_45+00_00_wa7m.csv",
        "data/2025-07-20T11_48_09+00_00_ssrb.csv", 
        "data/2025-07-20T11_48_28+00_00_ry7w.csv"
    ]
    
    for file in data_files:
        if os.path.exists(file):
            size_mb = os.path.getsize(file) / (1024 * 1024)
            print(f"✅ {file} ({size_mb:.1f} MB)")
        else:
            print(f"❌ {file} não encontrado")
    
    # Testar carregamento
    print("\n📊 Carregando dados...")
    processor = DataProcessor()
    processor.load_all_data()
    
    # Mostrar estatísticas
    if processor.messages is not None and not processor.messages.empty:
        print(f"✅ Mensagens: {len(processor.messages):,} registros")
        print(f"   - Período: {processor.messages['createdAt'].min()} a {processor.messages['createdAt'].max()}")
        print(f"   - Contatos únicos: {processor.messages['contactID'].nunique():,}")
        print(f"   - Sessões únicas: {processor.messages['sessionID'].nunique():,}")
    else:
        print("❌ Falha ao carregar mensagens")
    
    if processor.sessions is not None and not processor.sessions.empty:
        print(f"✅ Sessões: {len(processor.sessions):,} registros")
        if 'operatorFirstname' in processor.sessions.columns:
            print(f"   - Operadores únicos: {processor.sessions['operatorFirstname'].nunique()}")
    else:
        print("❌ Falha ao carregar sessões")
    
    return processor

def test_analytics(processor):
    """Testa as análises"""
    print("\n🔬 Testando análises...")
    
    if processor.messages is None or processor.sessions is None:
        print("❌ Dados não carregados, pulando testes de análise")
        return
    
    analytics = CXAnalytics(processor.messages, processor.sessions)
    
    # Testar performance dos operadores
    print("📊 Testando análise de performance dos operadores...")
    operator_perf = analytics.operator_performance_analysis()
    if operator_perf is not None:
        print(f"   ✅ {len(operator_perf)} operadores analisados")
        print(f"   - Melhor avaliado: {operator_perf['avg_rating'].idxmax()} ({operator_perf['avg_rating'].max():.2f}⭐)")
    else:
        print("   ❌ Falha na análise de operadores")
    
    # Testar análise de sentimento
    print("😊 Testando análise de sentimento...")
    sentiment = analytics.message_sentiment_analysis()
    if sentiment is not None:
        total_analyzed = sentiment['overall'].sum()
        print(f"   ✅ {total_analyzed:,} mensagens analisadas")
        for sentiment_type, count in sentiment['overall'].items():
            pct = (count / total_analyzed * 100) if total_analyzed > 0 else 0
            print(f"   - {sentiment_type}: {count:,} ({pct:.1f}%)")
    else:
        print("   ❌ Falha na análise de sentimento")
    
    # Testar análise de horários de pico
    print("📈 Testando análise de horários de pico...")
    peak_analysis = analytics.peak_hours_analysis()
    if peak_analysis is not None:
        peak_hours = peak_analysis.get('peak_hours', [])
        print(f"   ✅ Horários de pico identificados: {peak_hours}")
    else:
        print("   ❌ Falha na análise de picos")
    
    # Testar insights
    print("💡 Testando geração de insights...")
    insights = analytics.generate_insights_report()
    if insights:
        print(f"   ✅ {len(insights)} insights gerados:")
        for insight in insights[:3]:  # Mostrar apenas os 3 primeiros
            print(f"   - {insight}")
    else:
        print("   ❌ Nenhum insight gerado")

def test_performance():
    """Testa a performance do carregamento"""
    print("\n⚡ Testando performance...")
    
    import time
    
    start_time = time.time()
    
    # Testar carregamento de mensagens (arquivo grande)
    messages_file = "data/2025-07-20T11_47_45+00_00_wa7m.csv"
    if os.path.exists(messages_file):
        print(f"📁 Carregando {messages_file}...")
        load_start = time.time()
        
        # Carregar apenas uma amostra para teste rápido
        sample_messages = pd.read_csv(messages_file, nrows=10000)
        
        load_time = time.time() - load_start
        print(f"   ✅ Amostra de 10.000 linhas carregada em {load_time:.2f}s")
        print(f"   - Colunas: {len(sample_messages.columns)}")
        print(f"   - Memória: {sample_messages.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
    
    total_time = time.time() - start_time
    print(f"⏱️ Teste total: {total_time:.2f}s")

def main():
    """Função principal de teste"""
    print("=" * 60)
    print("🧪 TESTE DO DASHBOARD CX - TALQUI")
    print("=" * 60)
    
    # Testar carregamento
    processor = test_data_loading()
    
    # Testar análises
    test_analytics(processor)
    
    # Testar performance
    test_performance()
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 60)
    print("\n💡 Para executar o dashboard:")
    print("   python run.py")
    print("\n📊 Para gerar relatórios estáticos:")
    print("   python batch_analysis.py")

if __name__ == "__main__":
    main()