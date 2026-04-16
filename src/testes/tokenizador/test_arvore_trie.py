import pytest
from pathlib import Path
import json
from src.tokenizador.processadores_texto.arvore_trie import ArvoreTrie

@pytest.fixture(scope='function')
def fixture_arquivo_arvore_json(tmp_path):        
    # Cria diretório temporário para dataset
    arvore_json = tmp_path / "pasta_test"
    try:
        arvore_json.mkdir()
    except FileExistsError:
        pass
    yield arvore_json / 'arvore.json'

@pytest.fixture(scope='function')
def fixture_arquivo_csv_tokens(tmp_path):        
    # Cria diretório temporário para dataset
    arvore_json = tmp_path / "pasta_test"
    try:
        arvore_json.mkdir()
    except FileExistsError:
        pass
    yield arvore_json / 'arquivo_css_tokens.csv'

@pytest.fixture(scope='function')
def fixture_arvore_trie_pronta():
    yield {'texto':'amor amar amado', 'tokens':{'20': {'fim': 2},'61': {'6d': {'61': {'64': {'6f': {'fim': 1}}, '72': {'fim': 1}}, '6f': {'72': {'fim': 1}}, 'ramo': 3}}}}


#=============================================================
#               Classe de teste
#=============================================================
class TestArvoreTrie:        
    @pytest.fixture(scope='function', autouse=True)
    def setup_inical(self, request, fixture_arquivo_arvore_json, fixture_arquivo_csv_tokens):        
        request.instance.__classe_teste = ArvoreTrie()
        self.__classe_teste:ArvoreTrie
        self.__classe_teste.set_arquivo_csv_tokens(fixture_arquivo_csv_tokens)
        self.__classe_teste.set_arquivo_json_arvore(fixture_arquivo_arvore_json)
        #rodando os testes
        yield

        #encerrando a fixsture de teste
        del self.__classe_teste
        import gc # forçando a limpeza de memória
        gc.collect()
    
    def test_processar_texto_usando_trie(self, fixture_arvore_trie_pronta):
        #testando a geração da árvore de trie
        trie:ArvoreTrie = self.__classe_teste
        resposta = trie.processar_textos(fixture_arvore_trie_pronta['texto'])
        assert resposta == fixture_arvore_trie_pronta['tokens']
    
    def test_processar_texto_usando_trie_caso_2(self):
        #testando a geração da árvore de trie com um caractere só
        trie:ArvoreTrie = self.__classe_teste
        resposta = trie.processar_textos(' ')
        assert resposta == {'20':{'fim':1}}
    
    def test_processar_texto_usando_trie_com_erro(self ):
        #testando a geração da árvore de trie com string vazia
        trie:ArvoreTrie = self.__classe_teste
        with pytest.raises(ValueError):
            resposta = trie.processar_textos('')

    def test_verificar_arvore_trie_foi_salva(self, fixture_arvore_trie_pronta):
        # verifica se após processar texto é criado um json da árvore
        trie:ArvoreTrie = self.__classe_teste
        assert trie.get_arquivo_json_arvore.is_file() == False
        trie.processar_textos(fixture_arvore_trie_pronta['texto'])
        assert trie.get_arquivo_json_arvore.is_file() == True
        with trie.get_arquivo_json_arvore.open('r', encoding='utf-8') as f:
            arvore_carregada = json.load(f)
            assert arvore_carregada == fixture_arvore_trie_pronta['tokens']
    
    def test_verificar_arvore_trie_foi_salva_caso_2(self):
        # verifica se após processar texto é criado um json da árvore
        trie:ArvoreTrie = self.__classe_teste
        assert trie.get_arquivo_json_arvore.is_file() == False
        trie.processar_textos(' ')
        assert trie.get_arquivo_json_arvore.is_file() == True
        with trie.get_arquivo_json_arvore.open('r', encoding='utf-8') as f:
            arvore_carregada = json.load(f)
            assert arvore_carregada == {'20':{'fim':1}}
    
    def test_gerar_lista_tokens_caso_1(self, fixture_arvore_trie_pronta):
        trie:ArvoreTrie = self.__classe_teste
        trie.processar_textos(fixture_arvore_trie_pronta['texto'])
        #tokens possiveis:
        #[amado, am, amad]
        assert len(trie.montar_lista_tokens())>0

    '''
    def test_gerar_lista_tokens_caso_2(self, fixture_arvore_trie_pronta):
        trie:ArvoreTrie = self.__classe_teste
        trie.processar_textos(fixture_arvore_trie_pronta['texto'])
        opcional = []
        for i in trie.montar_lista_tokens():
            if i[2]=='opcional': 
                opcional.append([i[0], i[2]])
        assert len(opcional) == 7 #['am', 'amor', 'or', 'ama', amar, 'r', 'amado'] em hex como opcional e ['a', 'r', 'o', ' '] em hex como fixo
        assert len(trie.montar_lista_tokens())>5
    
    def test_verificar_se_cria_arquivo_tokens(self):
        trie:ArvoreTrie = self.__classe_teste
        resultado = trie.salvar_csv_tokens([])
        assert resultado == False

    def test_verificar_se_salva_lista_tokens(self):
        trie:ArvoreTrie = self.__classe_teste
        resultado = trie.salvar_csv_tokens([['a',1,'utf-8']])
        assert resultado == True
    
    def test_abrir_arquivo_vazio(self):
        trie:ArvoreTrie = self.__classe_teste
        trie.salvar_csv_tokens([])
        assert trie.carregar_lista_tokens() == []
        
    def test_abrir_arquivo_sem_dados(self):
        trie:ArvoreTrie = self.__classe_teste
        trie.salvar_csv_tokens([])
        assert trie.carregar_lista_tokens() == []
    
    def test_processo_completo(self, fixture_arvore_trie_pronta):        
        trie:ArvoreTrie = self.__classe_teste
        #verifica se o primeiro texto foi processado
        processado = trie.processar_textos(fixture_arvore_trie_pronta['texto'])
        assert processado == fixture_arvore_trie_pronta['tokens']
        assert trie.get_arquivo_json_arvore.is_file() == True

        #verifica se o segundo texto foi processado
        processado = trie.processar_textos(fixture_arvore_trie_pronta['texto'])
        assert processado == {'20': {'fim': 4},'61': {'6d': {'61': {'64': {'6f': {'fim': 2}}, '72': {'fim': 2}, 'fim': 4}, '6f': {'72': {'fim': 2}}, 'fim': 6}}}
        assert trie.get_arquivo_json_arvore.is_file() == True

        #criando o csv de tokens
        tokens = trie.montar_lista_tokens()
        salvo = trie.salvar_csv_tokens(tokens)
        assert salvo == True
        assert trie.get_arquivo_csv_tokens.is_file() == True
        lista_tokens =  trie.carregar_lista_tokens()
        assert lista_tokens != []'''
