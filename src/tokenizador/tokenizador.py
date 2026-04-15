from src.tokenizador.controle_arquivos import ControleArquivos
import pandas as pd
from pathlib import Path
from typing import Optional

class Tokenizador():

    def __init__(self):
        self.__arquivo_css_tokens = Path('src/arquivos/dados_processamento/tokens.csv')
        self.__df = pd.DataFrame()
        self.__tokenizador = {}
        
        self.__carregar_csv()

    def set_arquivo_csv_tokens(self, path:Path):
        self.__arquivo_css_tokens = path

    def gerar_tokens(self, quantidade=0)->dict:
        #se não houver tokens para carregar é reprocessado o dataset
        if self.__df.empty:
            controle_arquivos = ControleArquivos()
            lista_tokens = controle_arquivos.processar_textos()
            controle_arquivos.salvar_csv_tokens(lista_tokens)

        return self.__gerar_tokenizador(self.__df, quantidade)
    
    def __gerar_tokenizador(self, df:pd.DataFrame, quantidade:int)->dict:
            dict_tokens ={}
            df_fixo = df[df['tipo'] == 'fixo'].values.tolist()
            #adicionando os tokens fixos
            for i, token in enumerate(df_fixo):
                dict_tokens[token[0]]={'quantidade':token[1], 'tipo':token[2]}

            if quantidade<0: #caso quantidade zero retorna vazio
                dict_tokens = {}
            elif quantidade-len(df_fixo)<=0: # #caso quantidade menor que tokens fixos, retorna os tokens fixos
                pass
            elif quantidade>len(df): # caso quantidade maior que o total possível é lançado index error
                raise IndexError
            else:# nos demais casos monta o dicionário até o valor que falta para atingir a quantidade
                df_opcional = df[df['tipo'] == 'opcional'].sort_values('quantidade', ascending=False).values.tolist()
                
                cont=0
                while(len(dict_tokens.keys())<quantidade):
                    token = df_opcional[cont]
                    dict_tokens[token[0]]={'quantidade':token[1], 'tipo':token[2]}
                    cont+=1

            #salva como tokenizador
            self.__tokenizador = dict_tokens
            return dict_tokens

    @property
    def total_tokens_possiveis(self):
        return len(self.__df)

    def __carregar_csv(self)->pd.DataFrame:
        try:
            df = pd.read_csv(self.__arquivo_css_tokens)
            self.__df = df
        except pd.errors.EmptyDataError:
            pass
        except FileNotFoundError:
            pass
