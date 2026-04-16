
from src.tokenizador.controle_arquivos import ControleArquivos

def app():
    print("iniciando o processamento")
    controle_arquivos:ControleArquivos = ControleArquivos()
    lista_tokens = controle_arquivos.processar_textos()
    controle_arquivos.salvar_tokens(lista_tokens)