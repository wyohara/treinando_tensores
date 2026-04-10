
from pathlib import Path
import json
import re
import pandas as pd
from tokenizador.arvore_trie import ArvoreTrie

class ControleArquivos:
    def __init__(self):
        self.__pasta_dataset = Path('src/arquivos/dataset')
        self.__arquivos_processados = Path('src/arquivos/dados_processamento/arquivos_processados.csv')        
    
    @property
    def pasta_dataset(self)->Path:
        return self.__pasta_dataset
    
    @property
    def arquivos_processados(self)->Path:
        return self.__arquivos_processados 
    
    def _set_pasta_dataset(self, caminho_novo:Path):
        self.__pasta_dataset = caminho_novo
    
    def _set_pasta_arquivos_processados(self, caminho_novo:Path):
        self.__arquivos_processados = caminho_novo   

    def _get_lista_arquivos_processados(self)->list:
        '''
        Recupera a lista de arquivos processados
        '''
        try:
            df = pd.read_csv(self.__arquivos_processados)
            lista_nomes = df[['nome', 'modelo_processamento']].values.tolist()
            return lista_nomes
        except FileNotFoundError:
            return []
        except pd.errors.EmptyDataError:
            return []
    
    def _carregar_dataset(self)->list[Path]:
        '''
        Método que recupera os arquivos do dataset
        '''
        arquivos_dataset = [f for f in self.__pasta_dataset.iterdir() if f.is_file()]

        resultado = []
        nomes_arquivos_processados = set()
        #montagem da lista de nomes de arquivos processados
        for arquivo_processado in self._get_lista_arquivos_processados(): 
            if arquivo_processado[1] == 'trie':
                nomes_arquivos_processados.add(arquivo_processado[0])

        #verificando qual arquivo foi processado
        for arquivo in arquivos_dataset:
            if arquivo.name not in nomes_arquivos_processados:
                resultado.append(arquivo)
        return resultado

    def _processar_textos(self, path_texto:Path = None):
        texto = path_texto.read_text(encoding='utf-8')
        return ArvoreTrie().processar_textos(texto)

    