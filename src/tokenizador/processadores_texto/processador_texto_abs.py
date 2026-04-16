from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path

def tokens_fixos():
    # Total de 125 tokens fixos
    tokens = [',', '?', '!', '{', '}', '[', ']', '(', ')', ';', '_', '/', '|', '@', '#', '\'', '’', '"', '”', '-', '—', '...', '.',# Originais (sem duplicar com os que vêm depois)
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',# Letras minúsculas
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',# Letras maiúsculas
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',# Números                  
                '+', '*', '%', '**', '//', # Operadores aritméticos
                '==', '!=', '<', '>', '<=', '>=',# Operadores de comparação
                'and', 'or', 'not',# Operadores lógicos
                '=', '+=', '-=', '*=', '/=', '%=', '**=', '//=',# Operadores de atribuição
                '&', '^', '~', '<<', '>>',# Operadores bitwise
                ':', '$', '`',# Símbolos e pontuação (apenas os que não estão nos originais)
                '->', ':='# Outros operadores
                '\n', ' ', '\t'# Espaçadores
            ]
    for i in range(len(tokens)):
        tokens[i] = tokens[i].encode('utf-8').hex()
    return tokens

TOKENS = tokens_fixos()


class ProcessadorTextoAbs(ABC):
    def __init__(self):
        self.__arquivo_tokens = None

    @staticmethod
    def gerar_tokens_fixos()->list:
        resposta = []
        for tk in TOKENS:
            resposta.append([(tk), 0, 'fixo'])
        return resposta

    @staticmethod
    def get_set_valor_tokens_fixos():
        return set(TOKENS)

    @staticmethod
    def texto_para_hex(texto:str):
        if type(texto)== str:
            return texto.encode('utf-8').hex()
        else:
            raise TypeError
    
    @staticmethod
    def hex_para_texto(texto_hex):
        return bytes.fromhex(texto_hex).decode('utf-8',errors='surrogateescape')
    
    @abstractmethod
    def processar_textos(self, texto:str)->bool:
        pass

    
    def salvar_csv_tokens(self, path:Path, tokens:list[list], cabecalhos:list[str]):
        if not tokens:
            return False  # Sem dados
        
        num_colunas = len(cabecalhos)
        
        # Verifica se todas as linhas têm o número correto de colunas
        for i, linha in enumerate(tokens):
            if len(linha) != len(cabecalhos):
                raise ValueError
        
        try:
            # Cria DataFrame diretamente (sem copiar desnecessariamente)
            df = pd.DataFrame(tokens, columns=cabecalhos)
            
            # Garante que o diretório existe
            path.parent.mkdir(parents=True, exist_ok=True)
            # Salva CSV
            df.to_csv(str(path), index=False, encoding='utf-8')
            return True
            
        except (OSError, PermissionError, IOError) as e:
            return False
        
    def carregar_lista_tokens(self, path:Path)->list:
        try:
            df = pd.read_csv(str(path))
            dados = df.values.tolist()
            return dados
        except pd.errors.EmptyDataError:
            return []
        except FileNotFoundError:
            return []
