from app import utils, config, interface, entradas, database

from datetime import datetime

# =========================
# Fluxo do sistema
# =========================


# Fluxo de cadastro de uma nova tarefa.
def cadastrar_tarefa() -> None:
    interface.mostrar_cabecalho("CADASTRAR TAREFA")

    titulo_tarefa = input("Título da tarefa: ").strip()

    if not titulo_tarefa:
        print("\n[AVISO] O título não pode ficar vazio!")
        utils.pausar_e_limpar()
        return

    descricao_tarefa = input("Descrição da tarefa: ").strip()

    data = datetime.now().strftime(config.FORMATO_DATA)

    sucesso = database.inserir_tarefa(titulo_tarefa, descricao_tarefa, data)

    if sucesso:
        print("\n[OK] Tarefa cadastrada com sucesso!")
    else:
        print("\n[ERRO] Não foi possível cadastrar a tarefa. Tente novamente.")

    utils.pausar_e_limpar()


# Controla o submenu de listagem.
def listar_tarefas() -> None:
    while True:
        interface.mostrar_cabecalho("LISTAR TAREFAS", fechar=False)

        interface.mostrar_menu_listagem()

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            listar_todas_tarefas()

        elif opcao == "2":
            listar_tarefas_pendentes()

        elif opcao == "3":
            listar_tarefas_concluidas()

        elif opcao == "0":
            utils.voltar_ao_menu()
            return

        else:
            print("\n[AVISO] Escolha uma opção entre 0 e 3.")
            utils.pausar_e_limpar()
            continue

        utils.pausar_e_limpar()


# Lista todas as tarefas cadastradas.
def listar_todas_tarefas() -> None:
    tarefas = database.buscar_todas_tarefas()

    interface.mostrar_resultado_listagem("LISTAR TODAS TAREFAS", tarefas, "[AVISO] Nenhuma tarefa cadastrada.")


# Lista somente as tarefas pendentes.
def listar_tarefas_pendentes() -> None:
    tarefas = database.buscar_tarefas_por_status(config.STATUS_PENDENTE)

    interface.mostrar_resultado_listagem("LISTAR TAREFAS PENDENTES", tarefas, "[AVISO] Nenhuma tarefa pendente encontrada.")


# Lista somente as tarefas concluídas.
def listar_tarefas_concluidas() -> None:
    tarefas = database.buscar_tarefas_por_status(config.STATUS_CONCLUIDA)

    interface.mostrar_resultado_listagem("LISTAR TAREFAS CONCLUÍDAS", tarefas, "[AVISO] Nenhuma tarefa concluída encontrada.")


# Fluxo de pesquisa por uma palavra presente no título.
def pesquisar_tarefa_por_titulo() -> None:
    interface.mostrar_cabecalho("PESQUISAR TAREFA POR TÍTULO")

    palavra_titulo = input("Digite uma palavra do título: ").strip()

    if not palavra_titulo:
        print("\n[AVISO] O termo de pesquisa não pode ficar vazio.")
        utils.pausar_e_limpar()
        return

    tarefas = database.buscar_tarefas_por_titulo(palavra_titulo)

    interface.mostrar_resultado_listagem("RESULTADO DA PESQUISA", tarefas, "[AVISO] Nenhuma tarefa encontrada com esse título.")

    utils.pausar_e_limpar()


# Fluxo para marcar uma tarefa como concluída.
def marcar_tarefa_como_concluida() -> None:
    interface.mostrar_cabecalho("MARCAR TAREFA COMO CONCLUÍDA")

    id_tarefa = entradas.pedir_id_tarefa()

    if id_tarefa == 0:
        utils.voltar_ao_menu()
        return

    if id_tarefa is None:
        return

    busca_ok, resultado = database.buscar_tarefa_por_id(id_tarefa)

    if not busca_ok:
        print("\n[ERRO] Não foi possível buscar a tarefa no banco de dados. Tente novamente.")
        utils.pausar_e_limpar()
        return

    if resultado is None:
        print("\n[AVISO] Nenhuma tarefa encontrada com esse ID.")
        utils.pausar_e_limpar()
        return

    interface.mostrar_tarefa_encontrada(resultado)

    if resultado[3] == config.STATUS_CONCLUIDA:
        print("\n[AVISO] Essa tarefa já está concluída.")
        utils.pausar_e_limpar()
        return

    if utils.confirmar_acao("Deseja marcar essa tarefa como concluída? [s/n]: "):
        sucesso = database.concluir_tarefa_no_banco(resultado[0])

        if sucesso:
            print("\n[OK] Tarefa marcada como concluída com sucesso!")
        else:
            print("\n[ERRO] Não foi possível marcar a tarefa como concluída. Tente novamente.")

    else:
        print("\n[AVISO] Operação cancelada.")
        utils.pausar_e_limpar()
        return

    utils.pausar_e_limpar()


