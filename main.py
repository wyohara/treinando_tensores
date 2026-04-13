#!/usr/bin/env python3
from src.app import app

if __name__ == "__main__":
    try:
        import numpy
        import pytest
        import argparse
        import os
        
        # Biblioteca para verificar versões específicas
        from importlib.metadata import version
        
        # Versões requeridas
        REQUIRED_VERSIONS = {
            'numpy': '2.4.4',
            'pytest': '9.0.3',
            'pandas': '3.0.2',
        }
        
        # Verificar cada versão
        for package, versao in REQUIRED_VERSIONS.items():
            installed_version = version(package)
            if installed_version != versao:
                print(f"⚠️ Versão incorreta: {package}=={installed_version} (requer {versao})")
                print(f"Corrija com: pip install {package}=={versao}")
                exit(1)
                
    except ImportError as e:
        print(f"❌ Erro: Dependência faltando - {e}")

    finally:
        # Se chegou aqui, todas as dependências estão ok
        print("✅ Todas as dependências estão instaladas com as versões corretas!")
        for package, versao in REQUIRED_VERSIONS.items():
            print(f"   - {package}=={versao}")
        
        #=================================================================================
        #                               Código da Aplicação
        #=================================================================================
        
        # Aceitar também argumento posicional para conveniência:
        # python .\main.py -m teste ou python .\main.py --modo teste
        parser = argparse.ArgumentParser(description='Aprendendo Tensores')
        parser.add_argument('-m','--modo', nargs='?', default='normal', 
                        help='Modo de execução (normal, teste)')
        
        # Aceitar também argumento posicional para conveniência:
        # python .\main.py teste
        parser.add_argument('modo', 
                        nargs='?', 
                        default='normal',
                        help='Modo como argumento posicional')
        
        args = parser.parse_args()
        
        if args.modo == 'teste': # Executa em modo teste
            print("🔧 Executando em modo de teste...")
            os.system("py.test.exe -s -vv .\\src\\testes\\")
        else:
            app()