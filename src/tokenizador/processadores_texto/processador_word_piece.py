
from pathlib import Path
import re
import pandas as pd
import numpy as np

from src.ferramentas.medidores import wrapper_timer
from src.tokenizador.processadores_texto.processador_texto_abs import ProcessadorTextoAbs

class ProcessadorWordPiece(ProcessadorTextoAbs):
    def __init__(self, tamanho_max_token=5):
        super().__init__()
        self.__arquivo_lista_tokens = Path('src/arquivos/dados_processamento/lista_tokens.csv')
        self.__cabecalho_lista_tokens = ['ab_hex', 'quantidade_ab', 'probabilidade', 'tk_a_hex', 'tk_b_hex', 'processado']
        self.__lista_token = pd.DataFrame()
        self.__tamanho_max_token = tamanho_max_token
        self.__setlist_tokens = set()
    
    def set_arquivo_tokens(self, novo_path:Path):
        self.__arquivo_lista_tokens = novo_path
    
    @property
    def arquivo_lista_tokens(self):
        return self.__arquivo_lista_tokens
    
    def processar_textos(self, texto:str)->bool:
        '''
        Método central que processa o texto, é pesado mas usa probabilidade para gerar os dados
        Params:
            - texto:str = Texto a ser processado
        Return:
            - bool = True se salvo ou false se ocorrer erro
        '''
        if not texto: # se não houver texto retorna false
            return False
        
        self._carregar_dados() # carrega o csv e a set() de indice
        df = self.__lista_token
        
        # percorre cada caractere
        for i, c in enumerate(texto):
            c_hex = self.texto_para_hex(c)
            if i >0:
                # caso tenha palavras anteriores adiciona o marcador ##
                c_hex=f'##{c_hex}'
            
            count_tk = texto.count(c)
            self.__adicionar_token(c_hex, count_tk, '-', '-')

        self.__calcular_repeticoes(texto)

        self.__lista_token['processado'] = False
        return self.salvar_csv_tokens(self.__arquivo_lista_tokens,
                                      self.__ordenar_lista_tokens().values.tolist(),
                                      self.__cabecalho_lista_tokens)
    
    def __calcular_repeticoes(self,texto:str)->bool:
        '''
        Percorre as letras das palavras adicionando a contagem aos tokens
        Params:
            palavra:str = palavra a ser adicionada
            texto:str = texto a ser processado
        Return:
            bool = True se ocorrer sem problemas
        '''
        df = self.__lista_token
        MAX_SIZE =  min(self.__tamanho_max_token, len(texto))

        for i in range(MAX_SIZE): #percorre até concatenar no tamanho máximo
            print(f">>>> Calculando a repetição {i}")
            for id_a, row_a in df.iterrows():
                for id_b, row_b in df.iterrows():
                    if '##' in df.loc[id_b, 'ab_hex']: #o segundo token precisa ter "##", ou seja tem letras antes
                        token_novo = df.loc[id_a, 'ab_hex']+df.loc[id_b, 'ab_hex'].replace("#","")
                        count_tk = texto.count(self.hex_para_texto(token_novo))           

                        #verifica se o token é menor que o tamanho máximo e ocorre no texto             
                        if len(self.hex_para_texto(token_novo))<= MAX_SIZE:
                            self.__adicionar_token(token_novo, count_tk, id_a, id_b)

                self.salvar_csv_tokens(self.__arquivo_lista_tokens,
                                      self.__ordenar_lista_tokens(reset=True).values.tolist(),
                                      self.__cabecalho_lista_tokens)
        
    

    def __adicionar_token(self, token_novo:str, count_tk:int, token_a:str, token_b:str):        
        df = self.__lista_token

        if count_tk>0:
            #se existir na lista atualiza senão adiciona
            if token_novo not in set(df.index):
                df.loc[token_novo]=[token_novo, count_tk, 1.0, token_a, token_b, True]
            else:
                if  not df.loc[token_novo, 'processado']:
                    df.loc[token_novo, 'quantidade_ab'] += count_tk
                    df.loc[token_novo, 'processado'] = True

    
    def __gerar_probabilidade(self, freq_ab:int=0, freq_a:int=0, freq_b:int=0)->float:
        '''
        Método que calcula a probabilidade. usa freq_ab/freq_a*freq_b
        Param:
            - freq_ab:int = ocorrencia do token ab juntos
            - freq_a: inf = ocorrencia do token a
            - freq_b: int = ocorrencia do token b
        
        Return:
            - float: valor da probabilidade
        
        Raises:
            - ZeroDivisionError: caso divida por zero retorna 1.0
        '''
        prob = 1.0
        try:
            prob = freq_ab/(freq_a*freq_b)
            return prob
        except ZeroDivisionError:
            return prob
    
    def _carregar_dados(self):
        '''
        Método inicial que carrega os dados do csv e gera:
            - set() __setlist_tokens
            - dados em forma de lista
        '''
        try:
            #carrega o csv e define a primeira coluna como índice
            df = pd.read_csv(str(self.__arquivo_lista_tokens))
            df = df.set_index(df.columns[0], drop=False)
            df['processado'] = False
            self.__lista_token = df
            return df.values.tolist()
        
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=self.__cabecalho_lista_tokens)
            df = df.set_index(df.columns[0], drop=False)
            self.__lista_token = df

        except FileNotFoundError:
            df = pd.DataFrame(columns=self.__cabecalho_lista_tokens)
            df = df.set_index(df.columns[0], drop=False)
            self.__lista_token = df
    
    def __ordenar_lista_tokens(self, reset=False) -> pd.DataFrame:
        #ordena por probabilidade, se for igual por quantidade e por ultimo tamanho do texto
        self.__lista_token = self.__lista_token.reset_index(drop=True)
        self.__lista_token = self.__lista_token.sort_values(by=['probabilidade', 'quantidade_ab', 'ab_hex'], ascending=[False, False, False],
                                                     key=lambda col: col.str.len() if col.name == 'ab_hex' else col)
        
        self.__lista_token = self.__lista_token.set_index(self.__lista_token.columns[0], drop=False)
        if reset:            
            self.__lista_token ['processado'] = False
        return self.__lista_token 
    
    def montar_lista_tokens(self,quantidade=100) -> list[str,int,str, int]:
        df = pd.read_csv(str(self.__arquivo_lista_tokens), nrows=quantidade)
        df['id'] = np.arange(1, len(df)+1)   # 1,2,3...
        lista_tokens = df[['ab_hex', 'quantidade_ab', 'id']].values.tolist()

        lista_final = []
        for l in lista_tokens:
            lista_final.append([l[0],l[1], 'hex',l[2]])
        return lista_final