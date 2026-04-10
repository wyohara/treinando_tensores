


class ArvoreTrie:
    def __init__(self):
        self.__arvore = {}

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
        palavras = texto.split()
        lista_palavras = []
        if not palavras:
            raise ValueError
        for palavra in palavras:
            lista_palavras.append(palavra)

        #aplicando o algoritmo ao texto
        for i, palavra in enumerate(sorted(lista_palavras, key=len, reverse=True)):
            self.__arvore = self.__montar_arvore_trie(palavra)

        return self.__arvore

    def __montar_arvore_trie(self, palavra:str, contar_tokens=True) -> dict:
        """
        Método que monta a ávore de trie. Cria um dicionário onde a chave é cada caractere. 
        Caso a sequência de caracteres não exista é criada uma ramificação e a chave fim, 
        indicando o número de vezes que o contador passou pela bifurcação.

        Obs: 
            - A árvore precisa encontrar duas vezes o mesmo prefixo para bifurcar
            - Internamente o radical vira uma nova árvore, mas seu contador é 
            somado pela regra de integridade do banco de dados.
        
        Params:
            palavra: palavra processada que será usada na árvore
            arvore: ávore que será usada no processo
            contar_tokens: incrementa o contador de tokens

        Returns:
            arvore: a árvore inicial atualizada com os novos valores

        """
        no_atual = self.__arvore
        raiz = True

        # cria o step do range, se for hex irá andar 2 bytes (1 char UNICODE) se utf-8 uma letra
        step = 1 
        for i in range(0,len(palavra), step):
            letra = (palavra[i:i+step])
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
        return self.__arvore