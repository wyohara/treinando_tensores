from src.tokenizador.controle_arquivos import ControleArquivos
import pandas as pd
from pathlib import Path
from typing import Optional

class Tokenizador():

    def __init__(self):
        self.__arquivo_css_tokens = Path('src/arquivos/dados_processamento/tokens.csv')
        self.__df = pd.DataFrame()
        self.__tokenizador = {}
        self.__rev_tokenizador = {}
        
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

    
    def __tamanho_maior_token(self, tokenizador)->int:
        maior_chave= max(tokenizador.keys(), key=len)
        return len(bytes.fromhex(maior_chave).decode('utf-8',errors='surrogateescape'))
    
    def tokenizar_texto(self, tokenizador:dict, texto:str)->list:
        texto_tokenizado = []
        while(len(texto)>0):
            for i in range(min(self.__tamanho_maior_token(tokenizador), len(texto)),0,-1):
                texto_hex = texto[:i].encode('utf-8').hex()
                if texto_hex in self.__tokenizador.keys():
                    texto_tokenizado.append(self.__tokenizador[texto_hex]['id'])
                    texto = texto[i:]
        return texto_tokenizado
    
    def reverter_tokenizacao(self, lista_tokens:int, concatenar=False, utf8=False)->Optional:
        token_revertido = []
        for token_id in lista_tokens:
            token_utf8 = self.__rev_tokenizador[token_id]['valor']
            if utf8:
                token_utf8 = bytes.fromhex(token_utf8).decode('utf-8',errors='surrogateescape')
            token_revertido.append(token_utf8)
        
        texto_concatenado = ''
        if concatenar:
            for i in token_revertido:
                texto_concatenado +=i
            return texto_concatenado
        return token_revertido
    
    def __gerar_tokenizador(self, df:pd.DataFrame, quantidade:int)->dict:
            self.__rev_tokenizador = {}
            self.__tokenizador  ={}
            df_fixo = df[df['tipo'] == 'fixo'].values.tolist()
            #adicionando os tokens fixos
            
            for i, token in enumerate(df_fixo):
                self.__tokenizador [token[0]]={'quantidade':token[1], 'tipo':token[2], 'id':token[3]}
                self.__rev_tokenizador[token[3]] = {'quantidade':token[1], 'tipo':token[2], 'valor':token[0]}

            if quantidade<0: #caso quantidade zero retorna vazio
                self.__tokenizador = {}
                self.__rev_tokenizador = {}
            elif quantidade-len(df_fixo)<=0: # #caso quantidade menor que tokens fixos, retorna os tokens fixos
                pass
            elif quantidade>len(df): # caso quantidade maior que o total possível é lançado index error
                raise IndexError
            else:# nos demais casos monta o dicionário até o valor que falta para atingir a quantidade
                # Filtrar apenas opcionais e ordenar
                df_filtrado = df[df['tipo'] == 'opcional'].copy()
                df_opcional = (
                    df_filtrado.assign(comprimento=df_filtrado['valor'].str.len())         # coluna auxiliar comprimento de 'valor'
                    .sort_values(['quantidade', 'comprimento'], ascending=[False, False])  # ordenar
                    .drop('comprimento', axis=1)                                           # remove a coluna auxiliar
                )
                for i, token in enumerate(df_opcional.values.tolist()):
                    if i>=(quantidade-len(df_fixo)):
                        break
                    self.__tokenizador [token[0]]={'quantidade':token[1], 'tipo':token[2], 'id':token[3]}
                    self.__rev_tokenizador[token[3]] = {'quantidade':token[1], 'tipo':token[2], 'valor':token[0]}

            #salva como tokenizador
            return self.__tokenizador 

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
