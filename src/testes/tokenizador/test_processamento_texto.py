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

    def test_verificar_pastas_existem(self):
        controle_arquivos:ControleArquivos = self.__classe_teste
        assert controle_arquivos.get_pasta_dataset.is_dir()
    
    def test_verificar_existem_arquivos_dataset(self):
        controle_arquivos:ControleArquivos = self.__classe_teste
        assert(len(controle_arquivos._carregar_todo_dataset())>0)

    def test_pasta_dataset_vazia(self, tmp_path):        
        dataset_dir = tmp_path / "pasta_test2"
        dataset_dir.mkdir()
        controle_arquivos:ControleArquivos = self.__classe_teste
        controle_arquivos.set_pasta_dataset(dataset_dir)
        assert controle_arquivos._carregar_todo_dataset() == []

    def test_pasta_dataset_com_arquivo(self):
        controle_arquivos:ControleArquivos = self.__classe_teste
        assert len(controle_arquivos._carregar_todo_dataset()) == 2

    def test_buscar_arquivo_processado_vazio(self, tmp_path):
        dataset_dir = tmp_path / "pasta_test2"
        dataset_dir.mkdir()
        controle_arquivos:ControleArquivos = self.__classe_teste
        controle_arquivos.set_pasta_dataset(dataset_dir)
        assert controle_arquivos._get_lista_arquivos_processados() == []

    def test_buscar_arquivo_processado_em_branco(self):
        controle_arquivos:ControleArquivos = self.__classe_teste
        controle_arquivos.get_arquivo_arquivos_processados.write_text("", encoding='utf-8')
        assert controle_arquivos._get_lista_arquivos_processados() == []

    def test_buscar_arquivo_processado_sem_valores(self):
        controle_arquivos:ControleArquivos = self.__classe_teste
        controle_arquivos.get_arquivo_arquivos_processados.write_text("nome,modelo_processamento", encoding='utf-8')
        assert controle_arquivos._get_lista_arquivos_processados() == []

    def test_verificar_texto_ja_foi_processado(self):
        controle_arquivos:ControleArquivos = self.__classe_teste
        controle_arquivos.get_arquivo_arquivos_processados.write_text("nome,modelo_processamento\ntexto1.txt,trie\ntexto2.txt,trie", encoding='utf-8')
        assert controle_arquivos._carregar_todo_dataset() == []

    def test_verificar_texto_ja_foi_processado_caso_2(self):
        controle_arquivos:ControleArquivos = self.__classe_teste
        #criando dataset temporario        
        texto3 = self.__classe_teste.get_pasta_dataset / "texto3.txt"
        texto3.write_text("texto inicial 3", encoding='utf-8')

        #criando o arquivo_processado
        controle_arquivos.get_arquivo_arquivos_processados.write_text("nome,modelo_processamento\ntexto1.txt,trie\ntexto2.txt,trie", encoding='utf-8')

        # apenas o texto3 não foi processado
        resultado_esperado = ['texto3.txt']
        for texto in controle_arquivos._carregar_todo_dataset():
            assert texto.name in  resultado_esperado
    
    def test_salvar_lista_arquivos_processados(self):
        controle_arquivos:ControleArquivos = self.__classe_teste
        controle_arquivos._salvar_texto_processado('texto3.txt','trie')
        resultado = controle_arquivos._get_lista_arquivos_processados()
        assert resultado[0] == ['texto3.txt','trie']
    
    def test_processar_textos(self):
        controle_arquivos:ControleArquivos = self.__classe_teste

        controle_arquivos.processar_textos()
        assert controle_arquivos._get_lista_arquivos_processados()[0] == ['texto1.txt', 'trie']
        assert controle_arquivos._get_lista_arquivos_processados()[1] == ['texto2.txt', 'trie']

        with pytest.raises(IndexError): # verificando o index error
            assert controle_arquivos._get_lista_arquivos_processados()[2] == ['texto3.txt', 'trie']