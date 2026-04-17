
from pathlib import Path
import json
import re
import pandas as pd
import time
from src.ferramentas.medidores import wrapper_timer
from src.tokenizador.processadores_texto.processador_word_piece import ProcessadorWordPiece

class ControleArquivos:
    def __init__(self):
        self.__pasta_dataset = Path('src/arquivos/dataset')
        self.__arquivos_processados = Path('src/arquivos/dados_processamento/arquivos_processados.csv')     
        self.__processador_textos = ProcessadorWordPiece()   
    
    @property
    def get_pasta_dataset(self)->Path:
        return self.__pasta_dataset
    
    @property
    def get_path_arquivos_processados(self)->Path:
        return self.__arquivos_processados 
    
    def set_pasta_dataset(self, path_novo:Path):
        self.__pasta_dataset = path_novo
    
    def set_pasta_arquivos_processados(self, path_novo:Path):
        self.__arquivos_processados = path_novo   

    def _get_lista_arquivos_processados(self)->list:
        '''
        Recupera a lista de arquivos processados em formato de lista de 2 colunas

        Return:
            List [['nome', 'modelo_processamento']]: lista de dados

        Excepts:
            FileNotFoundError -> []: Não encontra o arquivo.
            pd.errors.EmptyDataError -> []: Arquivo sem nenhum dado.
        '''
        try:
            df = pd.read_csv(self.__arquivos_processados)
            lista_nomes = df[['nome', 'modelo_processamento']].values.tolist()
            return lista_nomes
        except FileNotFoundError:
            return []
        except pd.errors.EmptyDataError:
            return []
    
    def _salvar_texto_processado(self, nome_texto:str, modelo_processamento:str)->list:
        '''
        Salva o texto depois de processado
        Params:
            nome_texto str: nome do arquivo de texto processado
            modelo_processamento str: modelo de processamento de texto usado
        Return:
            List [['nome', 'modelo_processamento']]: lista de dados

        Excepts:
            FileNotFoundError -> []: Não encontrao arquivo.
            pd.errors.EmptyDataErro -> []: Arquivo sem nenhum dado.
        ''' 
        try:
            df = pd.read_csv(self.__arquivos_processados)
            nova_linha = pd.DataFrame({'nome': [nome_texto], 'modelo_processamento': [modelo_processamento]})
            df = pd.concat([df, nova_linha], ignore_index=True)
            # Salva o CSV
            df.to_csv(self.__arquivos_processados, index=False, encoding='utf-8')
        except FileNotFoundError:
            df = pd.DataFrame({'nome': [nome_texto], 'modelo_processamento': [modelo_processamento]})
            df.to_csv(self.get_path_arquivos_processados, index=False, encoding='utf-8')
        return self._get_lista_arquivos_processados()

    def _carregar_lista_arquivos_dataset(self)->list[Path]:
        '''
        Método que recupera a lista de Path dos arquivos do dataset

        Return:
            list[Path]: lista dos caminhos de todos os datasets, processado ou não
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

    def processar_textos(self, ):
        '''
        Método que processa os textos

        Params:
            path_test Path: Path opcional para teste, se houver ele processa o texto no path
                            Se não houver, ele carrega todos os datasets.
        
        return:
            list[token, quantidade_fim, tipo, id]: lista de tokens do texto processado
        '''        
        
        datasets = self._carregar_lista_arquivos_dataset()
        #processa todos os textos que não estão na lista de processados
        for dt in datasets:
            texto = dt.read_text(encoding='utf-8')            
            self.__processador_textos.processar_textos(texto)
            #salvando o arquivo
            self._salvar_texto_processado(str(dt.name), 'trie')
        return self.__processador_textos.montar_lista_tokens()
    
    def salvar_tokens(self, tokens:list):
        '''
        Método salva os tokens

        Params:
            list[token, quantidade_fim, tipo, id]: lista de tokens do texto processado
        '''        
        if len(tokens[0]) == 4: #caso o número de tokens não bata com o esperado
            return self.__processador_textos.salvar_csv_tokens(tokens)
        else:
            raise IndexError
