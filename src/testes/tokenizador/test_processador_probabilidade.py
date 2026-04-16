import pytest
import pandas as pd
from src.tokenizador.processadores_texto.processador_probabilidade import ProcessadorProbabilidade 

@pytest.fixture(scope='function')
def fixture_lista_tokens(tmp_path):
    lista_tokens = tmp_path / "pasta_test"
    try:
        lista_tokens.mkdir()
    except FileExistsError:
        pass
    yield lista_tokens / 'lista_tokens.csv'


#=============================================================
#               Classe de teste
#=============================================================
class TestArvoreTrie:     

    @pytest.fixture(scope='function', autouse=True)
    def setup_inical(self, request, fixture_lista_tokens):
        request.instance.__classe_teste = ProcessadorProbabilidade()
        self.__classe_teste:ProcessadorProbabilidade
        self.__classe_teste.set_lista_tokens(fixture_lista_tokens)
        
        yield
        #encerrando a fixture de teste
        del self.__classe_teste
        import gc # forçando a limpeza de memória
        gc.collect()
    
    def test_arquivo_dados_nao_existe(self):
        # teste para verificar se não existe o arquivo de lista de tokens
        self.__classe_teste:ProcessadorProbabilidade
        assert self.__classe_teste.arquivo_lista_tokens.is_file() == False

    def test_processar_texto_vazio(self):
        # teste tentando processar um texto vazio
        self.__classe_teste:ProcessadorProbabilidade
        assert self.__classe_teste.processar_textos('') == False
        assert self.__classe_teste.arquivo_lista_tokens.is_file() == False
    
    def test_processar_texto_simples(self):
        # teste tentando processar um texto com espaço simples
        self.__classe_teste:ProcessadorProbabilidade
        assert self.__classe_teste.processar_textos(' ') == True
        assert self.__classe_teste.arquivo_lista_tokens.is_file() == True

        #verifica o formato do arquivo recuperado
        df = pd.read_csv(str(self.__classe_teste.arquivo_lista_tokens))
        tokens:list[str,str,int,float] = df.values.tolist()
        assert tokens[0] == [20, ' ', 1, 1.0]
    
    
    def test_processar_palavra_simples(self):
        # teste tentando processar um texto com espaço simples
        self.__classe_teste:ProcessadorProbabilidade
        assert self.__classe_teste.processar_textos('  d') == True
        assert self.__classe_teste.arquivo_lista_tokens.is_file() == True

        #verifica o formato do arquivo recuperado
        df = pd.read_csv(str(self.__classe_teste.arquivo_lista_tokens))
        tokens:list[str,str,int,float] = df.values.tolist()
        
