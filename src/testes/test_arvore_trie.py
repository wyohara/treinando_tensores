import pytest
from pathlib import Path
import json
from src.tokenizador.processadores_texto.arvore_trie import ArvoreTrie

@pytest.fixture(scope='function')
def fixture_arquivo_json(tmp_path):        
    # Cria diretório temporário para dataset
    arvore_json = tmp_path / "pasta_test"
    arvore_json.mkdir()
    yield arvore_json / 'arvore.json'

@pytest.fixture(scope='function')
def fixture_json_arvore_trie():
    yield ['amor amar amado', {'61':{'6d':{'fim':3,'6f':{'72':{'fim':1}},'61':{'72':{'fim':1},'fim':2,'64':{'6f':{'fim':1}}}}},'20':{'fim':1}}]


#=============================================================
#               Classe de teste
#=============================================================
class TestArvoreTrie:        
    @pytest.fixture(scope='class', autouse=True)
    def setup_inical(self, request):
        #rodando os testes
        print(f'\n🚀 Rodando o teste...')
        yield

        #teardown
        print(f'\n🧹 rodando o teardown')
    
    def test_processar_texto_usando_trie(self, fixture_json_arvore_trie):
        trie = ArvoreTrie()
        resultado = trie._processar_textos(fixture_json_arvore_trie[0])
        assert resultado == fixture_json_arvore_trie[1]

    def test_salvar_arvore_trie_arquivo_nao_existe(self, fixture_arquivo_json):
        trie = ArvoreTrie()
        trie.set_arquivo_json_arvore(fixture_arquivo_json)
        assert trie.salvar_arvore_trie({'oi':1}) == True
        assert trie.get_arquivo_json_arvore.exists() == True
    
    def test_salvar_arvore_trie_arquivo_vazio(self, fixture_arquivo_json):
        trie = ArvoreTrie()
        trie.set_arquivo_json_arvore(fixture_arquivo_json)
        assert trie.salvar_arvore_trie({}) == False

    def test_carregar_arvore_trie_nao_existe(self, fixture_arquivo_json):
        trie = ArvoreTrie()
        trie.set_arquivo_json_arvore(fixture_arquivo_json)
        assert trie._get_arvore_trie() == {}

    def test_carregar_arvore_trie_vazia(self, fixture_arquivo_json):
        trie = ArvoreTrie()
        trie.set_arquivo_json_arvore(fixture_arquivo_json)
        with trie.get_arquivo_json_arvore.open('w', encoding='utf-8') as arq:
            arq.write('')
        assert trie._get_arvore_trie() == {}

    def test_carregar_arvore_trie_vazia_caso2(self, fixture_arquivo_json):
        trie = ArvoreTrie()
        trie.set_arquivo_json_arvore(fixture_arquivo_json)
        with trie.get_arquivo_json_arvore.open('w', encoding='utf-8') as arq:
            arq.write('{}')
        assert trie._get_arvore_trie() == {}
    
    def test_carregar_arvore_trie_existe(self, fixture_arquivo_json):
        trie = ArvoreTrie()
        trie.set_arquivo_json_arvore(fixture_arquivo_json)
        trie.salvar_arvore_trie({'oi': 1})
        assert trie._get_arvore_trie() == {'oi': 1}
    
    def test_salvar_arvore_trie_existente(self, fixture_arquivo_json):
        trie = ArvoreTrie()
        trie.set_arquivo_json_arvore(fixture_arquivo_json)        
        assert trie.salvar_arvore_trie({'oi': 1}) == True
        assert trie.salvar_arvore_trie({'casa': 'minha'}) == True
        assert trie._get_arvore_trie() == {'casa': 'minha'}
    
    def test_gerar_lista_tokens(self, fixture_arquivo_json):
        trie = ArvoreTrie()
        trie.set_arquivo_json_arvore(fixture_arquivo_json)
        print(trie.montar_lista_tokens())
        assert len(trie.montar_lista_tokens())>0
    
    def test_gerar_lista_tokens(self, fixture_arquivo_json, fixture_json_arvore_trie):
        trie = ArvoreTrie()
        trie._processar_textos(fixture_json_arvore_trie[0])
        trie.set_arquivo_json_arvore(fixture_arquivo_json)
        opcional = []
        for i in trie.montar_lista_tokens():
            if i[2]=='opcional': 
                opcional.append(i[2])
        assert len(opcional) == 6 #['am', 'a', 'r', 'o', 'do', ' '] em hex
        assert len(trie.montar_lista_tokens())>5

    def test_gerar_lista_tokens(self, fixture_arquivo_json, fixture_json_arvore_trie):
        trie = ArvoreTrie()
        trie._processar_textos(fixture_json_arvore_trie[0])
        trie.set_arquivo_json_arvore(fixture_arquivo_json)
        opcional = []
        for i in trie.montar_lista_tokens():
            if i[2]=='opcional': 
                opcional.append(i[2])
        assert len(opcional) == 6 #['am', 'a', 'r', 'o', 'do', ' '] em hex
        assert len(trie.montar_lista_tokens())>5
