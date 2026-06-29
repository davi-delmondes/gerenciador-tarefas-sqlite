import csv

from app import config, relatorios, database

TITULO_TESTE = "Gerenciador de Tarefas"
DESCRICAO_TESTE = "Pytest"
DATA_TESTE = "2026-06-29 10:00"


def preparar_banco_temporario(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PASTA_DADOS", str(tmp_path))
    resultado = database.criar_tabela()
    assert resultado is True


def preparar_banco_com_tarefa(tmp_path, monkeypatch):
    preparar_banco_temporario(tmp_path, monkeypatch)

    resultado_inserir_tarefa = database.inserir_tarefa(TITULO_TESTE, DESCRICAO_TESTE, DATA_TESTE)
    assert resultado_inserir_tarefa is True


def preparar_exportacao_sem_interacao(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PASTA_EXPORTS", str(tmp_path))
    monkeypatch.setattr(relatorios.utils, "pausar_e_limpar", lambda: None)
    monkeypatch.setattr(relatorios.interface, "mostrar_cabecalho", lambda titulo: None)


def executar_exportacao_csv_de_teste(tmp_path, monkeypatch):
    preparar_exportacao_sem_interacao(tmp_path, monkeypatch)

    resultado = relatorios.exportar_relatorio_csv()
    assert resultado is True


def test_exportar_relatorio_csv_retorna_true(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    executar_exportacao_csv_de_teste(tmp_path, monkeypatch)


def test_exportar_relatorio_csv_cria_arquivo(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    executar_exportacao_csv_de_teste(tmp_path, monkeypatch)

    caminho_relatorio = tmp_path / config.NOME_RELATORIO
    assert caminho_relatorio.exists()


def test_exportar_relatorio_csv_contem_cabecalho(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    executar_exportacao_csv_de_teste(tmp_path, monkeypatch)

    caminho_relatorio = tmp_path / config.NOME_RELATORIO

    with open(caminho_relatorio, "r", encoding="utf-8-sig") as arquivo:
        leitor = csv.reader(arquivo, delimiter=";")
        linhas = list(leitor)
        assert linhas[0] == ["ID", "Título", "Descrição", "Status", "Data de criação"]


def test_exportar_relatorio_csv_contem_tarefa_cadastrada(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    executar_exportacao_csv_de_teste(tmp_path, monkeypatch)

    caminho_relatorio = tmp_path / config.NOME_RELATORIO

    with open(caminho_relatorio, "r", encoding="utf-8-sig") as arquivo:
        leitor = csv.reader(arquivo, delimiter=";")
        linhas = list(leitor)
        assert linhas[1][0] == "1"
        assert linhas[1][1] == TITULO_TESTE
        assert linhas[1][2] == DESCRICAO_TESTE
        assert linhas[1][3] == config.STATUS_PENDENTE
        assert linhas[1][4] == DATA_TESTE


def test_exportar_relatorio_csv_sem_tarefas_retorna_false(tmp_path, monkeypatch):
    preparar_banco_temporario(tmp_path, monkeypatch)

    preparar_exportacao_sem_interacao(tmp_path, monkeypatch)

    resultado = relatorios.exportar_relatorio_csv()
    assert resultado is False


def test_exportar_relatorio_csv_sem_tarefas_nao_cria_arquivo(tmp_path, monkeypatch):
    preparar_banco_temporario(tmp_path, monkeypatch)

    preparar_exportacao_sem_interacao(tmp_path, monkeypatch)

    resultado = relatorios.exportar_relatorio_csv()
    caminho_relatorio = tmp_path / config.NOME_RELATORIO
    assert resultado is False
    assert not caminho_relatorio.exists()