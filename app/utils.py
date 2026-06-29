from app import config

import os
from time import sleep

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
    status_formatado = status.replace(config.STATUS_CONCLUIDA, "concluída")

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