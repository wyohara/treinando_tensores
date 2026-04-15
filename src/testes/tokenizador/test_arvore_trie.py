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
def fixture_json_arvore_trie_para_comparar():
    yield ['amor amar amado', {'20': {'fim': 2},'61': {'6d': {'61': {'64': {'6f': {'fim': 1}}, '72': {'fim': 1}, 'fim': 2}, '6f': {'72': {'fim': 1}}, 'fim': 3}}}]



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
    
    def test_processar_texto_usando_trie(self, fixture_json_arvore_trie_para_comparar):
        trie:ArvoreTrie = self.__classe_teste
        resultado = trie.processar_textos(fixture_json_arvore_trie_para_comparar[0])
        assert resultado == fixture_json_arvore_trie_para_comparar[1]

    def test_salvar_arvore_trie_arquivo_nao_existe(self):
        trie:ArvoreTrie = self.__classe_teste
        assert trie.salvar_arvore_trie({'oi':1}) == True
        assert trie.get_arquivo_json_arvore.exists() == True
    
    def test_salvar_arvore_trie_arquivo_vazio(self):
        trie:ArvoreTrie = self.__classe_teste
        assert trie.salvar_arvore_trie({}) == False

    def test_carregar_arvore_trie_vazia(self):
        trie:ArvoreTrie = self.__classe_teste
        with trie.get_arquivo_json_arvore.open('w', encoding='utf-8') as arq:
            arq.write('')
        assert trie.get_arvore_trie() == {}

    def test_carregar_arvore_trie_vazia_caso2(self):
        trie:ArvoreTrie = self.__classe_teste
        with trie.get_arquivo_json_arvore.open('w', encoding='utf-8') as arq:
            arq.write('{}')
        assert trie.get_arvore_trie() == {}
    
    def test_carregar_arvore_trie_existe(self):
        trie:ArvoreTrie = self.__classe_teste
        trie.salvar_arvore_trie({'oi': 1})
        assert trie.get_arvore_trie() == {'oi': 1}
    
    def test_salvar_arvore_trie_existente(self):
        trie:ArvoreTrie = self.__classe_teste
        assert trie.salvar_arvore_trie({'oi': 1}) == True
        assert trie.salvar_arvore_trie({'casa': 'minha'}) == True
        assert trie.get_arvore_trie() == {'casa': 'minha'}
    
    def test_gerar_lista_tokens_caso_1(self):
        trie:ArvoreTrie = self.__classe_teste
        assert len(trie.montar_lista_tokens())>0
    
    def test_gerar_lista_tokens_caso_2(self, fixture_json_arvore_trie_para_comparar):
        trie:ArvoreTrie = self.__classe_teste
        trie.processar_textos(fixture_json_arvore_trie_para_comparar[0])
        opcional = []
        for i in trie.montar_lista_tokens():
            if i[2]=='opcional': 
                opcional.append(i[2])
        assert len(opcional) == 2 #['am' 'do'] em hex como opcional e ['a', 'r', 'o', ' '] em hex como fixo
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
    
    def test_processo_completo(self, fixture_json_arvore_trie_para_comparar):        
        trie:ArvoreTrie = self.__classe_teste
        #verifica se o primeiro texto foi processado
        processado = trie.processar_textos(fixture_json_arvore_trie_para_comparar[0])
        assert processado == fixture_json_arvore_trie_para_comparar[1]
        assert trie.get_arquivo_json_arvore.is_file() == True

        #verifica se o segundo texto foi processado
        processado = trie.processar_textos(fixture_json_arvore_trie_para_comparar[0])
        assert processado == {'20': {'fim': 4},'61': {'6d': {'61': {'64': {'6f': {'fim': 2}}, '72': {'fim': 2}, 'fim': 4}, '6f': {'72': {'fim': 2}}, 'fim': 6}}}
        assert trie.get_arquivo_json_arvore.is_file() == True

        #criando o csv de tokens
        tokens = trie.montar_lista_tokens()
        salvo = trie.salvar_csv_tokens(tokens)
        assert salvo == True
        assert trie.get_arquivo_csv_tokens.is_file() == True
        lista_tokens =  trie.carregar_lista_tokens()
        assert lista_tokens != []
