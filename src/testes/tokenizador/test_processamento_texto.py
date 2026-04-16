#!/usr/bin/env python3
import pytest
import os
import tempfile
import shutil
from pathlib import Path
from src.tokenizador.controle_arquivos import ControleArquivos


@pytest.fixture(scope='function')
def fixture_pasta_dataset_temporaria(tmp_path):        
    # Cria diretório temporário para dataset
    dataset_dir = tmp_path / "pasta_test"
    dataset_dir.mkdir()

    yield dataset_dir

@pytest.fixture(scope='function')
def fixture_arquivos_processados_temporario(tmp_path):        
    # Cria diretório temporário para dataset
    dataset_dir = tmp_path / "pasta_test_arquivo"
    dataset_dir.mkdir()
    yield dataset_dir / 'arquivo_processado.csv'


#=============================================================
#               Classe de teste
#=============================================================
class TestProcessamentoTexto:
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_inical(self, request, fixture_pasta_dataset_temporaria,fixture_arquivos_processados_temporario):
        # Criar o objeto e armazenar na classe em resultado_trie 
        
        texto1 = fixture_pasta_dataset_temporaria / "texto1.txt"
        texto2 = fixture_pasta_dataset_temporaria / "texto2.txt"
        texto1.write_text("texto inicial 1", encoding='utf-8')
        texto2.write_text("texto inicial 2", encoding='utf-8')

        request.instance.__classe_teste = ControleArquivos()
        self.__classe_teste:ControleArquivos
        self.__classe_teste.set_pasta_dataset(fixture_pasta_dataset_temporaria)
        self.__classe_teste.set_pasta_arquivos_processados(fixture_arquivos_processados_temporario)
        
        #rodando os testes
        yield
        
        #encerrando a fixsture de teste
        del self.__classe_teste
        import gc # forçando a limpeza de memória
        gc.collect()

    def test_verificar_arquivos_dataset(self):
        # Verifica se consegue listar arquivos do dataset com 2 arquivos
        controle_arquivos:ControleArquivos = self.__classe_teste
        assert len(controle_arquivos._carregar_lista_arquivos_dataset()) == 2

    def test_verificar_arquivo_dataset_vazio(self, tmp_path):
        # Verifica se retorna lista vazia ao carregar pasta dataset vazia
        dataset_dir = tmp_path / "pasta_test2"
        dataset_dir.mkdir()
        controle_arquivos:ControleArquivos = self.__classe_teste
        controle_arquivos.set_pasta_dataset(dataset_dir)
        assert len(controle_arquivos._carregar_lista_arquivos_dataset()) == 0

    def test_buscar_arquivos_processados_vazios(self):
        # Verifica se retorna array vazio ao carregar lista de arquivo processado:
        # - Não existe
        controle_arquivos:ControleArquivos = self.__classe_teste
        assert len(controle_arquivos._get_lista_arquivos_processados()) == 0

    def test_buscar_arquivo_processado_em_branco(self):
        # Verifica se retorna array vazio ao carregar lista de arquivo processado:
        # - Existe, mas em branco
        controle_arquivos:ControleArquivos = self.__classe_teste
        controle_arquivos.get_path_arquivos_processados.write_text("", encoding='utf-8')
        assert controle_arquivos._get_lista_arquivos_processados() == []

    def test_buscar_arquivo_processado_sem_valores(self):
        # Verifica se retorna array vazio ao carregar lista de arquivo processado:
        # - Existe com cabeçalho, mas sem valores
        controle_arquivos:ControleArquivos = self.__classe_teste
        controle_arquivos.get_path_arquivos_processados.write_text("nome,modelo_processamento", encoding='utf-8')
        assert controle_arquivos._get_lista_arquivos_processados() == []

    def test_verificar_texto_ja_foi_processado(self):
        # Verifica:
        # - Arquivo processado com todo o dataset
        # - Não encontra nenhum texto para processar e retorna []
        texto = "nome,modelo_processamento\ntexto1.txt,trie\ntexto2.txt,trie"
        controle_arquivos:ControleArquivos = self.__classe_teste
        controle_arquivos.get_path_arquivos_processados.write_text(texto, encoding='utf-8')
        assert controle_arquivos._carregar_lista_arquivos_dataset() == []

    def test_verificar_texto_ja_foi_processado_caso_2(self):        
        # Verifica:
        # - Arquivo processado com apenas um arquivo do dataset
        # - Encontra somente o texto2.txt como não processado
        texto = "nome,modelo_processamento\ntexto1.txt,trie"
        controle_arquivos:ControleArquivos = self.__classe_teste
        controle_arquivos.get_path_arquivos_processados.write_text(texto, encoding='utf-8')

        #verifica se o texto 2 não foi processado
        resposta = controle_arquivos._carregar_lista_arquivos_dataset()
        assert len(resposta) == 1
        for texto in resposta:
            assert texto.name == 'texto2.txt'
    
    def test_verifica_erro_arquivos_processados(self):
        # teste que verifica como fica os arquivos processados processar texto após 
        controle_arquivos:ControleArquivos = self.__classe_teste

        controle_arquivos.processar_textos()
        assert controle_arquivos._get_lista_arquivos_processados()[0] == ['texto1.txt', 'trie']
        assert controle_arquivos._get_lista_arquivos_processados()[1] == ['texto2.txt', 'trie']

        with pytest.raises(IndexError): # verificando o index error
            assert controle_arquivos._get_lista_arquivos_processados()[2] == ['texto3.txt', 'trie']