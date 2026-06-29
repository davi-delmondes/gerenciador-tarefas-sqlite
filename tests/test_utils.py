from app.utils import organizar_e_limitar_texto, formatar_status


def test_formatar_status_concluida_com_acento():
    resultado = formatar_status("concluida")
    assert resultado == "concluída"


def test_formatar_status_pendente_sem_alteracao():
    resultado = formatar_status("pendente")
    assert resultado == "pendente"


def test_organizar_texto_menor_que_limite():
    resultado = organizar_e_limitar_texto("Davi", 10)
    assert resultado == "Davi      "


def test_organizar_texto_maior_que_limite():
    resultado = organizar_e_limitar_texto("Gerenciador de Tarefas", 10)
    assert resultado == "Gerenci..."


def test_organizar_texto_com_tamanho_exato():
    resultado = organizar_e_limitar_texto("Python1234", 10)
    assert resultado == "Python1234"
    assert len(resultado) == 10


def test_organizar_texto_tem_tamanho_correto():
    resultado = organizar_e_limitar_texto("Davi", 10)
    assert len(resultado) == 10