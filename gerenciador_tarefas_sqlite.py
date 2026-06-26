# Projeto: Gerenciador de Tarefas
# Objetivo: CRUD simples em terminal usando Python + SQLite.
# Observação: os comentários abaixo explicam partes importantes sem alterar a lógica.

import os
import sqlite3
import csv
from datetime import datetime
from time import sleep

# =========================
# Configurações e constantes
# =========================

# Nome do arquivo do banco de dados SQLite.
NOME_BANCO = "tarefas.db"

# Status usados no banco. Mantidos sem acento para facilitar comparação interna.
STATUS_PENDENTE = "pendente"
STATUS_CONCLUIDA = "concluida"

# Medidas usadas para manter o layout do terminal alinhado.
LARGURA_LAYOUT = 44

TAMANHO_ID = 4
TAMANHO_TITULO = 20
TAMANHO_DESCRICAO = 25
TAMANHO_STATUS = 12
TAMANHO_DATA = 19

FORMATO_DATA = "%Y-%m-%d %H:%M"

# Representa uma tarefa retornada do banco:
# (id_tarefa, titulo, descricao, status, data_criacao)
Tarefa = tuple[int, str, str, str, str]


# =========================
# Funções utilitárias
# =========================

# Limpa o terminal conforme o sistema operacional.
def limpar_tela() -> None:
    os.system("cls" if os.name == "nt" else "clear")


# Pausa a execução para o usuário conseguir ler a mensagem da tela.
def pausar() -> None:
    input("\nPressione ENTER para continuar...")


# Pausa e limpa a tela em seguida, usado após mensagens de retorno.
def pausar_e_limpar() -> None:
    pausar()
    limpar_tela()


# Limita textos grandes e completa espaços para manter a tabela alinhada.
def organizar_e_limitar_texto(texto: str, tamanho: int) -> str:
    texto_corrigido = texto

    if len(texto) > tamanho:
        texto_corrigido = texto[:tamanho - 3] + "..."

    texto_organizado = texto_corrigido.ljust(tamanho)

    return texto_organizado


# Formata o status apenas para exibição ao usuário.
def formatar_status(status: str) -> str:
    status_formatado = status.replace(STATUS_CONCLUIDA, "concluída")

    return status_formatado


# Confirma ações importantes, como editar, concluir ou excluir uma tarefa.
def confirmar_acao(mensagem: str) -> bool:
    while True:
        print()
        confirmacao = input(mensagem).strip().lower()

        if confirmacao == "s":
            return True

        elif confirmacao == "n":
            return False

        else:
            print("\n[AVISO] Opção inválida. Digite apenas 's' para sim ou 'n' para não.")
            continue


# Mostra uma pequena animação antes de voltar ao menu.
def voltar_ao_menu(mensagem: str = "Voltando ao menu...") -> None:
    tempo_escrita = 1.0

    tempo_total = 1.5

    print()

    intervalo = tempo_escrita / len(mensagem)

    for letra in mensagem:

        print(letra, end="", flush=True)

        sleep(intervalo)

    sleep(tempo_total - tempo_escrita)

    limpar_tela()


# =========================
# Conexão com banco de dados
# =========================

# Abre conexão com o banco e retorna conexão + cursor.
# Se falhar, retorna None para o restante do sistema tratar o erro.
def conectar_banco() -> tuple[sqlite3.Connection, sqlite3.Cursor] | None:
    try:
        conexao = sqlite3.connect(NOME_BANCO)
        cursor = conexao.cursor()
        return (conexao, cursor)

    except sqlite3.Error as ex:
        print(f"\n[ERRO] Erro no SQLite: {ex}")
        pausar_e_limpar()
        return None

    except Exception as ex:
        print(f"\n[ERRO] Erro inesperado: {ex}")
        pausar_e_limpar()
        return None


# Salva alterações no banco e fecha conexão/cursor no final.
# Retorna True se salvou corretamente e False se ocorreu erro.
def salvar_e_fechar(conexao: sqlite3.Connection, cursor: sqlite3.Cursor) -> bool:
    try:
        conexao.commit()
        return True

    except sqlite3.Error as ex:
        print(f"\n[ERRO] Erro ao salvar alterações: {ex}")
        conexao.rollback()
        return False

    finally:
        cursor.close()
        conexao.close()


