from app import config, utils

# =========================
# Interface
# =========================

# Exibe um cabeçalho padronizado para cada tela do sistema.
def mostrar_cabecalho(titulo: str, fechar: bool = True) -> None:
    utils.limpar_tela()

    print("╔" + "═" * config.LARGURA_LAYOUT + "╗")
    print("║" + f"{titulo}".center(config.LARGURA_LAYOUT) + "║")

    if fechar:
        print("╚" + "═" * config.LARGURA_LAYOUT + "╝\n")
    else:
        print("╠" + "═" * config.LARGURA_LAYOUT + "╣")


# Menu principal do sistema.
def mostrar_menu() -> None:
    print("╔" + "═" * config.LARGURA_LAYOUT + "╗")
    print("║" + "GERENCIADOR DE TAREFAS".center(config.LARGURA_LAYOUT) + "║")
    print("║" + "Python + SQLite".center(config.LARGURA_LAYOUT) + "║")
    print("╠" + "═" * config.LARGURA_LAYOUT + "╣")
    print("║" + " [1] Cadastrar tarefa".ljust(config.LARGURA_LAYOUT) + "║")
    print("║" + " [2] Listar tarefas".ljust(config.LARGURA_LAYOUT) + "║")
    print("║" + " [3] Marcar tarefa como concluída".ljust(config.LARGURA_LAYOUT) + "║")
    print("║" + " [4] Editar tarefa".ljust(config.LARGURA_LAYOUT) + "║")
    print("║" + " [5] Excluir tarefa".ljust(config.LARGURA_LAYOUT) + "║")
    print("║" + " [6] Pesquisar tarefa por título".ljust(config.LARGURA_LAYOUT) + "║")
    print("║" + " [7] Exportar relatório CSV".ljust(config.LARGURA_LAYOUT) + "║")
    print("║" + " [0] Sair".ljust(config.LARGURA_LAYOUT) + "║")
    print("╚" + "═" * config.LARGURA_LAYOUT + "╝")


# Submenu usado para escolher o tipo de listagem.
def mostrar_menu_listagem() -> None:
    print("║" + " [1] Listar todas".ljust(config.LARGURA_LAYOUT) + "║")
    print("║" + " [2] Listar pendentes".ljust(config.LARGURA_LAYOUT) + "║")
    print("║" + " [3] Listar concluídas".ljust(config.LARGURA_LAYOUT) + "║")
    print("║" + " [0] Voltar".ljust(config.LARGURA_LAYOUT) + "║")
    print("╚" + "═" * config.LARGURA_LAYOUT + "╝")


# Cabeçalho da tabela de tarefas exibida no terminal.
def mostrar_cabecalho_listar_tarefas() -> None:
    id_tarefa = utils.organizar_e_limitar_texto("ID", config.TAMANHO_ID)
    titulo = utils.organizar_e_limitar_texto("TÍTULO", config.TAMANHO_TITULO)
    descricao = utils.organizar_e_limitar_texto("DESCRIÇÃO", config.TAMANHO_DESCRICAO)
    status = utils.organizar_e_limitar_texto("STATUS", config.TAMANHO_STATUS)
    data = utils.organizar_e_limitar_texto("DATA", config.TAMANHO_DATA)

    linha_superior = (
        "╔" + "═" * (config.TAMANHO_ID + 2) +
        "╦" + "═" * (config.TAMANHO_TITULO + 2) +
        "╦" + "═" * (config.TAMANHO_DESCRICAO + 2) +
        "╦" + "═" * (config.TAMANHO_STATUS + 2) +
        "╦" + "═" * (config.TAMANHO_DATA + 2) +
        "╗"
    )

    linha_divisoria = (
        "╠" + "═" * (config.TAMANHO_ID + 2) +
        "╬" + "═" * (config.TAMANHO_TITULO + 2) +
        "╬" + "═" * (config.TAMANHO_DESCRICAO + 2) +
        "╬" + "═" * (config.TAMANHO_STATUS + 2) +
        "╬" + "═" * (config.TAMANHO_DATA + 2) +
        "╣"
    )

    print(linha_superior)
    print(f"║ {id_tarefa} ║ {titulo} ║ {descricao} ║ {status} ║ {data} ║")
    print(linha_divisoria)


# Exibe cada tarefa já formatada em linha de tabela.
def mostrar_linhas_tarefas(tarefas: list[config.Tarefa]) -> None:
    for tarefa in tarefas:
        id_tarefa, titulo, descricao, status, data_criacao = tarefa

        id_corrigido = utils.organizar_e_limitar_texto(str(id_tarefa), config.TAMANHO_ID)
        titulo_corrigido = utils.organizar_e_limitar_texto(titulo, config.TAMANHO_TITULO)
        descricao_corrigida = utils.organizar_e_limitar_texto(descricao, config.TAMANHO_DESCRICAO)
        status_corrigido = utils.formatar_status(status)
        status_formatado_e_alinhado = utils.organizar_e_limitar_texto(status_corrigido, config.TAMANHO_STATUS)
        data_criacao_corrigida = utils.organizar_e_limitar_texto(data_criacao, config.TAMANHO_DATA)

        print(
            f"║ {id_corrigido} ║ "
            f"{titulo_corrigido} ║ "
            f"{descricao_corrigida} ║ "
            f"{status_formatado_e_alinhado} ║ "
            f"{data_criacao_corrigida} ║"
        )

    linha_inferior = (
        "╚" + "═" * (config.TAMANHO_ID + 2) +
        "╩" + "═" * (config.TAMANHO_TITULO + 2) +
        "╩" + "═" * (config.TAMANHO_DESCRICAO + 2) +
        "╩" + "═" * (config.TAMANHO_STATUS + 2) +
        "╩" + "═" * (config.TAMANHO_DATA + 2) +
        "╝"
    )

    print(linha_inferior)


# Mostra os detalhes de uma tarefa encontrada pelo ID.
def mostrar_tarefa_encontrada(resultado: config.Tarefa) -> None:
    print("\nTarefa encontrada:")
    print(f"ID: {resultado[0]}")
    print(f"Título atual: {resultado[1]}")
    print(f"Descrição atual: {resultado[2]}")
    print(f"Status atual: {utils.formatar_status(resultado[3])}")
    print(f"Data de criação: {resultado[4]}")



# Mostra o resultado das listagens e pesquisas.
# Diferencia erro no banco (None) de busca sem resultados ([]).
def mostrar_resultado_listagem(titulo: str, tarefas: list[config.Tarefa] | None, mensagem_vazia: str) -> None:
    mostrar_cabecalho(titulo)

    if tarefas is None:
        print("[ERRO] Não foi possível carregar as tarefas. Tente novamente.")
        return

    if not tarefas:
        print(mensagem_vazia)
        return

    mostrar_cabecalho_listar_tarefas()

    mostrar_linhas_tarefas(tarefas)