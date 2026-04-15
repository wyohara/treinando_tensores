
import json
import os
import re
import pandas as pd
from pathlib import Path
from src.tokenizador.processadores_texto.processador_texto_abs import ProcessadorTestoAbs

class ArvoreTrie(ProcessadorTestoAbs):
    def __init__(self):
        self.__arquivo_json_arvore = Path('src/arquivos/dados_processamento/arvore_trie.json')     
        self.__arquivo_css_tokens = Path('src/arquivos/dados_processamento/tokens.csv')     
    
    @property
    def get_arquivo_json_arvore(self)->Path:
        return self.__arquivo_json_arvore
    
    def set_arquivo_json_arvore(self, path:Path):
        self.__arquivo_json_arvore = path

    def set_arquivo_csv_tokens(self, path:Path):
        self.__arquivo_css_tokens = path

    @property
    def get_arquivo_csv_tokens(self)->Path:
        return self.__arquivo_css_tokens
    
    
    def get_arvore_trie(self)->dict:
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

    def processar_textos(self, texto:str):    
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
        arvore = self.get_arvore_trie()
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

    def __montar_arvore_trie(self,  palavra:str, arvore:dict = {}) -> dict:
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

        Returns:
            arvore: a árvore inicial atualizada com os novos valores

        """
        no_atual = arvore
        raiz = True

        # cria o step do range, se for hex irá andar 2 bytes (1 char UNICODE) se utf-8 uma letra
        step = 1 
        for i in range(0,len(palavra), step):
            letra =  self.texto_para_hex((palavra[i:i+step]))

            if 'fim' in no_atual:
                no_atual['fim']+=1

            # Se o nó para esta letra não existe, cria um novo dicionário
            if letra not in no_atual:
                if len(no_atual.keys()) >0:
                    if not raiz:
                        no_atual['fim'] = no_atual.get('fim', 1) + 1
                no_atual[letra] = {}

            # Desce para o nó filho (agora ele com certeza existe)
            no_atual = no_atual[letra]

            # Se for a última letra, marca como fim de palavra
            if i == len(palavra) - step:
                no_atual['fim'] = no_atual.get('fim', 0) + 1
            raiz = False
        return arvore

    def montar_lista_tokens(self) -> list:
        """
        A partir do dicionário da Trie, retorna uma lista de TokenObject
        Params:
            formato: formato do texto em 'utf-8' ou 'hex'
        
        Returns:
            list[token, quantidade_fim, tipo]: lista de objetos de token para salvar no bd
        """
        arvore = self.get_arvore_trie()

        pilha = [[arvore, ""]]  # (nó_atual, token)
        resposta =[]
        while pilha:
            no_atual, token = pilha.pop()
        
            # Primeiro, verifica se o nó atual tem 'fim' diretamente e zera os tokens
            if isinstance(no_atual, dict):          
                if 'fim' in no_atual:
                    #caso o token já exista nos tokens fixos é ignorado
                    if token not in self.get_set_valor_tokens_fixos():
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
        resposta.extend(self.gerar_tokens_fixos())
        self.salvar_csv_tokens(resposta)
        return resposta
    
    def salvar_csv_tokens(self, tokens:list[list]):
        if not tokens:
            return False
        try:
            df = pd.DataFrame(tokens, columns=['valor', 'quantidade', 'tipo'])
            df.to_csv(self.__arquivo_css_tokens, index=False, encoding='utf-8')
            return True
        except IndexError:
            pass
        return False

    
    def carregar_lista_tokens(self)->list:
        try:
            df = pd.read_csv(self.__arquivo_css_tokens)
            dados = df.values.tolist()
            return dados
        except pd.errors.EmptyDataError:
            return []
        except FileNotFoundError:
            return []
