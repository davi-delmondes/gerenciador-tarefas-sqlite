from app import utils

# =========================
# Entrada de dados
# =========================

# Solicita o ID da tarefa.
# Retorna None para entrada inválida e 0 para voltar ao menu.
def pedir_id_tarefa() -> int | None:
    buscar_id = input("Digite o ID da tarefa ou 0 para voltar: ").strip()

    if not buscar_id.isdigit():
        print("\n[AVISO] ID inválido. Digite apenas números.")
        utils.pausar_e_limpar()
        return

    id_num = int(buscar_id)

    return id_num