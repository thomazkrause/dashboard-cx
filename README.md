# 📊 Dashboard CX - Talqui

Dashboard interativo para análise de dados de Customer Experience (CX) da plataforma Talqui.

## 🚀 Funcionalidades

### 📈 Análises Disponíveis

- **Volume de Mensagens**: Análise temporal de mensagens por dia, hora e dia da semana
- **Performance dos Operadores**: Métricas de eficiência, avaliações e tempos de resposta
- **Tempos de Resposta**: Distribuição de tempos de fila e duração das sessões
- **Análise de Sessões**: Motivos de fechamento, status e distribuição de mensagens
- **Canais e Tipos**: Análise de tipos de mensagem e canais de comunicação

### 📊 Métricas Principais

- Total de mensagens e sessões
- Mensagens recebidas vs enviadas
- Avaliação média dos atendimentos
- Tempo médio de fila e resposta
- Performance individual dos operadores
- Análise de sentimento básica
- Padrões de uso por horário

## 📁 Estrutura do Projeto

```
dashboard-cx/
├── app.py                 # Aplicação principal Streamlit
├── data_processor.py      # Processamento e limpeza de dados
├── analytics.py          # Análises avançadas de CX
├── run.py                # Script para executar o dashboard
├── requirements.txt      # Dependências Python
├── README.md            # Este arquivo
└── data/               # Diretório com arquivos CSV
    ├── 2025-07-20T11_47_45+00_00_wa7m.csv  # Dados de mensagens
    ├── 2025-07-20T11_48_09+00_00_ssrb.csv  # Dados de sessões
    └── 2025-07-20T11_48_28+00_00_ry7w.csv  # Sessões com plugins
```

## 🛠️ Instalação e Execução

### Opção 1: Execução Rápida
```bash
cd dashboard-cx
python run.py --install
```

### Opção 2: Instalação Manual
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar dashboard
streamlit run app.py
```

### Opção 3: Usando o script run.py
```bash
python run.py
```

## 📋 Requisitos

- Python 3.7+
- Arquivos CSV no diretório `data/`
- Dependências listadas em `requirements.txt`

## 🔧 Dependências

- **streamlit**: Interface web interativa
- **pandas**: Manipulação e análise de dados
- **plotly**: Gráficos interativos
- **numpy**: Computação numérica
- **seaborn/matplotlib**: Visualizações estatísticas

## 📊 Dados Suportados

### Mensagens (wa7m.csv)
- IDs de tenant, contato, mensagem e sessão
- Direção da mensagem (inbound/outbound)
- Tipo de mensagem (text/file/event)
- Conteúdo e metadados
- Timestamps de criação e atualização

### Sessões (ssrb.csv)
- Informações de sessão e operador
- Tempos de fila, manual e total
- Avaliações dos clientes
- Motivos de fechamento
- Contadores de mensagens

### Sessões com Plugins (ry7w.csv)
- Dados de sessão com informações de canal
- Conexões de plugin
- Labels de conexão

## 🎯 Como Usar

1. **Acesse o Dashboard**: Abra http://localhost:8501 no navegador
2. **Configure Filtros**: Use a barra lateral para filtrar por período
3. **Explore as Abas**: 
   - Volume de Mensagens
   - Performance dos Operadores
   - Tempos de Resposta
   - Análise de Sessões
   - Canais e Tipos
4. **Interaja com os Gráficos**: Hover, zoom e filtros nos gráficos Plotly

## 📈 Análises Avançadas

### Performance dos Operadores
- Sessões por operador
- Tempo médio de atendimento
- Avaliações recebidas
- Eficiência (sessões/hora)
- Taxa de satisfação

### Padrões Temporais
- Horários de pico
- Distribuição por dia da semana
- Tendências ao longo do tempo
- Sazonalidade

### Análise de Sentimento
- Classificação básica de mensagens
- Palavras-chave de problemas
- Tendências de satisfação
- Alertas de insatisfação

### Jornada do Cliente
- Classificação de clientes (único, ocasional, regular, frequente)
- Tempo de relacionamento
- Padrões de engajamento

## 🔍 Insights Gerados

O dashboard gera automaticamente insights como:
- Operador melhor avaliado
- Operador mais eficiente
- Horários de maior demanda
- Percentual de sentimento negativo
- Distribuição de tipos de cliente

## 🚨 Solução de Problemas

### Erro: Arquivos não encontrados
- Verifique se os arquivos CSV estão no diretório `data/`
- Confirme os nomes dos arquivos

### Erro: Dependências não instaladas
- Execute: `python run.py --install`
- Ou: `pip install -r requirements.txt`

### Erro: Memória insuficiente
- Os arquivos são carregados em chunks para otimizar memória
- Para arquivos muito grandes, considere filtrar os dados primeiro

### Dashboard não carrega
- Verifique se a porta 8501 está livre
- Execute: `streamlit run app.py --server.port=8502` para usar outra porta

## 🔧 Customização

### Adicionar Novas Análises
1. Edite `analytics.py` para incluir novas funções
2. Adicione novos gráficos em `app.py`
3. Atualize as abas conforme necessário

### Modificar Visualizações
- Os gráficos usam Plotly - documentação: https://plotly.com/python/
- Cores e temas podem ser customizados nos objetos `fig`

### Filtros Adicionais
- Adicione novos filtros na barra lateral (`st.sidebar`)
- Aplique filtros aos dataframes antes de gerar gráficos

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a seção de solução de problemas
2. Consulte a documentação do Streamlit
3. Revise os logs no terminal

## 📄 Licença

Este projeto é para uso interno da equipe Talqui.

---

📊 **Dashboard CX - Talqui** | Análise de dados de Customer Experience em tempo real