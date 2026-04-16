
import json
import os
import re
import pandas as pd
from pathlib import Path
from src.tokenizador.processadores_texto.processador_texto_abs import ProcessadorTextoAbs

class ArvoreTrie(ProcessadorTextoAbs):
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
    
    def _get_arvore_trie(self)->dict:
        try:
            with self.__arquivo_json_arvore.open('r', encoding='utf-8') as arquivo:
                return json.load(arquivo)
        except FileNotFoundError:
            return {}
        except json.decoder.JSONDecodeError:
            return {}

    def __salvar_arvore_trie(self, arvore:dict):
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
        arvore = self._get_arvore_trie() #carrega a árvore de trie se existir
        palavras =  re.findall(r'[^\s]+|\s+', texto) # faz slice usando espaço

        if not palavras: #se não houver palavras lança index error
            raise ValueError

        #aplicando o algoritmo ao texto e ordenando as palavras do maior para o menor
        for i, palavra in enumerate(sorted(palavras, key=len, reverse=True)):
            arvore = self.__montar_arvore_trie(palavra=palavra, arvore=arvore)

        self.__salvar_arvore_trie(arvore)
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
            if 'ramo' in no_atual:
                no_atual['ramo']+=1

            # Se o nó para esta letra não existe, cria um novo dicionário
            if letra not in no_atual :
                if len(no_atual.keys()) >0 and i != len(palavra) - step:
                    if not raiz:
                        no_atual['ramo'] = no_atual.get('ramo', 1) + 1
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
            list[token, quantidade_fim, tipo, id]: lista de objetos de token para salvar no bd
        """
        arvore = self._get_arvore_trie()
        pilha = [(arvore, "")]  # (nó_atual, token_acumulado, posicao_inicio_token_atual)

        lista_posicoes = []
        resposta_lista = []
        while pilha:
            no_atual, token_hex = pilha.pop()
            
            if not isinstance(no_atual, dict):
                continue
                
            # Processa 'fim' se existir no nó atual
            if 'ramo' in no_atual:
                valor_fim = no_atual['ramo']
                token = self.hex_para_texto(token_hex)
                lista_posicoes.append([len(token)-1, valor_fim])
            
            if (no_atual.keys()) == {'fim'}: 
                valor_fim = no_atual['fim']
                token = self.hex_para_texto(token_hex)
                lista_posicoes.append([len(token)-1, valor_fim])
                #caso ache um dicionário que é folha - somente com {'fim'}
                resposta_lista = self.__recortar_posicoes_tokens_da_lista(lista_posicoes,
                                                                    token,
                                                                    no_atual['fim'])
                
            # Adiciona filhos (exceto 'fim') à pilha
            for chave, valor in no_atual.items():
                if chave != 'fim':
                    novo_token = token_hex + chave
                    pilha.append((valor, novo_token))
                else:
                    lista_posicoes.append([len(token_hex), valor_fim])

        #adiciona os tokens fixos
        resultado = self.gerar_tokens_fixos()
        resultado.extend(resposta_lista)
        #salva os tokens
        self.salvar_csv_tokens(resultado)
        return resultado

    def __recortar_posicoes_tokens_da_lista(self, 
                                            lista_posicoes,
                                            palavra,
                                            quant_no_folha) -> list[str, int, str]:
        '''
        Método acessório de 'montar_lista_tokens', ele cria a lista das combinações de tokens possíveis e salva em uma lista, além de adicionar os tokens fixos
        Params:
            - lista_posicoes list[int,int]: lista com cada linha contendo a posição do token dentro da palavra final e a quantidade de vezes que ocorreu
            - palavra: palavra encontrada após chegar ao nó folha da árvore
            - quant_no_folha: número de vezes que o nó folha foi alcançado na árvore
        '''
        print(lista_posicoes)
        resposta_dict = {}
        # cria o primeiro token que é a palavra completa
        resposta_dict[palavra] = [quant_no_folha, 'opcional'] 
        #percorre as posicoes para criar os tokens possíveis
        for chave_i in lista_posicoes:
            for chave_f in lista_posicoes:
                #garante que a chave inicial é menor que a final
                if (chave_i[0]<=chave_f[0]) and chave_f[0]<=len(palavra):
                    tk_candidato = palavra[chave_i[0]:chave_f[0]]                    
                    #verifica se o trecho não é token fixo
                    if tk_candidato not in self.get_set_valor_tokens_fixos():
                        #verifica se o trecho não esta repetido
                        if tk_candidato not in resposta_dict.keys():
                            resposta_dict[tk_candidato] = [chave_f[1], 'opcional']
                            print(chave_i[0], chave_f[0],tk_candidato, palavra)
                        #se repetido usa a maior quantidade
                        else:
                            if resposta_dict[tk_candidato][0]<chave_f[1]:
                                resposta_dict[tk_candidato][0] = chave_f[1]
        
        # transformando a resposta em lista
        resposta_lista = []
        for chave_i in resposta_dict.keys():
            resposta_lista.append([chave_i, resposta_dict[chave_i][0], resposta_dict[chave_i][1]])
        return resposta_lista
    
    def salvar_csv_tokens(self, tokens:list[list]):
        if not tokens:
            return False
        
        checagem = set()
        token_nao_repetido=[]
        for tk in tokens:
            if (((tk[0]) not in checagem) or (tk[2] == 'fixo')):
                checagem.add(tk[0])
                token_nao_repetido.append(tk)
                
        try:
            token_indexado = []
            for i, tk in enumerate(token_nao_repetido):
                token_indexado.append([tk[0], tk[1], tk[2], i+1])
            df = pd.DataFrame(token_indexado, columns=['valor', 'quantidade', 'tipo', 'id'])
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
