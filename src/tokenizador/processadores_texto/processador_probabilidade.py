
from pathlib import Path
import re
from src.tokenizador.processadores_texto.processador_texto_abs import ProcessadorTextoAbs

class ProcessadorProbabilidade(ProcessadorTextoAbs):
    def __init__(self, tamanho_max_token=5):
        super().__init__()
        self.__arquivo_tokens = Path('src/arquivos/dados_processamento/lista_tokens.csv')
        self.__cabecalho_lista_tokens = ['valor_hex', 'valor', 'quantidade', 'probabilidade']
        self.__tamanho_max_token = tamanho_max_token
        self.__setlist_tokens = set()
    
    def set_lista_tokens(self, novo_path:Path):
        self.__arquivo_tokens = novo_path
    
    @property
    def arquivo_lista_tokens(self):
        return self.__arquivo_tokens
    
    def processar_textos(self, texto:str)->bool:
        '''
        Método central que processa o texto, é pesado mas usa probabilidade para gerar os dados
        Params:
            - texto:str = Texto a ser processado
        Return:
            - bool = True se salvo ou false se ocorrer erro
        '''
        if not texto:
            return False
        
        lista_tokens = self.carregar_lista_tokens(self.__arquivo_tokens)

        # se não existir preenche a lista com os tokens iniciais (tamanho 1)
        for c in texto:
            c_hex = self.texto_para_hex(c)
            if c_hex not in self.__setlist_tokens:
                self.__setlist_tokens.add(c_hex)
                lista_tokens.append([c_hex, c, texto.count(c), self.__gerar_probabilidade(1)])
        
        #concatena e acha as novas probabilidades até o maximo definido
        for i in range(1, min(self.__tamanho_max_token, len(texto)),1):
            lista_tokens = self.__recalcular_probabilidade(lista_tokens, texto)
         
        return self.salvar_csv_tokens(path=self.__arquivo_tokens,
                                      tokens=lista_tokens,
                                      cabecalhos=self.__cabecalho_lista_tokens)
    
    def __recalcular_probabilidade(self, lista_tokens:list, texto:str)->dict:
        lista_sorted = sorted(lista_tokens,key=lambda linha: (-len(linha[1]), -linha[3]))
        try:
            for i in range(0,len(lista_sorted), 2):
                token_a = lista_sorted[i]
                token_b = lista_sorted[i+1]
                token_ab_hex = token_a[0]+token_b[0]
                token_ab = self.hex_para_texto(token_a[0])+self.hex_para_texto(token_b[0])
                count_ab = texto.count(token_ab)
                lista_tokens.append([token_ab_hex, token_ab, count_ab, self.__gerar_probabilidade(count_ab, token_a[2],token_b[2])])
        except IndexError:
            pass
        
        lista_sorted = sorted(lista_tokens,key=lambda linha: (-len(linha[1]), -linha[3]))
        print(lista_sorted)
        return lista_sorted

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
    
    def __gerar_dict_lista_tokens(self)->dict:
        '''
        Método que carrega o arquivo de tokens e gera o dicionario de trabalho
        Return:
            - dict= dicionario de token com {valor utf8, quantidade, probabilidade atual}
        '''
        lista = self.carregar_lista_tokens(self.__arquivo_tokens)
        dict_tokens ={}
        if not lista:
            return {}
        else:
            for l in lista:
                dict_tokens[l[0]] = {'valor':l[1], 'quantidade':l[2], 'probabilidade':l[3]}
        return dict_tokens
    
    def __transformar_dict_em_lista_tokens(self, lista_dict:dict)->list:
        '''
        Método que transforma o dicionario de trabalho em uma lista
        Return:
            - list= lista de token com [valor_hex, valor utf8, quantidade, probabilidade atual]
        '''
        lista_tokens = []
        for i in lista_dict.keys():
            lista_tokens.append([i,
                                 lista_dict[i]['valor'],
                                 lista_dict[i]['quantidade'],
                                 lista_dict[i]['probabilidade']])
        
        return lista_tokens