from app import utils, interface, database, tarefas, relatorios

# Mensagem final ao encerrar o sistema.
def encerrar_programa() -> None:
    print("\nEncerrando o programa...")


# =========================
# Função principal
# =========================

# Função principal: cria a tabela e controla o loop do menu.
def executar_sistema() -> None:
    utils.limpar_tela()

    sucesso = database.criar_tabela()

    if not sucesso:
        print("[ERRO] Não foi possível iniciar o banco de dados.")
        utils.pausar()
        return

    while True:
        interface.mostrar_menu()

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            tarefas.cadastrar_tarefa()

        elif opcao == "2":
            tarefas.listar_tarefas()

        elif opcao == "3":
            tarefas.marcar_tarefa_como_concluida()

        elif opcao == "4":
            tarefas.editar_tarefa()

        elif opcao == "5":
            tarefas.excluir_tarefa()

        elif opcao == "6":
            tarefas.pesquisar_tarefa_por_titulo()

        elif opcao == "7":
            relatorios.exportar_relatorio_csv()

        elif opcao == "0":
            encerrar_programa()
            break

        else:
            print("\n[AVISO] Escolha uma opção entre 0 e 7.")
            utils.pausar_e_limpar()
            continue