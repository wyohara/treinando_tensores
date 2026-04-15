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
            tk.gerar_tokens(quantidade=tk.total_tokens_possiveis+1)
    
    def test_tokenizar_texto(self):
        tk:Tokenizador = self.__classe_teste
        for i in tk.tokenizar_texto(tk.gerar_tokens(100000),"claraboia, acho"):
            assert isinstance(i,int) == True

    def test_reversao_token_lista_utf8(self):
        tk:Tokenizador = self.__classe_teste
        tokens = tk.tokenizar_texto(tk.gerar_tokens(100000),"claraboia, acho")
        reversao = tk.reverter_tokenizacao(tokens,utf8=True)
        for i in reversao:
            assert isinstance(i,str) == True
            assert all(c in '0123456789abcdefABCDEF' for c in i) == False

    def test_reversao_token_lista_hex(self):
        tk:Tokenizador = self.__classe_teste
        tokens = tk.tokenizar_texto(tk.gerar_tokens(100000),"claraboia, acho")
        reversao = tk.reverter_tokenizacao(tokens)
        for i in reversao:
            assert isinstance(i,str) == True
            assert all(c in '0123456789abcdefABCDEF' for c in i) == True

    def test_reversao_token_concatenado(self):
        tk:Tokenizador = self.__classe_teste
        tokens = tk.tokenizar_texto(tk.gerar_tokens(100000),"claraboia, acho")
        reversao = tk.reverter_tokenizacao(tokens,concatenar=True)
        assert isinstance(reversao, str)

    def test_reversao_token_concatenado_utf8(self):
        tk:Tokenizador = self.__classe_teste
        tokens = tk.tokenizar_texto(tk.gerar_tokens(100000),"claraboia, acho")
        reversao = tk.reverter_tokenizacao(tokens,concatenar=True,utf8=True)
        assert isinstance(reversao, str)
        assert all(c in '0123456789abcdefABCDEF' for c in reversao) == False

    def test_reversao_token_concatenado_hex(self):
        tk:Tokenizador = self.__classe_teste
        tokens = tk.tokenizar_texto(tk.gerar_tokens(100000),"claraboia, acho")
        reversao = tk.reverter_tokenizacao(tokens,concatenar=True,utf8=False)
        assert all(c in '0123456789abcdefABCDEF' for c in reversao) == True


