from app import config, database

TITULO_TESTE = "Gerenciador de Tarefas"
DESCRICAO_TESTE = "Pytest"
DATA_TESTE = "2026-06-29 10:00"
NOVO_TITULO_TESTE = "Tarefa Atualizada"
NOVA_DESCRICAO_TESTE = "Descrição atualizada"


def preparar_banco_temporario(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PASTA_DADOS", str(tmp_path))
    resultado = database.criar_tabela()
    assert resultado is True


def preparar_banco_com_tarefa(tmp_path, monkeypatch):
    preparar_banco_temporario(tmp_path, monkeypatch)

    resultado = database.inserir_tarefa(TITULO_TESTE, DESCRICAO_TESTE, DATA_TESTE)
    assert resultado is True


def test_criar_tabela_retorna_true(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PASTA_DADOS", str(tmp_path))
    resultado = database.criar_tabela()
    assert resultado is True


def test_criar_tabela_cria_arquivo_do_banco(tmp_path, monkeypatch):
    preparar_banco_temporario(tmp_path, monkeypatch)

    caminho_banco = tmp_path / config.NOME_BANCO
    assert caminho_banco.exists()


def test_inserir_tarefa_retorna_true(tmp_path, monkeypatch):
    preparar_banco_temporario(tmp_path, monkeypatch)

    resultado = database.inserir_tarefa(TITULO_TESTE, DESCRICAO_TESTE, DATA_TESTE)
    assert resultado is True


def test_buscar_todas_tarefas_retorna_tarefas_cadastradas(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    resultado = database.buscar_todas_tarefas()
    assert isinstance(resultado, list)
    assert len(resultado) == 1
    assert resultado[0][1] == TITULO_TESTE
    assert resultado[0][2] == DESCRICAO_TESTE
    assert resultado[0][3] == config.STATUS_PENDENTE
    assert resultado[0][4] == DATA_TESTE


def test_buscar_tarefa_por_id_existente_retorna_tarefa(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    busca_ok, tarefa_encontrada = database.buscar_tarefa_por_id(1)
    assert busca_ok is True
    assert tarefa_encontrada is not None
    assert tarefa_encontrada[0] == 1
    assert tarefa_encontrada[1] == TITULO_TESTE
    assert tarefa_encontrada[2] == DESCRICAO_TESTE
    assert tarefa_encontrada[3] == config.STATUS_PENDENTE
    assert tarefa_encontrada[4] == DATA_TESTE


def test_buscar_tarefa_por_id_inexistente_retorna_none(tmp_path, monkeypatch):
    preparar_banco_temporario(tmp_path, monkeypatch)

    busca_ok, tarefa_encontrada = database.buscar_tarefa_por_id(999)
    assert busca_ok is True
    assert tarefa_encontrada is None


def test_buscar_tarefa_por_id_none_retorna_false_e_none(tmp_path, monkeypatch):
    preparar_banco_temporario(tmp_path, monkeypatch)

    busca_ok, tarefa_encontrada = database.buscar_tarefa_por_id(None)
    assert busca_ok is False
    assert tarefa_encontrada is None


def test_buscar_tarefas_por_status_pendente(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    tarefas_encontradas = database.buscar_tarefas_por_status(config.STATUS_PENDENTE)
    assert isinstance(tarefas_encontradas, list)
    assert len(tarefas_encontradas) == 1
    assert tarefas_encontradas[0][1] == TITULO_TESTE
    assert tarefas_encontradas[0][2] == DESCRICAO_TESTE
    assert tarefas_encontradas[0][3] == config.STATUS_PENDENTE
    assert tarefas_encontradas[0][4] == DATA_TESTE


def test_buscar_tarefas_por_status_concluida(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    resultado_concluir = database.concluir_tarefa_no_banco(1)
    assert resultado_concluir is True

    resultado = database.buscar_tarefas_por_status(config.STATUS_CONCLUIDA)
    assert isinstance(resultado, list)
    assert len(resultado) == 1
    assert resultado[0][1] == TITULO_TESTE
    assert resultado[0][2] == DESCRICAO_TESTE
    assert resultado[0][3] == config.STATUS_CONCLUIDA
    assert resultado[0][4] == DATA_TESTE


def test_buscar_tarefas_por_status_sem_resultados_retorna_lista_vazia(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    resultado = database.buscar_tarefas_por_status(config.STATUS_CONCLUIDA)
    assert isinstance(resultado, list)
    assert resultado == []


def test_buscar_tarefas_por_titulo_encontra_termo_parcial(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    resultado = database.buscar_tarefas_por_titulo("Gerenciador")
    assert isinstance(resultado, list)
    assert len(resultado) == 1
    assert resultado[0][1] == TITULO_TESTE
    assert resultado[0][2] == DESCRICAO_TESTE
    assert resultado[0][3] == config.STATUS_PENDENTE
    assert resultado[0][4] == DATA_TESTE


def test_buscar_tarefas_por_titulo_sem_resultados_retorna_lista_vazia(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    resultado = database.buscar_tarefas_por_titulo("Inexistente")
    assert isinstance(resultado, list)
    assert resultado == []


def test_buscar_todas_tarefas_retorna_lista_vazia_quando_nao_tem_tarefas(tmp_path, monkeypatch):
    preparar_banco_temporario(tmp_path, monkeypatch)

    resultado = database.buscar_todas_tarefas()
    assert isinstance(resultado, list)
    assert resultado == []


def test_concluir_tarefa_no_banco_altera_status_para_concluida(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    resultado = database.concluir_tarefa_no_banco(1)
    assert resultado is True

    busca_ok, tarefa_encontrada = database.buscar_tarefa_por_id(1)
    assert busca_ok is True
    assert tarefa_encontrada is not None
    assert tarefa_encontrada[3] == config.STATUS_CONCLUIDA


def test_atualizar_tarefa_no_banco_retorna_true(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    resultado = database.atualizar_tarefa_no_banco(1, NOVO_TITULO_TESTE, NOVA_DESCRICAO_TESTE)
    assert resultado is True


def test_atualizar_tarefa_no_banco_altera_titulo_e_descricao(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    resultado_atualizar = database.atualizar_tarefa_no_banco(1, NOVO_TITULO_TESTE, NOVA_DESCRICAO_TESTE)
    assert resultado_atualizar is True

    busca_ok, tarefa_encontrada = database.buscar_tarefa_por_id(1)
    assert busca_ok is True
    assert tarefa_encontrada is not None
    assert tarefa_encontrada[1] == NOVO_TITULO_TESTE
    assert tarefa_encontrada[2] == NOVA_DESCRICAO_TESTE
    assert tarefa_encontrada[3] == config.STATUS_PENDENTE


def test_excluir_tarefa_no_banco_remove_tarefa(tmp_path, monkeypatch):
    preparar_banco_com_tarefa(tmp_path, monkeypatch)

    resultado_excluir = database.excluir_tarefa_no_banco(1)
    assert resultado_excluir is True

    busca_ok, tarefa_encontrada = database.buscar_tarefa_por_id(1)
    assert busca_ok is True
    assert tarefa_encontrada is None