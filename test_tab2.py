#!/usr/bin/env python3
"""
Teste unitário para verificar a aba Volume de Sessões
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px

def test_sessions_tab():
    """Testa a lógica da aba Volume de Sessões"""
    
    print("🧪 Iniciando teste da aba Volume de Sessões...")
    
    # Criar dados de teste simulando sessions_filtered
    np.random.seed(42)
    
    # Gerar datas de teste
    dates = [datetime.now().date() - timedelta(days=i) for i in range(30)]
    
    # Criar DataFrame de teste
    test_data = []
    for date in dates:
        # Simular várias sessões por dia
        num_sessions = np.random.randint(10, 50)
        for _ in range(num_sessions):
            hour = np.random.randint(8, 20)  # Horário comercial
            weekday = date.strftime('%A')
            status = np.random.choice(['closed', 'open', 'pending'], p=[0.7, 0.2, 0.1])
            
            test_data.append({
                'date': date,
                'hour': hour,
                'weekday': weekday,
                'sessionStatus': status
            })
    
    sessions_filtered = pd.DataFrame(test_data)
    
    print(f"✅ Dados de teste criados: {len(sessions_filtered)} sessões")
    
    # Teste 1: Sessões por dia
    try:
        daily_sessions = sessions_filtered.groupby('date').size().reset_index(name='count')
        fig_daily = px.line(
            daily_sessions, 
            x='date', 
            y='count',
            title="Sessões por Dia",
            labels={'count': 'Número de Sessões', 'date': 'Data'}
        )
        print("✅ Teste 1 - Gráfico sessões por dia: PASSOU")
    except Exception as e:
        print(f"❌ Teste 1 - Gráfico sessões por dia: FALHOU - {e}")
        return False
    
    # Teste 2: Sessões por hora
    try:
        hourly_sessions = sessions_filtered.groupby('hour').size().reset_index(name='count')
        fig_hourly = px.bar(
            hourly_sessions,
            x='hour',
            y='count',
            title="Sessões por Hora do Dia",
            labels={'count': 'Número de Sessões', 'hour': 'Hora'}
        )
        print("✅ Teste 2 - Gráfico sessões por hora: PASSOU")
    except Exception as e:
        print(f"❌ Teste 2 - Gráfico sessões por hora: FALHOU - {e}")
        return False
    
    # Teste 3: Status das sessões
    try:
        status_counts = sessions_filtered['sessionStatus'].value_counts()
        fig_direction = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Distribuição: Status das Sessões"
        )
        print("✅ Teste 3 - Gráfico status das sessões: PASSOU")
    except Exception as e:
        print(f"❌ Teste 3 - Gráfico status das sessões: FALHOU - {e}")
        return False
    
    # Teste 4: Sessões por dia da semana
    try:
        weekday_sessions = sessions_filtered.groupby('weekday').size().reindex([
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ]).reset_index(name='count')
        weekday_sessions['weekday_pt'] = weekday_sessions['weekday'].map({
            'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
            'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        })
        
        fig_weekday = px.bar(
            weekday_sessions,
            x='weekday_pt',
            y='count',
            title="Sessões por Dia da Semana",
            labels={'count': 'Número de Sessões', 'weekday_pt': 'Dia da Semana'}
        )
        print("✅ Teste 4 - Gráfico sessões por dia da semana: PASSOU")
    except Exception as e:
        print(f"❌ Teste 4 - Gráfico sessões por dia da semana: FALHOU - {e}")
        return False
    
    # Verificar se há dados válidos
    print(f"\n📊 Estatísticas dos dados de teste:")
    print(f"   - Total de sessões: {len(sessions_filtered)}")
    print(f"   - Período: {sessions_filtered['date'].min()} a {sessions_filtered['date'].max()}")
    print(f"   - Status únicos: {sessions_filtered['sessionStatus'].unique()}")
    print(f"   - Horários: {sessions_filtered['hour'].min()}h a {sessions_filtered['hour'].max()}h")
    
    print("\n🎉 Todos os testes da aba Volume de Sessões PASSARAM!")
    return True

if __name__ == "__main__":
    test_sessions_tab()