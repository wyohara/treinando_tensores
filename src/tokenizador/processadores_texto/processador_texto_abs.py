from abc import ABC, abstractmethod

TOKENS = [',', '?', '!', '{', '}', '[', ']', '(', ')', ';', '_', '/', '|', '@', '#', '\'', '’', '"', '”', '-', '—', '...', '.',# Originais (sem duplicar com os que vêm depois)
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',# Letras minúsculas
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',# Letras maiúsculas
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',# Números                  
            '+', '-', '*', '/', '%', '**', '//', # Operadores aritméticos
            '==', '!=', '<', '>', '<=', '>=',# Operadores de comparação
            'and', 'or', 'not',# Operadores lógicos
            '=', '+=', '-=', '*=', '/=', '%=', '**=', '//=',# Operadores de atribuição
            '&', '|', '^', '~', '<<', '>>',# Operadores bitwise
            ':', ';', '@', '$', '`', ' ',# Símbolos e pontuação (apenas os que não estão nos originais)
            '->', ':='# Outros operadores
            '\n', ' ', '\t'# Espaçadores
        ]

class ProcessadorTestoAbs(ABC):

    @staticmethod
    def definit_tokens_fixos()->list:
        resposta = []
        for tk in TOKENS:
            resposta.append([tk, 0, 'fixo'])
        return resposta

    @staticmethod
    def texto_para_hex(texto:str):
        if type(texto)== str:
            return texto.encode('utf-8').hex()
        else:
            raise TypeError
    
    @staticmethod
    def hex_para_texto(texto_hex):
        return bytes.fromhex(texto_hex).decode('utf-8',errors='surrogateescape')