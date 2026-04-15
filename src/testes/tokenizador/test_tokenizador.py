import pytest
from src.tokenizador.tokenizador import Tokenizador

@pytest.fixture(scope='function')
def fixture_arquivo_csv_tokens(tmp_path):        
    # Cria diretório temporário para dataset
    arvore_json = tmp_path / "pasta_test"
    try:
        arvore_json.mkdir()
    except FileExistsError:
        pass
    yield arvore_json / 'arquivo_csv_tokens.csv'


#=============================================================
#               Classe de teste
#=============================================================
class TestTokenizador:
    @pytest.fixture(scope='function', autouse=True)
    def setup_inical(self, request, fixture_arquivo_csv_tokens):
        request.instance.__classe_teste = Tokenizador()
        self.__classe_teste:Tokenizador
        #self.__classe_teste.set_arquivo_csv_tokens(fixture_arquivo_csv_tokens)

        yield
        #encerrando a fixsture de teste
        del self.__classe_teste
        import gc # forçando a limpeza de memória
        gc.collect()

    def test_gerando_tokens(self):
        tk:Tokenizador = self.__classe_teste
        assert tk.total_tokens_possiveis>0

    def test_tentar_recuperar_quantidade_invalida(self):
        tk:Tokenizador = self.__classe_teste
        assert len(tk.gerar_tokens(quantidade=-1).keys())==0
    
    def test_tentar_recuperar_zero_tokens(self):
        tk:Tokenizador = self.__classe_teste
        assert len(tk.gerar_tokens(quantidade=0).keys()) == 119
    
    def test_tentar_recuperar_150_tokens(self):
        tk:Tokenizador = self.__classe_teste
        assert len(tk.gerar_tokens(quantidade=150).keys()) == 150

    def test_tentar_recuperar_mais_tokens_que_existe(self):
        tk:Tokenizador = self.__classe_teste
        with pytest.raises(IndexError):
            tk.gerar_tokens(quantidade=1500000000)



