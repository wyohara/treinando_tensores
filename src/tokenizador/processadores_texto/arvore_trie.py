
import json
import os
import re
from pathlib import Path
from src.tokenizador.processadores_texto.processador_texto_abs import ProcessadorTestoAbs

class ArvoreTrie(ProcessadorTestoAbs):
    def __init__(self):
        self.__arquivo_json_arvore = Path('src/arquivos/dados_processamento/arvore_trie.json')     
        self.__arvore = {}
    
    @property
    def get_arquivo_json_arvore(self)->Path:
        return self.__arquivo_json_arvore
    
    def set_arquivo_json_arvore(self, path:Path):
        self.__arquivo_json_arvore = path
    
    def _get_arvore_trie(self)->dict:
        try:
            with self.__arquivo_json_arvore.open('r', encoding='utf-8') as arquivo:
                return json.load(arquivo)
        except FileNotFoundError:
            return {}
        except json.decoder.JSONDecodeError:
            return {}

    def salvar_arvore_trie(self, arvore:dict):
        if not arvore:
            return False      
        with self.__arquivo_json_arvore.open('w',encoding='utf-8') as arquivo:
            json.dump(arvore, arquivo, ensure_ascii=False, separators=(',', ':'))
            return True           

    @property
    def arvore(self):
        return self.__arvore

    def _processar_textos(self, texto:str):    
        """
        Método central que gerencia toda a criação da árvore de trier
        Percorre o corpus separando em palavras e aplica o processamento, após isso
        gera a chave que é transformada em tokens e salvo no banco de dados.
        Processa apenas a cópia da árvore original para manter a lógica dos tokens

        Params:
            texto: corpus do texto usado para tokenizar
            formato: formato de saída, pode ser utf-8 ou hex
        Returns:
            list[TokenObject]: lista de objetos tokens
        """
        arvore = self._get_arvore_trie()
        palavras =  re.findall(r'[^\s]+|\s+', texto)
        lista_palavras = []
        if not palavras:
            raise ValueError
        for palavra in palavras:
            lista_palavras.append(palavra)

        #aplicando o algoritmo ao texto e ordenando as palavras do maior para o menor
        for i, palavra in enumerate(sorted(lista_palavras, key=len, reverse=True)):
            arvore = self.__montar_arvore_trie(palavra=palavra, arvore=arvore)

        self.salvar_arvore_trie(arvore)
        return arvore

    def __montar_arvore_trie(self,  palavra:str, arvore:dict = {},contar_tokens=True) -> dict:
        """
        Método que monta a ávore de trie. Cria um dicionário onde a chave é cada caractere. 
        Caso a sequência de caracteres não exista é criada uma ramificação e a chave fim, 
        indicando o número de vezes que o contador passou pela bifurcação.

        Obs: 
            - A árvore precisa encontrar duas vezes o mesmo prefixo para bifurcar
            - Internamente o radical vira uma nova árvore
        
        Params:
            palavra: palavra processada que será usada na árvore
            arvore: ávore que será usada no processo
            contar_tokens: incrementa o contador de tokens

        Returns:
            arvore: a árvore inicial atualizada com os novos valores

        """
        no_atual = arvore
        raiz = True

        # cria o step do range, se for hex irá andar 2 bytes (1 char UNICODE) se utf-8 uma letra
        step = 1 
        for i in range(0,len(palavra), step):
            letra =  self.texto_para_hex((palavra[i:i+step]))

            # Cria o nó fim para uma bifurcação
            if letra not in no_atual and letra != ' ':
                # verifica se é raiz para não criar a chave fim no início da árvore
                if (len(no_atual.keys())==1 and not raiz):
                    no_atual['fim'] = 1
                no_atual[letra] = {}
            
            # incrementao contador de fim
            if ('fim' in no_atual.keys()) and contar_tokens:
                no_atual['fim'] += 1

            # Se for a última letra, marca como fim de palavra
            if i == len(palavra) - step:
                no_atual[letra]['fim'] = 1
            
            no_atual = no_atual[letra] #incrementa a árvore para o próximo nó
            raiz = False # marca como não sendo mais raiz
        return arvore

    def montar_lista_tokens(self) -> list:
        """
        A partir do dicionário da Trie, retorna uma lista de TokenObject
        Params:
            formato: formato do texto em 'utf-8' ou 'hex'
        
        Returns:
            list[token, quantidade_fim, tipo]: lista de objetos de token para salvar no bd
        """
        arvore = self._get_arvore_trie()

        pilha = [[arvore, ""]]  # (nó_atual, token)
        resposta =[]
        while pilha:
            no_atual, token = pilha.pop()
        
            # Primeiro, verifica se o nó atual tem 'fim' diretamente e zera os tokens
            if isinstance(no_atual, dict):          
                if 'fim' in no_atual:
                    #caso utf-8 retorna para texto o hexadecimal
                    resposta.append((token, no_atual['fim'], 'opcional'))
                    token = ''
                
                # Depois, processa os filhos (exceto 'fim')
                #amarrado com try, caso entre por acidente em uma chave 'fim'
                try:
                    for chave, valor in no_atual.items():
                        if chave != 'fim':
                            pilha.append((valor, token + chave)) 
                except AttributeError:
                    pass
        
        #extend para unir os tokens fixos e opcionais
        resposta.extend(self.definit_tokens_fixos())
        return resposta