# Fecha cursor e conexão quando não há alteração para salvar.
def fechar_banco(conexao: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
    cursor.close()
    conexao.close()


# =========================
# Banco de dados
# =========================

# Cria a tabela principal caso ela ainda não exista.
def criar_tabela() -> bool:
    dados_conexao = conectar_banco()

    if dados_conexao is None:
        return False

    conexao, cursor = dados_conexao

    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS tarefas (
                id_tarefa INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                status TEXT NOT NULL,
                data_criacao TEXT NOT NULL)""")

    except sqlite3.Error as ex:
        print(f"[ERRO] Erro ao criar tabela: {ex}")
        conexao.rollback()
        fechar_banco(conexao, cursor)
        return False

    return salvar_e_fechar(conexao, cursor)


# Insere uma nova tarefa no banco com status inicial pendente.
def inserir_tarefa(titulo: str, descricao: str, data: str) -> bool:
    dados_conexao = conectar_banco()

    if dados_conexao is None:
        return False

    conexao, cursor = dados_conexao

    comando = ("""INSERT INTO tarefas
                (titulo, descricao, status, data_criacao) VALUES
                (?, ?, ?, ?)""")

    valores = (titulo, descricao, STATUS_PENDENTE, data)

    try:
        cursor.execute(comando, valores)

    except sqlite3.Error as ex:
        print(f"\n[ERRO] Erro ao cadastrar tarefa: {ex}")
        conexao.rollback()
        fechar_banco(conexao, cursor)
        return False

    return salvar_e_fechar(conexao, cursor)


# Retorna todas as tarefas.
# [] significa busca feita sem resultados; None significa erro na busca.
def buscar_todas_tarefas() -> list[Tarefa] | None:
    dados_conexao = conectar_banco()

    if dados_conexao is None:
        return None

    conexao, cursor = dados_conexao

    try:
        cursor.execute("""SELECT id_tarefa, titulo, descricao, status, data_criacao FROM tarefas ORDER BY id_tarefa""")
        tarefas = cursor.fetchall()

    except sqlite3.Error as ex:
        print(f"\n[ERRO] Erro ao buscar tarefas: {ex}")
        fechar_banco(conexao, cursor)
        return None

    fechar_banco(conexao, cursor)

    return tarefas


# Busca uma tarefa específica pelo ID.
# Retorno:
# - (False, None): erro na busca/conexão
# - (True, None): busca funcionou, mas o ID não existe
# - (True, tarefa): tarefa encontrada
def buscar_tarefa_por_id(id_tarefa: int | None) -> tuple[bool, Tarefa | None]:
    if id_tarefa is None:
        return False, None

    dados_conexao = conectar_banco()

    if dados_conexao is None:
        return False, None

    conexao, cursor = dados_conexao

    id_tuple = (id_tarefa,)

    try:
        query = "SELECT id_tarefa, titulo, descricao, status, data_criacao FROM tarefas WHERE id_tarefa = ?"
        cursor.execute(query, id_tuple)
        resultado = cursor.fetchone()

    except sqlite3.Error as ex:
        print(f"\n[ERRO] Erro ao buscar tarefas por ID: {ex}")
        fechar_banco(conexao, cursor)
        return False, None

    fechar_banco(conexao, cursor)

    return (True, resultado)


# Busca tarefas filtrando pelo status informado.
# Segue a mesma ideia: lista vazia = sem resultados; None = erro.
def buscar_tarefas_por_status(status: str) -> list[Tarefa] | None:
    dados_conexao = conectar_banco()

    if dados_conexao is None:
        return None

    conexao, cursor = dados_conexao

    query = "SELECT id_tarefa, titulo, descricao, status, data_criacao FROM tarefas WHERE status = ? ORDER BY id_tarefa"
    texto_tuple = (status,)

    try:
        cursor.execute(query, texto_tuple)
        tarefas = cursor.fetchall()

    except sqlite3.Error as ex:
        print(f"\n[ERRO] Erro ao buscar tarefas por status: {ex}")
        fechar_banco(conexao, cursor)
        return None

    fechar_banco(conexao, cursor)

    return tarefas


# Pesquisa tarefas pelo título usando LIKE para encontrar termos parciais.
def buscar_tarefas_por_titulo(termo: str) -> list[Tarefa] | None:
    dados_conexao = conectar_banco()

    if dados_conexao is None:
        return None

    conexao, cursor = dados_conexao

    query = "SELECT id_tarefa, titulo, descricao, status, data_criacao FROM tarefas WHERE titulo LIKE ? ORDER BY id_tarefa"

    termo_buscado = f"%{termo}%"
    termo_tuple = (termo_buscado,)

    try:
        cursor.execute(query, termo_tuple)
        tarefas = cursor.fetchall()

    except sqlite3.Error as ex:
        print(f"\n[ERRO] Erro ao buscar tarefas: {ex}")
        fechar_banco(conexao, cursor)
        return None

    fechar_banco(conexao, cursor)

    return tarefas


# Atualiza o status da tarefa para concluída.
def concluir_tarefa_no_banco(id_tarefa: int) -> bool:
    dados_conexao = conectar_banco()

    if dados_conexao is None:
        return False

    conexao, cursor = dados_conexao

    update = """UPDATE tarefas
            SET status = ?
            WHERE id_tarefa = ?"""

    status_e_id = (STATUS_CONCLUIDA, id_tarefa)

    try:
        cursor.execute(update, status_e_id)

    except sqlite3.Error as ex:
        print(f"\n[ERRO] Erro ao concluir tarefa: {ex}")
        conexao.rollback()
        fechar_banco(conexao, cursor)
        return False

    return salvar_e_fechar(conexao, cursor)


# Atualiza título e descrição de uma tarefa existente.
def atualizar_tarefa_no_banco(id_tarefa: int, titulo: str, descricao: str) -> bool:
    dados_conexao = conectar_banco()

    if dados_conexao is None:
        return False

    conexao, cursor = dados_conexao

    parametros = (titulo, descricao, id_tarefa)

    update = ("""UPDATE tarefas
            SET titulo = ?,
            descricao = ?
            WHERE id_tarefa = ?""")

    try:
        cursor.execute(update, parametros)

    except sqlite3.Error as ex:
        print(f"\n[ERRO] Erro ao atualizar tarefa: {ex}")
        conexao.rollback()
        fechar_banco(conexao, cursor)
        return False

    return salvar_e_fechar(conexao, cursor)


# Remove uma tarefa do banco pelo ID.
def excluir_tarefa_no_banco(id_tarefa: int) -> bool:
    dados_conexao = conectar_banco()

    if dados_conexao is None:
        return False

    conexao, cursor = dados_conexao

    delete = "DELETE FROM tarefas WHERE id_tarefa = ?"

    id_tuple = (id_tarefa,)

    try:
        cursor.execute(delete, id_tuple)

    except sqlite3.Error as ex:
        print(f"\n[ERRO] Erro ao excluir tarefa: {ex}")
        conexao.rollback()
        fechar_banco(conexao, cursor)
        return False

    return salvar_e_fechar(conexao, cursor)


# =========================
# Interface
# =========================

# Exibe um cabeçalho padronizado para cada tela do sistema.
def mostrar_cabecalho(titulo: str, fechar: bool = True) -> None:
    limpar_tela()

    print("╔" + "═" * LARGURA_LAYOUT + "╗")
    print("║" + f"{titulo}".center(LARGURA_LAYOUT) + "║")

    if fechar:
        print("╚" + "═" * LARGURA_LAYOUT + "╝\n")
    else:
        print("╠" + "═" * LARGURA_LAYOUT + "╣")


# Menu principal do sistema.
def mostrar_menu() -> None:
    print("╔" + "═" * LARGURA_LAYOUT + "╗")
    print("║" + "GERENCIADOR DE TAREFAS".center(LARGURA_LAYOUT) + "║")
    print("║" + "Python + SQLite".center(LARGURA_LAYOUT) + "║")
    print("╠" + "═" * LARGURA_LAYOUT + "╣")
    print("║" + " [1] Cadastrar tarefa".ljust(LARGURA_LAYOUT) + "║")
    print("║" + " [2] Listar tarefas".ljust(LARGURA_LAYOUT) + "║")
    print("║" + " [3] Marcar tarefa como concluída".ljust(LARGURA_LAYOUT) + "║")
    print("║" + " [4] Editar tarefa".ljust(LARGURA_LAYOUT) + "║")
    print("║" + " [5] Excluir tarefa".ljust(LARGURA_LAYOUT) + "║")
    print("║" + " [6] Pesquisar tarefa por título".ljust(LARGURA_LAYOUT) + "║")
    print("║" + " [7] Exportar relatório CSV".ljust(LARGURA_LAYOUT) + "║")
    print("║" + " [0] Sair".ljust(LARGURA_LAYOUT) + "║")
    print("╚" + "═" * LARGURA_LAYOUT + "╝")


# Submenu usado para escolher o tipo de listagem.
def mostrar_menu_listagem() -> None:
    print("║" + " [1] Listar todas".ljust(LARGURA_LAYOUT) + "║")
    print("║" + " [2] Listar pendentes".ljust(LARGURA_LAYOUT) + "║")
    print("║" + " [3] Listar concluídas".ljust(LARGURA_LAYOUT) + "║")
    print("║" + " [0] Voltar".ljust(LARGURA_LAYOUT) + "║")
    print("╚" + "═" * LARGURA_LAYOUT + "╝")


# Cabeçalho da tabela de tarefas exibida no terminal.
def mostrar_cabecalho_listar_tarefas() -> None:
    id_tarefa = organizar_e_limitar_texto("ID", TAMANHO_ID)
    titulo = organizar_e_limitar_texto("TÍTULO", TAMANHO_TITULO)
    descricao = organizar_e_limitar_texto("DESCRIÇÃO", TAMANHO_DESCRICAO)
    status = organizar_e_limitar_texto("STATUS", TAMANHO_STATUS)
    data = organizar_e_limitar_texto("DATA", TAMANHO_DATA)

    linha_superior = (
        "╔" + "═" * (TAMANHO_ID + 2) +
        "╦" + "═" * (TAMANHO_TITULO + 2) +
        "╦" + "═" * (TAMANHO_DESCRICAO + 2) +
        "╦" + "═" * (TAMANHO_STATUS + 2) +
        "╦" + "═" * (TAMANHO_DATA + 2) +
        "╗"
    )

    linha_divisoria = (
        "╠" + "═" * (TAMANHO_ID + 2) +
        "╬" + "═" * (TAMANHO_TITULO + 2) +
        "╬" + "═" * (TAMANHO_DESCRICAO + 2) +
        "╬" + "═" * (TAMANHO_STATUS + 2) +
        "╬" + "═" * (TAMANHO_DATA + 2) +
        "╣"
    )

    print(linha_superior)
    print(f"║ {id_tarefa} ║ {titulo} ║ {descricao} ║ {status} ║ {data} ║")
    print(linha_divisoria)


# Exibe cada tarefa já formatada em linha de tabela.
def mostrar_linhas_tarefas(tarefas: list[Tarefa]) -> None:
    for tarefa in tarefas:
        id_tarefa, titulo, descricao, status, data_criacao = tarefa

        id_corrigido = organizar_e_limitar_texto(str(id_tarefa), TAMANHO_ID)
        titulo_corrigido = organizar_e_limitar_texto(titulo, TAMANHO_TITULO)
        descricao_corrigida = organizar_e_limitar_texto(descricao, TAMANHO_DESCRICAO)
        status_corrigido = formatar_status(status)
        status_formatado_e_alinhado = organizar_e_limitar_texto(status_corrigido, TAMANHO_STATUS)
        data_criacao_corrigida = organizar_e_limitar_texto(data_criacao, TAMANHO_DATA)

        print(
            f"║ {id_corrigido} ║ "
            f"{titulo_corrigido} ║ "
            f"{descricao_corrigida} ║ "
            f"{status_formatado_e_alinhado} ║ "
            f"{data_criacao_corrigida} ║"
        )

    linha_inferior = (
        "╚" + "═" * (TAMANHO_ID + 2) +
        "╩" + "═" * (TAMANHO_TITULO + 2) +
        "╩" + "═" * (TAMANHO_DESCRICAO + 2) +
        "╩" + "═" * (TAMANHO_STATUS + 2) +
        "╩" + "═" * (TAMANHO_DATA + 2) +
        "╝"
    )

    print(linha_inferior)


# Mostra os detalhes de uma tarefa encontrada pelo ID.
def mostrar_tarefa_encontrada(resultado: Tarefa) -> None:
    print("\nTarefa encontrada:")
    print(f"ID: {resultado[0]}")
    print(f"Título atual: {resultado[1]}")
    print(f"Descrição atual: {resultado[2]}")
    print(f"Status atual: {formatar_status(resultado[3])}")
    print(f"Data de criação: {resultado[4]}")


# =========================
# Entrada de dados
# =========================

# Solicita o ID da tarefa.
# Retorna None para entrada inválida e 0 para voltar ao menu.
def pedir_id_tarefa() -> int | None:
    buscar_id = input("Digite o ID da tarefa ou 0 para voltar: ").strip()

    if not buscar_id.isdigit():
        print("\n[AVISO] ID inválido. Digite apenas números.")
        pausar_e_limpar()
        return

    id_num = int(buscar_id)

    return id_num


# =========================
# Fluxo do sistema
# =========================

# Mostra o resultado das listagens e pesquisas.
# Diferencia erro no banco (None) de busca sem resultados ([]).
def mostrar_resultado_listagem(titulo: str, tarefas: list[Tarefa] | None, mensagem_vazia: str) -> None:
    mostrar_cabecalho(titulo)

    if tarefas is None:
        print("[ERRO] Não foi possível carregar as tarefas. Tente novamente.")
        return

    if not tarefas:
        print(mensagem_vazia)
        return

    mostrar_cabecalho_listar_tarefas()

    mostrar_linhas_tarefas(tarefas)


# Fluxo de cadastro de uma nova tarefa.
def cadastrar_tarefa() -> None:
    mostrar_cabecalho("CADASTRAR TAREFA")

    titulo_tarefa = input("Título da tarefa: ").strip()

    if not titulo_tarefa:
        print("\n[AVISO] O título não pode ficar vazio!")
        pausar_e_limpar()
        return

    descricao_tarefa = input("Descrição da tarefa: ").strip()

    data = datetime.now().strftime(FORMATO_DATA)

    sucesso = inserir_tarefa(titulo_tarefa, descricao_tarefa, data)

    if sucesso:
        print("\n[OK] Tarefa cadastrada com sucesso!")
    else:
        print("\n[ERRO] Não foi possível cadastrar a tarefa. Tente novamente.")

    pausar_e_limpar()


# Controla o submenu de listagem.
def listar_tarefas() -> None:
    while True:
        mostrar_cabecalho("LISTAR TAREFAS", fechar=False)

        mostrar_menu_listagem()

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            listar_todas_tarefas()

        elif opcao == "2":
            listar_tarefas_pendentes()

        elif opcao == "3":
            listar_tarefas_concluidas()

        elif opcao == "0":
            voltar_ao_menu()
            return

        else:
            print("\n[AVISO] Escolha uma opção entre 0 e 3.")
            pausar_e_limpar()
            continue

        pausar_e_limpar()


# Lista todas as tarefas cadastradas.
def listar_todas_tarefas() -> None:
    tarefas = buscar_todas_tarefas()

    mostrar_resultado_listagem("LISTAR TODAS TAREFAS", tarefas, "[AVISO] Nenhuma tarefa cadastrada.")


# Lista somente as tarefas pendentes.
def listar_tarefas_pendentes() -> None:
    tarefas = buscar_tarefas_por_status(STATUS_PENDENTE)

    mostrar_resultado_listagem("LISTAR TAREFAS PENDENTES", tarefas, "[AVISO] Nenhuma tarefa pendente encontrada.")


# Lista somente as tarefas concluídas.
def listar_tarefas_concluidas() -> None:
    tarefas = buscar_tarefas_por_status(STATUS_CONCLUIDA)

    mostrar_resultado_listagem("LISTAR TAREFAS CONCLUÍDAS", tarefas, "[AVISO] Nenhuma tarefa concluída encontrada.")


# Fluxo de pesquisa por uma palavra presente no título.
def pesquisar_tarefa_por_titulo() -> None:
    mostrar_cabecalho("PESQUISAR TAREFA POR TÍTULO")

    palavra_titulo = input("Digite uma palavra do título: ").strip()

    if not palavra_titulo:
        print("\n[AVISO] O termo de pesquisa não pode ficar vazio.")
        pausar_e_limpar()
        return

    tarefas = buscar_tarefas_por_titulo(palavra_titulo)

    mostrar_resultado_listagem("RESULTADO DA PESQUISA", tarefas, "[AVISO] Nenhuma tarefa encontrada com esse título.")

    pausar_e_limpar()


# Fluxo para marcar uma tarefa como concluída.
def marcar_tarefa_como_concluida() -> None:
    mostrar_cabecalho("MARCAR TAREFA COMO CONCLUÍDA")

    id_tarefa = pedir_id_tarefa()

    if id_tarefa == 0:
        voltar_ao_menu()
        return

    if id_tarefa is None:
        return

    busca_ok, resultado = buscar_tarefa_por_id(id_tarefa)

    if not busca_ok:
        print("\n[ERRO] Não foi possível buscar a tarefa no banco de dados. Tente novamente.")
        pausar_e_limpar()
        return

    if resultado is None:
        print("\n[AVISO] Nenhuma tarefa encontrada com esse ID.")
        pausar_e_limpar()
        return

    mostrar_tarefa_encontrada(resultado)

    if resultado[3] == STATUS_CONCLUIDA:
        print("\n[AVISO] Essa tarefa já está concluída.")
        pausar_e_limpar()
        return

    if confirmar_acao("Deseja marcar essa tarefa como concluída? [s/n]: "):
        sucesso = concluir_tarefa_no_banco(resultado[0])

        if sucesso:
            print("\n[OK] Tarefa marcada como concluída com sucesso!")
        else:
            print("\n[ERRO] Não foi possível marcar a tarefa como concluída. Tente novamente.")

    else:
        print("\n[AVISO] Operação cancelada.")
        pausar_e_limpar()
        return

    pausar_e_limpar()


# Fluxo de edição de título e descrição da tarefa.
def editar_tarefa() -> None:
    mostrar_cabecalho("EDITAR TAREFA")

    id_tarefa = pedir_id_tarefa()

    if id_tarefa == 0:
        voltar_ao_menu()
        return

    if id_tarefa is None:
        return

    busca_ok, resultado = buscar_tarefa_por_id(id_tarefa)

    if not busca_ok:
        print("\n[ERRO] Não foi possível buscar a tarefa no banco de dados. Tente novamente.")
        pausar_e_limpar()
        return

    if resultado is None:
        print("\n[AVISO] Nenhuma tarefa encontrada com esse ID.")
        pausar_e_limpar()
        return

    mostrar_tarefa_encontrada(resultado)

    if resultado[3] == STATUS_CONCLUIDA:
        print("\n[AVISO] Essa tarefa já está concluída e não pode ser editada.")
        pausar_e_limpar()
        return

    novo_titulo = input("\nNovo título (ENTER para manter o atual): ").strip()
    nova_descricao = input("Nova descrição (ENTER para manter a atual): ").strip()

    titulo_final = novo_titulo if novo_titulo != "" else resultado[1]
    descricao_final = nova_descricao if nova_descricao != "" else resultado[2]

    if titulo_final == resultado[1] and descricao_final == resultado[2]:
        print("\n[AVISO] Os dados informados são iguais aos atuais. Nenhuma alteração foi feita.")
        pausar_e_limpar()
        return

    if confirmar_acao("Deseja salvar as alterações? [s/n]: "):
        sucesso = atualizar_tarefa_no_banco(resultado[0], titulo_final, descricao_final)

        if sucesso:
            print("\n[OK] Tarefa atualizada com sucesso!")
        else:
            print("\n[ERRO] Não foi possível atualizar a tarefa. Tente novamente.")

    else:
        print("\n[AVISO] Edição cancelada.")
        pausar_e_limpar()
        return

    pausar_e_limpar()


# Fluxo de exclusão de uma tarefa.
def excluir_tarefa() -> None:
    mostrar_cabecalho("EXCLUIR TAREFA")

    id_tarefa = pedir_id_tarefa()

    if id_tarefa == 0:
        voltar_ao_menu()
        return

    if id_tarefa is None:
        return

    busca_ok, resultado = buscar_tarefa_por_id(id_tarefa)

    if not busca_ok:
        print("\n[ERRO] Não foi possível buscar a tarefa no banco de dados. Tente novamente.")
        pausar_e_limpar()
        return

    if resultado is None:
        print("\n[AVISO] Nenhuma tarefa encontrada com esse ID.")
        pausar_e_limpar()
        return

    mostrar_tarefa_encontrada(resultado)

    if confirmar_acao("Tem certeza que deseja excluir essa tarefa? [s/n]: "):
        sucesso = excluir_tarefa_no_banco(resultado[0])

        if sucesso:
            print("\n[OK] Tarefa excluída com sucesso!")
        else:
            print("\n[ERRO] Não foi possível excluir a tarefa. Tente novamente.")

    else:
        print("\n[AVISO] Exclusão cancelada.")
        pausar_e_limpar()
        return

    pausar_e_limpar()


# Fluxo de exportação do relatório CSV.
def exportar_relatorio_csv() -> None:
    mostrar_cabecalho("EXPORTAR RELATÓRIO CSV")

    tarefas = buscar_todas_tarefas()

    if tarefas is None:
        print("[ERRO] Não foi possível carregar as tarefas para exportação.")
        pausar_e_limpar()
        return
    
    if not tarefas:
        print("[AVISO] Nenhuma tarefa cadastrada para exportar.")
        pausar_e_limpar()
        return

    try:
        with open("relatorio_tarefas.csv", "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["ID", "Título", "Descrição", "Status", "Data de criação"])
            escritor.writerows(tarefas)
    
    except (OSError, csv.Error) as ex:
        print(f"\n[ERRO] Não foi possível gerar o relatório CSV: {ex}")
        pausar_e_limpar()
        return
    
    print("[OK] Relatório exportado com sucesso!")
    print("\nArquivo gerado: relatorio_tarefas.csv")
    print(f"Total de tarefas exportadas: {len(tarefas)}")
    pausar_e_limpar()


# Mensagem final ao encerrar o sistema.
def encerrar_programa() -> None:
    print("\nEncerrando o programa...")


# =========================
# Função principal
# =========================

# Função principal: cria a tabela e controla o loop do menu.
def main() -> None:
    limpar_tela()

    sucesso = criar_tabela()

    if not sucesso:
        print("[ERRO] Não foi possível iniciar o banco de dados.\n")
        return

    while True:
        mostrar_menu()

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            cadastrar_tarefa()

        elif opcao == "2":
            listar_tarefas()

        elif opcao == "3":
            marcar_tarefa_como_concluida()

        elif opcao == "4":
            editar_tarefa()

        elif opcao == "5":
            excluir_tarefa()

        elif opcao == "6":
            pesquisar_tarefa_por_titulo()

        elif opcao == "7":
            exportar_relatorio_csv()

        elif opcao == "0":
            encerrar_programa()
            break

        else:
            print("\n[AVISO] Escolha uma opção entre 0 e 7.")
            pausar_e_limpar()
            continue


if __name__ == "__main__":
    main()
