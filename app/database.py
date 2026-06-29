from app import config

import os
import sqlite3

# =========================
# Conexão com banco de dados
# =========================

# Abre conexão com o banco e retorna conexão + cursor.
# Se falhar, retorna None para o restante do sistema tratar o erro.
def conectar_banco() -> tuple[sqlite3.Connection, sqlite3.Cursor] | None:
    try:
        caminho_pasta = config.PASTA_DADOS
        nome_arquivo = config.NOME_BANCO
        caminho_completo = os.path.join(caminho_pasta, nome_arquivo)

        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)

        conexao = sqlite3.connect(caminho_completo)
        cursor = conexao.cursor()
        return (conexao, cursor)

    except sqlite3.Error:
        return None

    except Exception:
        return None


# Salva alterações no banco e fecha conexão/cursor no final.
# Retorna True se salvou corretamente e False se ocorreu erro.
def salvar_e_fechar(conexao: sqlite3.Connection, cursor: sqlite3.Cursor) -> bool:
    try:
        conexao.commit()
        return True

    except sqlite3.Error:
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

    except sqlite3.Error:
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

    valores = (titulo, descricao, config.STATUS_PENDENTE, data)

    try:
        cursor.execute(comando, valores)

    except sqlite3.Error:
        conexao.rollback()
        fechar_banco(conexao, cursor)
        return False

    return salvar_e_fechar(conexao, cursor)


# Retorna todas as tarefas.
# [] significa busca feita sem resultados; None significa erro na busca.
def buscar_todas_tarefas() -> list[config.Tarefa] | None:
    dados_conexao = conectar_banco()

    if dados_conexao is None:
        return None

    conexao, cursor = dados_conexao

    try:
        cursor.execute("""SELECT id_tarefa, titulo, descricao, status, data_criacao FROM tarefas ORDER BY id_tarefa""")
        tarefas = cursor.fetchall()

    except sqlite3.Error:
        fechar_banco(conexao, cursor)
        return None

    fechar_banco(conexao, cursor)

    return tarefas


# Busca uma tarefa específica pelo ID.
# Retorno:
# - (False, None): erro na busca/conexão
# - (True, None): busca funcionou, mas o ID não existe
# - (True, tarefa): tarefa encontrada
def buscar_tarefa_por_id(id_tarefa: int | None) -> tuple[bool, config.Tarefa | None]:
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

    except sqlite3.Error:
        fechar_banco(conexao, cursor)
        return False, None

    fechar_banco(conexao, cursor)

    return (True, resultado)


# Busca tarefas filtrando pelo status informado.
# Segue a mesma ideia: lista vazia = sem resultados; None = erro.
def buscar_tarefas_por_status(status: str) -> list[config.Tarefa] | None:
    dados_conexao = conectar_banco()

    if dados_conexao is None:
        return None

    conexao, cursor = dados_conexao

    query = "SELECT id_tarefa, titulo, descricao, status, data_criacao FROM tarefas WHERE status = ? ORDER BY id_tarefa"
    texto_tuple = (status,)

    try:
        cursor.execute(query, texto_tuple)
        tarefas = cursor.fetchall()

    except sqlite3.Error:
        fechar_banco(conexao, cursor)
        return None

    fechar_banco(conexao, cursor)

    return tarefas


# Pesquisa tarefas pelo título usando LIKE para encontrar termos parciais.
def buscar_tarefas_por_titulo(termo: str) -> list[config.Tarefa] | None:
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

    except sqlite3.Error:
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

    status_e_id = (config.STATUS_CONCLUIDA, id_tarefa)

    try:
        cursor.execute(update, status_e_id)

    except sqlite3.Error:
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

    except sqlite3.Error:
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

    except sqlite3.Error:
        conexao.rollback()
        fechar_banco(conexao, cursor)
        return False

    return salvar_e_fechar(conexao, cursor)