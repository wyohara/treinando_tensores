import pytest
import pandas as pd
import numpy as np

from src.tokenizador.processadores_texto.processador_word_piece import ProcessadorWordPiece 

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
class TestWordPiece:     

    @pytest.fixture(scope='function', autouse=True)
    def setup_inical(self, request, fixture_lista_tokens):
        request.instance.__classe_teste = ProcessadorWordPiece()
        self.__classe_teste:ProcessadorWordPiece
        self.__classe_teste.set_arquivo_tokens(fixture_lista_tokens)
        
        yield
        #encerrando a fixture de teste
        del self.__classe_teste
        import gc # forçando a limpeza de memória
        gc.collect()
    
    def test_arquivo_dados_nao_existe(self):
        # teste para verificar se não existe o arquivo de lista de tokens
        self.__classe_teste:ProcessadorWordPiece
        assert self.__classe_teste.arquivo_lista_tokens.is_file() == False

    def test_processar_texto_vazio(self):
        # teste tentando processar um texto vazio
        self.__classe_teste:ProcessadorWordPiece
        assert self.__classe_teste.processar_textos('') == False
        assert self.__classe_teste.arquivo_lista_tokens.is_file() == False
    
    def test_processar_caracter_simples(self):
        # teste tentando processar um texto com espaço simples
        self.__classe_teste:ProcessadorWordPiece
        assert self.__classe_teste.processar_textos('a') == True
        assert self.__classe_teste.arquivo_lista_tokens.is_file() == True

        #verifica o formato do arquivo recuperado
        df = pd.read_csv(str(self.__classe_teste.arquivo_lista_tokens))
        tokens:list[str, int, float, str, str] = df.values.tolist()
        assert len(tokens) == 1
        assert tokens[0] == [61, 1, 1.0, '-', '-', False]    
    
    def test_processar_palavra_simples(self):
        # teste tentando processar um texto com espaço simples
        self.__classe_teste:ProcessadorWordPiece
        assert self.__classe_teste.processar_textos('casa') == True
        assert self.__classe_teste.arquivo_lista_tokens.is_file() == True

        #verifica o formato do arquivo recuperado
        df = pd.read_csv(str(self.__classe_teste.arquivo_lista_tokens))
        tokens:list[str, int, float, str, str] = df.values.tolist()
        
        for i in tokens:
            print(self.__classe_teste.hex_para_texto(i[0]))
        assert len(tokens) == 9 #[a, asa, casa, as, sa, cas, s, ca, c]
    
    '''def test_processar_palavra_simples_2(self):
        # teste tentando processar um texto com espaço simples
        self.__classe_teste:ProcessadorWordPiece
        assert self.__classe_teste.processar_textos('casa caso') == True
        assert self.__classe_teste.arquivo_lista_tokens.is_file() == True

        #verifica o formato do arquivo recuperado
        df = pd.read_csv(str(self.__classe_teste.arquivo_lista_tokens))
        tokens:list[str,str,int,float] = df.values.tolist()
        for i in tokens:
            print(self.__classe_teste.hex_para_texto(i[0].replace("#",'')))
        assert len(tokens) == 14 #[a, s, c, o, ' ', cas, caso, aso, so, as, ca, casa, asa, sa]
        self.__classe_teste.montar_lista_tokens()'''
  

