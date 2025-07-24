#!/usr/bin/env python3
"""
Script para executar o Dashboard CX - Talqui

Uso:
    python run.py
    
ou para instalar dependências automaticamente:
    python run.py --install
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Instala as dependências necessárias"""
    print("📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def check_data_files():
    """Verifica se os arquivos de dados existem"""
    data_dir = Path("data")
    required_files = [
        "2025-07-20T11_47_45+00_00_wa7m.csv",
        "2025-07-20T11_48_09+00_00_ssrb.csv", 
        "2025-07-20T11_48_28+00_00_ry7w.csv"
    ]
    
    missing_files = []
    for file in required_files:
        if not (data_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Arquivos de dados não encontrados:")
        for file in missing_files:
            print(f"   - data/{file}")
        print("\n💡 Certifique-se de que os arquivos CSV estão no diretório 'data/'")
        return False
    
    print("✅ Todos os arquivos de dados encontrados!")
    return True

def run_streamlit():
    """Executa a aplicação Streamlit"""
    print("🚀 Iniciando Dashboard CX...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar dashboard: {e}")

def main():
    """Função principal"""
    print("=" * 50)
    print("📊 DASHBOARD CX - TALQUI")
    print("=" * 50)
    
    # Verificar argumentos
    if "--install" in sys.argv:
        if not install_requirements():
            sys.exit(1)
    
    # Verificar se streamlit está instalado
    try:
        import streamlit
    except ImportError:
        print("❌ Streamlit não encontrado. Instalando dependências...")
        if not install_requirements():
            sys.exit(1)
    
    # Verificar arquivos de dados
    if not check_data_files():
        sys.exit(1)
    
    # Mostrar informações
    print("\n📋 Informações do Dashboard:")
    print("   - URL: http://localhost:8501")
    print("   - Para parar: Ctrl+C")
    print("   - Logs: aparecerão abaixo")
    print("\n" + "=" * 50)
    
    # Executar dashboard
    run_streamlit()

if __name__ == "__main__":
    main()