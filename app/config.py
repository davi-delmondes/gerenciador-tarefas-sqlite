# =========================
# Configurações e constantes
# =========================

# Nome do arquivo do banco de dados SQLite.
NOME_BANCO = "tarefas.db"

# Pastas usadas pelo sistema.
PASTA_DADOS = "data"
PASTA_EXPORTS = "exports"

# Nome do arquivo CSV gerado na exportação.
NOME_RELATORIO = "relatorio_tarefas.csv"

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