# Fluxo de edição de título e descrição da tarefa.
def editar_tarefa() -> None:
    interface.mostrar_cabecalho("EDITAR TAREFA")

    id_tarefa = entradas.pedir_id_tarefa()

    if id_tarefa == 0:
        utils.voltar_ao_menu()
        return

    if id_tarefa is None:
        return

    busca_ok, resultado = database.buscar_tarefa_por_id(id_tarefa)

    if not busca_ok:
        print("\n[ERRO] Não foi possível buscar a tarefa no banco de dados. Tente novamente.")
        utils.pausar_e_limpar()
        return

    if resultado is None:
        print("\n[AVISO] Nenhuma tarefa encontrada com esse ID.")
        utils.pausar_e_limpar()
        return

    interface.mostrar_tarefa_encontrada(resultado)

    if resultado[3] == config.STATUS_CONCLUIDA:
        print("\n[AVISO] Essa tarefa já está concluída e não pode ser editada.")
        utils.pausar_e_limpar()
        return

    novo_titulo = input("\nNovo título (ENTER para manter o atual): ").strip()
    nova_descricao = input("Nova descrição (ENTER para manter a atual): ").strip()

    titulo_final = novo_titulo if novo_titulo != "" else resultado[1]
    descricao_final = nova_descricao if nova_descricao != "" else resultado[2]

    if titulo_final == resultado[1] and descricao_final == resultado[2]:
        print("\n[AVISO] Os dados informados são iguais aos atuais. Nenhuma alteração foi feita.")
        utils.pausar_e_limpar()
        return

    if utils.confirmar_acao("Deseja salvar as alterações? [s/n]: "):
        sucesso = database.atualizar_tarefa_no_banco(resultado[0], titulo_final, descricao_final)

        if sucesso:
            print("\n[OK] Tarefa atualizada com sucesso!")
        else:
            print("\n[ERRO] Não foi possível atualizar a tarefa. Tente novamente.")

    else:
        print("\n[AVISO] Edição cancelada.")
        utils.pausar_e_limpar()
        return

    utils.pausar_e_limpar()


# Fluxo de exclusão de uma tarefa.
def excluir_tarefa() -> None:
    interface.mostrar_cabecalho("EXCLUIR TAREFA")

    id_tarefa = entradas.pedir_id_tarefa()

    if id_tarefa == 0:
        utils.voltar_ao_menu()
        return

    if id_tarefa is None:
        return

    busca_ok, resultado = database.buscar_tarefa_por_id(id_tarefa)

    if not busca_ok:
        print("\n[ERRO] Não foi possível buscar a tarefa no banco de dados. Tente novamente.")
        utils.pausar_e_limpar()
        return

    if resultado is None:
        print("\n[AVISO] Nenhuma tarefa encontrada com esse ID.")
        utils.pausar_e_limpar()
        return

    interface.mostrar_tarefa_encontrada(resultado)

    if utils.confirmar_acao("Tem certeza que deseja excluir essa tarefa? [s/n]: "):
        sucesso = database.excluir_tarefa_no_banco(resultado[0])

        if sucesso:
            print("\n[OK] Tarefa excluída com sucesso!")
        else:
            print("\n[ERRO] Não foi possível excluir a tarefa. Tente novamente.")

    else:
        print("\n[AVISO] Exclusão cancelada.")
        utils.pausar_e_limpar()
        return

    utils.pausar_e_limpar()