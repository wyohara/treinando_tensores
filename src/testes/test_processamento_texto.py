#!/usr/bin/env python3
import pytest
import os
import tempfile
import shutil
from pathlib import Path
from tokenizador.controle_arquivos import ControleArquivos


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


class TestProcessamentoTexto:
    
    @pytest.fixture(scope='class', autouse=True)
    def setup_inical(self, request):
        # Criar o objeto e armazenar na classe em __controle_arquivos
        request.cls.controle_arquivos = ControleArquivos()

        #rodando os testes
        print(f'\n🚀 Rodando o teste...')
        yield

        #teardown
        print(f'\n🧹 rodando o teardown')

    def test_verificar_pastas_existem(self):
        controle_arquivos = ControleArquivos()
        assert controle_arquivos.pasta_dataset.is_dir()
    
    def test_verificar_existem_arquivos_dataset(self):
        controle_arquivos = ControleArquivos()
        assert(len(controle_arquivos._carregar_dataset())>0)

    def test_pasta_dataset_vazia(self, fixture_pasta_dataset_temporaria):
        controle_arquivos = ControleArquivos()
        controle_arquivos._set_pasta_dataset(fixture_pasta_dataset_temporaria)
        assert controle_arquivos._carregar_dataset() == []

    def test_pasta_dataset_com_arquivo(self, fixture_pasta_dataset_temporaria):
        controle_arquivos = ControleArquivos()
        
        texto1 = fixture_pasta_dataset_temporaria / "texto1.txt"
        texto2 = fixture_pasta_dataset_temporaria / "texto2.txt"
        texto1.write_text("texto inicial 1", encoding='utf-8')
        texto2.write_text("texto inicial 2", encoding='utf-8')
        controle_arquivos._set_pasta_dataset(fixture_pasta_dataset_temporaria)
        controle_arquivos._set_pasta_arquivos_processados('')
        assert len(controle_arquivos._carregar_dataset()) == 2

    def test_buscar_arquivo_processado_vazio(self, fixture_arquivos_processados_temporario):
        controle_arquivos = ControleArquivos()
        controle_arquivos._set_pasta_arquivos_processados((fixture_arquivos_processados_temporario))
        assert controle_arquivos._get_lista_arquivos_processados() == []

    def test_buscar_arquivo_processado_em_branco(self, fixture_arquivos_processados_temporario):
        controle_arquivos = ControleArquivos()
        arquivo_processado = fixture_arquivos_processados_temporario
        arquivo_processado.write_text("", encoding='utf-8')
        controle_arquivos._set_pasta_arquivos_processados(fixture_arquivos_processados_temporario)
        assert controle_arquivos._get_lista_arquivos_processados() == []

    def test_buscar_arquivo_processado_sem_valores(self, fixture_arquivos_processados_temporario):
        controle_arquivos = ControleArquivos()
        arquivo_processado = fixture_arquivos_processados_temporario
        arquivo_processado.write_text("nome,modelo_processamento", encoding='utf-8')
        controle_arquivos._set_pasta_arquivos_processados(fixture_arquivos_processados_temporario)
        assert controle_arquivos._get_lista_arquivos_processados() == []

    def test_buscar_arquivo_processado_preenchido(self, fixture_arquivos_processados_temporario):
        controle_arquivos = ControleArquivos()
        arquivo_processado = fixture_arquivos_processados_temporario
        controle_arquivos._set_pasta_arquivos_processados(fixture_arquivos_processados_temporario)
        arquivo_processado.write_text("nome,modelo_processamento\ntexto1.txt,trie\ntexto2.txt,trie", encoding='utf-8')

    def test_verificar_texto_ja_foi_processado(self, fixture_arquivos_processados_temporario, fixture_pasta_dataset_temporaria):
        controle_arquivos = ControleArquivos()

        #criando dataset temporario        
        texto1 = fixture_pasta_dataset_temporaria / "texto1.txt"
        texto2 = fixture_pasta_dataset_temporaria / "texto2.txt"
        texto1.write_text("texto inicial 1", encoding='utf-8')
        texto2.write_text("texto inicial 2", encoding='utf-8')
        controle_arquivos._set_pasta_dataset(fixture_pasta_dataset_temporaria)

        #criando o arquivo_processado
        arquivo_processado = fixture_arquivos_processados_temporario
        controle_arquivos._set_pasta_arquivos_processados(fixture_arquivos_processados_temporario)
        arquivo_processado.write_text("nome,modelo_processamento\ntexto1.txt,trie\ntexto2.txt,trie", encoding='utf-8')
        controle_arquivos._set_pasta_arquivos_processados(fixture_arquivos_processados_temporario)

        assert controle_arquivos._carregar_dataset() == []

    def test_verificar_texto_ja_foi_processado_caso_2(self, fixture_arquivos_processados_temporario, fixture_pasta_dataset_temporaria):
        controle_arquivos = ControleArquivos()

        #criando dataset temporario        
        texto1 = fixture_pasta_dataset_temporaria / "texto1.txt"
        texto2 = fixture_pasta_dataset_temporaria / "texto2.txt"
        texto3 = fixture_pasta_dataset_temporaria / "texto3.txt"
        texto1.write_text("texto inicial 1", encoding='utf-8')
        texto2.write_text("texto inicial 2", encoding='utf-8')
        texto3.write_text("texto inicial 3", encoding='utf-8')
        controle_arquivos._set_pasta_dataset(fixture_pasta_dataset_temporaria)

        #criando o arquivo_processado
        arquivo_processado = fixture_arquivos_processados_temporario
        controle_arquivos._set_pasta_arquivos_processados(fixture_arquivos_processados_temporario)
        arquivo_processado.write_text("nome,modelo_processamento\ntexto1.txt,trie\ntexto2.txt,trie", encoding='utf-8')
        controle_arquivos._set_pasta_arquivos_processados(fixture_arquivos_processados_temporario)

        # apenas o texto3 não foi processado
        resultado_esperado = ['texto3.txt']
        for texto in controle_arquivos._carregar_dataset():
            assert texto.name in  resultado_esperado

    def test_gerar_arvore_trier(self, fixture_pasta_dataset_temporaria):
        texto = fixture_pasta_dataset_temporaria / "texto1.txt"
        texto.write_text('amor amar amado', encoding='utf-8')
        controle_arquivos = ControleArquivos()
        resultado = {'a':{'m':{'fim':3,'o':{'r':{'fim':1}},'a':{'r':{'fim':1},'fim':2,'d':{'o':{'fim':1}}}}}}
        assert controle_arquivos._processar_textos(texto) == resultado
    



