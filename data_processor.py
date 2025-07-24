import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class DataProcessor:
    """Classe para processamento e limpeza dos dados de CX"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.messages = None
        self.sessions = None
        self.sessions_plugins = None
    
    def load_all_data(self):
        """Carrega todos os arquivos de dados"""
        self.messages = self.load_messages()
        self.sessions = self.load_sessions()
        self.sessions_plugins = self.load_sessions_plugins()
        return self
    
    def load_messages(self):
        """Carrega e processa dados de mensagens"""
        file_path = os.path.join(self.data_dir, "2025-07-20T11_47_45+00_00_wa7m.csv")
        
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            return pd.DataFrame()
        
        try:
            # Carregar com chunks para arquivos grandes
            chunks = []
            chunk_size = 10000
            
            for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
                chunks.append(chunk)
            
            df = pd.concat(chunks, ignore_index=True)
            
            # Processamento dos dados
            df = self._process_messages(df)
            
            print(f"Mensagens carregadas: {len(df):,} registros")
            return df
            
        except Exception as e:
            print(f"Erro ao carregar mensagens: {str(e)}")
            return pd.DataFrame()
    
    def load_sessions(self):
        """Carrega e processa dados de sessões"""
        file_path = os.path.join(self.data_dir, "2025-07-20T11_48_09+00_00_ssrb.csv")
        
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path, low_memory=False)
            df = self._process_sessions(df)
            
            print(f"Sessões carregadas: {len(df):,} registros")
            return df
            
        except Exception as e:
            print(f"Erro ao carregar sessões: {str(e)}")
            return pd.DataFrame()
    
    def load_sessions_plugins(self):
        """Carrega dados de sessões com plugins"""
        file_path = os.path.join(self.data_dir, "2025-07-20T11_48_28+00_00_ry7w.csv")
        
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path, low_memory=False)
            df = self._process_sessions_plugins(df)
            
            print(f"Sessões com plugins carregadas: {len(df):,} registros")
            return df
            
        except Exception as e:
            print(f"Erro ao carregar sessões com plugins: {str(e)}")
            return pd.DataFrame()
    
    def _process_messages(self, df):
        """Processa dados de mensagens"""
        # Converter datas com formato ISO8601
        date_columns = ['createdAt', 'updatedAt']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='ISO8601', errors='coerce')
        
        # Adicionar colunas derivadas
        if 'createdAt' in df.columns:
            df['date'] = df['createdAt'].dt.date
            df['hour'] = df['createdAt'].dt.hour
            df['minute'] = df['createdAt'].dt.minute
            df['weekday'] = df['createdAt'].dt.day_name()
            df['weekday_num'] = df['createdAt'].dt.weekday
            df['month'] = df['createdAt'].dt.month
            df['day'] = df['createdAt'].dt.day
        
        # Limpar dados de mensagem
        if 'messageValue' in df.columns:
            df['message_length'] = df['messageValue'].str.len()
            df['has_content'] = df['messageValue'].notna() & (df['messageValue'] != '')
        
        # Categorizar tipos de mensagem
        if 'messageKey' in df.columns:
            df['message_category'] = df['messageKey'].map({
                'text': 'Texto',
                'file': 'Arquivo',
                'event': 'Evento',
                'image': 'Imagem',
                'audio': 'Áudio',
                'video': 'Vídeo'
            }).fillna('Outro')
        
        return df
    
    def _process_sessions(self, df):
        """Processa dados de sessões"""
        # Converter datas com formato ISO8601
        date_columns = ['queuedAt', 'manualAt', 'closedAt', 'createdAt', 'updatedAt', 'sessionRatingAt']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='ISO8601', errors='coerce')
        
        # Adicionar colunas derivadas
        if 'createdAt' in df.columns:
            df['date'] = df['createdAt'].dt.date
            df['hour'] = df['createdAt'].dt.hour
            df['weekday'] = df['createdAt'].dt.day_name()
        
        # Calcular tempos
        if 'queuedAt' in df.columns and 'manualAt' in df.columns:
            df['response_time_minutes'] = (df['manualAt'] - df['queuedAt']).dt.total_seconds() / 60
        
        if 'createdAt' in df.columns and 'closedAt' in df.columns:
            df['total_session_time_minutes'] = (df['closedAt'] - df['createdAt']).dt.total_seconds() / 60
        
        # Converter durações de segundos para minutos
        duration_columns = ['__sessionDuration', '__sessionQueueDuration', '__sessionManualDuration']
        for col in duration_columns:
            if col in df.columns:
                df[f"{col}_minutes"] = df[col] / 60
        
        # Categorizar avaliações
        if 'sessionRatingStars' in df.columns:
            df['rating_category'] = pd.cut(
                df['sessionRatingStars'], 
                bins=[0, 2, 3, 4, 5], 
                labels=['Ruim', 'Regular', 'Bom', 'Excelente'],
                include_lowest=True
            )
        
        return df
    
    def _process_sessions_plugins(self, df):
        """Processa dados de sessões com plugins"""
        # Converter datas com formato ISO8601
        date_columns = ['queuedAt', 'manualAt', 'closedAt', 'createdAt', 'updatedAt']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='ISO8601', errors='coerce')
        
        # Adicionar colunas derivadas
        if 'createdAt' in df.columns:
            df['date'] = df['createdAt'].dt.date
            df['hour'] = df['createdAt'].dt.hour
            df['weekday'] = df['createdAt'].dt.day_name()
        
        return df
    
    def get_summary_stats(self):
        """Retorna estatísticas resumidas dos dados"""
        stats = {}
        
        if self.messages is not None and not self.messages.empty:
            stats['messages'] = {
                'total': len(self.messages),
                'date_range': (
                    self.messages['createdAt'].min(),
                    self.messages['createdAt'].max()
                ),
                'inbound': len(self.messages[self.messages['messageDirection'] == 'inbound']),
                'outbound': len(self.messages[self.messages['messageDirection'] == 'outbound']),
                'unique_contacts': self.messages['contactID'].nunique(),
                'unique_sessions': self.messages['sessionID'].nunique()
            }
        
        if self.sessions is not None and not self.sessions.empty:
            stats['sessions'] = {
                'total': len(self.sessions),
                'avg_duration_minutes': self.sessions['__sessionDuration'].mean() / 60 if '__sessionDuration' in self.sessions.columns else None,
                'avg_queue_time_minutes': self.sessions['__sessionQueueDuration'].mean() / 60 if '__sessionQueueDuration' in self.sessions.columns else None,
                'avg_rating': self.sessions['sessionRatingStars'].mean() if 'sessionRatingStars' in self.sessions.columns else None,
                'unique_operators': self.sessions['operatorFirstname'].nunique() if 'operatorFirstname' in self.sessions.columns else None
            }
        
        return stats
    
    def export_processed_data(self, output_dir="processed_data"):
        """Exporta dados processados para arquivos CSV"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if self.messages is not None and not self.messages.empty:
            self.messages.to_csv(os.path.join(output_dir, "messages_processed.csv"), index=False)
            print(f"Mensagens exportadas para {output_dir}/messages_processed.csv")
        
        if self.sessions is not None and not self.sessions.empty:
            self.sessions.to_csv(os.path.join(output_dir, "sessions_processed.csv"), index=False)
            print(f"Sessões exportadas para {output_dir}/sessions_processed.csv")
        
        if self.sessions_plugins is not None and not self.sessions_plugins.empty:
            self.sessions_plugins.to_csv(os.path.join(output_dir, "sessions_plugins_processed.csv"), index=False)
            print(f"Sessões com plugins exportadas para {output_dir}/sessions_plugins_processed.csv")

# Exemplo de uso
if __name__ == "__main__":
    processor = DataProcessor()
    processor.load_all_data()
    
    # Mostrar estatísticas
    stats = processor.get_summary_stats()
    print("\n=== ESTATÍSTICAS DOS DADOS ===")
    for data_type, data_stats in stats.items():
        print(f"\n{data_type.upper()}:")
        for key, value in data_stats.items():
            print(f"  {key}: {value}")
    
    # Exportar dados processados
    processor.export_processed_data()